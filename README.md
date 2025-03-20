The goal is to transform the provided [Python script](https://www.aivi.fyi/llms/deploy-Mistral-Small-3.1) into a fully functional, interactive web application with enhanced features, proper markdown rendering, and clipboard functionality, while maintaining code quality through validation and testing.

![image](https://github.com/user-attachments/assets/c1c60c00-5790-41a4-9d8c-20bedc060714)

```bash
$ python3 chat_app-v3.py
* Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.

API Request:
{
  "url": "https://openrouter.ai/api/v1/chat/completions",
  "headers": {
    "Content-Type": "application/json"
  },
  "payload": {
    "model": "mistralai/mistral-small-3.1-24b-instruct:free",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI Assistant who thinks deeply using long chain of thoughts to carefully explore various options before choosing the best option to answer me. enclose your monologue for your chain of thoughts in tags <think> </think>, follow by your answer."
      },
      {
        "role": "user",
        "content": "How many \"r\"s are there in the word \"strawberry\"?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 8192
  }
}

API Response:
{
  "id": "gen-1742447817-Q04m3JUfnEVPvuWuKbKc",
  "provider": "Chutes",
  "model": "mistralai/mistral-small-3.1-24b-instruct",
  "object": "chat.completion",
  "created": 1742447817,
  "choices": [
    {
      "logprobs": null,
      "finish_reason": "stop",
      "native_finish_reason": "stop",
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<think>\nThe word \"strawberry\" has multiple syllables and contains the letter \"r\" in a few places. Let's break it down syllable by syllable:\n\n1. \"straw\" - no \"r\"\n2. \"ber\" - one \"r\"\n\nTo ensure accuracy, let's also count the total occurrences of \"r\" in the entire word:\n\n- s-t-r-a-w-b-e-r-r-y\n\nThere are two \"r\"s in the word \"strawberry.\"\n\n</think>\n\nThere are two \"r\"s in the word \"strawberry\".",
        "refusal": null
      }
    }
  ],
  "usage": {
    "prompt_tokens": 72,
    "completion_tokens": 121,
    "total_tokens": 193,
    "cost": 0,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```
