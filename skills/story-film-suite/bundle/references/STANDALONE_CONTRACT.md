# Standalone Contract

Story-Film Skills is a complete standalone Agent Skills product.

## Required capability rule

A required production capability must be implemented by this package or represented by a portable artifact this package can create itself.

Never require another skill pack to finish:

- story or book development
- screenplay work
- character, world, continuity, or visual bibles
- character performance identity and ensemble relationship baselines
- reference planning
- production breakdowns
- directing documents
- visible-dialogue synchronization planning and end-frame continuity handoff
- previz specifications
- shot lists or storyboards
- model-neutral generation briefs
- model-specific prompt documents
- voice, score, sound, or editorial planning

## External tool rule

ComfyUI, video editors, image editors, 3D tools, and other agents are downstream consumers.

The suite may create files intended for them, but it must not:

- assume a particular extension is installed
- tell the user to install another skill pack to complete core planning
- rely on another skill's private schema
- hardcode another project's node names, widget indices, model paths, or private runtime details
- stop simply because an optional external integration is missing

## Portable boundary

When a downstream renderer or editor is not present, finish the planning task by producing a portable specification using project-relative paths and documented fields.

A valid portable artifact contains enough information for a separate tool or human to continue without reading the originating chat.

## Integration policy

Future integrations may be added as optional adapters. They must consume the standalone artifacts instead of becoming the only implementation of a required capability.
