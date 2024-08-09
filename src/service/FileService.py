from datetime import datetime
import os
from fastapi import File, UploadFile
import fitz  # PyMuPDF
import docx
import textract
class FileService:
    def extract_text_from_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    def extract_text_from_docx(self, file_path):
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text

    def extract_text_from_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text

    def extract_text_from_doc(self, file_path):
        text = textract.process(file_path).decode('utf-8')
        return text
    
    def extract_content_from_file(self, file, file_path):
         # Determine file type and extract text
        if file.filename.endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)
        elif file.filename.endswith(".docx"):
            text = self.extract_text_from_docx(file_path)
        elif file.filename.endswith(".txt"):
            text = self.extract_text_from_txt(file_path)
        elif file.filename.endswith(".doc"):
            text = self.extract_text_from_doc(file_path)
        return text
    
    async def uploadFiles(
        self,
        files: list[UploadFile] = File(...)
    ):
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d-%H-%M_%S")
        save_directory = f'./public/{formatted_date}/'
        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)

        file_paths = []
        file_contents = ""
        for file in files:
            contents = await file.read()
            # Save the file or process it as needed
            file_path = os.path.join(save_directory, file.filename)
            with open(file_path, 'wb') as f:
                f.write(contents)
            file_paths.append(file_path)
            file_contents += self.extract_content_from_file(file, file_path)
        
        return file_contents