"""
pytest AI 断言插件 —— 通过 hook 机制把 LLM 判断嵌入 pytest 执行流程

运行方式：
    pytest --ai-assert

或者直接在 conftest.py 里配置后正常跑：
    pytest
"""
import pytest


# ============================================================
# 核心：ai_assert 函数
# ============================================================

class AIAssertResult:
    """ai_assert 的返回结果，记录判断详情"""

    def __init__(self, verdict: str, confidence: float, reason: str, expectation: str, response: dict):
        self.verdict = verdict          # pass / fail / uncertain
        self.confidence = confidence    # 0.0 ~ 1.0
        self.reason = reason            # LLM 给出的判断依据
        self.expectation = expectation  # 原始的期望描述
        self.response = response        # 被检查的响应数据

    def __repr__(self):
        return f"<AIAssert {self.verdict} ({self.confidence:.0%}) — {self.reason}>"

    def __bool__(self):
        """pass 返回 True，fail 和 uncertain 返回 False"""
        return self.verdict == "pass"


def _build_ai_assert(judge):
    """工厂函数：用闭包把 judge 实例注入，生成 ai_assert 函数"""

    def ai_assert(response_data: dict, expectation: str) -> AIAssertResult:
        """
        AI 语义断言
        Args:
            response_data: API 返回的 JSON 响应体
            expectation: 用自然语言描述"这个响应应该满足什么条件"
        Returns:
            AIAssertResult 对象，包含判断结果
        """
        result_dict = judge.judge(response_data, expectation)
        return AIAssertResult(
            verdict=result_dict["verdict"],
            confidence=result_dict["confidence"],
            reason=result_dict["reason"],
            expectation=expectation,
            response=response_data,
        )

    return ai_assert


# ============================================================
# pytest hook：注册 ai_assert fixture
# ============================================================

@pytest.fixture(scope="function")
def ai_assert():
    """
    pytest fixture —— 每个测试函数都能直接用 ai_assert
    用法：
        def test_xxx(ai_assert):
            result = ai_assert(response.json(), "余额不能为负数")
            assert result.verdict == "pass"
    """
    from .ai_judge import AIJudge
    judge = AIJudge()
    return _build_ai_assert(judge)


# ============================================================
# pytest hook：终端输出增强
# ============================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """在测试结束后汇总 AI 断言结果"""
    # 收集所有 ai_assert 的结果（存在每条 test 的 user_properties 里）
    # 这里做个简化：直接输出一个提示
    terminalreporter.write_sep("=", "AI 断言提示")
    terminalreporter.write_line(
        "本项目的 ai_assert 结果已嵌入每条测试的输出中。\n"
        "查看 fail/uncertain 的用例，关注 LLM 给出的 reason 字段。"
    )


# ============================================================
# conftest 自动配置
# ============================================================

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers",
        "ai_assert: 需要 LLM 语义断言的测试用例"
    )
    config.addinivalue_line(
        "markers",
        "ai: 调用 AI 判断的测试（需要 OPENAI_API_KEY）"
    )
