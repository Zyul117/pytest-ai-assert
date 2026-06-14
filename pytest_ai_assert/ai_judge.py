"""
AI 语义断言 —— 封装 LLM 调用，让 pytest 用例能用自然语言描述期望
通过 OpenAI 兼容接口调用大模型，返回 pass / fail / uncertain 判断结果
"""
import os
import json
from openai import OpenAI


class AIJudge:
    """AI 断言判断器"""

    SYSTEM_PROMPT = """你是一个 API 测试断言审查员。你的任务很简单：

给你一段"期望描述"和"API 实际响应"，判断响应是否符合期望。

## 判断规则
- 只基于给出的期望描述和响应数据来判断
- 如果期望描述里提到的要求都满足了，就是 pass
- 如果有任何一条要求没满足，就是 fail
- 如果信息不足、期望描述模糊、或者你拿不准，就说 uncertain

## 输出格式（严格 JSON）
{
  "verdict": "pass" 或 "fail" 或 "uncertain",
  "confidence": 0.0 到 1.0,
  "reason": "一句话说明判断依据"
}"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "sk-your-api-key-here")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def judge(self, response_data: dict, expectation: str) -> dict:
        """判断响应是否符合期望"""
        user_input = f"""=== 期望描述 ===
{expectation}

=== API 实际响应 ===
{json.dumps(response_data, ensure_ascii=False, indent=2)}"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_input},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content
            return self._parse(raw)
        except Exception as e:
            return {
                "verdict": "uncertain",
                "confidence": 0.0,
                "reason": f"LLM 调用失败: {e}",
            }

    def _parse(self, raw_text: str) -> dict:
        fallback = {"verdict": "uncertain", "confidence": 0.0, "reason": "无法解析 LLM 回复"}

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

        import re
        match = re.search(r"```json\s*([\s\S]*?)\s*```", raw_text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw_text[start:end + 1])
            except json.JSONDecodeError:
                pass

        return fallback
