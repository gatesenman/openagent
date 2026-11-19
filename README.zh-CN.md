# OpenAgent

[English](./README.md) | **简体中文**

AI 驱动的全生命周期开发平台命令行与桌面工具。

## 本轮更新

`openagent new-project <dir>` 会写出可验证的项目骨架：`openagent.project.json`、`requirements.txt` 占位文件，以及一个会通过的占位测试。不调用远程 API。

```bash
python3 cli/openagent_cli.py new-project ./demo-app
python -m unittest discover -s cli/tests
```
