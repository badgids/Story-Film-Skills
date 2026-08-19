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
const ROWS = 10;
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
  page(delta: number): boolean { return this.scroll(delta * Math.max(1, ROWS - 1)); }
  follow(render = true): boolean { if (!this.lines.length) return false; this.manual = false; const before = this.offset; this.offset = Math.max(0, this.current - Math.floor(ROWS / 2)); this.clamp(); if (render) this.tui?.requestRender?.(); return before !== this.offset; }
  state() { return { active: this.lines.length > 0, offset: this.offset, total: this.lines.length, current: this.current, manual: this.manual }; }
  private clamp(): void { this.offset = Math.max(0, Math.min(Math.max(0, this.lines.length - ROWS), this.offset)); }
  private render(width: number): string[] {
    if (!this.value || !this.lines.length) return [];
    const end = Math.min(this.lines.length, this.offset + ROWS);
    const title = `Story-Film Todo - ${this.value.label || this.value.pipeline_id || "Active pipeline"} [${this.offset + 1}-${end}/${this.lines.length}] ${this.manual ? "manual" : "following"}`;
    const out = [title, ...this.lines.slice(this.offset, end), "Ctrl+Alt+Shift+Up/Down scroll | Ctrl+Alt+Shift+PgUp/PgDn page | Ctrl+Alt+Shift+Home follow"];
    if (this.value.status !== "complete" && this.value.next_action) out.push(`NEXT -> ${this.value.next_action}`);
    if (this.value.blocker) out.push(`BLOCKED -> ${this.value.blocker}`);
    if (this.resource && this.resource.phase && this.resource.phase !== "idle") {
      const jobs = this.resource.job_total ? ` | jobs ${this.resource.job_index ?? 0}/${this.resource.job_total}` : "";
      const currentJob = this.resource.current_job_id ? ` | ${this.resource.current_job_id}` : "";
      out.push(`RESOURCE -> ${this.resource.phase}${jobs}${currentJob}`);
      if (this.resource.message) out.push(`RUNTIME -> ${this.resource.message}`);
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
  pi.on?.("before_agent_start", refresh);
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
    description: "Inspect or scroll the active Story-Film pipeline todo.",
    handler: async (args: string, ctx: any) => {
      render(ctx);
      const action = (args || "status").trim().toLowerCase() || "status";
      const changed = action === "up" ? viewport.scroll(-1)
        : action === "down" ? viewport.scroll(1)
        : action === "page-up" ? viewport.page(-1)
        : action === "page-down" ? viewport.page(1)
        : action === "current" || action === "follow" ? viewport.follow()
        : false;
      const state = viewport.state();
      if (!state.active) { ctx.ui.notify?.("No active Story-Film pipeline todo is available.", "info"); return; }
      if (action === "status" || !["up", "down", "page-up", "page-down", "current", "follow"].includes(action)) {
        const value = load(ctx.cwd);
        const extra = value?.blocker ? ` Blocker: ${value.blocker}` : value?.next_action ? ` Next: ${value.next_action}` : "";
        ctx.ui.notify?.(`Story-Film todo: line ${state.offset + 1} of ${state.total}; ${state.manual ? "manual scroll" : "following current"}.${extra} Use /story-todo up|down|page-up|page-down|current.`, value?.blocker ? "warning" : "info");
      } else if (!changed && !["current", "follow"].includes(action)) {
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
    pi.registerShortcut("ctrl+alt+shift+up", { description: "Scroll Story-Film todo up", handler: async () => { viewport.scroll(-1); } });
    pi.registerShortcut("ctrl+alt+shift+down", { description: "Scroll Story-Film todo down", handler: async () => { viewport.scroll(1); } });
    pi.registerShortcut("ctrl+alt+shift+pageUp", { description: "Page Story-Film todo up", handler: async () => { viewport.page(-1); } });
    pi.registerShortcut("ctrl+alt+shift+pageDown", { description: "Page Story-Film todo down", handler: async () => { viewport.page(1); } });
    pi.registerShortcut("ctrl+alt+shift+home", { description: "Follow current Story-Film todo", handler: async () => { viewport.follow(); } });
  }
}
