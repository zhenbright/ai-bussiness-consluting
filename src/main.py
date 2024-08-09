import os
import sys
from uvicorn import run
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# Get the current script's directory
current_script_directory = os.path.dirname(os.path.abspath(__file__))
# Get the project root path
project_root = os.path.abspath(os.path.join(current_script_directory, os.pardir))

# Append the project root and current script directory to the system path
sys.path.append(project_root)
sys.path.append(current_script_directory)

# Import the API endpoints from the endpoints module
from src.api.endpoints import (
    docs, 
)

# Import the CustomLogger class from the logging configuration module
from src.utils.logging_config import CustomLogger

# Create a FastAPI application
app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})

# Configure CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router for endpoint
app.include_router(docs.router)

# Run the FastAPI application using Uvicorn server
if __name__ == "__main__":
    # Load environment variables from the .env file
    load_dotenv()

    # Initialize the logger
    logger = CustomLogger()
    logger.log_example_messages()

    run(
        "src.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
