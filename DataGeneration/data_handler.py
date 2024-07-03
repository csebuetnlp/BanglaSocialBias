from abc import ABC, abstractmethod
import yaml
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)


def sanitize_model_name(model_name: str):
    model_name = model_name.split("/")[0]
    model_name = model_name.replace(".", "_").replace("-", "_")
    return model_name


class DataHandlerBase(ABC):
    @abstractmethod
    def get_model_name(self):
        pass

    @abstractmethod
    def return_data_point(self, total=-1):
        pass

    @abstractmethod
    def get_config_data(self, key):
        pass

    @abstractmethod
    def save_generated_data(self, content, index, filepath=None):
        pass


class DataHandler(DataHandlerBase):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.__read_config_file()

    def __read_config_file(self):
        with open(self.config_file_path, "r") as f:
            self.config = yaml.safe_load(f)

    def __read_prompts(self):
        prompt_df = pd.read_csv(self.config["prompt_data_path"])
        print(f"\nSelected data points length: {len(prompt_df)}")
        return prompt_df

    def __is_datapoint_eligible(self, index):
        # skip if the response already exists
        model_name = sanitize_model_name(self.config["model"])

        response_file_path = os.path.join(
            self.config["storage_folder_path"],
            str(index),
            f"{model_name}_response.txt",
        )
        if os.path.exists(response_file_path):
            logger.info(f"Response already exist for index: {index}")
            return False

        return True

    def __create_valid_data_points(self):
        prompt_df = self.__read_prompts()
        prompt_df_valid_mask = prompt_df["ID"].apply(
            lambda x: self.__is_datapoint_eligible(x)
        )
        prompt_df_valid = prompt_df[prompt_df_valid_mask]
        return prompt_df_valid.to_dict(orient="records")

    def get_model_name(self):
        return self.config["model"]

    def get_config_data(self, key):
        return self.config[key]

    def return_data_point(self, total=-1):
        valid_data_points = self.__create_valid_data_points()

        for i, data_point in enumerate(valid_data_points):
            yield data_point
            if i == total - 1:
                break

    def save_generated_data(self, content, index, filepath=None):
        """
        Save generated data to a file.

        Args:
            content (str): The content to be saved.
            persona (str): The persona associated with the content.
            index (int): The index of the data point.
            filepath (str, optional): The file path to save the content. If not provided,
                the file will be saved in the default location. Defaults to None.
        """
        # If filepath is not provided, generate a default filepath
        if filepath is None:
            # Generate the filename based on the persona, model name and index
            filename = f"{sanitize_model_name(self.config['model'])}_response.txt"
            # Generate the folder path based on the index
            folder_path = os.path.join(self.config["storage_folder_path"], str(index))
            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # Generate the filepath by joining the folder path and filename
            filepath = os.path.join(folder_path, filename)
        else:
            # If filepath is provided, join it with the base storage folder path
            filepath = os.path.join(self.config["storage_folder_path"], filepath)

        try:
            # Write the content to the file
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
                logger.info(f"Content saved to file: {filepath}\n")
        except Exception as e:
            # Log any errors that occur during the writing operation
            logger.error(f"Error occurred while writing to file: {e}\n")
            pass  # Skip the operation if an error occurs


class DataHandlerEBE(DataHandlerBase):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.__read_config_file()

    def __read_config_file(self):
        with open(self.config_file_path, "r") as f:
            self.config = yaml.safe_load(f)

    def __read_prompts_df(self):
        if os.path.exists(self.config["storage_path"]):
            prompt_df = pd.read_csv(self.config["storage_path"])
        else:
            os.makedirs(os.path.dirname(self.config["storage_path"]), exist_ok=True)
            prompt_df = pd.read_csv(self.config["prompt_data_path"])
        print(f"\nSelected data points length: {len(prompt_df)}")
        return prompt_df

    def __create_valid_data_points(self):
        prompt_df = self.__read_prompts_df()
        prompt_df_valid = prompt_df[prompt_df["response"].isna()]
        print("Valid Data Points: ", len(prompt_df_valid))
        logger.info(f"Starting from index: {prompt_df_valid['ID'].iloc[0]}\n\n")
        return prompt_df_valid.to_dict(orient="records")

    def get_model_name(self):
        return self.config["model"]

    def get_config_data(self, key):
        return self.config[key]

    def return_data_point(self, total=-1):
        valid_data_points = self.__create_valid_data_points()

        for i, data_point in enumerate(valid_data_points):
            yield data_point
            if i == total - 1:
                break

    def save_generated_data(self, content, index):
        """
        Save generated data to the 'response' field in the CSV file.

        Args:
            content (str): The content to be saved.
            index (int): The index of the data point.
        """
        # Read the current CSV file
        if os.path.exists(self.config["storage_path"]):
            prompt_df = pd.read_csv(self.config["storage_path"])
        else:
            prompt_df = pd.read_csv(self.config["prompt_data_path"])

        # Ensure the index is within the DataFrame bounds
        if index < 0 or index >= len(prompt_df):
            logger.error(
                f"Index {index} is out of bounds for the DataFrame with length {len(prompt_df)}"
            )
            return

        # Update the 'response' field for the specific index
        try:
            prompt_df.at[index, "response"] = str(content)

            # Save the updated DataFrame back to the CSV file
            prompt_df.to_csv(self.config["storage_path"], index=False)
            logger.info(f"Content saved to 'response' field in CSV at index {index}\n")
        except Exception as e:
            # Log any errors that occur during the updating operation
            logger.error(f"Error occurred while updating the CSV file: {e}\n")
            pass  # Skip the operation if an error occurs


class DataHandlerIBE(DataHandlerBase):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.__read_config_file()

    def __read_config_file(self):
        with open(self.config_file_path, "r") as f:
            self.config = yaml.safe_load(f)

    def __read_prompts_df(self):
        if os.path.exists(self.config["storage_path"]):
            prompt_df = pd.read_csv(self.config["storage_path"])
        else:
            os.makedirs(os.path.dirname(self.config["storage_path"]), exist_ok=True)
            prompt_df = pd.read_csv(self.config["prompt_data_path"])
        print(f"\nSelected data points length: {len(prompt_df)}")
        return prompt_df

    def __create_valid_data_points(self):
        prompt_df = self.__read_prompts_df()

        prompt_df_valid = prompt_df[prompt_df["response"].isna()]
        print("Valid Data Points: ", len(prompt_df_valid))
        logger.info(f"Starting from index: {prompt_df_valid['ID'].iloc[0]}\n\n")
        return prompt_df_valid.to_dict(orient="records")

    def get_model_name(self):
        return self.config["model"]

    def get_config_data(self, key):
        return self.config[key]

    def return_data_point(self, total=-1):
        valid_data_points = self.__create_valid_data_points()

        for i, data_point in enumerate(valid_data_points):
            yield data_point
            if i == total - 1:
                break

    def save_generated_data(self, content, index):
        """
        Save generated data to the 'response' field in the CSV file.

        Args:
            content (str): The content to be saved.
            index (int): The index of the data point.
        """
        # Read the current CSV file
        if os.path.exists(self.config["storage_path"]):
            prompt_df = pd.read_csv(self.config["storage_path"])
        else:
            prompt_df = pd.read_csv(self.config["prompt_data_path"])

        # Ensure the index is within the DataFrame bounds
        if index < 0 or index >= len(prompt_df):
            logger.error(
                f"Index {index} is out of bounds for the DataFrame with length {len(prompt_df)}"
            )
            return

        # Update the 'response' field for the specific index
        try:
            prompt_df.at[index, "response"] = str(content)

            # Save the updated DataFrame back to the CSV file
            prompt_df.to_csv(self.config["storage_path"], index=False)
            logger.info(f"Content saved to 'response' field in CSV at index {index}\n")
        except Exception as e:
            # Log any errors that occur during the updating operation
            logger.error(f"Error occurred while updating the CSV file: {e}\n")
            pass  # Skip the operation if an error occurs


if __name__ == "__main__":
    data_handler = DataHandlerEBE("config_ebe.yaml")

    print(data_handler.get_model_name())
    datapoints = data_handler.return_data_point(1)
    for data in datapoints:
        print(data)

        data_handler.save_generated_data("abcd", data["ID"])
