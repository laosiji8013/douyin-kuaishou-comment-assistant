# 抖音 / 快手交互式评论助手

这是一个从历史自动化原型整理而来的 Python + Playwright 项目。它保留抖音、快手的平台适配、搜索/手动导航、随机观看时间、随机事件、评论候选和浏览器登录态，改为**逐条人工审核和二次确认后互动**。

> 默认是 `dry-run`：可以观察随机计划和操作流程，但不会输入评论、发送或点赞。实时模式也不会无人值守批量发布，每条评论和点赞都需要人在终端确认。

## 项目状态

- 历史资料记录：抖音和快手版本曾在 2026 年 6—7 月完成本机测试；
- 当前公开整理版：代码、配置和离线测试已校验；
- 平台页面会变化，历史选择器不代表现在仍兼容；
- 其他平台不在本仓库范围内，也没有宣称经过测试。

## 它能做什么

- 打开抖音或快手网页版并复用本机浏览器资料目录；
- 由用户手动打开视频，或用关键词搜索后打开首条视频；
- 为每条视频随机生成观看档位、等待时间、行为候选和节奏；
- 从本地评论库随机选择一条，交给用户跳过、编辑或确认；
- 实时模式下，只有经过本条确认和最终 `SEND` 二次确认才点击发送；
- 将点赞作为随机“候选事件”，但每次仍询问用户；
- 用 `--seed` 固定随机结果，方便调试和复现。

## 安装

需要 Python 3.11—3.13。

```bash
git clone YOUR_REPOSITORY_URL
cd douyin-kuaishou-comment-assistant
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m playwright install chromium
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
```

## 第一次运行

先使用默认安全模式：

```bash
comment-assistant kuaishou --navigation manual --max-videos 3 --seed 42
```

程序会：

1. 打开浏览器；
2. 等你扫码登录；
3. 等你手动打开第一条视频；
4. 打印本条随机计划；
5. 展示评论候选并询问选择；
6. 因为默认是 `dry-run`，不会向平台输入或发送。

抖音同理：

```bash
comment-assistant douyin --navigation manual --max-videos 3 --seed 42
```

自动搜索导航：

```bash
comment-assistant kuaishou --navigation search --keyword "公开教程" --max-videos 3
```

如果页面改版导致搜索或下一条失效，改用 `--navigation manual`，其余审核流程仍可使用。

## 实时交互模式

```bash
comment-assistant kuaishou --navigation manual --interactive-live
```

实时模式有三道明确的人为动作：

1. 启动时输入 `INTERACTIVE LIVE`；
2. 每条候选选择发送或编辑；
3. 输入框填好后输入 `SEND`，程序才点击发送。

没有 `--interactive-live` 时，即使你在审核菜单里选了发送，也不会操作平台输入框和按钮。

## 修改评论与关键词

公开示例在：

- `data/comments.example.json`
- `data/keywords.example.json`

不要直接把真实内部资料提交到 Git。推荐复制为本地文件：

```bash
cp data/comments.example.json data/comments.local.json
cp data/keywords.example.json data/keywords.local.json
```

运行时指定：

```bash
comment-assistant douyin \
  --comments data/comments.local.json \
  --keywords data/keywords.local.json
```

这两个 `.local.json` 已被 `.gitignore` 排除。

## 随机时间和随机事件

所有参数集中在 `config/default.json`，无需改 Python。主要分为四组：

- `timing.watch_tiers`：短看、正常看、深度看三个时间区间和权重；
- `timing`：超长观看、评论区阅读、输入前思考、发送前停顿、连续处理与间歇、快慢节奏；
- `events`：行为模式、悬停、鼠标游走、滚动、错字、取消、点赞候选、跳过窗口；
- `session`：单次上限、错误阈值、工作区间和休息区间。

完整解释、计算方式和修改示例见 [随机时间与随机事件配置手册](docs/CONFIGURATION.md)。

## 命令参数

```text
comment-assistant {douyin,kuaishou}
  [--config PATH]
  [--comments PATH]
  [--keywords PATH]
  [--keyword TEXT]
  [--navigation {manual,search}]
  [--max-videos N]
  [--seed INTEGER]
  [--interactive-live]
```

## 隐私和安全

- `browser_data/` 保存本机登录态，已被 Git 忽略，绝对不要上传；
- 真实评论库、截图、日志、本地配置同样不要提交；
- 示例语料已替换为中性虚构内容；
- 项目没有代理池、验证码绕过、多账号控制或无人值守批量发布；
- 使用者必须遵守平台当前规则，并对自己的每次互动负责。

见 [安全设计](docs/SAFETY.md)、[脱敏记录](docs/SANITIZATION.md) 和 [发布前检查](docs/PUBLISH_CHECKLIST.md)。

## 开发与验证

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
python -m compileall -q src
```

## 许可证

本项目使用 [MIT License](LICENSE)。它允许他人使用、修改和再发布代码，但不提供平台兼容性或账号安全保证。
