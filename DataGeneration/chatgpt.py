from openai import OpenAI
from models import Model

pricing_option = {
    "gpt-3.5-turbo": (0.5 / 1e6, 1.5 / 1e6),
    "gpt-4o": (5 / 1e6, 15 / 1e6),
}


class ChatgptModel(Model):
    def __init__(self, model_name, key=None) -> None:
        super().__init__()
        self.model_name = model_name
        if key == None:
            self.client = OpenAI()
        else:
            self.client = OpenAI(api_key=key)

    def create_response(self, model_message) -> dict:
        completion = self.client.chat.completions.create(
            model=self.model_name, messages=model_message, temperature=0.1
        )

        response = {
            "content": completion.choices[0].message.content,
            "total_tokens": completion.usage.total_tokens,
            "input_tokens": completion.usage.prompt_tokens,
            "output_tokens": completion.usage.completion_tokens,
        }

        return response

    def calculate_cost(self, input_tokens, output_tokens):
        if self.model_name not in pricing_option:
            raise ValueError("Model not found in pricing options")
        input_cost, output_cost = pricing_option[self.model_name]
        return input_cost * input_tokens + output_cost * output_tokens
