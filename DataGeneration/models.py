from abc import ABC, abstractmethod
import requests


class Model(ABC):
    @abstractmethod
    def create_response(self, model_message):
        pass

    @abstractmethod
    def calculate_cost(self, input_tokens, output_tokens):
        pass
