from setuptools import setup, find_packages

setup(
    name="pytest-ai-assert",
    version="0.1.0",
    description="基于 pytest 的 AI 语义断言插件 — 用自然语言描述期望，让 LLM 帮忙判断 API 响应",
    packages=find_packages(),
    install_requires=["openai>=1.0.0", "pytest>=7.0.0"],
    entry_points={
        "pytest11": [
            "ai_assert = pytest_ai_assert.plugin",
        ],
    },
    python_requires=">=3.8",
)
