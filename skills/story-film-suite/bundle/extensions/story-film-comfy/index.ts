// Copyright 2026 Alan Guice (Badgids)
// SPDX-License-Identifier: Apache-2.0
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const RUNTIME = resolve(ROOT, "scripts/comfy_official_runtime.py");
const MAX_TEXT = 120_000;
const MAX_CAPTURE = 64 * 1024 * 1024;

const RequestSchema = Type.Object({
  action: Type.Union([
    Type.Literal("doctor"),
    Type.Literal("server-info"),
    Type.Literal("list-tools"),
    Type.Literal("search-tools"),
    Type.Literal("call"),
    Type.Literal("proxy-status"),
    Type.Literal("proxy-start"),
    Type.Literal("proxy-stop"),
    Type.Literal("v2-request"),
  ]),
  query: Type.Optional(Type.String()),
  tool: Type.Optional(Type.String()),
  arguments: Type.Optional(Type.Record(Type.String(), Type.Any())),
  method: Type.Optional(Type.String()),
  path: Type.Optional(Type.String()),
  body: Type.Optional(Type.Any()),
  comfyui_url: Type.Optional(Type.String()),
  v2_url: Type.Optional(Type.String()),
  upgrade: Type.Optional(Type.Boolean()),
});

type RuntimeResult = { ok?: boolean; error?: string; [key: string]: unknown };

function pythonCandidates(): string[] {
  const explicit = process.env.STORY_FILM_PYTHON?.trim();
  return explicit ? [explicit] : process.platform === "win32" ? ["python", "python3"] : ["python3", "python"];
}

function runOne(python: string, cwd: string, request: Record<string, unknown>, signal?: AbortSignal): Promise<RuntimeResult> {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(python, [RUNTIME, "request", "--project", cwd], {
      cwd,
      env: process.env,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    let captureExceeded = false;
    const append = (current: string, chunk: Buffer | string): string => {
      if (captureExceeded) return current;
      const next = current + chunk.toString();
      if (next.length > MAX_CAPTURE) {
        captureExceeded = true;
        try { child.kill("SIGTERM"); } catch {}
        return current;
      }
      return next;
    };
    child.stdout.on("data", chunk => { stdout = append(stdout, chunk); });
    child.stderr.on("data", chunk => { stderr = append(stderr, chunk); });
    const abort = () => { try { child.kill("SIGTERM"); } catch {} };
    if (signal) {
      if (signal.aborted) abort();
      else signal.addEventListener("abort", abort, { once: true });
    }
    child.on("error", reject);
    child.on("close", code => {
      signal?.removeEventListener("abort", abort);
      if (captureExceeded) {
        resolvePromise({ ok: false, error: "managed runtime response exceeded 64 MiB; narrow the MCP query or fetch outputs to files" });
        return;
      }
      const raw = stdout.trim();
      let value: RuntimeResult;
      try {
        value = raw ? JSON.parse(raw) as RuntimeResult : { ok: false, error: stderr.trim() || `managed runtime exited ${code}` };
      } catch {
        value = { ok: false, error: `managed runtime returned invalid JSON${stderr.trim() ? `: ${stderr.trim()}` : ""}` };
      }
      if (code && value.ok !== false) value = { ...value, ok: false, error: value.error || `managed runtime exited ${code}` };
      resolvePromise(value);
    });
    child.stdin.end(JSON.stringify(request));
  });
}

async function runRuntime(cwd: string, request: Record<string, unknown>, signal?: AbortSignal): Promise<RuntimeResult> {
  let last: unknown;
  for (const python of pythonCandidates()) {
    try {
      return await runOne(python, cwd, request, signal);
    } catch (error: any) {
      last = error;
      if (error?.code !== "ENOENT") throw error;
    }
  }
  throw last instanceof Error ? last : new Error("Python 3 was not found");
}

function highRiskMcpCall(tool: string, args: Record<string, unknown>): string | undefined {
  const name = tool.toLowerCase();
  if (/^(?:install_node|update_comfyui|switch_comfyui_version|download_model|partner_generate)$/.test(name)) {
    return `official comfy-mcp tool ${tool}`;
  }
  if ((name === "run_workflow" || name === "run_template") && args.confirm_spend === true) {
    return `${tool} with paid-partner spend confirmation`;
  }
  return undefined;
}

function resultText(value: RuntimeResult): string {
  const text = JSON.stringify(value, null, 2);
  return text.length <= MAX_TEXT ? text : text.slice(0, MAX_TEXT) + "\n... Story-Film truncated this display; narrow the query with search-tools.";
}

function storyProjectRoot(cwd: string): string | undefined {
  let here = resolve(cwd);
  for (;;) {
    if (existsSync(resolve(here, "00_project/state.json"))) return here;
    const parent = dirname(here);
    if (parent === here) return undefined;
    here = parent;
  }
}

export default function storyFilmComfy(pi: any): void {
  pi.on?.("before_agent_start", async (_event: any, ctx: any) => {
    if (!storyProjectRoot(ctx.cwd)) return undefined;
    return {
      systemPromptAppend: `\nSTORY-FILM MANAGED COMFY RUNTIME:\n- The Pi-native story_comfy tool is the primary interactive control surface for the user's existing ComfyUI. Start live Comfy work with story_comfy action=server-info and use action=search-tools when the exact official comfy-mcp verb is unknown.\n- Story-Film automatically bootstraps comfy-cli, comfy-mcp, and comfy-api-proxy into its separate managed runtime. Do not ask the user to install or configure those control packages or a generic MCP server.\n- The user owns ComfyUI itself and their model collection. Managed bootstrap never installs ComfyUI, models, or custom nodes.\n- References elsewhere to comfyui_control.py, model_inventory.py, comfyui_batch.py, resource_handoff.py, or workflow-catalog describe Story-Film's deterministic internal paths. Do not ask the user to run them and do not invoke them through permission-gated bash for ordinary interactive ComfyUI discovery/control when story_comfy can perform the operation.\n- Do not replace story_comfy with curl, wget, urllib, requests, httpx, aiohttp, raw /prompt loops, or guessed class_type graphs.\n`,
    };
  });

  pi.registerTool?.({
    name: "story_comfy",
    label: "Story-Film ComfyUI",
    description:
      "Primary Story-Film control surface for the user's existing ComfyUI. Story-Film automatically installs its own separate official comfy-cli/comfy-mcp/comfy-api-proxy control runtime on first use; it does NOT install ComfyUI or models. Start with server-info, use search-tools before generic call, and use the live official MCP tool surface rather than guessed nodes/workflows or raw curl/bash ComfyUI calls.",
    parameters: RequestSchema,
    async execute(_toolCallId: string, params: any, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      if (params.action === "call") {
        const tool = String(params.tool || "").trim();
        if (!tool) return { content: [{ type: "text", text: "story_comfy call requires tool." }], details: {}, isError: true };
        const args = params.arguments && typeof params.arguments === "object" ? params.arguments : {};
        const risk = highRiskMcpCall(tool, args);
        if (risk) {
          if (!ctx.hasUI || typeof ctx.ui?.confirm !== "function") {
            return { content: [{ type: "text", text: `${risk} requires explicit user approval in an interactive Pi session.` }], details: { approval_required: true }, isError: true };
          }
          const approved = await ctx.ui.confirm("Story-Film ComfyUI approval", `Allow ${risk}?`);
          if (!approved) return { content: [{ type: "text", text: `User declined ${risk}.` }], details: { approval_required: true, approved: false }, isError: true };
        }
      }
      onUpdate?.({ content: [{ type: "text", text: "Story-Film is using its managed official Comfy control runtime..." }] });
      const value = await runRuntime(ctx.cwd, params, signal);
      return {
        content: [{ type: "text", text: resultText(value) }],
        details: value,
        isError: value.ok === false,
      };
    },
  });

  pi.registerCommand?.("story-comfy", {
    description: "Check or bootstrap Story-Film's managed official Comfy control runtime.",
    handler: async (args: string, ctx: any) => {
      const action = (args || "doctor").trim().toLowerCase();
      if (action !== "doctor" && action !== "server-info") {
        ctx.ui.notify?.("Use /story-comfy doctor or /story-comfy server-info.", "info");
        return;
      }
      const value = await runRuntime(ctx.cwd, { action });
      ctx.ui.notify?.(value.ok === false ? String(value.error || "Story-Film Comfy runtime failed") : `Story-Film Comfy ${action}: ready`, value.ok === false ? "error" : "info");
    },
  });
}
