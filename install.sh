#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
install_mode="${1:-all}"

usage() {
  printf 'Usage: %s [all|codex|claude]\n' "${0##*/}"
  printf '  all     Register every Skill for Codex and Claude Code (default).\n'
  printf '  codex   Register every Skill only for Codex.\n'
  printf '  claude  Register every Skill only for Claude Code.\n'
}

case "${install_mode}" in
  -h|--help)
    usage
    exit 0
    ;;
  all|codex|claude) ;;
  *)
    usage >&2
    exit 2
    ;;
esac

if [[ -f "${repo_root}/.gitmodules" && ! -f "${repo_root}/external/figures4papers/scientific-figure-making/SKILL.md" ]]; then
  if ! command -v git >/dev/null 2>&1; then
    printf 'ERROR: git is required to initialize the external Skill submodules.\n' >&2
    exit 1
  fi
  printf 'Initializing external Skill submodules...\n'
  if ! git -C "${repo_root}" submodule update --init --recursive --depth 1; then
    printf 'ERROR: failed to initialize external Skill submodules. Check network access and retry.\n' >&2
    exit 1
  fi
fi

missing_commands=()
for command_name in bash python3 tmux ss; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    missing_commands+=("${command_name}")
  fi
done

if ((${#missing_commands[@]} > 0)); then
  printf 'WARNING: missing runtime dependencies: %s\n' "${missing_commands[*]}" >&2
  printf 'Skills will be registered, but some build, plotting, or preview actions may not work.\n' >&2
  printf 'Install system dependencies yourself; this installer will not modify the OS or firewall.\n' >&2
fi

shopt -s nullglob
skill_sources=()
for candidate in "${repo_root}"/skills/*; do
  if [[ -f "${candidate}/SKILL.md" ]]; then
    skill_sources+=("${candidate}")
  fi
done
shopt -u nullglob

if ((${#skill_sources[@]} == 0)); then
  printf 'ERROR: no Skill directories were found.\n' >&2
  exit 1
fi

declare -A seen_skill_names=()
skill_names=()
for source_path in "${skill_sources[@]}"; do
  skill_name="${source_path##*/}"
  if [[ -n "${seen_skill_names[${skill_name}]:-}" ]]; then
    printf 'ERROR: duplicate Skill name: %s\n' "${skill_name}" >&2
    exit 1
  fi
  seen_skill_names["${skill_name}"]="${source_path}"
  skill_names+=("${skill_name}")
done

platform_names=()
platform_skill_dirs=()

add_codex_platform() {
  local codex_root
  if [[ -n "${CODEX_HOME:-}" ]]; then
    codex_root="${CODEX_HOME}"
  elif [[ -n "${HOME:-}" ]]; then
    codex_root="${HOME}/.codex"
  else
    printf 'ERROR: set CODEX_HOME or HOME before installing for Codex.\n' >&2
    exit 1
  fi
  platform_names+=("Codex")
  platform_skill_dirs+=("${codex_root}/skills")
}

add_claude_platform() {
  local claude_root
  if [[ -n "${CLAUDE_CONFIG_DIR:-}" ]]; then
    claude_root="${CLAUDE_CONFIG_DIR}"
  elif [[ -n "${HOME:-}" ]]; then
    claude_root="${HOME}/.claude"
  else
    printf 'ERROR: set CLAUDE_CONFIG_DIR or HOME before installing for Claude Code.\n' >&2
    exit 1
  fi
  platform_names+=("Claude Code")
  platform_skill_dirs+=("${claude_root}/skills")
}

case "${install_mode}" in
  all)
    add_codex_platform
    add_claude_platform
    ;;
  codex) add_codex_platform ;;
  claude) add_claude_platform ;;
esac

conflict_found=0
for platform_index in "${!platform_names[@]}"; do
  skills_dir="${platform_skill_dirs[${platform_index}]}"
  mkdir -p -- "${skills_dir}"

  for skill_index in "${!skill_names[@]}"; do
    skill_name="${skill_names[${skill_index}]}"
    source_path="${skill_sources[${skill_index}]}"
    target_path="${skills_dir}/${skill_name}"
    legacy_path="${repo_root}/${skill_name}"
    upstream_figure_path="${repo_root}/external/figures4papers/scientific-figure-making"

    if [[ -L "${target_path}" ]]; then
      current_link="$(readlink -- "${target_path}")"
      if [[ "${target_path}" -ef "${source_path}" || "${current_link}" == "${legacy_path}" || \
        ("${skill_name}" == "scientific-figure-making" && "${current_link}" == "${upstream_figure_path}") ]]; then
        continue
      fi
      printf 'ERROR: preserving existing symlink with a different target: %s -> %s\n' \
        "${target_path}" "${current_link}" >&2
      conflict_found=1
    elif [[ -e "${target_path}" ]]; then
      printf 'ERROR: preserving existing non-symlink path: %s\n' "${target_path}" >&2
      conflict_found=1
    fi
  done
done

if ((conflict_found)); then
  printf 'Resolve the paths above manually, then run this installer again. Nothing was overwritten.\n' >&2
  exit 1
fi

for platform_index in "${!platform_names[@]}"; do
  platform_name="${platform_names[${platform_index}]}"
  skills_dir="${platform_skill_dirs[${platform_index}]}"
  printf '\n%s Skills: %s\n' "${platform_name}" "${skills_dir}"

  for skill_index in "${!skill_names[@]}"; do
    skill_name="${skill_names[${skill_index}]}"
    source_path="${skill_sources[${skill_index}]}"
    target_path="${skills_dir}/${skill_name}"
    legacy_path="${repo_root}/${skill_name}"
    upstream_figure_path="${repo_root}/external/figures4papers/scientific-figure-making"

    if [[ -L "${target_path}" && "${target_path}" -ef "${source_path}" ]]; then
      printf 'Already installed: %s\n' "${skill_name}"
      continue
    fi

    current_link=""
    if [[ -L "${target_path}" ]]; then
      current_link="$(readlink -- "${target_path}")"
    fi

    if [[ -L "${target_path}" && ("${current_link}" == "${legacy_path}" || \
      ("${skill_name}" == "scientific-figure-making" && "${current_link}" == "${upstream_figure_path}")) ]]; then
      rm -- "${target_path}"
      ln -s -- "${source_path}" "${target_path}"
      printf 'Migrated: %s -> %s\n' "${skill_name}" "${source_path}"
    else
      ln -s -- "${source_path}" "${target_path}"
      printf 'Installed: %s -> %s\n' "${skill_name}" "${source_path}"
    fi
  done
done

printf '\nInstallation complete. Start a new Agent session to refresh its Skill list.\n'
printf 'Future Skills added under skills/ are discovered automatically the next time this installer runs.\n'
