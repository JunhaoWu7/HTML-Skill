# HTML-Skill

这个仓库包含两套可以组合使用的 Skill：

- `generate-html-report`：把文字、Markdown、CSV、截图、进展和反馈整理成响应式 HTML 汇报，自动构建和测试。
- `serve-web-over-ssh`：让静态 HTML、训练面板和其他网页在远程服务器持久运行，并通过 SSH 安全访问。

组合后的默认链路是：

```text
材料和需求 → generate-html-report → public/ 静态报告
                                     ↓
                           serve-web-over-ssh
                                     ↓
                           本地浏览器安全查看
```

`serve-web-over-ssh` 是一套面向远程 Linux 服务器的通用 Skill：让 Codex 将静态 HTML、
训练面板、评测页面、TensorBoard、Gradio、Streamlit 等网页持久运行在服务器本机，并通过
SSH 加密隧道安全地带回你的电脑。

它解决两个彼此独立的问题：

```text
远端网页进程 ── tmux 持久运行，SSH 断开也不退出
      │
服务器 127.0.0.1:18000-18099
      │
      └──── SSH LocalForward 加密隧道 ────> 本地 127.0.0.1:18000-18099
```

网页不会直接暴露到公网。SSH 在线时，本地浏览器访问 `http://127.0.0.1:端口`；SSH
断开后，远端网页仍然运行，但本地入口暂时失效，重新连接后恢复。

## 一、安装 Skill

在每台远程服务器上执行：

```bash
git clone https://github.com/JunhaoWu7/HTML-Skill.git
cd HTML-Skill
mkdir -p ~/.codex/skills
ln -s "$PWD/serve-web-over-ssh" ~/.codex/skills/serve-web-over-ssh
ln -s "$PWD/generate-html-report" ~/.codex/skills/generate-html-report
```

如果目标位置已经存在，先检查它是不是旧版本或正确的符号链接，不要直接覆盖。更新仓库：

```bash
cd HTML-Skill
git pull --ff-only
```

脚本要求远端 Linux 具备：

- Bash
- Python 3
- `tmux`
- `ss`（通常由 `iproute2` 提供，用于验证服务没有监听公网）

Skill 不会自行安装系统软件或修改防火墙。

## 二、让 Agent 自动生成 HTML 汇报

安装两套 Skill 后，直接告诉 Agent：

```text
把这些材料做成 HTML 展示，结论放前面。
把 feedback.csv 做成反馈分析页面。
把本周进展和截图整理成给领导看的周报。
```

`generate-html-report` 会优先复用项目现有的报告工作流。如果项目还没有报告中心，它会用自带模板进行初始化，然后生成报告、运行构建和测试，最后调用 `serve-web-over-ssh` 返回安全预览地址。

默认不会把报告公开到互联网，也不会主动上传原始材料。需要公网分享时必须明确提出，并在发布前检查敏感信息。

## 三、在自己的电脑配置固定端口段

**这一步必须在你自己的电脑上完成，不是在远程服务器上完成。** 远端安装 Skill 只能保持
网页进程运行；没有本地 SSH 转发，浏览器仍然无法访问远端的 `127.0.0.1`。

OpenSSH 不支持 `18000-18099` 这样的范围语法，但可以自动生成全部规则，不需要手写。

先在任意已经克隆本仓库的机器生成配置：

```bash
./serve-web-over-ssh/scripts/web-session forward-config 18000 18099
```

把输出放到你自己电脑的 `~/.ssh/config` 对应服务器条目中：

```sshconfig
Host cot-server
    HostName 服务器的 IP 或域名
    User ec2-user
    IdentityFile ~/.ssh/你的私钥

    LocalForward 127.0.0.1:18000 127.0.0.1:18000
    LocalForward 127.0.0.1:18001 127.0.0.1:18001
    # 中间规则由脚本生成
    LocalForward 127.0.0.1:18099 127.0.0.1:18099

    ServerAliveInterval 30
    ServerAliveCountMax 3
    TCPKeepAlive yes
    ExitOnForwardFailure yes
```

以后直接登录：

```bash
ssh cot-server
```

这次 SSH 连接会同时提供终端和整个端口段。只建立隧道、不需要终端时：

```bash
ssh -N cot-server
```

如果尚未写入固定端口段，可以先用单端口命令立即访问。例如网页在远端 `18037`：

```bash
ssh -L 127.0.0.1:18037:127.0.0.1:18037 ec2-user@服务器地址
```

保持这条 SSH 连接运行，然后在本地浏览器打开 `http://127.0.0.1:18037`。确认可用后，再把
整段规则写入本地 SSH config。

Windows 自带 OpenSSH 的配置文件通常位于 `%USERPROFILE%\.ssh\config`；Linux 和 macOS
通常位于 `~/.ssh/config`。

需要断线自动重连时，可以在自己的电脑安装 `autossh`，然后运行：

```bash
autossh -M 0 -N cot-server
```

`autossh` 只负责本地隧道；远端网页由本 Skill 的 `tmux` 会话保持。

### 同时连接多台服务器

同一台电脑不能让两个 SSH 进程同时监听相同的本地端口。为每台服务器分配不同本地端口段，
但远端仍统一使用 `18000-18099`：

```text
服务器 A：本地 18000-18099 → 远端 18000-18099
服务器 B：本地 18100-18199 → 远端 18000-18099
服务器 C：本地 18200-18299 → 远端 18000-18099
```

生成服务器 B 的规则：

```bash
./serve-web-over-ssh/scripts/web-session forward-config 18000 18099 18100
```

此时服务器 B 的远端 `18037` 对应你电脑的：

```text
http://127.0.0.1:18137
```

## 四、持久展示静态 HTML

假设网页目录是 `/path/to/report`：

```bash
./serve-web-over-ssh/scripts/web-session \
  start-static my-report /path/to/report auto
```

脚本会从 `18000-18099` 中选择空闲端口，并输出类似：

```text
SERVICE_NAME=my-report
REMOTE_PORT=18000
TMUX_SESSION=web-ssh-my-report
LOG=/home/user/.local/state/serve-web-over-ssh/my-report.log
REMOTE_URL=http://127.0.0.1:18000/
LOCAL_URL=http://127.0.0.1:18000/
SSH_CONFIG=LocalForward 127.0.0.1:18000 127.0.0.1:18000
```

如果本地 SSH 端口段已经配置好，直接在自己的浏览器打开 `LOCAL_URL`。

不要为了方便把整个项目根目录、Home 目录、凭证目录、原始训练数据或私有 session 目录作为
网页目录。

## 五、持久运行现有网页应用

通用格式：

```bash
./serve-web-over-ssh/scripts/web-session \
  start 服务名 auto 工作目录 -- \
  应用启动命令 --host 127.0.0.1 --port __PORT__
```

`__PORT__` 会被替换成自动选择的端口。例如：

```bash
./serve-web-over-ssh/scripts/web-session \
  start tensorboard auto /path/to/project -- \
  tensorboard --host 127.0.0.1 --port __PORT__ --logdir runs
```

不同框架的 host/port 参数名称不同，运行前先查看该应用的 `--help`。必须绑定
`127.0.0.1`，不要绑定 `0.0.0.0`。

如果应用依赖虚拟环境，先激活环境，再调用脚本；脚本会继承当前环境。不要把 API key 或
令牌直接写进命令参数。

## 六、查询、日志与停止

```bash
# 查看全部由 Skill 管理的服务
./serve-web-over-ssh/scripts/web-session list

# 查看一个服务的状态
./serve-web-over-ssh/scripts/web-session status my-report

# 查看最后 100 行日志
./serve-web-over-ssh/scripts/web-session logs my-report 100

# 停止服务；日志会保留
./serve-web-over-ssh/scripts/web-session stop my-report
```

服务状态和日志默认保存在：

```text
~/.local/state/serve-web-over-ssh/
```

## 七、常见故障

### 浏览器显示无法连接

依次检查：

```bash
# 远端：服务是否仍在运行
./serve-web-over-ssh/scripts/web-session list

# 远端：网页是否本机可访问
curl -I http://127.0.0.1:18000/

# 本地：SSH 是否正在监听对应端口
ssh -v cot-server
```

还要确认浏览器使用的是本地映射端口。如果服务器 B 将远端 `18037` 映射到本地 `18137`，
就应访问 `http://127.0.0.1:18137`。

### SSH 连接失败，提示端口占用

本地已有进程占用了这个端口，或者另一条 SSH 隧道已经绑定该端口。停止冲突进程，或者为该
服务器使用另一段本地端口。

### SSH 断开后网页发生了什么

- 远端 `tmux` 中的网页进程继续运行；
- 本地转发端口消失；
- 重新执行 `ssh cot-server` 后，转发恢复；
- 如果服务器重启，`tmux` 服务不会自动恢复。需要跨重启自动启动时，应另外配置
  `systemd --user`，并明确评估权限和安全设置。

## 安全原则

- 网页服务仅监听远端 `127.0.0.1`。
- SSH 本地转发仅监听本地 `127.0.0.1`。
- 不开放云安全组或防火墙入站端口。
- 不在仓库、命令参数、网页目录或日志中保存令牌和凭证。
- 公网分享是另一种部署模式，不属于这个 Skill 的默认行为。
