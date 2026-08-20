// Copyright 2026 Alan Guice (Badgids)
// SPDX-License-Identifier: Apache-2.0
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

type Status = "completed" | "current" | "blocked" | "pending" | "skipped" | string;
type NodeRecord = { id: string; label: string; position?: number; total?: number; status: Status; steps?: NodeRecord[]; substeps?: NodeRecord[] };
type Progress = {
  owner?: string; pipeline_id?: string; label?: string; status?: string; stages?: NodeRecord[];
  next_action?: string; blocker?: string; updated_at?: string;
};
type ResourceStatus = {
  phase?: string; message?: string; batch_id?: string; current_job_id?: string;
  job_index?: number; job_total?: number; llm_state?: string; comfyui_state?: string;
  error?: string; updated_at?: string;
};
type Ui = {
  setWidget?: (key: string, content: string[] | ((tui: any, theme: any) => any) | undefined, options?: { placement?: "aboveEditor" | "belowEditor" }) => void;
  setStatus?: (key: string, text: string | undefined) => void;
  notify?: (message: string, type?: "info" | "warning" | "error") => void;
  theme?: { fg?: (role: string, text: string) => string };
};

const KEY = "story-film-pipeline-todo";
const EXPANDED_ROWS = 10;
const COLLAPSED_ROWS = 3;
const SHORTCUTS = {
  toggle: "ctrl+alt+t",
  toggleFallback: "ctrl+alt+shift+t",
  up: "ctrl+alt+up",
  down: "ctrl+alt+down",
  pageUp: "ctrl+alt+pageUp",
  pageDown: "ctrl+alt+pageDown",
  follow: "ctrl+alt+home",
} as const;
const ANSI = /\x1b\[[0-?]*[ -/]*[@-~]/g;

function projectRoot(cwd: string): string | undefined {
  let here = resolve(cwd);
  for (;;) {
    if (existsSync(join(here, "00_project", "state.json"))) return here;
    const parent = dirname(here);
    if (parent === here) return undefined;
    here = parent;
  }
}

function load(cwd: string): Progress | undefined {
  const root = projectRoot(cwd);
  if (!root) return undefined;
  const path = join(root, "00_project", "pipeline_progress.json");
  try {
    const value = JSON.parse(readFileSync(path, "utf8")) as Progress;
    return ["story-film-skills", "badgids-story-film-skills"].includes(value.owner || "") ? value : undefined;
  } catch { return undefined; }
}

function loadResource(cwd: string): ResourceStatus | undefined {
  const root = projectRoot(cwd);
  if (!root) return undefined;
  const path = join(root, "00_project", "resource_handoff.json");
  try { return JSON.parse(readFileSync(path, "utf8")) as ResourceStatus; } catch { return undefined; }
}

function resourceOwnsInput(value: ResourceStatus | undefined): boolean {
  return !!value && ["waiting-for-agent-end", "unloading-llm", "running-comfyui", "unloading-comfyui", "reloading-llm"].includes(value.phase || "");
}

function signalResourceRelease(cwd: string): boolean {
  const root = projectRoot(cwd);
  const value = loadResource(cwd);
  if (!root || value?.phase !== "waiting-for-agent-end") return false;
  const path = join(root, "00_project", "resource_handoff.release");
  if (!existsSync(path)) writeFileSync(path, `${new Date().toISOString()}\n`, { encoding: "utf8", flag: "wx" });
  return true;
}

function marker(status: Status): string {
  if (status === "completed") return "✓";
  if (status === "current") return "▶";
  if (status === "blocked") return "!";
  if (status === "skipped") return "-";
  return "○";
}

function flatten(value: Progress): { lines: string[]; current: number } {
  const lines: string[] = [];
  let current = 0;
  const push = (node: NodeRecord, indent: string, kind: string): void => {
    if (node.status === "current" || node.status === "blocked") current = lines.length;
    const count = node.position && node.total ? ` - ${kind} ${node.position} of ${node.total}` : "";
    lines.push(`${indent}${marker(node.status)} ${node.id} ${node.label}${count}`);
    for (const step of node.steps ?? []) push(step, `${indent}  `, "Step");
    for (const sub of node.substeps ?? []) push(sub, `${indent}  `, "Substep");
  };
  for (const stage of value.stages ?? []) push(stage, "", "Stage");
  return { lines, current };
}

function labelSkillNames(label: string): string[] {
  return [...label.matchAll(/`([a-z0-9][a-z0-9-]*)`/gi)].map(match => match[1].toLowerCase());
}

function activePathSkillNames(value: Progress): Set<string> {
  const result = new Set<string>();
  const visit = (node: NodeRecord): boolean => {
    const ownActive = node.status === "current" || node.status === "blocked";
    let childActive = false;
    for (const child of [...(node.steps ?? []), ...(node.substeps ?? [])]) {
      if (visit(child)) childActive = true;
    }
    if (ownActive || childActive) {
      for (const name of labelSkillNames(node.label)) result.add(name);
      return true;
    }
    return false;
  };
  for (const stage of value.stages ?? []) visit(stage);
  return result;
}

function skillStatuses(value: Progress): Map<string, Set<Status>> {
  const result = new Map<string, Set<Status>>();
  const visit = (node: NodeRecord): void => {
    for (const name of labelSkillNames(node.label)) {
      const statuses = result.get(name) ?? new Set<Status>();
      statuses.add(node.status);
      result.set(name, statuses);
    }
    for (const child of [...(node.steps ?? []), ...(node.substeps ?? [])]) visit(child);
  };
  for (const stage of value.stages ?? []) visit(stage);
  return result;
}

function requestedSkillName(event: any): string | undefined {
  const tool = String(event?.toolName ?? "").toLowerCase();
  if (!new Set(["read", "read_file", "readfile"]).has(tool)) return undefined;
  const input = event?.input ?? {};
  const path = String(input.path ?? input.file_path ?? input.filepath ?? "").replace(/\\/g, "/");
  const match = /(?:^|\/)skills\/([^/]+)\/SKILL\.md$/i.exec(path);
  return match?.[1]?.toLowerCase();
}

function pipelineGuardPrompt(value: Progress | undefined): string | undefined {
  if (!value?.stages?.length || !["active", "blocked", "paused"].includes(value.status || "")) return undefined;
  const flat = flatten(value);
  const currentLine = flat.lines[flat.current] || value.next_action || "current Story-Film target";
  return `\nSTORY-FILM PIPELINE RUNTIME GUARD:\n- 00_project/pipeline_progress.json is authoritative.\n- Current target: ${currentLine}\n- Do not work ahead on a later Story-Film target. Finish the current target, validate its artifact, then checkpoint it with scripts/pipeline_progress.py before starting the next specialist.\n- If Pi's generic Todo is used, mirror at most three items: current Story-Film target, immediate next target, and requested endpoint. Update that mirror after each Story-Film checkpoint. The generic Todo never overrides pipeline_progress.json.\n- For ComfyUI model discovery, use Story-Film's scripts/model_inventory.py scan and menu commands against the live server. ComfyUI's /models registry includes server-registered external model directories such as extra_model_paths.yaml. Do not call /models directly with curl, wget, urllib, requests, or one-off parser scripts. Do not use filesystem-wide find/grep scans to decide that models are missing. Do not infer model absence from an ad hoc /object_info parser.\n`;
}

function futureSkillBlockReason(value: Progress | undefined, requested: string | undefined): string | undefined {
  if (!value || !requested || !["active", "blocked", "paused"].includes(value.status || "")) return undefined;
  const statuses = skillStatuses(value).get(requested);
  if (!statuses || !statuses.has("pending")) return undefined;
  if (statuses.has("completed") || statuses.has("current") || statuses.has("blocked")) return undefined;
  if (activePathSkillNames(value).has(requested)) return undefined;
  const flat = flatten(value);
  const currentLine = flat.lines[flat.current] || value.next_action || "the current Story-Film target";
  return `Story-Film progress is still at ${currentLine}. Validate and checkpoint the current target before opening the future specialist '${requested}'. Do not work ahead.`;
}


function genericTodoBlockReason(value: Progress | undefined, event: any): string | undefined {
  if (!value || !["active", "blocked", "paused"].includes(value.status || "")) return undefined;
  const tool = String(event?.toolName ?? "").toLowerCase();
  if (!new Set(["todo", "todo_write"]).has(tool)) return undefined;
  const input = event?.input ?? {};
  const op = String(input.op ?? input.operation ?? "").toLowerCase();
  if (op && op !== "init" && op !== "replace") return undefined;
  let count = 0;
  if (Array.isArray(input.list)) {
    count = input.list.reduce((sum: number, phase: any) => sum + (Array.isArray(phase?.items) ? phase.items.length : 0), 0);
  } else if (Array.isArray(input.todos)) {
    count = input.todos.length;
  } else if (Array.isArray(input.items)) {
    count = input.items.length;
  }
  if (count <= 3) return undefined;
  return `Story-Film already has a detailed authoritative pipeline Todo. Keep Pi's generic Todo to at most three Story-Film mirror items: current target, immediate next target, and requested endpoint. The attempted generic Todo contains ${count} items.`;
}

function comfyModelFilesystemScanBlockReason(value: Progress | undefined, event: any): string | undefined {
  if (!value || !["active", "blocked", "paused"].includes(value.status || "")) return undefined;
  const tool = String(event?.toolName ?? "").toLowerCase();
  const input = event?.input ?? {};
  const approvedInventoryText = (text: string): boolean => text.toLowerCase().includes("model_inventory.py");
  const reason = "Use Story-Film's scripts/model_inventory.py scan/menu for ComfyUI model discovery. The bundled inventory tool owns calls to /models and /models/{folder}, including models registered through extra_model_paths.yaml. Do not write or run one-off curl/wget/Python parsers and do not scan model directories on the filesystem.";

  if (new Set(["bash", "shell", "terminal"]).has(tool)) {
    const command = String(input.command ?? input.cmd ?? input.script ?? "");
    const lower = command.toLowerCase();
    if (approvedInventoryText(command)) return undefined;

    const looksLikeWideFind = /(?:^|[;&|\n]\s*)find\s+(?:\/|\$home|~)(?:\s|$)/i.test(command);
    const modelTokens = [
      ".safetensors", ".ckpt", "models/checkpoints", "models/diffusion", "models/vae", "models/loras",
      "extra_model_paths", "checkpointloader", "vaeloader",
    ];
    const modelRelated = modelTokens.some(token => lower.includes(token));
    const rawRegistryEndpoint = /\/models(?:\/[^\s'\";|)]+)?(?:\b|[?])/i.test(command);
    const rawHttpClient = /\b(?:curl|wget)\b|urllib(?:\.request)?|urlopen\s*\(|requests\.|httpx\.|aiohttp\./i.test(command);
    const adHocObjectInfoInventory = lower.includes("/object_info") && modelRelated;
    const filesystemModelEnumeration = modelRelated && /\b(?:find|locate|ls|du|grep|rg)\b/i.test(command);

    if ((rawRegistryEndpoint && rawHttpClient) || adHocObjectInfoInventory || (looksLikeWideFind && modelRelated) || filesystemModelEnumeration) {
      return reason;
    }
    return undefined;
  }

  if (new Set(["write", "write_file", "writefile"]).has(tool)) {
    const path = String(input.path ?? input.file_path ?? input.filepath ?? "");
    const content = String(input.content ?? input.text ?? input.data ?? "");
    if (approvedInventoryText(content)) return undefined;
    const codeFile = /\.(?:py|sh|bash|zsh|js|mjs|cjs|ts)$/i.test(path);
    const rawRegistryEndpoint = /\/models(?:\/[^\s'\";|)]+)?(?:\b|[?])/i.test(content);
    const rawHttpClient = /\b(?:curl|wget)\b|urllib(?:\.request)?|urlopen\s*\(|requests\.|httpx\.|aiohttp\./i.test(content);
    const filesystemModelParser = /extra_model_paths|\.safetensors|models\/checkpoints|models\/diffusion|models\/vae|models\/loras/i.test(content)
      && /\b(?:find|glob|walk|listdir|scandir|rglob)\b/i.test(content);
    if (codeFile && ((rawRegistryEndpoint && rawHttpClient) || filesystemModelParser)) return reason;
  }

  return undefined;
}

function safeWidth(text: string, width: number): string {
  const plain = text.replace(ANSI, "");
  if (plain.length <= width) return text;
  if (width <= 1) return "";
  return `${plain.slice(0, Math.max(0, width - 1))}…`;
}

class Viewport {
  private value?: Progress;
  private resource?: ResourceStatus;
  private offset = 0;
  private manual = false;
  private current = 0;
  private lines: string[] = [];
  private tui?: any;
  private expanded = false;

  private rows(): number { return this.expanded ? EXPANDED_ROWS : COLLAPSED_ROWS; }
  update(value: Progress | undefined, resource?: ResourceStatus): void {
    this.value = value; this.resource = resource;
    if (!value?.stages?.length || value.status === "inactive") {
      this.lines = []; this.offset = 0; this.manual = false; this.current = 0;
    } else {
      const flat = flatten(value); this.lines = flat.lines; this.current = flat.current;
      if (!this.manual) this.follow(false);
      this.clamp();
    }
    this.tui?.requestRender?.();
  }
  attach(tui: any): any {
    this.tui = tui;
    return { render: (width: number) => this.render(width), invalidate: () => tui.requestRender?.(), dispose: () => { if (this.tui === tui) this.tui = undefined; } };
  }
  scroll(delta: number): boolean { if (!this.lines.length) return false; this.manual = true; const before = this.offset; this.offset += delta; this.clamp(); this.tui?.requestRender?.(); return before !== this.offset; }
  page(delta: number): boolean { return this.scroll(delta * Math.max(1, this.rows() - 1)); }
  follow(render = true): boolean { if (!this.lines.length) return false; this.manual = false; const before = this.offset; this.offset = Math.max(0, this.current - Math.floor(this.rows() / 2)); this.clamp(); if (render) this.tui?.requestRender?.(); return before !== this.offset; }
  setExpanded(expanded: boolean): boolean { const changed = this.expanded !== expanded; this.expanded = expanded; if (!this.manual) this.follow(false); this.clamp(); this.tui?.requestRender?.(); return changed; }
  toggle(): boolean { return this.setExpanded(!this.expanded); }
  state() { return { active: this.lines.length > 0, offset: this.offset, total: this.lines.length, current: this.current, manual: this.manual, expanded: this.expanded, rows: this.rows() }; }
  private clamp(): void { const rows = this.rows(); this.offset = Math.max(0, Math.min(Math.max(0, this.lines.length - rows), this.offset)); }
  private render(width: number): string[] {
    if (!this.value || !this.lines.length) return [];
    const rows = this.rows();
    const end = Math.min(this.lines.length, this.offset + rows);
    const mode = this.expanded ? "expanded" : "compact";
    const title = `Story-Film Todo - ${this.value.label || this.value.pipeline_id || "Active pipeline"} [${this.offset + 1}-${end}/${this.lines.length}] ${this.manual ? "manual" : "following"} ${mode}`;
    const out = [title, ...this.lines.slice(this.offset, end)];
    if (this.expanded) {
      out.push("Keys: Ctrl+Alt+T compact | fallback Ctrl+Alt+Shift+T | Ctrl+Alt+Up/Down scroll | Ctrl+Alt+Home follow");
      if (this.value.status !== "complete" && this.value.next_action) out.push(`NEXT -> ${this.value.next_action}`);
      if (this.value.blocker) out.push(`BLOCKED -> ${this.value.blocker}`);
    } else {
      out.push("Keys: Ctrl+Alt+T expand | fallback Ctrl+Alt+Shift+T | /story-todo help");
      if (this.value.blocker) out.push(`BLOCKED -> ${this.value.blocker}`);
    }
    if (this.resource && this.resource.phase && this.resource.phase !== "idle") {
      const jobs = this.resource.job_total ? ` | jobs ${this.resource.job_index ?? 0}/${this.resource.job_total}` : "";
      const currentJob = this.resource.current_job_id ? ` | ${this.resource.current_job_id}` : "";
      out.push(`RESOURCE -> ${this.resource.phase}${jobs}${currentJob}`);
      if (this.expanded && this.resource.message) out.push(`RUNTIME -> ${this.resource.message}`);
      if (this.resource.error) out.push(`RESOURCE ERROR -> ${this.resource.error}`);
    }
    return out.map(line => safeWidth(line, width));
  }
}

const viewport = new Viewport();

function render(ctx: any): void {
  const ui = ctx.ui as Ui;
  const value = load(ctx.cwd);
  const resource = loadResource(ctx.cwd);
  viewport.update(value, resource);
  if (!ctx.hasUI || !ui.setWidget) return;
  if (resource?.phase && resource.phase !== "idle") {
    const jobs = resource.job_total ? ` ${resource.job_index ?? 0}/${resource.job_total}` : "";
    ui.setStatus?.("story-film-resource", `Resources: ${resource.phase}${jobs}`);
  } else ui.setStatus?.("story-film-resource", undefined);
  if (!value?.stages?.length || value.status === "inactive" || value.status === "complete") {
    if (resourceOwnsInput(resource) || resource?.phase === "complete" || resource?.phase === "failed") {
      const lines = [`Story-Film Resource Handoff - ${resource?.phase || "idle"}`, resource?.message || "", resource?.current_job_id ? `Current job: ${resource.current_job_id}` : ""].filter(Boolean);
      ui.setWidget(KEY, lines, { placement: "aboveEditor" });
    } else ui.setWidget(KEY, undefined, { placement: "aboveEditor" });
    ui.setStatus?.("story-film-stage", value?.status === "complete" ? `Story-Film: ${value.label} complete` : undefined);
    ui.setStatus?.("story-film-next", undefined);
    return;
  }
  ui.setWidget(KEY, (tui: any) => viewport.attach(tui), { placement: "aboveEditor" });
  ui.setStatus?.("story-film-stage", `Story-Film: ${value.label || value.pipeline_id} (${value.status})`);
  ui.setStatus?.("story-film-next", value.next_action ? `Next: ${value.next_action}` : undefined);
}

export default function storyFilmProgress(pi: any): void {
  let lastCtx: any | undefined;
  let timer: ReturnType<typeof setInterval> | undefined;
  let lastResourcePhase = "";
  const refresh = async (_event: any, ctx: any) => { lastCtx = ctx; render(ctx); };
  pi.on?.("session_start", async (event: any, ctx: any) => {
    await refresh(event, ctx);
    if (timer) clearInterval(timer);
    timer = setInterval(() => {
      if (!lastCtx) return;
      const resource = loadResource(lastCtx.cwd);
      const phase = resource?.phase || "";
      render(lastCtx);
      if (phase && phase !== lastResourcePhase && resource?.message) {
        lastCtx.ui.notify?.(resource.message, phase === "failed" ? "error" : "info");
      }
      lastResourcePhase = phase;
    }, 1000);
  });
  pi.on?.("before_agent_start", async (event: any, ctx: any) => {
    await refresh(event, ctx);
    const systemPromptAppend = pipelineGuardPrompt(load(ctx.cwd));
    return systemPromptAppend ? { systemPromptAppend } : undefined;
  });
  pi.on?.("tool_call", async (event: any, ctx: any) => {
    const value = load(ctx.cwd);
    const reason = futureSkillBlockReason(value, requestedSkillName(event))
      ?? genericTodoBlockReason(value, event)
      ?? comfyModelFilesystemScanBlockReason(value, event);
    if (!reason) return undefined;
    ctx.ui.notify?.(reason, "warning");
    return { block: true, reason };
  });
  pi.on?.("tool_result", refresh);
  pi.on?.("agent_end", async (_event: any, ctx: any) => {
    lastCtx = ctx;
    if (signalResourceRelease(ctx.cwd)) {
      ctx.ui.notify?.("Story-Film generation handoff released after the agent turn. The local LLM can now unload while the model-free ComfyUI runner continues.", "info");
    }
    render(ctx);
  });
  pi.on?.("session_shutdown", async (_event: any, ctx: any) => {
    if (timer) { clearInterval(timer); timer = undefined; }
    lastCtx = undefined;
    const ui = ctx.ui as Ui; viewport.update(undefined, undefined); ui.setWidget?.(KEY, undefined, { placement: "aboveEditor" }); ui.setStatus?.("story-film-stage", undefined); ui.setStatus?.("story-film-next", undefined); ui.setStatus?.("story-film-resource", undefined);
  });

  pi.registerCommand?.("story-todo", {
    description: "Inspect, compact, expand, or scroll the active Story-Film pipeline todo.",
    handler: async (args: string, ctx: any) => {
      render(ctx);
      const action = (args || "status").trim().toLowerCase() || "status";
      const changed = action === "up" ? viewport.scroll(-1)
        : action === "down" ? viewport.scroll(1)
        : action === "page-up" ? viewport.page(-1)
        : action === "page-down" ? viewport.page(1)
        : action === "current" || action === "follow" ? viewport.follow()
        : action === "toggle" ? viewport.toggle()
        : action === "expand" ? viewport.setExpanded(true)
        : action === "collapse" || action === "compact" ? viewport.setExpanded(false)
        : false;
      const state = viewport.state();
      if (!state.active) { ctx.ui.notify?.("No active Story-Film pipeline todo is available.", "info"); return; }
      const known = ["up", "down", "page-up", "page-down", "current", "follow", "toggle", "expand", "collapse", "compact", "help", "keys"];
      if (action === "help" || action === "keys") {
        ctx.ui.notify?.("Story-Film Todo keys: Ctrl+Alt+T toggles compact/expanded; Ctrl+Alt+Shift+T is the fallback toggle if the primary chord is intercepted; Ctrl+Alt+Up/Down scroll; Ctrl+Alt+PageUp/PageDown page; Ctrl+Alt+Home follows current. Slash commands remain available as /story-todo toggle|up|down|page-up|page-down|current.", "info");
        return;
      }
      if (action === "status" || !known.includes(action)) {
        const value = load(ctx.cwd);
        const extra = value?.blocker ? ` Blocker: ${value.blocker}` : value?.next_action ? ` Next: ${value.next_action}` : "";
        ctx.ui.notify?.(`Story-Film todo: ${state.expanded ? "expanded" : "compact"}, ${state.rows} visible items, line ${state.offset + 1} of ${state.total}; ${state.manual ? "manual scroll" : "following current"}.${extra} Use /story-todo help for keys and controls.`, value?.blocker ? "warning" : "info");
      } else if (!changed && !["current", "follow", "expand", "collapse", "compact"].includes(action)) {
        ctx.ui.notify?.("Story-Film todo viewport is already at that boundary.", "info");
      }
    },
  });

  pi.on?.("input", async (event: any, ctx: any) => {
    const resource = loadResource(ctx.cwd);
    if (!resourceOwnsInput(resource) || event?.source === "extension") return { action: "continue" as const };
    const jobs = resource?.job_total ? ` Jobs: ${resource.job_index ?? 0}/${resource.job_total}.` : "";
    ctx.ui.notify?.(`${resource?.message || "Story-Film resource handoff is active."}${jobs} Your message was not sent to the LLM because the local model is intentionally unavailable during ComfyUI generation.`, "info");
    return { action: "handled" as const };
  });

  pi.registerCommand?.("story-resource", {
    description: "Show the current model-free Story-Film resource handoff status.",
    handler: async (_args: string, ctx: any) => {
      const r = loadResource(ctx.cwd);
      if (!r || !r.phase || r.phase === "idle") { ctx.ui.notify?.("No Story-Film resource handoff is active.", "info"); return; }
      const jobs = r.job_total ? ` jobs ${r.job_index ?? 0}/${r.job_total}` : "";
      ctx.ui.notify?.(`Story-Film resources: ${r.phase}${jobs}. ${r.message || ""}`, r.phase === "failed" ? "error" : "info");
    },
  });

  if (typeof pi.registerShortcut === "function") {
    const runShortcut = (action: () => void) => async (ctx: any) => { action(); render(ctx); };
    pi.registerShortcut(SHORTCUTS.up, { description: "Scroll Story-Film todo up", handler: runShortcut(() => { viewport.scroll(-1); }) });
    pi.registerShortcut(SHORTCUTS.down, { description: "Scroll Story-Film todo down", handler: runShortcut(() => { viewport.scroll(1); }) });
    pi.registerShortcut(SHORTCUTS.pageUp, { description: "Page Story-Film todo up", handler: runShortcut(() => { viewport.page(-1); }) });
    pi.registerShortcut(SHORTCUTS.pageDown, { description: "Page Story-Film todo down", handler: runShortcut(() => { viewport.page(1); }) });
    pi.registerShortcut(SHORTCUTS.follow, { description: "Follow current Story-Film todo", handler: runShortcut(() => { viewport.follow(); }) });
    pi.registerShortcut(SHORTCUTS.toggle, { description: "Toggle compact Story-Film todo", handler: runShortcut(() => { viewport.toggle(); }) });
    pi.registerShortcut(SHORTCUTS.toggleFallback, { description: "Toggle compact Story-Film todo (fallback)", handler: runShortcut(() => { viewport.toggle(); }) });
  }
}
