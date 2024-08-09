import os
import logging
import colorlog

from dotenv import load_dotenv


class CustomLogger:
    _instance = None

    def __new__(cls):
        # This method ensures that only one instance of the class is created
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
            cls._instance.setup_logger()
        return cls._instance

    def setup_logger(self):
        # Load environment variables
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path)

        # Get log level from environment variable
        log_level_name = os.getenv('LOG_LEVEL', 'INFO')
        self.log_level = logging.getLevelName(log_level_name)

        # Configuration of logs with colorlog
        self.log_colors = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red',
        }

        # Log configuration
        formatter = colorlog.ColoredFormatter(
            '%(asctime)s [%(log_color)s%(levelname)-8s%(reset)s] %(filename)-8s:%(funcName)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors=self.log_colors
        )

        # Create console handler
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)

        # Create custom logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)  # EYE
        self.logger.addHandler(console_handler)

    def log_example_messages(self):
        self.logger.debug("Debug message")
        self.logger.info("Information message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")

    @property
    def get_logger(self):
        return self.logger
    