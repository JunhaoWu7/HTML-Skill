# Personal Research Skills

一套面向长期科研和工作的个人 Skill 仓库，同时支持 **Claude Code** 与 **Codex**。仓库当前仍使用 `HTML-Skill` 名称，后续可以直接在 GitHub 改名；安装器不依赖仓库目录名。

## Skill 目录

| Skill | 来源 | 用途 |
|---|---|---|
| `generate-html-report` | 本仓库 | 把文字、Markdown、CSV、截图、进展和反馈整理成响应式 HTML 汇报，并构建和测试结果。 |
| `serve-web-over-ssh` | 本仓库 | 在远程 Linux 上持久运行静态页面或 Web UI，通过 SSH 转发安全访问，不公开端口。 |
| `scientific-figure-making` | [figures4papers](https://github.com/ChenLiu-1996/figures4papers) | 用 Matplotlib 制作论文级柱状图、趋势图、热力图、多面板图和矢量输出。 |

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
│   └── serve-web-over-ssh/
├── external/                       # 固定版本的第三方 Git 子模块
│   └── figures4papers/
│       └── scientific-figure-making/
├── scripts/validate-skills.py      # 全仓库 Skill 校验
├── tests/test-install.sh           # 双平台安装与冲突保护测试
├── install.sh                      # 自动发现并注册全部 Skill
├── CLAUDE.md                       # 仓库维护约定
└── AGENTS.md -> CLAUDE.md          # Claude Code / Codex 共用约定
```

新增第一方 Skill 时，只需放到 `skills/<skill-name>/` 并再次运行安装器，不需要手工修改 Skill 列表。

## 安装

推荐连同第三方 Skill 一起克隆：

```bash
git clone --recurse-submodules https://github.com/JunhaoWu7/HTML-Skill.git
cd HTML-Skill
./install.sh
```

普通 `git clone` 也可以；首次运行 `install.sh` 时会自动初始化声明过的 Git 子模块。

默认同时注册给 Claude Code 和 Codex，也可以只装一边：

```bash
./install.sh all       # 默认：两边都安装
./install.sh codex     # 仅 Codex
./install.sh claude    # 仅 Claude Code
```

默认安装位置：

- Codex：`${CODEX_HOME:-$HOME/.codex}/skills/`
- Claude Code：`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/`

安装器使用符号链接，因此更新仓库后现有 Skill 会立即使用新内容。它会自动迁移本仓库旧版的顶层链接；如果目标位置是普通文件、目录或指向其他项目的链接，则保留原内容并停止，不会覆盖。

安装完成后，重新打开 Claude Code 或 Codex 会话，让 Agent 刷新 Skill 列表。

## 更新

```bash
git pull --ff-only
git submodule update --init --recursive
./install.sh all
```

已有 Skill 只需 `git pull`；增加了新 Skill、调整目录或首次安装到另一种 Agent 时，再运行 `install.sh`。

## 依赖

安装器只检查和提示依赖，不会安装系统软件、修改防火墙或公开端口。

- 所有 Skill：Bash、Python 3
- 初始化第三方 Skill：Git 和网络访问
- 科研绘图：目标 Python 环境中的 `matplotlib`、`numpy`
- SSH 安全预览：`tmux`、`ss`（通常来自 `iproute2`）

Python 包应安装在实际研究项目的虚拟环境中，不要由 Skill 仓库强行修改全局环境。

## 使用科研绘图 Skill

可以直接告诉 Agent：

```text
把 results.csv 做成论文里的多方法对比柱状图，同时输出 PDF 和 PNG。
根据这组训练结果画两栏趋势图，带置信区间，适合论文双栏排版。
参考 figures4papers 的风格重做这张消融实验图，但不要改变数据含义。
```

`scientific-figure-making` 来自固定版本的 `figures4papers` 子模块，保留上游提交历史和作者来源。上游当前未提供明确的 `LICENSE` 文件，因此本仓库不复制或改写其 Skill 内容；更新上游版本时应先审查差异，再提交新的子模块指针。

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
