# Writing Rules

These rules apply to Story-Film-authored artifacts written for a human or generation model. ComfyUI workflow JSON is workflow data and has the explicit punctuation exemption below.

## Required style

- Use concrete nouns and verbs.
- Prefer observable behavior over abstract emotional labels.
- Vary sentence length naturally.
- Keep exposition proportional to what the reader needs now.
- Give dialogue each character's vocabulary, rhythm, evasions, and priorities.
- Let subtext carry meaning when the scene can support it.
- Use specific sensory detail only when it changes the image, action, mood, or understanding.
- Name camera, light, action, or sound directly instead of using "cinematic" as a substitute for detail.

## Hard rules

- Never use an em dash character outside ComfyUI workflow JSON. Preserve punctuation inside imported, user-authored, vendor, and Story-Film ComfyUI workflows instead of style-normalizing the graph data.
- Never write "same as before", "as above", "previously described", or any other shortcut inside a generation prompt.
- Never invent praise, importance, symbolism, or emotional depth that the story has not earned.
- Never summarize the theme inside dialogue unless a character would naturally do so.
- Never pad a section to make it look complete.

## Common slop patterns to remove

Rewrite or delete these when they appear as filler:

- "not just X, but Y"
- "a testament to"
- "a tapestry of"
- "delve into"
- "in a world where" when the sentence adds no useful premise information
- "a haunting reminder"
- "the very essence of"
- "echoes of" when used as vague mood language
- repeated three-item adjective stacks
- repeated rhetorical fragments
- generic statements that a moment is "powerful", "poignant", "breathtaking", or "cinematic" without showing why

Words on this list are not forbidden when literal and necessary. The problem is filler use.

## Dialogue check

For every important line, ask:

1. What does the speaker want right now?
2. Why do they phrase it this way instead of saying the goal directly?
3. Could another character say the same line unchanged? If yes, rewrite it.
4. Does the line repeat information the audience already knows? If yes, cut or change it.

## Prompt check

Every generation prompt must state enough subject, setting, action, framing, continuity, and audio information to stand alone without chat history.
