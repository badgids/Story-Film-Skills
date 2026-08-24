// Copyright 2026 Alan Guice (Badgids)
// SPDX-License-Identifier: Apache-2.0
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
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
    Type.Literal("model-inventory"),
    Type.Literal("model-search"),
    Type.Literal("mcp-status"),
    Type.Literal("workflow-catalog"),
    Type.Literal("workflow-fetch"),
    Type.Literal("node-search"),
    Type.Literal("node-info"),
    Type.Literal("node-path"),
    Type.Literal("workflow-validate"),
    Type.Literal("workflow-promote"),
    Type.Literal("list-tools"),
    Type.Literal("search-tools"),
    Type.Literal("call"),
    Type.Literal("proxy-status"),
    Type.Literal("proxy-start"),
    Type.Literal("proxy-stop"),
    Type.Literal("v2-request"),
  ]),
  query: Type.Optional(Type.String()),
  folder: Type.Optional(Type.String()),
  limit: Type.Optional(Type.Number()),
  source: Type.Optional(Type.String()),
  name: Type.Optional(Type.String()),
  module: Type.Optional(Type.String()),
  out_path: Type.Optional(Type.String()),
  workflow_path: Type.Optional(Type.String()),
  class_type: Type.Optional(Type.String()),
  from_type: Type.Optional(Type.String()),
  to_type: Type.Optional(Type.String()),
  max_depth: Type.Optional(Type.Number()),
  max_paths: Type.Optional(Type.Number()),
  tool: Type.Optional(Type.String()),
  arguments: Type.Optional(Type.Record(Type.String(), Type.Any())),
  method: Type.Optional(Type.String()),
  path: Type.Optional(Type.String()),
  body: Type.Optional(Type.Any()),
  comfyui_url: Type.Optional(Type.String()),
  v2_url: Type.Optional(Type.String()),
  project: Type.Optional(Type.String()),
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
    child.on("close", (code, closeSignal) => {
      signal?.removeEventListener("abort", abort);
      if (captureExceeded) {
        resolvePromise({ ok: false, error: "managed runtime response exceeded 64 MiB; narrow the MCP query or fetch outputs to files" });
        return;
      }
      const raw = stdout.trim();
      const exitError = signal?.aborted
        ? "managed runtime request was cancelled"
        : closeSignal
          ? `managed runtime terminated by ${closeSignal}`
          : code === null
            ? "managed runtime exited without a status"
            : `managed runtime exited ${code}`;
      let value: RuntimeResult;
      try {
        value = raw ? JSON.parse(raw) as RuntimeResult : { ok: false, error: stderr.trim() || exitError };
      } catch {
        value = { ok: false, error: `managed runtime returned invalid JSON${stderr.trim() ? `: ${stderr.trim()}` : ""}` };
      }
      if ((code || closeSignal) && value.ok !== false) value = { ...value, ok: false, error: value.error || exitError };
      resolvePromise(value);
    });
    child.stdin.end(JSON.stringify(request));
  });
}

function requestedProjectCwd(cwd: string, value: unknown): string {
  const raw = String(value ?? "").trim();
  if (!raw) return cwd;
  return raw.startsWith("~/") || raw.startsWith("~\\")
    ? resolve(homedir(), raw.slice(2))
    : resolve(cwd, raw);
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

const COMFY_DISCOVERY_BLOCK_REASON =
  "Story-Film blocks shell/filesystem ComfyUI discovery. Use story_comfy action=server-info for the live server, action=model-inventory or action=model-search for installed models, action=workflow-catalog for workflows inside Story-Film's comfyui_workflows directory, and action=node-search or action=node-info for nodes. Story-Film does not scan ComfyUI userdata, project workflow folders, external workflow paths, or template catalogs. Add custom workflows under comfyui_workflows/custom/<task>/<model>/.";

function comfyDiscoveryShellReason(command: string): string | undefined {
  const text = String(command || "").trim();
  if (!text) return undefined;

  // Story-Film's documented deterministic fallback remains allowed.
  if (/(?:comfy_official_runtime\.py|comfyui_control\.py|model_inventory\.py)/i.test(text)) return undefined;

  // Direct attempts to locate or interrogate the managed CLI belong behind story_comfy.
  if (/\bwhich\s+comfy\b/i.test(text) || /(?:^|\s)(?:\.\/)?comfy\s+(?:templates?|models?|generate)\b/i.test(text)) {
    return COMFY_DISCOVERY_BLOCK_REASON;
  }

  const liveTarget = /(?:[\\/]ComfyUI(?:[\\/]|\b)|\bcomfy-cli\b|\bextra_model_paths(?:\.yaml)?\b|\b(?:checkpoints|diffusion_models|unet|loras?|vae|clip_vision|text_encoders)\b|\.safetensors\b|\.ckpt\b|\/models(?:\/|\b)|\bobject_info\b|\bworkflow_templates\b|\buserdata\b|(?:127\.0\.0\.1|localhost):8188\b)/i;
  const discoveryOperation = /(?:\bfind\b|\bls\b|\blocate\b|\bwhich\b|\bwhereis\b|\bfd\b|\brg\b|\bgrep\b|\bcat\b|\bcurl\b|\bwget\b)/i;
  return liveTarget.test(text) && discoveryOperation.test(text) ? COMFY_DISCOVERY_BLOCK_REASON : undefined;
}

export default function storyFilmComfy(pi: any): void {
  pi.on?.("tool_call", async (event: any, ctx: any) => {
    const toolName = String(event?.toolName || "").toLowerCase();
    if (!["bash", "find", "ls", "grep"].includes(toolName)) return undefined;
    const input = event?.input || {};
    const command = toolName === "bash" ? String(input.command || "") : `${toolName} ${JSON.stringify(input)}`;
    const probe = `${String(ctx?.cwd || "")} ${command}`;
    const reason = comfyDiscoveryShellReason(probe);
    return reason ? { block: true, reason } : undefined;
  });

  pi.on?.("before_agent_start", async (_event: any, _ctx: any) => {
    return {
      systemPromptAppend: `\nSTORY-FILM MANAGED COMFY RUNTIME:\n- These ComfyUI rules apply whenever Story-Film is loaded, even when the current working directory is the parent of a Story-Film project or the project has not been initialized yet.\n- The Pi-native story_comfy tool is the primary interactive control surface for the user's existing ComfyUI. Start live Comfy work with story_comfy action=server-info. Before deciding that any local model is missing, run story_comfy action=model-inventory; use action=model-search to search the complete live inventory.\n- For ComfyUI installation/location, live server status, model inventory, model search, node discovery, or workflow discovery, never use bash/find/ls/which/locate, guessed personal paths, home-directory scans, model-folder scans, direct comfy-cli discovery commands, or raw config-file inspection. Use story_comfy.\n- A failed cd, missing guessed directory, empty checkpoints directory, or empty filesystem search is NEVER evidence that ComfyUI or a model is absent. The live Story-Film/ComfyUI registry is authoritative.\n- Never treat the checkpoints folder as the complete image/video model inventory. Valid local weights may be registered under unet, diffusion_models, checkpoints, diffusers, or model-choice inputs exposed by installed loader nodes. The live ComfyUI registry is authoritative, including extra_model_paths.yaml registrations.\n- Workflow discovery is NOT MCP tool-name search. For normal selection, call story_comfy action=workflow-catalog. It catalogs only Story-Film's comfyui_workflows directory: built-ins plus comfyui_workflows/custom/<task>/<model>/. Never scan ComfyUI userdata, project workflow folders, arbitrary external paths, or template catalogs. If the user supplies another existing workflow, copy it into the appropriate extension custom directory.\n- If the user explicitly asks Story-Film to create/build/author/design a new workflow, route to the bounded comfyui-workflow authoring path. Use live schemas, validate before promotion, and place reusable authored JSON under comfyui_workflows/custom/<task>/<model>/. Extension-only discovery does not disable workflow creation.\n- If no suitable workflow exists, synthesize only a project candidate workflow from node classes returned by node-search/node-info and type paths returned by node-path. Never invent a class_type, model choice, input name, output index, or connection type.\n- Candidate graphs belong under 04_generation/comfyui/candidates or templates. Run workflow-validate, repair every live-schema/link error, then use workflow-promote. Never write an unvalidated candidate directly into 04_generation/comfyui/workflows.\n- Building a workflow means composing JSON from ALREADY INSTALLED nodes. It does not mean creating a custom node. Never author code under custom_nodes, never invoke install_node as a workflow fallback, and never create/install/update a node pack unless the user explicitly asked for that separate action and approved it.\n- Use action=search-tools only to discover official comfy-mcp tool names; never use it to search for workflows, templates, model names, or node classes. Do not call template-related MCP tools. Native workflow/node actions remain available when comfy-mcp is unavailable. A search-tools miss is not permission to fall back to Bash.\n- Story-Film automatically bootstraps comfy-cli, comfy-mcp, and comfy-api-proxy into its separate managed runtime. Do not ask the user to install or configure those control packages or a generic MCP server.\n- The user owns ComfyUI itself and their model collection. Managed bootstrap never installs ComfyUI, models, or custom nodes.\n- References elsewhere to comfyui_control.py, model_inventory.py, comfyui_batch.py, resource_handoff.py, or workflow-catalog describe Story-Film's deterministic internal paths. Do not ask the user to run them and do not invoke them through permission-gated bash for ordinary interactive ComfyUI discovery/control when story_comfy can perform the operation.\n- Do not replace story_comfy with curl, wget, urllib, requests, httpx, aiohttp, raw /prompt loops, or guessed class_type graphs.\n`,
    };
  });

  pi.registerTool?.({
    name: "story_comfy",
    label: "Story-Film ComfyUI",
    description:
      "Primary Story-Film control surface for the user's existing ComfyUI. Story-Film automatically installs its own separate official comfy-cli/comfy-mcp/comfy-api-proxy control runtime on first use; it does NOT install ComfyUI or models. Start with server-info, run model-inventory before deciding models are missing, use model-search across every live model folder/node choice, and use the official MCP tool surface rather than guessed nodes/workflows or raw curl/bash ComfyUI calls.",
    parameters: RequestSchema,
    async execute(_toolCallId: string, params: any, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      if (params.action === "call") {
        const tool = String(params.tool || "").trim();
        if (!tool) return { content: [{ type: "text", text: "story_comfy call requires tool." }], details: {}, isError: true };
        if (tool.toLowerCase().includes("template")) {
          return {
            content: [{ type: "text", text: "Story-Film does not search or run ComfyUI template-catalog tools. Save or copy the desired template into the user's ComfyUI workflow area first, then use it as a user workflow." }],
            details: { template_tools_disabled: true },
            isError: true,
          };
        }
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
      const runtimeCwd = requestedProjectCwd(ctx.cwd, params.project);
      const request = { ...params };
      delete request.project;
      const value = await runRuntime(runtimeCwd, request, signal);
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
