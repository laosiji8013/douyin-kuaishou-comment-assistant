# GitHub 发布前检查

## 本地内容

- [ ] `data/comments.example.json` 只有虚构内容；
- [ ] `data/keywords.example.json` 不含内部业务信息；
- [ ] 没有 `browser_data/`、Cookie、Storage、截图或日志；
- [ ] 没有手机号、邮箱、真实账号名、主页引流和内部价格；
- [ ] `git ls-files` 中只有准备公开的文件；
- [ ] 敏感信息扫描无命中；
- [ ] `ruff check .`、`pytest`、`compileall` 全部通过。

## 仓库设置

- [ ] 仓库说明明确“逐条人工确认”；
- [ ] 先创建为 Private，上传后再做一次网页端检查；
- [ ] 开启 Secret scanning 与 Push protection；
- [ ] 开启 Private vulnerability reporting；
- [ ] 确认 `LICENSE` 选择符合你的开放意图；
- [ ] 检查 Actions 的首次 CI 结果。

## 转为公开前

- [ ] 浏览 GitHub 的 Code 页面，确认没有本机资料；
- [ ] 用 GitHub 搜索仓库内的 `cookie`、`token`、`手机号`、`主页`、`广告`；
- [ ] 下载仓库 ZIP，在一个新目录重新安装和运行 dry-run；
- [ ] 确认 README 没有“当前保证可用”“防封”“规避风控”等表述；
- [ ] 最后再把可见性从 Private 改为 Public。
