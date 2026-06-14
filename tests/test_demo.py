"""
演示 AI 语义断言的用法
运行方式：pytest tests/ -v
"""
import pytest
import requests


# ============================================================
# 基础用法：直接判断一个字典是否符合预期
# ============================================================

def test_balance_not_negative(ai_assert):
    """余额不该为负数 —— 这是个 fail 案例"""
    response = {"user_id": 1, "balance": -500, "currency": "CNY"}

    result = ai_assert(response, "余额 balance 不应该为负数")

    print(f"\n  AI 判断: {result.verdict}")
    print(f"  置信度: {result.confidence}")
    print(f"  理由: {result.reason}")

    # 断言：AI 应该发现余额为负是不正常的
    assert result.verdict == "fail", f"期望 fail，但 AI 判定为 {result.verdict}"


def test_normal_user_data(ai_assert):
    """正常用户数据 —— 应该是 pass"""
    response = {
        "user_id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25,
    }

    result = ai_assert(response, "用户的 name、email、age 字段都存在且值合理")

    print(f"\n  AI 判断: {result.verdict}")
    print(f"  置信度: {result.confidence}")
    print(f"  理由: {result.reason}")

    assert result.verdict == "pass", f"AI 判定为 {result.verdict}: {result.reason}"


def test_missing_required_field(ai_assert):
    """缺少必填字段 —— 应该是 fail"""
    response = {"user_id": 2, "name": "李四"}  # 缺了 email

    result = ai_assert(response, "响应应该包含 user_id、name、email 三个必填字段")

    print(f"\n  AI 判断: {result.verdict}")
    print(f"  理由: {result.reason}")

    assert result.verdict == "fail", f"期望 fail，但 AI 判定为 {result.verdict}"


def test_uncertain_scenario(ai_assert):
    """故意给一个模糊的期望 —— AI 应该说不确定"""
    response = {"status": "active", "code": 42}

    result = ai_assert(response, "这个响应应该符合某个我不知道的规范")

    print(f"\n  AI 判断: {result.verdict}")
    print(f"  置信度: {result.confidence}")
    print(f"  理由: {result.reason}")

    # 不确定不算失败，只是一个提示
    assert result.verdict in ("pass", "fail", "uncertain"), f"非法 verdict: {result.verdict}"


# ============================================================
# 参数化：同一个接口，不同场景
# ============================================================

@pytest.mark.parametrize("payload,expectation", [
    pytest.param(
        {"username": "admin", "password": "123456"},
        "用户名和密码格式都合法，应该返回 200",
        id="合法登录",
    ),
    pytest.param(
        {"username": "", "password": ""},
        "用户名和密码都为空，应该返回错误信息而不是 200",
        id="空用户名密码",
    ),
    pytest.param(
        {"username": "a" * 1000, "password": "123"},
        "用户名长度异常（1000个字符），应该返回参数校验失败的提示",
        id="超长用户名",
    ),
])
def test_login_scenarios(ai_assert, payload, expectation):
    """参数化测试：同一个接口，不同参数组合"""
    # 注意：这里用的是模拟数据，实际场景替换为真实 API
    response = {"code": 400, "message": "用户名不能为空"}

    result = ai_assert(response, expectation)

    print(f"\n  [{expectation}]")
    print(f"  AI 判断: {result.verdict} (置信度: {result.confidence:.0%})")
    print(f"  理由: {result.reason}")
