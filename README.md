# 抖音 / 快手交互式评论助手

一个从已验证历史原型整理而来的 Python + Playwright 项目，面向抖音、快手网页版的评论准备、浏览节奏编排和逐条发布确认。项目保留了平台适配、关键词导航、浏览器登录态、随机时间、随机事件、评论候选和会话节奏，并把所有关键参数集中到 JSON 配置中。

> 鉴于平台规则和网页变化，本仓库对功能采用相对保守、可核验的表述。默认配置只是示例，使用者可以自行修改观看时间、事件概率、动作权重、评论内容和会话上限；修改不代表平台许可，也不保证账号不会受到限制。

默认运行模式是 `dry-run`：生成并展示计划，但不会输入评论、发送或点赞。浏览器实时模式需要启动确认、逐条审核和最终 `SEND` 二次确认。

## 适用场景

在账号、内容和发布行为均已获得授权，并符合平台规则的前提下，可用于：

- 自有账号的评论回复准备与逐条发布；
- 创作者或品牌账号的活动答疑、售前咨询和客户服务回复；
- 从本地语料库抽取候选文案，人工编辑后发布；
- 宣传活动、商品介绍或广告内容的审核与发布辅助；
- 演示 Playwright 平台适配、随机计划、配置校验和可复现测试；
- 作为接入平台官方开放接口、企业客服系统或内容审核系统的基础框架。

不适用于未经许可的批量广告、骚扰评论、虚假互动、刷量、多账号控制、验证码绕过、指纹伪装或规避平台限制。

## 当前能力

| 能力 | 当前实现 | 是否自动产生平台动作 |
| --- | --- | --- |
| 打开抖音 / 快手网页版 | Playwright 平台适配器 | 是，仅导航 |
| 登录态复用 | 本机持久浏览器资料目录 | 是，资料只保存在本机 |
| 视频导航 | 手动切换或关键词搜索 | 可配置 |
| 观看时间 | 按档位、权重和节奏随机生成 | 是，等待动作 |
| 评论区浏览 | 滚动、悬停、停顿、游走等权重动作 | 是，不发布内容 |
| 评论选择 | 从本地 JSON 随机抽取，可跳过或编辑 | 需要人工审核 |
| 评论发送 | 填入后输入 `SEND` 才点击发送 | 需要逐条确认 |
| 点赞 | 随机生成候选事件 | 需要逐次确认 |
| 随机复现 | `--seed` 固定随机序列 | 不产生额外动作 |
| 无人值守批量发送 | 当前浏览器模式未提供；已给出合规扩展路线 | 否 |

这不是“只能看不能用”的演示：实时模式已经完整覆盖打开页面、生成计划、执行浏览动作、抽取文案、编辑、填入输入框和点击发送。人工确认是当前发布策略，而不是代码尚未完成。需要自动发布的团队可在测试通过后替换发布策略，但应通过平台官方接口或企业授权能力实现，不建议直接删除浏览器模式的确认步骤。

## 项目状态

- 历史资料记录：抖音和快手版本曾在 2026 年 6—7 月完成本机测试；
- 当前公开版：代码、配置、打包和离线测试已校验；
- GitHub CI 覆盖 Python 3.11、3.12、3.13；
- 平台页面可能随时改版，历史选择器不代表当前页面永久兼容；
- 其他平台不在本仓库范围内，也没有宣称经过测试。

## 工作流程

```text
读取配置和本地语料
        ↓
打开浏览器并由使用者登录
        ↓
手动导航或关键词搜索视频
        ↓
生成本条随机计划
        ↓
执行等待和非发布型浏览动作
        ↓
展示候选评论 → 跳过 / 编辑 / 确认
        ↓
dry-run：只打印结果
实时模式：填入内容 → 再次输入 SEND → 发送
        ↓
达到连续处理阈值后休息并切换节奏
```

## 安装

需要 Python 3.11—3.13，以及 Chromium。

### macOS / Linux

```bash
git clone https://github.com/laosiji8013/douyin-kuaishou-comment-assistant.git
cd douyin-kuaishou-comment-assistant
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m playwright install chromium
```

### Windows PowerShell

```powershell
git clone https://github.com/laosiji8013/douyin-kuaishou-comment-assistant.git
cd douyin-kuaishou-comment-assistant
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
```

## 五分钟上手

### 1. 先运行安全演练

快手：

```bash
comment-assistant kuaishou --navigation manual --max-videos 3 --seed 42
```

抖音：

```bash
comment-assistant douyin --navigation manual --max-videos 3 --seed 42
```

程序会打开浏览器，等待你登录和手动打开第一条视频，然后打印每条随机计划并展示评论候选。默认不会向平台输入或发送。

### 2. 尝试关键词导航

```bash
comment-assistant kuaishou \
  --navigation search \
  --keyword "公开教程" \
  --max-videos 3
```

网页改版导致搜索或下一条失效时，使用 `--navigation manual`。随机计划和审核流程不受影响。

### 3. 启用实时交互

```bash
comment-assistant kuaishou --navigation manual --interactive-live
```

实时模式包含三道明确的人为动作：

1. 启动时输入 `INTERACTIVE LIVE`；
2. 对每条候选选择发送、编辑或跳过；
3. 内容填入输入框后输入 `SEND`，程序才点击发送。

没有 `--interactive-live` 时，即使在菜单中选择发送，也只会完成演练，不会操作平台输入框和按钮。

## 评论与关键词

仓库只提供中性、虚构示例：

- `data/comments.example.json`
- `data/keywords.example.json`

复制为本地文件后再修改：

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

`*.local.json` 已被 `.gitignore` 排除，适合存放自己的活动文案、客服回复或宣传内容。发布广告或营销内容前，应确认账号资质、素材授权、广告标识和平台政策，不要向无关内容重复投放相同文案。

## 随机时间

全部参数位于 `config/default.json`。建议复制为 `config/local.json` 后修改，不要直接覆盖默认文件。

### 观看档位

默认有三档：

| 档位 | 时间 | 权重 | 说明 |
| --- | ---: | ---: | --- |
| `skip` | 2—6 秒 | 0.25 | 短暂停留 |
| `normal` | 7—20 秒 | 0.55 | 常规观看 |
| `deep` | 18—50 秒 | 0.20 | 较长观看 |

权重是相对值，不要求总和为 1。例如 `1、2、1` 会被解释为 25%、50%、25%。实际等待时间还会乘以当前节奏倍率，并可能叠加 `deep_extra`。

### 节奏切换

```json
"pace_multipliers": {"normal": 1.0, "fast": 0.65, "slow": 1.4},
"pace_weights": {"normal": 0.55, "fast": 0.25, "slow": 0.20}
```

- `pace_multipliers` 决定所有相关等待的倍率；
- `pace_weights` 决定达到连续处理阈值后切换到各节奏的相对概率；
- 两组名称必须一致，否则程序会拒绝启动。

### 评论流程时间

- `read_comments_min/max_seconds`：打开评论区后的阅读时间；
- `think_before_type_min/max_seconds`：输入前停顿；
- `pre_send_pause_min/max_seconds`：填入后复查停顿；
- `burst_count_min/max`：连续处理多少条后进入间歇；
- `burst_rest_min/max_seconds`：间歇长度。

## 随机事件与浏览动作

事件分成“行为模式”“评论区动作”“独立概率事件”三层。

### 行为模式

`events.behavior_weights` 决定每条视频的主流程：

- `watch_and_prepare_comment`：观看后准备评论；
- `quick_skip`：短暂停留并跳过评论；
- `watch_and_offer_like`：只提出点赞候选；
- `deep_engage`：使用较长观看档并准备评论；
- `browse_author`：悬停作者区域后准备评论。

把某个权重设为 `0` 可以关闭该模式。不要删除程序预期的键。

### 评论区动作

`events.comment_browse_action_weights` 当前提供十种可见但不发布内容的动作：

- `scroll_down` / `scroll_up`：小幅滚动；
- `hover_item`：悬停一条可见评论；
- `wiggle`：在页面右侧小范围移动；
- `pause`：短暂停顿；
- `wander`：两段可视区移动；
- `drift`：三至六段缓慢移动；
- `read_line`：模拟横向阅读轨迹；
- `micro_scroll`：小幅下滚、停顿并部分回滚；
- `settle_cursor`：把鼠标停靠在内容区域一小段时间。

这些动作的用途是让演示过程更接近真实浏览流程，并测试页面元素是否可操作；不是反检测功能，也不提供账号安全保证。

### 独立概率事件

- `hover_comment_probability`：尝试悬停评论；
- `mouse_wander_probability`：在可视区移动鼠标；
- `page_scroll_probability`：小幅滚动页面；
- `typing_typo_probability`：输入字母数字时演示错字和退格；
- `cancel_draft_probability`：发送前随机提出取消草稿；
- `like_offer_probability`：提出点赞候选，但不自动点击。

概率范围是 `0` 到 `1`：`0` 表示关闭，`1` 表示每次触发。完整字段、计算顺序和修改例子见 [配置手册](docs/CONFIGURATION.md)。

## 如何扩展动作

如果要加入更多浏览动作，推荐把动作限定为滚动、悬停、停顿、打开或关闭可见区域等非发布型操作：

1. 在 `config/default.json` 的 `comment_browse_action_weights` 添加动作名和权重；
2. 在 `src/comment_assistant/session.py` 的 `perform_comment_browse_action()` 实现动作；
3. 给配置校验和随机计划补充测试；
4. 使用 `--seed` 验证相同配置能复现相同计划；
5. 先在 `dry-run` 和测试账号环境验证页面选择器。

不要把扩展动作设计为验证码处理、指纹伪装、隐藏自动化痕迹或绕过频率限制。需要真正的自动发布时，优先为 `PlatformAdapter` 增加平台官方开放接口实现，并保留内容审核、速率限制、幂等记录和停止开关。

## 自动发布与广告内容扩展

本仓库当前的浏览器实时模式是逐条确认，不是无人值守群发器。读者可以清楚看到当前确认发生在 `src/comment_assistant/session.py` 的 `review_comment()`，平台输入和发送按钮由 `PlatformAdapter` 提供。测试通过后若要改造自动发布，不应简单删掉 `SEND` 判断，而应把“内容决策”和“发布通道”拆开：

1. 保留 `SessionRandomizer` 负责计划，不让随机逻辑决定内容是否合法；
2. 抽出 `PublicationPolicy`，统一处理审核、去重、速率、活动范围和停止开关；
3. 抽出 `Publisher`，浏览器交互版与平台官方 API 版分别实现；
4. 在 `Publisher.publish()` 前生成幂等键，避免重试造成重复评论；
5. 只在测试账号、沙箱或平台允许的授权账号上通过端到端测试后启用；
6. 默认配置继续保持人工确认，自动模式必须由部署方显式开启并承担审计责任。

若业务确实需要自动发布，应使用平台允许的官方接口或企业工具，并至少实现：

- 只操作已授权账号；
- 明确的内容来源、审核人和活动范围；
- 平台级和账号级速率限制；
- 去重与幂等，避免同一广告或回复重复发送；
- 敏感词、链接、广告资质和目标内容相关性检查；
- 发送日志、失败重试上限和人工停止开关；
- 对删除、撤回、投诉和封禁事件的处理流程。

宣传文案可以存放在本地评论库中供审核和发布辅助，但不得把“随机时间”或“浏览动作”视为规避平台规则的方法。

完整的模块设计、接口骨架、测试用例和上线检查见 [自动发布扩展指南](docs/AUTOMATION_EXTENSION.md)。这份指南用于帮助维护者把当前完整的交互式流程扩展成可审计的授权发布系统，而不是让使用者靠关闭确认去批量投放无关内容。

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

示例：使用自己的配置和语料，固定随机序列演练五条：

```bash
comment-assistant douyin \
  --config config/local.json \
  --comments data/comments.local.json \
  --keywords data/keywords.local.json \
  --navigation manual \
  --max-videos 5 \
  --seed 2026
```

## 项目结构

```text
.
├── config/default.json              # 默认参数
├── data/                            # 中性示例语料
├── docs/                            # 配置、安全与发布文档
├── src/comment_assistant/
│   ├── cli.py                       # 命令入口
│   ├── config.py                    # 配置读取与校验
│   ├── randomizer.py                # 随机计划生成
│   ├── session.py                   # 会话与审核流程
│   └── platforms/                   # 抖音 / 快手适配器
└── tests/                           # 配置、随机计划和 CLI 测试
```

## 隐私与安全

- `browser_data/` 可能包含 Cookie、Local Storage 和账号状态，只能留在本机；
- 真实评论库、关键词、本地配置、截图、日志和构建产物不应提交；
- 公开示例已替换为中性、虚构内容；
- 项目没有代理池、验证码绕过、多账号控制或指纹规避；
- 开源许可证允许使用代码，不等于平台授权；
- 使用者必须查看并遵守平台当前的服务协议、开发者规则、社区规范和广告政策。

详见 [安全设计](docs/SAFETY.md)、[脱敏记录](docs/SANITIZATION.md) 和 [发布前检查](docs/PUBLISH_CHECKLIST.md)。

## 常见问题

### 找不到搜索框、评论框或下一条按钮

平台页面可能已经改版。先切换到 `--navigation manual`；如果评论选择器也失效，在对应的 `platforms/douyin.py` 或 `platforms/kuaishou.py` 中更新精确选择器。不要改成大范围模糊点击。

### 为什么相同配置的结果不同

默认随机种子每次不同。调试时增加 `--seed 42`；相同种子、配置和操作顺序会产生相同计划。

### 为什么改了权重却启动失败

概率必须在 `0` 到 `1` 之间，区间下限不能大于上限，权重总和不能为零，节奏权重和倍率的键名必须一致。程序会在启动时指出具体字段。

### 能否直接无人值守发送

当前公开实现不提供该模式。浏览器实时发布需要逐条确认。合规的自动发布应通过平台官方接口扩展，并实现审核、限速、去重、记录和停止机制。

## 开发与验证

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
python -m compileall -q src tests
```

提交前建议同时检查：

```bash
git status --short --ignored
git ls-files
```

## 许可证

本项目使用 [MIT License](LICENSE)，允许所有人使用、修改和再发布代码。许可证不提供平台兼容性、商业效果或账号安全保证。
