# Personal Research Skills — Repository Guide

## Architecture

- `skills/<name>/`: first-party Skills maintained in this repository.
- `install.sh`: discovers first-party adapters under `skills/`; no argument installs Codex by default, while explicit modes support Claude Code or both.
- `scripts/validate-skills.py`: validates names, frontmatter, folder matching, and duplicate names.
- `tests/`: repository-level installer and integration tests.

## Adding a Skill

1. Create a lowercase, hyphenated, action-oriented directory under `skills/`.
2. Keep `SKILL.md` concise with only `name` and `description` in YAML frontmatter.
3. Put deterministic automation in `scripts/`, detailed guidance in `references/`, and reusable output material in `assets/`.
4. Add `agents/openai.yaml` when Codex UI metadata is useful; the core Skill must still work without it in Claude Code.
5. Run `make test` and the official Skill validator before committing.

Copy third-party Skill material only when its license or explicit author permission permits redistribution. Record the source URL, exact revision, permission basis, imported scope, and local changes in a direct `references/` file; preserve attribution and avoid unrelated examples or assets.

## Compatibility and Safety

- Keep Skill instructions platform-neutral unless behavior genuinely differs between Claude Code and Codex.
- Do not commit credentials, unpublished research data, private papers, datasets, model weights, or generated research artifacts.
- Installation may create safe Skill symlinks. It must not install OS packages, modify firewalls, download unrelated example repositories, or overwrite unrelated paths.
- Keep `CLAUDE.md` and `AGENTS.md` synchronized. `AGENTS.md` is normally a symlink to this file.

## Validation

Run before and after changes:

```bash
make test
bash -n install.sh tests/test-install.sh
git diff --check
```
