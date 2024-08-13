import os
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from src.service.FileService import FileService
from src.utils.logging_config import CustomLogger
from starlette.responses import RedirectResponse
from src.service.GenerateService import GenerateService
import time
# Get the logger instance from the CustomLogger class
logger = CustomLogger().get_logger

# Create a new APIRouter instance
router = APIRouter()

# Create a FastAPI application
app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True})

# Import Services
generate_service = GenerateService()
file_service = FileService()
# Define a Docmentation endpoint
@router.get("/")
async def root():
    return RedirectResponse(app.docs_url)

@router.post('/generate')
async def generate(
        service: str = Form(...),
        promptText: str = Form(...),
        pageAnalysis: str = Form(...),
        pageResult: str = Form(...),
        pageUseCase: str = Form(...),
        requirement: str = Form(...),
        files: list[UploadFile] = File(...),
    ):
    print('generate')
    print(requirement)
    # return {"file_url": f"/public/doc/2024-07-28-12-34_10.docx","pdf_url": f"/public/pdf/2024-08-01-02-49_47.pdf", "success": True}
    file_contents = await file_service.uploadFiles(files)
    
    response = generate_service.generate(
        service,
        promptText,
        pageAnalysis,
        pageResult,
        pageUseCase,
        file_contents,
        requirement
    )            
    return response
@router.get('/public/doc/{file_name}')
async def download_doc(file_name: str):
    file_path = os.path.join('public', 'doc', file_name)
    print(f"Checking file path: {file_path}")  # Debug print statement

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debug print statement
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=file_name)

@router.get('/public/pdf/{file_name}')
async def download_doc(file_name: str):
    file_path = os.path.join('public', 'pdf', file_name)
    print(f"Checking file path: {file_path}")  # Debug print statement

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debug print statement
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=file_name)