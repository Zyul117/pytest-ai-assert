"""
验证插件结构 —— 不需要 API Key，测试插件加载、fixture 注册等基础功能
拿到项目后先跑这个，确认环境没问题
"""
import pytest
import sys
import os


def test_plugin_is_registered():
    """验证插件已被 pytest 识别"""
    # 通过 pip install -e . 安装后，pytest 应自动发现 ai_assert 插件
    import pytest_ai_assert
    assert pytest_ai_assert.__version__ == "0.1.0"


def test_aijudge_import():
    """验证 AIJudge 可以导入"""
    from pytest_ai_assert.ai_judge import AIJudge
    judge = AIJudge()
    assert hasattr(judge, "judge")
    assert hasattr(judge, "SYSTEM_PROMPT")


def test_aijudge_parse_json():
    """验证 JSON 解析逻辑（不调 API）"""
    from pytest_ai_assert.ai_judge import AIJudge
    judge = AIJudge()

    # 测试直接 JSON 解析
    result = judge._parse('{"verdict": "pass", "confidence": 0.9, "reason": "正常"}')
    assert result["verdict"] == "pass"
    assert result["confidence"] == 0.9

    # 测试代码块提取
    result = judge._parse('这是分析... ```json\n{"verdict": "fail", "confidence": 0.8, "reason": "有问题"}\n``` 结束')
    assert result["verdict"] == "fail"
    assert result["confidence"] == 0.8

    # 测试花括号提取
    result = judge._parse('结论：{"verdict": "uncertain", "confidence": 0.5, "reason": "不确定"}，供参考')
    assert result["verdict"] == "uncertain"
    assert result["confidence"] == 0.5

    # 测试解析失败兜底
    result = judge._parse('完全无法解析的内容')
    assert result["verdict"] == "uncertain"
    assert result["confidence"] == 0.0


def test_ai_assert_result_object():
    """验证 AIAssertResult 对象的行为"""
    from pytest_ai_assert.plugin import AIAssertResult

    # pass 的结果
    r = AIAssertResult("pass", 0.95, "符合预期", "测试期望", {"id": 1})
    assert r.verdict == "pass"
    assert bool(r) is True
    assert "95%" in repr(r)

    # fail 的结果
    r = AIAssertResult("fail", 0.9, "余额为负数", "余额应大于0", {"balance": -500})
    assert r.verdict == "fail"
    assert bool(r) is False

    # uncertain 的结果
    r = AIAssertResult("uncertain", 0.5, "信息不足", "模糊期望", {})
    assert r.verdict == "uncertain"
    assert bool(r) is False


def test_system_prompt_is_valid():
    """验证 System Prompt 写的是合理的"""
    from pytest_ai_assert.ai_judge import AIJudge
    prompt = AIJudge.SYSTEM_PROMPT
    assert "API 测试断言审查员" in prompt
    assert "pass" in prompt
    assert "fail" in prompt
    assert "uncertain" in prompt
    assert "JSON" in prompt
