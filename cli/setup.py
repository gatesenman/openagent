"""OpenAgent CLI 安装配置."""

from setuptools import setup

setup(
    name="openagent-cli",
    version="0.1.0",
    description="OpenAgent CLI — AI 驱动的全生命周期开发平台命令行工具",
    author="gaosichun888",
    py_modules=["openagent_cli"],
    entry_points={
        "console_scripts": [
            "openagent=openagent_cli:main",
        ],
    },
    python_requires=">=3.10",
)
