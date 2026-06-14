# 基于 pytest 的 AI 语义断言插件设计与实现

给 pytest 加一条 AI 断言，遇到不太好写断言规则的情况，直接用自然语言描述期望，让大模型来判断。

## 缘起

做接口测试的时候，有些场景靠 hardcode 的 assert 很难覆盖——比如"返回的用户信息应该合理""余额不能为负数，商品数量和金额应该匹配"。传统做法的解决方案就两种：要么写一长串 if/else 加一堆边界值判断，要么干脆不测。

于是想到让 LLM 来做这件事——把"期望"用自然语言写出来，AI 帮你判断响应符不符合。然后看了 pytest 的 hook 机制和插件文档，照着 fixture 规范把这个功能做成了 pytest 插件。

## 是怎么做的

整体思路比较简单：

1. 写了 `AIJudge` 类，封装了 OpenAI 的调用，每次都带上一段 System Prompt 告诉 LLM 怎么判断
2. 写了一个 pytest fixture（`ai_assert`），在测试函数里注入这个 fixture
3. 调用的时候传入"API 响应 JSON"和"自然语言写的期望描述"，AI 返回 pass / fail / uncertain
4. 通过 `setup.py` 的 `entry_points` 注册为 pytest 插件，`pip install -e .` 后就能直接用

判断逻辑分三个结果：
- **pass**：响应符合期望描述
- **fail**：不符合，存在疑似 Bug
- **uncertain**：信息不足或期望描述太模糊，不强行判断

## 安装

```bash
pip install -e .
```

## 怎么用

```python
def test_user_api(ai_assert):
    response = requests.get("http://api.example.com/user/1")

    # 常规断言
    assert response.status_code == 200

    # AI 语义断言
    result = ai_assert(response.json(), "余额不能为负数，用户名和邮箱必须存在")

    assert result.verdict == "pass"
```

## 局限

- 每条 ai_assert 都要调一次 LLM API，用例多了成本不低，不太适合大批量回归测试
- LLM 偶尔会判断错误，建议用在复杂场景的辅助判断上，简单的还是用 assert
- 目前只支持 OpenAI 兼容的 API（DeepSeek 等也可以用）
- 还不太成熟，比如没有做 LLM 调用的缓存，相同响应重复判断会重复花钱

## 跑一下

```bash
# 先设好 API Key（用 DeepSeek 便宜点）
export OPENAI_API_KEY="sk-你的key"
export OPENAI_BASE_URL="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"

# 跑演示用例
pytest tests/test_demo.py -v -s
```

## 文件说明

```
├── pytest_ai_assert/
│   ├── __init__.py      # 包说明
│   ├── ai_judge.py      # LLM 调用 + JSON 解析
│   └── plugin.py        # pytest 插件：fixture + hook
├── tests/
│   ├── conftest.py      # pytest 配置
│   └── test_demo.py     # 演示用例
├── setup.py             # 插件打包
└── requirements.txt
```

