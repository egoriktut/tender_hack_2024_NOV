import openai
import json


class AIModel:
    def __init__(self):
        self.client = openai.OpenAI(
            base_url="http://0.0.0.0:8080",
            api_key="sk-no-key-required"
        )

    def make_a_prompt(self, prompt_msg: str):
        completion = self.client.chat.completions.create(
            model="llama",
            messages=[
                {"role": "system", "content": prompt_msg}
            ],
        )
        return completion.choices[0].message.content
