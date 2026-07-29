---
name: serve-web-over-ssh
description: Persistently serve static HTML, reports, dashboards, notebooks, TensorBoard, Gradio, Streamlit, or other web UIs on a remote Linux server and make them accessible through secure SSH local-port forwarding. Use when Codex needs to launch, recover, inspect, list, stop, or explain access to a remote localhost web service without exposing it publicly, especially when the service must survive an SSH disconnect or several web pages share a reserved port range.
---

# Serve Web over SSH

Keep the web process and the transport separate:

- Run the remote web process inside a named `tmux` session.
- Bind the process to remote `127.0.0.1`, never a public interface.
- Reach it through SSH `LocalForward` rules on the user's computer.

Use `scripts/web-session` for deterministic lifecycle management. Do not expose a firewall port,
change a cloud security group, or bind to `0.0.0.0` unless the user explicitly asks for public
hosting and accepts that separate security model.

## Launch a static page

Run:

```bash
scripts/web-session start-static <name> <directory> [port|auto]
```

The default automatic range is `18000-18099`. The command prints the selected port, log path,
remote loopback URL, and required `LocalForward` rule.

Before launching, confirm that the directory contains only content the user intends to serve.
Do not serve a repository root, home directory, credential directory, raw session directory, or
other broad location merely for convenience.

## Launch an existing web application

Read the application's help or configuration to identify its host and port flags. Then run:

```bash
scripts/web-session start <name> <port|auto> <working-directory> -- \
  <command> --host 127.0.0.1 --port __PORT__
```

`__PORT__` is replaced in each argument with the selected port. Preserve the application's
existing environment instead of copying secrets into command-line arguments. If the application
cannot bind to loopback, stop and explain the exposure risk.

After launch, verify all of the following:

1. The named `tmux` session is alive.
2. The selected port is listening.
3. The listener is loopback-only. Treat wildcard or private/public interface listeners as unsafe.
4. The page responds locally on the remote host when an HTTP check is appropriate.
5. The log contains no immediate startup error.

The helper performs the first three checks when the server provides `ss`.

## Report access instructions

Always report:

- service name and selected remote port;
- remote session and log path;
- the exact `LocalForward` line;
- the URL to open on the user's computer;
- that the URL works only while the SSH connection or persistent tunnel is active.

For a fixed range, generate rules instead of writing them manually:

```bash
scripts/web-session forward-config 18000 18099
```

OpenSSH has no native port-range syntax; the helper expands the range into individual
`LocalForward` rules. Once those rules are under a host alias in the user's local
`~/.ssh/config`, an ordinary `ssh <alias>` activates the whole range.

When the user connects to multiple remote servers simultaneously, assign a distinct local range
to each server. For example:

```bash
# Remote 18000-18099 becomes local 18100-18199.
scripts/web-session forward-config 18000 18099 18100
```

## Manage services

Use:

```bash
scripts/web-session list
scripts/web-session status <name>
scripts/web-session logs <name> [line-count]
scripts/web-session stop <name>
```

Inspect before stopping. `stop` terminates only the helper-owned named `tmux` session and retains
its log. Do not kill unrelated processes that happen to use a requested port.

## Failure handling

- If `tmux`, Python, or `ss` is unavailable, report the missing prerequisite; do not silently
  install system packages.
- If a port is occupied, choose another free port in the reserved range.
- If the remote session remains alive but the user's browser cannot connect, check the local SSH
  configuration, local port conflicts, active SSH process, and application WebSocket/base-path
  settings in that order.
- If SSH disconnects, the remote `tmux` service continues, but the local URL stops until the
  tunnel reconnects.
- For restart-after-reboot requirements, propose a user-level `systemd` service as a separate,
  explicit change. Do not enable lingering or create system services without authorization.
