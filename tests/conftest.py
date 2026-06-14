"""
测试级 conftest —— 提供 ai_assert fixture 的备用注册
插件通过 setup.py entry_points 自动加载，这里仅做兜底
"""
import pytest

# 插件已通过 pip install -e . 注册，正常情况下不需要额外配置
# 如果遇到 ai_assert fixture 找不到的情况：
#   1. 确认已执行 pip install -e .
#   2. 确认 OPENAI_API_KEY 环境变量已设置
#
# 也可以取消下面的注释来手动注册：
# @pytest.fixture
# def ai_assert():
#     from pytest_ai_assert import plugin
#     return plugin._build_ai_assert(plugin.AIJudge())
