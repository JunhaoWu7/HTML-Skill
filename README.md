# Personal Research Skills

一套面向长期科研和工作的个人 Skill 仓库，默认安装到 **Codex**，同时支持 **Claude Code**。仓库当前仍使用 `HTML-Skill` 名称，后续可以直接在 GitHub 改名；安装器不依赖仓库目录名。

## Skill 目录

| Skill | 来源 | 用途 |
|---|---|---|
| `generate-html-report` | 本仓库 | 把文字、Markdown、CSV、截图、进展和反馈整理成响应式 HTML 汇报，并构建和测试结果。 |
| `serve-web-over-ssh` | 本仓库 | 在远程 Linux 上持久运行静态页面或 Web UI，通过 SSH 转发安全访问，不公开端口。 |
| `scientific-figure-making` | 经授权集成自 [figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 自动准备项目绘图环境，并用 Matplotlib 制作论文级柱状图、趋势图、热力图、多面板图和矢量输出。 |

HTML 汇报链路可以独立使用，也可以与其他科研 Skill 组合：

```text
研究材料 → 分析或绘图 Skill → generate-html-report → public/ 静态报告
                                                    ↓
                                          serve-web-over-ssh
                                                    ↓
                                             本地浏览器查看
```

## 仓库架构

```text
.
├── skills/                         # 自己维护的第一方 Skill
│   ├── generate-html-report/
│   ├── scientific-figure-making/   # 本地集成的方法、规范和依赖工作流
│   └── serve-web-over-ssh/
├── scripts/validate-skills.py      # 全仓库 Skill 校验
├── tests/test-install.sh           # 双平台安装与冲突保护测试
├── install.sh                      # 自动发现并注册全部 Skill
├── CLAUDE.md                       # 仓库维护约定
└── AGENTS.md -> CLAUDE.md          # Claude Code / Codex 共用约定
```

新增 Skill 时，只需放到 `skills/<skill-name>/` 并再次运行安装器，不需要手工修改 Skill 列表。

## 安装

克隆并安装：

```bash
git clone https://github.com/JunhaoWu7/HTML-Skill.git
cd HTML-Skill
./install.sh
```

无参数运行时默认只注册给 Codex。需要 Claude Code 或两边同时使用时，显式选择对应模式：

```bash
./install.sh           # 默认：仅 Codex
./install.sh codex     # 明确指定仅 Codex
./install.sh claude    # 仅 Claude Code
./install.sh all       # Codex + Claude Code
```

默认安装位置：

- Codex：`${CODEX_HOME:-$HOME/.codex}/skills/`
- Claude Code：`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/`

安装器使用符号链接，因此更新仓库后现有 Skill 会立即使用新内容。它会自动迁移本仓库旧版的顶层链接；如果目标位置是普通文件、目录或指向其他项目的链接，则保留原内容并停止，不会覆盖。

安装完成后，重新打开 Claude Code 或 Codex 会话，让 Agent 刷新 Skill 列表。

## 更新

```bash
git pull --ff-only
./install.sh           # 默认更新或安装 Codex
```

已有 Skill 只需 `git pull`；增加了新 Skill、调整目录或首次安装到另一种 Agent 时，再运行对应模式，例如 `./install.sh claude` 或 `./install.sh all`。

## 依赖

安装器只检查和提示依赖，不会安装系统软件、修改防火墙或公开端口。

- 所有 Skill：Bash、Python 3
- 科研绘图：Skill 会按需在目标项目环境中安装 `matplotlib`、`numpy`，并且只在脚本需要时增加 `scipy`、`seaborn`、`python-dateutil` 或 `pandas`
- SSH 安全预览：`tmux`、`ss`（通常来自 `iproute2`）

Python 包会安装在实际研究项目已有的环境或项目本地 `.venv` 中，不会修改 Agent 自身或系统全局 Python。若安装需要 `sudo`、系统包、替换冲突的锁文件或强制升级已有依赖，Agent 会停止并说明原因。

## 使用科研绘图 Skill

可以直接告诉 Agent：

```text
把 results.csv 做成论文里的多方法对比柱状图，同时输出 PDF 和 PNG。
根据这组训练结果画两栏趋势图，带置信区间，适合论文双栏排版。
参考 figures4papers 的风格重做这张消融实验图，但不要改变数据含义。
```

`scientific-figure-making` 的方法规范经作者许可，从 `figures4papers` 的提交 `6790a93` 集成并保留来源说明；本仓库另外加入项目环境、按需安装、输出验证和可复现性规则。没有复制上游的 `figure_*` 案例脚本、图片或生成结果，因此安装时也不会额外下载案例库。在线案例链接只在 Agent 确实需要参考时使用。

## 使用 HTML 汇报 Skill

可以直接告诉 Agent：

```text
把这些材料做成 HTML 展示，结论放前面。
把 feedback.csv 做成反馈分析页面。
把本周实验进展、图表和问题整理成组会汇报页面。
```

`generate-html-report` 会优先复用当前项目已有的报告链路。若不存在，它会用自带模板初始化报告中心，生成 Markdown 源文件和静态 HTML，运行构建与测试；需要远程预览时，再交给 `serve-web-over-ssh`。

默认不公开部署，也不上传原始材料。公网发布必须由用户明确提出，并先检查未发表结果、个人信息和凭证。

## SSH 安全预览快速用法

远端静态页面目录为 `/path/to/report` 时：

```bash
./skills/serve-web-over-ssh/scripts/web-session \
  start-static my-report /path/to/report auto
```

工具只绑定远端 `127.0.0.1`，并返回端口和 SSH 转发规则。本地电脑建立单端口隧道：

```bash
ssh -L 127.0.0.1:18037:127.0.0.1:18037 USER@SERVER
```

固定端口段可以生成全部 OpenSSH 配置：

```bash
./skills/serve-web-over-ssh/scripts/web-session forward-config 18000 18099
```

常用管理命令：

```bash
./skills/serve-web-over-ssh/scripts/web-session list
./skills/serve-web-over-ssh/scripts/web-session status my-report
./skills/serve-web-over-ssh/scripts/web-session logs my-report 100
./skills/serve-web-over-ssh/scripts/web-session stop my-report
```

不要把仓库根目录、Home、凭证目录、原始训练数据或私有会话目录作为网页根目录。

## 开发和验证

添加或更新 Skill 后运行：

```bash
make test
bash -n install.sh tests/test-install.sh
git diff --check
```

每个第一方 Skill 应遵循以下原则：

1. 名称使用小写字母、数字和连字符，目录名与 `SKILL.md` 的 `name` 一致。
2. `SKILL.md` 只保留核心流程；详细规范放 `references/`，确定性操作放 `scripts/`，模板放 `assets/`。
3. 核心说明保持平台中立；`agents/openai.yaml` 可以提供 Codex 界面元数据，但不能成为 Claude Code 使用 Skill 的前提。
4. 不提交 API Key、未发表研究数据、私有论文、数据集、模型权重或生成产物。
