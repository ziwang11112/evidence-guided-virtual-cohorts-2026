# Architecture diagram build

28 October 2026. Documentation artifact only; no generator, experiment, or export repository was modified.

- Native editable source: `architecture.drawio` (43 unique cells; 16 edges).
- Export: `architecture.drawio.svg` (1162 by 1012 pixels; embedded editable diagram XML and local font resources). Exported with the installed draw.io desktop CLI, using a local `draw.io` executable (machine-local path omitted in export).
- Followed the draw.io skill's XML reference and repair pass. Native XML and exported SVG parse successfully; every edge has existing endpoints and geometry. The hidden target node connects only to independent evaluation.
- Green nodes (`#e8f5f1`, stroke `#087e76`) are implemented milestone-1 interfaces/tools, amber nodes (`#fff3df`, stroke `#bc862a`) are prior-pilot reuse candidates, and lilac nodes (`#f0ebf8`, stroke `#68509b`) are pending integration or planned capabilities. Solid edges indicate implemented milestone-1 file/tool paths; dashed edges indicate planned or not-yet-integrated links. These edge styles are not claims that the complete Agent workflow is currently automated.
- The diagram preserves program versus direct-row alternatives. Program execution is pending; source-table checks do not establish that a table came from a frozen generator. Independent evaluation has no feedback edge to the builder. The isolated execution boundary still requires implementation.
- The SVG retains draw.io's standard fallback link for SVG text compatibility. It makes no data requests. The parent HTML is the delivery/preview surface; no separate editor was intentionally opened.
- Source of implementation status: `../../README.md` and `../../MILESTONE_1_REPORT.md`. Diagram text is Chinese for the user's requested visual explanation.
- Visual-review revision: A (program) and B (direct rows) are explicit independent alternatives from the Agent. The B connector is pinned through the gap to the left of A, eliminating a misleading apparent A-to-B route. Both alternatives merge at distinct harness ports. There is no program-to-direct edge. Re-export retained 1162 by 1012 pixels.
