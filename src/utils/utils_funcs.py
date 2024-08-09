import os
from src.utils.logging_config import CustomLogger

logger = CustomLogger().get_logger

def delete_file(file_path):
    # Check if the file exists before attempting to remove it
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file at {file_path} has been removed.")
    else:
        print(f"The file at {file_path} does not exist.")
