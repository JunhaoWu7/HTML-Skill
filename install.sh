#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
skills_dir="${codex_home}/skills"
skill_names=(
  generate-html-report
  serve-web-over-ssh
)

missing_commands=()
for command_name in bash python3 tmux ss; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    missing_commands+=("${command_name}")
  fi
done

if ((${#missing_commands[@]} > 0)); then
  printf 'WARNING: missing system dependencies: %s\n' "${missing_commands[*]}" >&2
  printf 'The Skills will be registered, but some build or preview actions may not work.\n' >&2
  printf 'Install dependencies with your system package manager; this installer will not do it for you.\n' >&2
fi

mkdir -p -- "${skills_dir}"

conflict_found=0
for skill_name in "${skill_names[@]}"; do
  source_path="${repo_root}/${skill_name}"
  target_path="${skills_dir}/${skill_name}"

  if [[ ! -f "${source_path}/SKILL.md" ]]; then
    printf 'ERROR: invalid Skill source: %s\n' "${source_path}" >&2
    exit 1
  fi

  if [[ -L "${target_path}" ]]; then
    if [[ ! "${target_path}" -ef "${source_path}" ]]; then
      printf 'ERROR: preserving existing symlink with a different target: %s -> %s\n' \
        "${target_path}" "$(readlink -- "${target_path}")" >&2
      conflict_found=1
    fi
  elif [[ -e "${target_path}" ]]; then
    printf 'ERROR: preserving existing non-symlink path: %s\n' "${target_path}" >&2
    conflict_found=1
  fi
done

if ((conflict_found)); then
  printf 'Resolve the paths above manually, then run this installer again. Nothing was overwritten.\n' >&2
  exit 1
fi

for skill_name in "${skill_names[@]}"; do
  source_path="${repo_root}/${skill_name}"
  target_path="${skills_dir}/${skill_name}"

  if [[ -L "${target_path}" ]]; then
    printf 'Already installed: %s -> %s\n' "${target_path}" "${source_path}"
  else
    ln -s -- "${source_path}" "${target_path}"
    printf 'Installed: %s -> %s\n' "${target_path}" "${source_path}"
  fi
done

printf '\nInstallation complete. Start a new Codex session to discover the Skills.\n'
printf 'Then ask for an HTML 展示、HTML 汇报、周报或反馈分析页面。\n'
