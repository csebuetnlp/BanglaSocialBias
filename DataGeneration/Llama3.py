from models import Model
import logging
import torch
import transformers
from transformers import (
    AutoTokenizer,
    LlamaForCausalLM,
    GenerationConfig,
    BitsAndBytesConfig,
)

logger = logging.getLogger(__name__)


class Llama3(Model):
    def __init__(self, model_name, device, token) -> None:
        super().__init__()
        self.model_name = model_name
        self.device = device
        self.token = token

    def activate_model(self):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, token=self.token
        )
        self.model = LlamaForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            quantization_config=bnb_config,
            device_map=self.device,
            token=self.token,
        )
        self.model.eval()

        logger.info(f"Model: {self.model_name} is activated.")

    def __evaluate(
        self,
        prompt,
        temperature=0.1,
        top_p=0.9,
        top_k=40,
        num_beams=4,
        max_new_tokens=32,
        **kwargs,
    ):
        input_ids = self.tokenizer.apply_chat_template(
            prompt, add_generation_prompt=True, return_tensors="pt"
        ).to(self.device)
        terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
        ]

        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_beams=num_beams,
            **kwargs,
        )

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids,
                do_sample=True,
                max_new_tokens=max_new_tokens,
                generation_config=generation_config,
                eos_token_id=terminators,
            )
            response = outputs[0][input_ids.shape[-1] :]

        return self.tokenizer.decode(response, skip_special_tokens=True)

    def create_response(self, model_message):
        content = self.__evaluate(prompt=model_message)

        response = {"content": content}

        return response

    def calculate_cost(self, input_tokens, output_tokens):
        return 0.0
