from data_handler import *
from prompt_creator import *
from Llama3 import *
from datetime import datetime
from tqdm import tqdm
from response_processor import *

logger = logging.getLogger(__name__)
# To add the variables from .env file
#  export $(cat .env | xargs) && env


def generate_inference_data(
    data_handler: DataHandlerBase,
    prompt_creator: PromptCreator,
    model: Model,
    response_processor: ResponseProcessor,
    total: int = -1,
    calcualate_cost: bool = False,
):
    datapoints = data_handler.return_data_point(total)
    total_input_tokens = 0
    total_output_tokens = 0
    current_input_tokens = 0
    current_output_tokens = 0
    for data_point in tqdm(datapoints):
        current_index = data_point["ID"]
        logger.info(f"Current index: {current_index}")

        try:
            for iteration in range(2):
                logger.info("Iteration: " + str(iteration))
                if iteration == 0:
                    prompt = prompt_creator.create_prompt(
                        prompt=data_point["prompt"],
                    )
                else:
                    prompt = prompt_creator.refine_prompt(
                        prompt_list=prompt,
                        response=response,
                    )

                model_response = model.create_response(prompt)
                response = model_response["content"]
                (status, modified_response) = response_processor.process_response(
                    response
                )

                if calcualate_cost:
                    current_input_tokens = model_response["input_tokens"]
                    current_output_tokens = model_response["output_tokens"]
                if status == 1:
                    break
        except Exception as e:
            logger.error(f"Error in creating response for index {current_index}")
            logger.error(e)
            continue

        if status == 0:
            logger.error(f"INCORRECT RESPONSE FOR {current_index}: {modified_response}")
        data_handler.save_generated_data(modified_response, index=current_index)

        if calcualate_cost:
            total_input_tokens += current_input_tokens
            total_output_tokens += current_output_tokens
            cost = model.calculate_cost(current_input_tokens, current_output_tokens)
            cost_till_now = model.calculate_cost(
                total_input_tokens, total_output_tokens
            )
            logger.info(
                f"Cost for index {current_index}: {cost}, Total cost: {cost_till_now}"
            )

            current_input_tokens = 0
            current_output_tokens = 0


def sanitize_log_name(filename):
    return filename.replace(" ", "_").replace(":", "_").replace("-", "_")


def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    parser.add_argument("--total", type=int, default=-1)
    parser.add_argument("--calculate_cost", type=bool, default=False)
    parser.add_argument("--datahandler", type=str, default="template")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    logging.basicConfig(
        filename=sanitize_log_name(f"./logs/data_generation_{datetime.now()}.log"),
        level=logging.INFO,
    )

    with open("./hf_token.txt", "r") as f:
        token = f.read().strip()

    if args.datahandler == "template":
        data_handler = DataHandler(args.config)
        logger.info(f"Template Based Data Handler")
    elif args.datahandler == "ibe":
        data_handler = DataHandlerIBE(args.config)
        logger.info(f"IBE Based Data Handler")
    else:
        data_handler = DataHandlerEBE(args.config)
        logger.info(f"EBE Based Data Handler")

    template_version = data_handler.get_config_data("template_version")
    message_creator = ChatGptMessageCreator(version=template_version)

    response_processor_version = data_handler.get_config_data(
        "response_processor_version"
    )

    if response_processor_version == "base":
        response_processor = ResponseProcessor()
    elif response_processor_version == "ibe":
        response_processor = ResponseProcessorIBE()
    elif response_processor_version == "ebe":
        response_processor = ResponseProcessorEBE()
    else:
        raise ValueError("Invalid response_processor_version")

    logger.info(f"Model name: {data_handler.get_model_name()}")
    model = Llama3(model_name=data_handler.get_model_name(), device="cuda:0", token=token)
    model.activate_model()
    logger.info("Data generation started")
    generate_inference_data(
        data_handler=data_handler,
        prompt_creator=message_creator,
        model=model,
        response_processor=response_processor,
        total=args.total,
    )

    logger.info("Data generation finished")
