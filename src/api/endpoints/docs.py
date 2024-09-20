import os
from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from src.service.FileService import FileService
from src.utils.logging_config import CustomLogger
from starlette.responses import RedirectResponse
from src.service.GenerateService import GenerateService
from src.contstants.style import style
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
@router.post('/generate/graph_table')
async def generateGraphTable(
    files: list[UploadFile] = File(...),
):
    file_contents = await file_service.uploadFiles(files)
    response = generate_service.generateGraphTable(file_contents)
    with open("temp.html", 'w', encoding="utf-8") as file:
        html = """
                <html>\n<head>\n<title>Document</title>\n
                <meta charset="utf-8" />\n
                </head>\n<body>\n
                <script src="https://code.highcharts.com/highcharts.js"></script>
            """
        html += f"<style>{style}</style>"
        for graph in response["graphs"]:
            print('0000000')
            html += graph["content"]
        for table in response["tables"]:
            print('111111')
            html += table["content"]
        file.write(html)
        file.write('</body>\n</html>')
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