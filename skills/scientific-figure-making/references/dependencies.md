# Plotting Dependencies

Use this guide before installing packages. Work inside the user's target research project.

## Select the environment

Apply the first compatible option:

1. Follow project instructions and the existing manager indicated by `uv.lock`, `pyproject.toml`, `poetry.lock`, `environment.yml`, `conda-lock.yml`, or `requirements*.txt`.
2. Reuse an active project virtual environment or an existing `.venv`.
3. If the project has no environment convention, create a local `.venv` with `python3 -m venv .venv` and use `.venv/bin/python` on Linux/macOS or `.venv\Scripts\python.exe` on Windows.

Do not silently switch managers, regenerate an unrelated lockfile, or install into the interpreter that owns the Agent.

## Check before installing

Use the selected interpreter to test the imports required by the planned script. The core stack is:

```bash
python -c "import matplotlib, numpy"
```

Install only missing packages through the selected environment. Typical core package names are:

```text
numpy
matplotlib
```

Optional packages are evidence-driven:

- `scipy`: KDE, interpolation, distances, or statistical routines.
- `seaborn`: a selected heatmap or statistical plotting implementation that imports it.
- `python-dateutil`: calendar-aware month or date calculations.
- `pandas`: tabular loading or transformation when the project does not already provide it.

Do not install every optional package preemptively.

## Preserve reproducibility

- When the project already tracks dependencies, use its normal add/install command and update the corresponding lockfile consistently.
- For an unmanaged one-off project, keep packages in `.venv` and record the exact install command in the handoff.
- Run the plotting script with the same interpreter used for the import check.
- Report every dependency file changed and every package added.

If package resolution conflicts with existing pins, stop and show the conflicting requirements instead of forcing upgrades.
