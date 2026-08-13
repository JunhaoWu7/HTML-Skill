---
name: generate-html-report
description: Turn notes, Markdown, CSV files, screenshots, research, progress updates, and feedback into polished responsive HTML reports, dashboards, or result pages. Use when Codex is asked for an HTML 展示、HTML 汇报、可视化汇报、结果展示、周报、反馈分析页面、项目复盘页面, or another shareable browser-based presentation; also use when it should initialize or reuse a report-center workflow, build and test the result, then hand off private remote preview to serve-web-over-ssh.
---

# Generate HTML Report

Produce an evidence-based report from the user's materials, not a generic website mockup. Keep source content editable as Markdown and generate static HTML for reading, printing, or later publishing.

## Workflow

1. Inspect the current project and its instructions. If `report-center.json` and `scripts/build.py` exist, reuse that workflow and do not overwrite its templates or configuration.
2. Otherwise initialize the current project with:

   ```bash
   <this-skill>/scripts/init-report-center .
   ```

   The initializer preserves every existing file. Inspect its `PRESERVED` output and resolve incompatible existing paths instead of replacing user work.
3. Read only the materials the user supplied or placed in scope. Infer the audience and format when evidence is sufficient; ask only when missing information would materially change the report.
4. Create `reports/YYYY-MM-DD-topic.md`. Put report-owned CSV under `reports/data/` and images under `reports/images/`. Never invent facts, metrics, quotes, progress, or attribution.
5. Lead with the decision-useful conclusion. Select components according to evidence:

   - `metrics`: a few verified headline numbers.
   - `progress`: genuinely measurable 0–100 progress only.
   - `feedback`: representative positive, neutral, or negative quotes with sources.
   - `csv`: raw or summarized tabular data stored inside `reports/`.
   - Markdown tables and images: comparisons, mappings, evidence, or screenshots.

6. Run `make build` and `make test`. Inspect `public/index.html`, the generated report, unresolved `{{...}}` placeholders, missing relative assets, and accidental sensitive content.
7. For remote private preview, use `$serve-web-over-ssh` to serve only `public/`. Reuse the service name and preferred port from `report-center.json` when possible. Do not serve the repository root.
8. Return the report title, source path, generated HTML path, test result, service/session/log, SSH forwarding line, and local browser URL.

## Report defaults

- Use concise Chinese and put conclusions before process unless the user asks otherwise.
- Default to personal review. Let an explicit audience such as leadership, clients, or a technical team override tone and density.
- Use restrained typography, responsive layout, and print-friendly output. Prefer clarity over decorative animation.
- Preserve traceability to source materials. Surface uncertainty and missing evidence.
- Default to local files and loopback-only SSH preview. Public deployment or uploading source materials requires explicit user authorization and a sensitive-data check.

## Existing projects

Honor a project's `report-center.json` and local instructions as the source of truth. The bundled template is only a portable bootstrap. Do not copy it into a project that already has a compatible report center.

If the user requests a standalone downloadable HTML rather than a project report, copy the complete required output into the task's authorized artifact directory and verify that every linked asset is included. Do not treat ordinary project source files as downloadable artifacts.

## Failure handling

- Stop before publishing when confidential or personal data may be exposed.
- Keep the generated source when build or preview fails; report the exact failing stage.
- If `serve-web-over-ssh` is unavailable, finish the HTML report and explain that only persistent remote preview is missing.
- If a service already exists, inspect it before stopping or replacing it.
