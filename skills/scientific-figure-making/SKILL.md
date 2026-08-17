---
name: scientific-figure-making
description: Create or refine publication-ready Matplotlib figures for academic papers, slides, and technical reports using an attributed figures4papers-derived design system. Use for bar charts, trends, scatter plots, heatmaps, radar plots, multi-panel layouts, ablations, confidence intervals, and PDF/SVG/high-DPI export; also use when the plotting environment or required Python packages must be prepared. Do not use for interactive web dashboards, exploratory-only plots without a publication target, GIS-first work, or Illustrator/Figma-first infographics.
---

# Scientific Figure Making

Produce a reproducible plotting script and verified outputs from the user's real data. Preserve data meaning and uncertainty; never invent measurements, labels, error bars, or statistical significance.

## Workflow

1. Inspect the project instructions, existing environment, data schema, nearby plotting scripts, target venue, and requested output formats. Ask only when a missing choice would materially change the figure.
2. Prepare the project-local Python environment before writing the final script. Read [references/dependencies.md](references/dependencies.md), reuse the project's package manager or virtual environment, check imports, and install only missing packages.
3. Treat installation of required Python packages into an existing project-local environment as part of the requested figure task. Do not pause merely to ask whether `numpy` or `matplotlib` may be installed. Pause when installation would affect a global/system environment, replace an incompatible lockfile, require `sudo`, or make another material project-level choice.
4. Open only the references needed for the requested chart. Use [references/design-theory.md](references/design-theory.md) for visual decisions, [references/api.md](references/api.md) for helper contracts, [references/common-patterns.md](references/common-patterns.md) for layouts, and [references/tutorials.md](references/tutorials.md) for end-to-end flows. Use [references/demos.md](references/demos.md) only when an online upstream example is materially helpful.
5. Create or update the plotting script inside the user's research project, not inside this Skill repository. Separate data loading, validation, plotting, and export so the figure can be regenerated.
6. Use a non-interactive backend for unattended runs. Prefer PDF or SVG for publication and PNG at 300 DPI or higher for review; follow explicit venue requirements over defaults.
7. Run the script with the prepared environment. Verify every expected file exists, inspect the rendered figure when visual tools are available, and check clipping, legibility, legend placement, color semantics, grayscale distinction, and consistency between panels.
8. Report the script path, output paths, environment or dependency changes, validation performed, and any remaining uncertainty.

## Boundaries

- Install Python libraries only into the current project's managed environment or a project-local `.venv`.
- Never run global `pip`, `sudo`, `apt`, `yum`, or equivalent system installers automatically.
- Prefer MathText and portable font fallbacks when TeX or proprietary fonts are absent. Installing system TeX or fonts requires explicit user approval.
- Add optional libraries only when the selected implementation imports them; keep the default dependency set minimal.
- Do not commit `.venv`, caches, private datasets, generated intermediate data, or credentials.

## Provenance

This Skill incorporates the `scientific-figure-making` methods and reference material from [figures4papers](https://github.com/ChenLiu-1996/figures4papers) with permission reported by this repository's maintainer. See [references/source.md](references/source.md) for the exact source revision and integration scope.
