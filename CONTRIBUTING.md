# Contributing

欢迎改进页面兼容性、配置校验、交互体验、文档和测试。

不会接受以下贡献：

- 无人值守批量评论、点赞、关注或私信；
- 代理池、多账号控制、验证码绕过、设备指纹或反检测；
- 真实 Cookie、账号资料、联系方式或内部评论语料；
- 删除默认 `dry-run`、实时模式启动确认或候选审核的改动。

提交前请运行：

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
```

Pull Request 需要说明“为什么修改”和“对使用者的影响”。
