"""
AgentCodex – Interface avec GPT, Gemini ou autre backend
"""
import openai

def call_codex(prompt: str, model: str = "gpt-4", temperature: float = 0.4) -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message["content"].strip()
