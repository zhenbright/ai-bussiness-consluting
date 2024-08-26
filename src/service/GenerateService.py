from datetime import datetime
import json
import time
import os
import re
from dotenv import load_dotenv
from html2docx import html2docx
from openai import OpenAI
import pdfkit
from src.contstants.requirement import outline

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

class GenerateService:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)
        # self.assistant = {} 
        
    def generate_analysis_outline(self, pageAnalysis, information):
        
        prompt = """
                You are an AI language model tasked with generating an outline or table of contents for Analysis Chapter of a new document based on this company information.
                
                Highlight key insights, data, and trends.
                Discuss the methodology and approach used in the service.
                Provide detailed explanations and interpretations of the data.
               
                Ensure that the content is well-organized, coherent, and flows logically from one section to the next.
                Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.
                Each section should have a section number, section title, and pages and can have subsections which also involves pages.
                            The depth of this json object is 2, any subsection don't have its subsections.
                You are also an assistant that generates structured content. 
                I want you to create a book table of contents in JSON format.
                The sum of page should be _pageAnalysis pages
               
                The output structure must be a valid JSON object with a structure like this example format:
                {
                    "chapter" : "Analysis of Company",
                    "sections": [
                        {
                        "section_number": "1",
                        "section_title": "Background",
                        "pages": 1,
                        },
                        //Add more sections
                    ]    
                }
                JSON output with no extraneous text or wrappers.
            """
        prompt = prompt.replace('_pageAnalysis', str(pageAnalysis))
        
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            instructions=prompt
        )
        
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": f"Please generated outline according to below: {information}",
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text.value
        outline = self.extract_json_from_string(content=message_content)
        
        return outline
    
    def generate_result_outline(self, pageResult, requirement):
    
        prompt = """
            You are an AI language model tasked with generating an outline or table of contents for Result Chapter of a new document based on given requirement.
            
            Ensure that the content is well-organized, coherent, and flows logically from one section to the next.
            Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.
            Each section should have a section number, section title, and pages and can have subsections which also involves pages.
            The depth of this json object is 2, any subsection don't have its subsections.
            You are also an assistant that generates structured content. 
            I want you to create a book table of contents in JSON format.
            The sum of page should be _pageResult pages
            
            The output structure must be a valid JSON object with a structure like this example format:
            {
                "chapter" : "Result",
                "sections": [
                    {
                    "section_number": "1",
                    "section_title": "Background",
                    "pages": 1,
                    },
                    //Add more sections
                ]    
            }
            JSON output with no extraneous text or wrappers.
        """
        prompt = prompt.replace('_pageResult', str(pageResult))
        
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            instructions=prompt
        )
        
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": f"Please generated outline according to below requirement: {requirement}",
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text.value
        print('result')
        outline = self.extract_json_from_string(content=message_content)
        
        return outline

    def generate_case_use_outline(self, pageUseCase, requirement):
        
        prompt = """
            You are an AI language model tasked with generating an outline or table of contents for Case Use Chapter of a new document based on given requirement.
            
            Ensure that the content is well-organized, coherent, and flows logically from one section to the next.
            Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.
            Each section should have a section number, section title, and pages and can have subsections which  also involves pages and has same structure.
            The depth of this json object is 2, any subsection don't have its subsections.
            You are also an assistant that generates structured content. 
            I want you to create a book table of contents in JSON format.
            The sum of page should be _pageUseCase pages
            
            The output structure must be a valid JSON object with a structure like this example format:
            {
                "chapter" : "Case Uses",
                "sections": [
                    {
                    "section_number": "1",
                    "section_title": "Background",
                    "pages": 1,
                    },
                    //Add more sections
                ]    
            }
            
            JSON output with no extraneous text or wrappers.
        """
        prompt = prompt.replace('_pageUseCase', str(pageUseCase))
        
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            instructions=prompt
        )
        
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": f"Please generated outline according to below requirement: {requirement}",
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text.value
        print('----------------------use case')
        outline = self.extract_json_from_string(content=message_content)
        
        outline = {}
        return outline
    
    def extract_key_information(self, file_contents):
        self.assistant = self.client.beta.assistants.create(
            model="gpt-4o",
            name="Business Analysis Assistant",
            instructions="""
                        You are an AI language model specialized in extracting key information from text.
                        Your task is to identify and present the most relevant details from any given passage.
                        You should focus on facts, figures, dates, names, and other significant pieces of information, while ignoring filler content and irrelevant details.
                        Always provide concise and clear summaries of the extracted information.
                        """,
        )
        # Create new thread to extract main points from file contents
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content":  f"""Please read the following text and extract the main points and key information:{file_contents}""",
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=self.assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        key_information = messages[0].content[0].text.value
        
        return key_information
    
    def extract_json_from_string(self, content):
        match = re.search(r'```json(.*?)```', content, re.DOTALL)
        print(match)
        if match:
            json_string = match.group(1).strip()
            outline_object = json.loads(json_string)
        else:
            outline_object = json.loads(content)
        return outline_object
    
    def generate_content(self, outline, file, thread, chapter):
        for section in outline['sections']:
            print(section['section_number'])
            # file.write(f"<h2>Section {section['section_number']}. {section['section_title']}</h2>")
            try:
                if section.get('subsections'):
                    for subsection in section['subsections']:
                        print(subsection)
                        if subsection.get('section_number'):
                            section_number = subsection['section_number']
                            section_title = subsection['section_title']
                            section_pages = subsection['pages']
                        else:
                            section_number = subsection['subsection_number']
                            section_title = subsection['subsection_title']
                            section_pages = subsection['pages']
                        # file.write(f"<h3>Section {section_number}. {section_title}</h3>")
                        
                        message = self.client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role="user",
                            content=f"{section_title} of {chapter} in {section_pages * 500} words"
                        )
                        run = self.client.beta.threads.runs.create_and_poll(
                            thread_id=thread.id, assistant_id=self.assistant.id
                        )
                        messages = self.client.beta.threads.messages.list(
                            thread_id=thread.id
                        )
                        run_messages = [msg for msg in messages if msg.run_id == run.id]
                        
                        if run.status == 'completed':
                            for msg in run_messages:
                                if msg.role == 'assistant':  # Assuming the assistant's role is labeled as 'assistant'
                                    description = ''
                                    match = re.search(r'```html(.*?)```', msg.content[0].text.value, re.DOTALL)
                                    if match:
                                        description = match.group(1).strip()
                                    else:
                                        description = msg.content[0].text.value

                                    response = self.client.images.generate(
                                        model="dall-e-3",
                                        prompt=f"{section_title} of Analysis Company",
                                        size="1024x1024",
                                        quality="standard",
                                        n=1
                                    )
                                    image_url = response.data[0].url
                                    file.write(f"<h2>Section {section_number} {section_title}</h2>")
                                    # Add image
                                    file.write(f"<img src='{image_url}' alt='{section_title} image'>")
                                    # Add paragraph
                                    file.write(f"{description}")
                else:
                    if section.get('section_number'):
                        section_number = section['section_number']
                        section_title = section['section_title']
                        section_pages = section['pages']
                    else:
                        section_number = section['subsection_number']
                        section_title = section['subsection_title']
                        section_pages = section['pages']
                    # file.write(f"<h3>Section {section_number}. {section_title}</h3>")
                    
                    message = self.client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=f"{section_title} in {section_pages * 500} words"
                    )
                    run = self.client.beta.threads.runs.create_and_poll(
                        thread_id=thread.id, assistant_id=self.assistant.id
                    )
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    run_messages = [msg for msg in messages if msg.run_id == run.id]
                    
                    if run.status == 'completed':
                        for msg in run_messages:
                            if msg.role == 'assistant':  # Assuming the assistant's role is labeled as 'assistant'
                                description = ''
                                match = re.search(r'```html(.*?)```', msg.content[0].text.value, re.DOTALL)
                                if match:
                                    description = match.group(1).strip()
                                else:
                                    description = msg.content[0].text.value

                                response = self.client.images.generate(
                                    model="dall-e-3",
                                    prompt=f"{section_title} of Analysis Company",
                                    size="1024x1024",
                                    quality="standard",
                                    n=1
                                )
                                image_url = response.data[0].url
                                file.write(f"<h2>Section {section_number} {section_title}</h2>")
                                # Add image
                                file.write(f"<img src='{image_url}' alt='{section_title} image'>")
                                # Add paragraph
            except IOError as e:
                # Log the specific error
                print(f"IOError occurred: {e}")
                file.write('')
                
    def generate(
        self,
        service: str,
        promptText: str,
        pageAnalysis: str,
        pageResult: str,
        pageUseCase: str,
        file_contents: str,
        requirement: str
    ):  
        # Create Assistant
        key_information = self.extract_key_information(file_contents)
        # Extract Outlines from main points for PDF
        
        analysis_outline = self.generate_analysis_outline(pageAnalysis, information=file_contents)
        # print(analysis_outline)
        result_outline = self.generate_result_outline(pageResult, requirement=outline[service]['result'])
        # print(result_outline)
        case_outline = self.generate_case_use_outline(pageUseCase, requirement=outline[service]['use_case'])
        # print(case_outline)
        thread = self.client.beta.threads.create()
        
        system_prompt = f"""
                            You are an expert business analyst assistant tasked with generating comprehensive and tailored sections of a business analysis document.
                            Your objective is to produce detailed, non-repetitive content that aligns closely with the client’s goals and provides actionable insights.

                            Key Requirements:
                             **Content Structure and Depth**:
                                - Ensure that all content is tightly correlated with the main objectives of the consultancy.
                                - Each section should logically build upon the previous one, enhancing coherence and flow.
                                - Expand paragraphs by including detailed and specific content relevant to the client’s business environment, addressing their unique challenges.
                                
                            **In-Depth Research and Data Analysis**:
                                - Include industry-specific benchmarks, trends, and data to contextualize recommendations.
                                - Conduct comparative analysis to highlight the advantages of proposed AI strategies over traditional methods, with a focus on potential ROI.

                            **Enhanced Visual Aids**:
                                - Utilize info graphics, flowcharts, and diagrams to simplify complex concepts and enhance engagement.
                                - Incorporate advanced data visualizations or interactive elements to allow for deeper exploration of data.

                            Company information:
                            {key_information}
                            You should meet these requirement at least:
                            {requirement}
                            Instructions:
                            - The content should be delivered in HTML format, excluding body and head tags, for easy integration into existing HTML documents.
                            - Conclusions are only needed at the end of each chapter, not for every section.
                            - Ensure all content is unique, and specifically tailored to the client’s needs, avoiding any duplication.
                            - Please do not too detailed (Don't explain with too many subscriptions).
                            """
        
        with open("temp.html", 'w', encoding="utf-8") as file:
            html = """"
                    <html>\n<head>\n<title>Document</title>\n
                    <meta charset="utf-8" />\n
                    </head>\n<body>\n
                    """
            html += "<h1>Chapter 1. Analysis of Company</h1>\n"
            
            file.write(html)
            self.assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant.id,
                instructions=system_prompt
            )
            self.generate_content(analysis_outline, file, thread, 'analysis of company')
            # Result Company
            file.write("<h1>Chapter 2. Result\n")
            self.generate_content(result_outline, file, thread, 'result of analysis')
            # Case Use Company
            file.write("<h1>Chapter 2. Case Use\n")
            self.generate_content(result_outline, file, thread, 'case use of successful companies which have same goal and objective with given company')           
            
            file.write('</body>\n</html>')

        # create docx file from html
        with open("temp.html", encoding='utf-8') as fp:
            html = fp.read()

        # html2docx() returns an io.BytesIO() object. The HTML must be valid.
        buf = html2docx(html, title=f"{service}") 
        
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d-%H-%M_%S")
        save_directory = f'public/doc/'
        # Ensure the directory exists
        os.makedirs(save_directory, exist_ok=True)
        file_path =os.path.join(save_directory, f"{formatted_date}.docx") 
        print(file_path)
        with open(f"{file_path}", "wb") as fp:
            fp.write(buf.getvalue())
            
        # create pdf file from html
        html_file_path = "temp.html"
        output_pdf_path = f"public/pdf/{formatted_date}.pdf"
        with open(f"{output_pdf_path}", "wb") as fp:
            try:
                pdfkit.from_file(html_file_path, output_pdf_path,  options={'enable-local-file-access': '', 'quiet': ''})
            except IOError as e:
                # Log the specific error
                print(f"IOError occurred: {e}")
        
        print(f"PDF created: {output_pdf_path}")  
        return {"file_url": f"/{file_path}", "pdf_url": f"/{output_pdf_path}", "success": True}
        # return ''
    
    