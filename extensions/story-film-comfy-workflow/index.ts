// Copyright 2026 Alan Guice (Badgids)
// SPDX-License-Identifier: Apache-2.0
import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Type } from "typebox";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const SCRIPT = resolve(ROOT, "scripts/comfy_workflow_pipeline.py");
const MAX_CAPTURE = 64 * 1024 * 1024;
const MAX_TEXT = 120_000;

const RequestSchema = Type.Object({
  action: Type.Union([
    Type.Literal("prepare"),
    Type.Literal("finalize"),
    Type.Literal("status"),
  ]),
  query: Type.Optional(Type.String()),
  media_type: Type.Optional(Type.String()),
  records_path: Type.Optional(Type.String()),
  source_limit: Type.Optional(Type.Number()),
  workflow: Type.Optional(Type.Record(Type.String(), Type.Any())),
  candidate_path: Type.Optional(Type.String()),
  arm_handoff: Type.Optional(Type.Boolean()),
  comfyui_url: Type.Optional(Type.String()),
});

type RuntimeResult = { ok?: boolean; error?: string; [key: string]: unknown };

function projectRoot(cwd: string): string | undefined {
  let here = resolve(cwd);
  for (;;) {
    if (existsSync(resolve(here, "00_project/state.json"))) return here;
    const parent = dirname(here);
    if (parent === here) return undefined;
    here = parent;
  }
}

function pythonCandidates(): string[] {
  const explicit = process.env.STORY_FILM_PYTHON?.trim();
  return explicit ? [explicit] : process.platform === "win32" ? ["python", "python3"] : ["python3", "python"];
}

function runOne(python: string, project: string, request: Record<string, unknown>, signal?: AbortSignal): Promise<RuntimeResult> {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(python, [SCRIPT, "request", "--project", project], {
      cwd: project,
      env: process.env,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    let tooLarge = false;
    const append = (current: string, chunk: Buffer | string): string => {
      if (tooLarge) return current;
      const next = current + chunk.toString();
      if (next.length > MAX_CAPTURE) {
        tooLarge = true;
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
      if (tooLarge) {
        resolvePromise({ ok: false, error: "bounded workflow runtime response exceeded 64 MiB" });
        return;
      }
      const raw = stdout.trim();
      let value: RuntimeResult;
      try {
        value = raw ? JSON.parse(raw) as RuntimeResult : { ok: false, error: stderr.trim() || `workflow runtime exited ${code ?? closeSignal ?? "without status"}` };
      } catch {
        value = { ok: false, error: `workflow runtime returned invalid JSON${stderr.trim() ? `: ${stderr.trim()}` : ""}` };
      }
      if ((code || closeSignal) && value.ok !== false) {
        value = { ...value, ok: false, error: value.error || `workflow runtime exited ${code ?? closeSignal}` };
      }
      resolvePromise(value);
    });
    child.stdin.end(JSON.stringify(request));
  });
}

async function runRuntime(project: string, request: Record<string, unknown>, signal?: AbortSignal): Promise<RuntimeResult> {
  let last: unknown;
  for (const python of pythonCandidates()) {
    try { return await runOne(python, project, request, signal); }
    catch (error: any) {
      last = error;
      if (error?.code !== "ENOENT") throw error;
    }
  }
  throw last instanceof Error ? last : new Error("Python 3 was not found");
}

function resultText(value: RuntimeResult): string {
  const text = JSON.stringify(value, null, 2);
  return text.length <= MAX_TEXT ? text : text.slice(0, MAX_TEXT) + "\n... Story-Film truncated this display.";
}

function boundedPhase(project: string): boolean {
  const contract = resolve(project, "04_generation/comfyui/recovery/workflow_build_contract.json");
  if (!existsSync(contract)) return false;
  const result = resolve(project, "04_generation/comfyui/recovery/workflow_finalize_result.json");
  if (!existsSync(result)) return true;
  try {
    const value = JSON.parse(readFileSync(result, "utf8"));
    return !["waiting-for-agent-end", "ready-for-resource-handoff"].includes(String(value?.status || ""));
  } catch { return true; }
}

function bypassReason(event: any, project: string): string | undefined {
  if (!boundedPhase(project)) return undefined;
  const tool = String(event?.toolName ?? "").toLowerCase();
  const input = event?.input ?? {};
  if (tool === "story_comfy") {
    const action = String(input.action ?? "").toLowerCase();
    if (["node-search", "node-info", "node-path", "server-info"].includes(action)) return undefined;
    return "The bounded Story-Film workflow phase is active. Use story_comfy_workflow prepare/finalize; only node-search, node-info, node-path, or server-info remain available from story_comfy while authoring the one canonical graph.";
  }
  if (["bash", "shell", "terminal"].includes(tool)) {
    const command = String(input.command ?? input.cmd ?? input.script ?? "").toLowerCase();
    if (/comfyui_(?:control|batch)|comfy_workflow_pipeline|resource_handoff|offline_batch\.json|04_generation[\\/]comfyui[\\/]workflows/.test(command)) {
      return "The bounded Story-Film workflow phase owns source fetching, validation, SHOT fan-out, offline_batch.json, and resource handoff. Do not bypass it with backend shell commands.";
    }
  }
  if (["write", "write_file", "writefile"].includes(tool)) {
    const path = String(input.path ?? input.file_path ?? input.filepath ?? "").replace(/\\/g, "/").toLowerCase();
    if (path.includes("04_generation/comfyui/workflows/") || path.endsWith("04_generation/comfyui/offline_batch.json")) {
      return "Do not write runnable SHOT workflows or offline_batch.json directly while the bounded workflow phase is active. Pass one canonical graph to story_comfy_workflow finalize.";
    }
  }
  return undefined;
}

export default function storyFilmComfyWorkflow(pi: any): void {
  pi.on?.("before_agent_start", async (_event: any, ctx: any) => {
    const root = projectRoot(ctx.cwd);
    if (!root) return undefined;
    return {
      systemPromptAppend: `\nSTORY-FILM BOUNDED COMFY WORKFLOW PHASE:\n- For production workflow recovery/building, use the Pi-native story_comfy_workflow tool. Call action=prepare once with the concrete model/workflow query and media_type.\n- The deterministic script owns extension-local workflow selection/preservation, complete live node/model snapshots, prompt-artifact discovery, runnable validation, per-shot fan-out, offline-batch compilation, and resource-handoff arming. It never scans ComfyUI userdata, project workflow folders, or arbitrary external workflow paths.\n- Explicit workflow authoring remains supported. If the user asks to create/build/author/design a new workflow, use live node/model schemas to build one bounded candidate, validate it before promotion, and save/copy reusable JSON into comfyui_workflows/custom/<task>/<model>/ before refreshing selection. Do not require a generate-new catalog row.\n- The LLM may do one thing in the middle: adapt a preserved source or author exactly ONE canonical API-format workflow object from the live schemas. It may use story_comfy node-search/node-info/node-path while designing that canonical graph.\n- The canonical graph must use only installed class_type values and live model choices. Put __STORY_FILM_PROMPT__ in the real positive-prompt string input. Optional markers are __STORY_FILM_NEGATIVE_PROMPT__ and __STORY_FILM_FILENAME_PREFIX__.\n- Pass the single canonical graph to story_comfy_workflow action=finalize. If finalization reports a graph error, repair only that canonical graph and retry finalize. Do not create per-shot graphs yourself.\n- Finalize prefers already-approved Story-Film prompt artifacts under 04_generation/prompts/<adapter>/<source-id>.md; it does not ask the LLM to rewrite prompts already produced earlier in the pipeline.\n- Never create, install, or update a ComfyUI custom node during this phase unless the user explicitly requested custom-node development as a separate task.\n- When finalize returns waiting-for-agent-end, stop backend work and end the turn cleanly so Story-Film's existing agent-end resource handoff can continue model-free generation.\n`,
    };
  });

  pi.on?.("tool_call", async (event: any, ctx: any) => {
    const root = projectRoot(ctx.cwd);
    if (!root) return undefined;
    const reason = bypassReason(event, root);
    if (!reason) return undefined;
    ctx.ui.notify?.(reason, "warning");
    return { block: true, reason };
  });

  pi.registerTool?.({
    name: "story_comfy_workflow",
    label: "Story-Film Comfy Workflow",
    description: "Bounded workflow orchestration. The LLM may author one canonical ComfyUI API graph; deterministic Story-Film code owns source discovery, live validation, prompt reuse, SHOT fan-out, offline batch rebuild, and resource handoff.",
    parameters: RequestSchema,
    async execute(_toolCallId: string, params: any, signal: AbortSignal | undefined, onUpdate: any, ctx: any) {
      const root = projectRoot(ctx.cwd);
      if (!root) return { content: [{ type: "text", text: "No Story-Film project was found." }], details: {}, isError: true };
      onUpdate?.({ content: [{ type: "text", text: "Story-Film is running the bounded Comfy workflow pipeline..." }] });
      const value = await runRuntime(root, params, signal);
      return { content: [{ type: "text", text: resultText(value) }], details: value, isError: value.ok === false };
    },
  });
}
