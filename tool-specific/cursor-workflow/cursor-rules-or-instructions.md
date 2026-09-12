# Cursor rules and instructions used

Persistent instructions live in the repository:

- [`.cursorrules`](../../.cursorrules) — layer contracts, DQ names, Gold outputs, no secrets
- This folder’s `project-context.md` and `spec.md` — runtime and invariants
- Markdown design docs at repo root — schemas and quality strategy

How they were used:

1. Before generating a layer, the agent was pointed at the spec and the target file path.
2. After generation, output was checked against `.cursorrules` (especially “do not delete Silver rows”).
3. When the agent suggested extra libraries (`faker`, Unity Catalog helpers), those suggestions were rejected to stay Community Edition / dependency-light.

No additional unpublished system prompt was used.
