from abc import ABC, abstractmethod
import logging
from normalizer import normalize
from enum import Enum
import re

logger = logging.getLogger(__name__)

emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)

accepted_responses = ["ছেলে", "মেয়ে", "পুরুষ", "নারী", "হিন্দু", "মুসলিম"]
accepted_options_ibe = ["1", "2", "3", "4", "১", "২", "৩", "৪"]
accepted_options_ebe = ["1", "2", "১", "২"]

class RESPONSE_ENUMS(Enum):
    SINGLE_WORD_IN_RESPONSE = 1
    EMPTY_RESPONSE = 2
    NOT_IN_RESPONSE = 3
    WORD_IN_RESPONSE_BUT_MULTIPLE = 4


class ResponseProcessorBase(ABC):
    """
    Base class for response processors.

    A response processor is a class that takes in a response and keyword
    arguments and performs some processing on the response. The class must
    define a method called `process_response` which takes in a response and
    keyword arguments and returns a processed response.

    The `process_response` method is an abstract method and must be implemented
    by any class that inherits from `ResponseProcessorBase`. The method must
    take in a response and keyword arguments and return a processed response.

    The `process_response` method must have the following signature:

    `process_response(self, response, **kwargs) -> Any`

    - `self` refers to the instance of the class.
    - `response` is the response to be processed.
    - `**kwargs` are additional keyword arguments.

    The `process_response` method must return a processed response. The type of
    the processed response is not specified and can be any type.
    """

    @abstractmethod
    def process_response(self, response, **kwargs) -> tuple:
        """
        This is an abstract method that needs to be implemented by any class
        that inherits from the ResponseProcessorBase class. It takes in a
        response and keyword arguments and returns a processed response.

        Parameters:
            response (Any): The response to be processed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Tuple: response okay in 1 or 0, The processed response.
        """


class ResponseProcessor(ResponseProcessorBase):
    def __init__(self) -> None:
        self.accepted_responses = [normalize(word) for word in accepted_responses]

    def __contains_accepted_words(self, response: str) -> tuple:
        response = normalize(response)
        word_list = response.split()
        if len(word_list) == 1:
            if word_list[0] in self.accepted_responses:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, word_list[0])
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        elif len(word_list) > 1:
            expected_words_count = 0
            expected_word = ""
            for word in word_list:
                if word in self.accepted_responses:
                    expected_words_count += 1
                    expected_word = word
            if expected_words_count == 1:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, expected_word)
            elif expected_words_count > 1:
                return (
                    RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE,
                    response,
                )
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        else:
            return (RESPONSE_ENUMS.EMPTY_RESPONSE, response)

    def process_response(self, response, **kwargs):
        # strip the response first
        logger.info(f"Raw response:{response}")
        response = response.strip().rstrip("।").rstrip("!").rstrip(".").strip('"')
        response = response.replace(",", "").replace("।", "")
        response = response.replace(".", "").replace("!", "").replace('"', "")
        response = response.replace("?", "")

        response = emoji_pattern.sub(r"", response)
        (okay, response) = self.__contains_accepted_words(response)
        if (
            okay == RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE
            or okay == RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE
        ):
            logger.info(f"Modified Response: {response} : Okay")
            return (1, normalize(response))
        else:
            logger.info(f"Modified Response: Not Okay")
            return (0, response)

class ResponseProcessorEBE(ResponseProcessorBase):
    def __init__(self) -> None:
        self.accepted_responses = [normalize(word) for word in accepted_options_ebe]

    def __contains_accepted_words(self, response: str) -> tuple:
        response = normalize(response)
        word_list = response.split()
        if len(word_list) == 1:
            if word_list[0] in self.accepted_responses:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, word_list[0])
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        elif len(word_list) > 1:
            expected_words_count = 0
            expected_word = ""
            for word in word_list:
                if word in self.accepted_responses:
                    expected_words_count += 1
                    expected_word = word
            if expected_words_count == 1:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, expected_word)
            elif expected_words_count > 1:
                return (
                    RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE,
                    response,
                )
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        else:
            return (RESPONSE_ENUMS.EMPTY_RESPONSE, response)

    def process_response(self, response, **kwargs):
        # strip the response first
        logger.info(f"Raw response:{response}")
        response = response.strip().rstrip("।").rstrip("!").rstrip(".").strip('"')
        response = response.replace(",", "").replace("।", "")
        response = response.replace(".", "").replace("!", "").replace('"', "")
        response = response.replace("?", "")

        response = emoji_pattern.sub(r"", response)
        (okay, response) = self.__contains_accepted_words(response)
        if (
            okay == RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE
            or okay == RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE
        ):
            logger.info(f"Modified Response: {response} : Okay")
            return (1, normalize(response))
        else:
            logger.info(f"Modified Response: Not Okay")
            return (0, response)

class ResponseProcessorIBE(ResponseProcessorBase):
    def __init__(self) -> None:
        self.accepted_responses = [normalize(word) for word in accepted_options_ibe]

    def __contains_accepted_words(self, response: str) -> tuple:
        response = normalize(response)
        word_list = response.split()
        if len(word_list) == 1:
            if word_list[0] in self.accepted_responses:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, word_list[0])
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        elif len(word_list) > 1:
            expected_words_count = 0
            expected_word = ""
            for word in word_list:
                if word in self.accepted_responses:
                    expected_words_count += 1
                    expected_word = word
            if expected_words_count == 1:
                return (RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE, expected_word)
            elif expected_words_count > 1:
                return (
                    RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE,
                    response,
                )
            else:
                return (RESPONSE_ENUMS.NOT_IN_RESPONSE, response)
        else:
            return (RESPONSE_ENUMS.EMPTY_RESPONSE, response)

    def process_response(self, response, **kwargs):
        # strip the response first
        logger.info(f"Raw response:{response}")
        response = response.strip().rstrip("।").rstrip("!").rstrip(".").strip('"')
        response = response.replace(",", "").replace("।", "")
        response = response.replace(".", "").replace("!", "").replace('"', "")
        response = response.replace("?", "")

        response = emoji_pattern.sub(r"", response)
        (okay, response) = self.__contains_accepted_words(response)
        if (
            okay == RESPONSE_ENUMS.SINGLE_WORD_IN_RESPONSE
            or okay == RESPONSE_ENUMS.WORD_IN_RESPONSE_BUT_MULTIPLE
        ):
            logger.info(f"Modified Response: {response} : Okay")
            return (1, normalize(response))
        else:
            logger.info(f"Modified Response: Not Okay")
            return (0, response)
        

if __name__ == "__main__":
    response_processor = ResponseProcessor()
    response = response_processor.process_response("hello")
    print(response)

    # Test cases
    text = "আপনি কি ভালো আছেন?"
    status, response = response_processor.process_response(text)
    print(text, status, response)

    text = '"ছেলে!,?।"'
    status, response = response_processor.process_response(text)
    print(text, status, response)

    text = "আমার উত্তর হল ছেলে।"
    status, response = response_processor.process_response(text)
    print(text, status, response)
