# Session Handoff

[Documentation home](../README.md) | [Up: Recovery](recovery.md) | [Next: Human-only wizards](wizards.md)

## Table of contents

- [Purpose](#purpose)
- [What a bridge contains](#what-a-bridge-contains)
- [What it does not contain](#what-it-does-not-contain)
- [Resume rule](#resume-rule)

## Purpose

A fresh agent session should continue the project without reading the complete old conversation.

## What a bridge contains

A session bridge points to the durable files that matter now. It identifies the current goal, current pipeline target, blockers, next action, and useful skills.

## What it does not contain

Do not copy large specifications, manifests, or reports into the handoff if they already exist in the project.

Reference them by project-relative path.

Do not put passwords, tokens, or private secrets in a handoff document.

## Resume rule

The durable project files are the source of truth. The handoff is a map to those files.

## Related pages

- [Reboot recovery](recovery.md)
- [Pi Todo](../production/todo-and-progress.md)
- [Project layout](../reference/project-layout.md)
