# 随机时间与随机事件配置手册

所有可调参数都在 `config/default.json`。修改 JSON 后，程序启动时会校验：概率必须在 `0` 到 `1` 之间、最小值不能大于最大值、权重不能全部为零、跳过数量不能超过窗口大小。配置错误会直接退出并指出字段。

## 1. 随机数如何工作

程序为每条视频生成一个 `RandomPlan`，顺序是：

1. 选择当前节奏 `pace`；
2. 按权重抽取观看档位；
3. 在该档位的最小、最大秒数间均匀取值；
4. 如果是 `deep`，再判断是否追加超长观看；
5. 按权重抽取行为模式；
6. 按权重抽取一项评论区浏览动作；
7. 分别判断游走、悬停、滚动、取消和点赞候选事件；
8. 达到连续处理阈值后，随机休息并重新抽取节奏。

使用相同的 `--seed`、相同配置和相同操作顺序，可以得到相同的随机计划，便于排查问题：

```bash
comment-assistant kuaishou --max-videos 5 --seed 2026
```

正式使用时不传 `--seed`，每次会话会使用不同随机序列。

## 2. 观看时间 `watch_tiers`

默认配置：

| 档位 | 秒数范围 | 权重 | 含义 |
| --- | ---: | ---: | --- |
| `skip` | 2—6 秒 | 0.25 | 短暂停留 |
| `normal` | 7—20 秒 | 0.55 | 常规观看 |
| `deep` | 18—50 秒 | 0.20 | 较长观看 |

权重是相对值，不强制相加等于 1。默认合计为 1，因此可直接理解为 25%、55%、20%。如果改为 `1、2、1`，程序会自动按 25%、50%、25% 抽取。

单条实际等待时间：

```text
档位内随机秒数 × 当前 pace_multiplier + 可能的 deep_extra
```

如果只想固定观看时间，可把最小和最大设成相同值：

```json
{"name":"normal","min_seconds":10,"max_seconds":10,"weight":1}
```

## 3. 超长观看

| 参数 | 默认值 | 作用 |
| --- | ---: | --- |
| `deep_extra_probability` | `0.05` | 只有抽中 `deep` 时，追加额外时间的概率 |
| `deep_extra_min_seconds` | `60` | 追加时间下限 |
| `deep_extra_max_seconds` | `120` | 追加时间上限 |

关闭：把概率设为 `0`。始终追加：设为 `1`。

注意：它是“先命中 deep，再有 5% 概率追加”，不是所有视频都有 5%。按默认权重，整体触发率约为 `20% × 5% = 1%`。

## 4. 评论相关时间

| 参数 | 默认值 | 作用 |
| --- | ---: | --- |
| `read_comments_min_seconds` | 2.0 | 打开评论区后的阅读下限 |
| `read_comments_max_seconds` | 6.0 | 阅读上限 |
| `think_before_type_min_seconds` | 1.0 | 输入前停顿下限 |
| `think_before_type_max_seconds` | 3.5 | 输入前停顿上限 |
| `pre_send_pause_min_seconds` | 0.5 | 填写完成后的复查下限 |
| `pre_send_pause_max_seconds` | 2.5 | 复查上限 |

这些时间只在实时模式且本条进入评论流程时使用。最终发送仍必须输入 `SEND`。

## 5. 行为模式权重

`events.behavior_weights` 默认值：

| 模式 | 权重 | 程序行为 |
| --- | ---: | --- |
| `watch_and_prepare_comment` | 0.45 | 观看后展示评论候选 |
| `quick_skip` | 0.12 | 强制使用 `skip` 观看档，不进入评论候选 |
| `watch_and_offer_like` | 0.10 | 只提出点赞候选，仍需人工确认 |
| `deep_engage` | 0.18 | 强制使用 `deep` 观看档，再进入评论候选 |
| `browse_author` | 0.15 | 悬停作者入口但不进入主页，再进入评论候选 |

要关闭某个模式，把权重设为 `0`。不要删除键；删除后会改变代码预期。

示例：只保留“准备评论”和“跳过”，比例 4:1：

```json
"behavior_weights": {
  "watch_and_prepare_comment": 4,
  "quick_skip": 1,
  "watch_and_offer_like": 0,
  "deep_engage": 0,
  "browse_author": 0
}
```

## 6. 独立概率事件

| 参数 | 默认值 | 命中后的动作 |
| --- | ---: | --- |
| `hover_comment_probability` | 0.35 | 记录为悬停候选；当前版本不主动定位他人评论 |
| `mouse_wander_probability` | 0.30 | 在页面可视区域随机移动鼠标 |
| `page_scroll_probability` | 0.12 | 小幅滚动页面 |
| `typing_typo_probability` | 0.05 | 对每个字母数字字符判断是否先输入一个错字再删除 |
| `cancel_draft_probability` | 0.06 | 在已选择发送后，再提示是否按随机取消事件放弃 |
| `like_offer_probability` | 0.38 | 提出点赞候选；不自动点击 |

概率含义：`0` 为从不，`1` 为每次命中，`0.3` 为每次独立判断约 30%。

`typing_typo_probability` 是“每个可输入字符”的概率，而不是“每条评论”的概率。长文本会更容易至少触发一次。若不想出现模拟错字，设为 `0`。

## 7. 评论区浏览动作权重

`events.comment_browse_action_weights` 每条抽取一个可见动作：

| 动作 | 默认权重 | 实际行为 |
| --- | ---: | --- |
| `scroll_down` | 0.26 | 向下滚动 80—240 像素 |
| `scroll_up` | 0.08 | 向上滚动 80—240 像素 |
| `hover_item` | 0.16 | 打开评论区并悬停一条可见评论；找不到时跳过 |
| `wiggle` | 0.10 | 在页面右侧小范围移动三次 |
| `pause` | 0.10 | 停顿 0.5—1.5 秒 |
| `wander` | 0.12 | 在可视区随机移动两段 |
| `drift` | 0.10 | 在可视区随机移动 3—6 段 |
| `read_line` | 0.08 | 在页面右侧做一次横向移动 |
| `micro_scroll` | 0.08 | 小幅向下滚动，短暂停顿后部分回滚 |
| `settle_cursor` | 0.06 | 将鼠标移动到内容区域并短暂停靠 |

它们是相对权重，规则与行为模式相同，不要求总和为 1。动作不点击发送、点赞或关注。`hover_item` 依赖页面选择器，页面改版时可能无动作，但不会改用模糊点击。这些可见动作只用于浏览流程编排和页面适配测试，不是反检测功能。

## 8. 鼠标游走和退格

| 参数 | 默认值 | 作用 |
| --- | ---: | --- |
| `mouse_wander_steps` | 2 | 每次命中游走事件时移动几段 |
| `backspace_min_ms` | 40 | 删除错字后的等待下限 |
| `backspace_max_ms` | 100 | 删除错字后的等待上限 |

鼠标仅在可视区域 15%—85% 范围内移动，不点击。它用于展示页面动作差异，不是绕过平台识别的保证。

## 9. 连续处理、间歇和节奏

默认连续处理 2—5 条后，随机等待 5—18 秒，并重新抽取节奏。

| 参数 | 默认值 | 作用 |
| --- | ---: | --- |
| `burst_count_min` | 2 | 连续处理阈值下限 |
| `burst_count_max` | 5 | 连续处理阈值上限 |
| `burst_rest_min_seconds` | 5 | 间歇下限 |
| `burst_rest_max_seconds` | 18 | 间歇上限 |

节奏配置：

```json
"pace_multipliers": {"normal": 1.0, "fast": 0.65, "slow": 1.4},
"pace_weights": {"normal": 0.55, "fast": 0.25, "slow": 0.20}
```

- `pace_multipliers` 决定时间倍率：`0.65` 表示缩短到 65%，`1.4` 表示延长到 140%；
- `pace_weights` 决定切换节奏时各模式被选中的相对概率；
- 两组键名必须完全一致，否则配置校验失败。

## 10. 跳过窗口

默认参数：

```json
"skip_window_min": 3,
"skip_window_max": 5,
"skip_per_window_min": 0,
"skip_per_window_max": 0
```

程序先随机生成一个 3—5 条的窗口，再从中随机选择要强制跳过评论候选的位置。默认每个窗口跳过 0 条，所以此机制默认关闭。

示例：每 4—6 条中随机跳过 1—2 条：

```json
"skip_window_min": 4,
"skip_window_max": 6,
"skip_per_window_min": 1,
"skip_per_window_max": 2
```

如果随机行为模式本身已经是 `quick_skip`，不会重复产生额外效果。

## 11. 会话参数

| 参数 | 默认值 | 当前用途 |
| --- | ---: | --- |
| `default_max_videos` | 20 | 未传 `--max-videos` 时的单次上限 |
| `error_reset_threshold` | 3 | 为平台错误恢复保留的配置 |
| `work_start` / `work_end` | 09:20 / 02:00 | 记录历史工作区间，当前不自动限制启动 |
| `work_duration_min_minutes` / `max` | 45 / 60 | 为会话计时扩展保留，当前单次以条数上限为准 |
| `rest_min_seconds` / `max` | 60 / 180 | 为长会话休息扩展保留，当前使用 burst 间歇 |

“保留但当前未执行”的参数会明确标注，不把配置存在误写成已经生效。

## 12. 推荐修改方法

不要直接改仓库默认配置。复制为本地文件：

```bash
cp config/default.json config/local.json
```

然后运行：

```bash
comment-assistant douyin --config config/local.json --seed 42
```

`config/local.json` 已被 Git 忽略。这样既方便升级，也避免把本机习惯或敏感路径提交到公开仓库。
