from datetime import datetime
import json
import time
import os
import re
from dotenv import load_dotenv
from html2docx import html2docx
from openai import OpenAI
import pdfkit

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')

class GenerateService:
    def __init__(self):
        self.client = OpenAI(api_key=api_key)
    
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
        assistant = self.client.beta.assistants.create(
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
                "content":  f"""Please read the following text and extract the main points and key information:{file_contents}
                            You should meet these requirement at leat.
                            {requirement}
                            """,
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        key_information = messages[0].content[0].text
        print(key_information)
        # Extract Outlines from mainpoints for PDF
        # This is System Prompt to extract
        outline_system_prompt = """
            You are an AI language model tasked with generating an outline or table of contents for a new document based on the provided specifications about ****.
            The document should be structured into three main sections: Analysis, Results, and Case Uses. The total length of the document should be 3 chaperters, 70 pages, divided as follows:

            Analysis: {xx} pages
            Results: {yy} pages
            Case Uses: {zz} pages
            Follow these steps:

            Analysis ({xx} pages):

                Thoroughly analyze the content of the uploaded files.
                Highlight key insights, data, and trends.
                Discuss the methodology and approach used in the service.
                Provide detailed explanations and interpretations of the data.
            Results ({yy} pages):

                Summarize the findings and outcomes from the analysis.
                Present quantitative and qualitative results.
                Include relevant charts, graphs, and tables for better understanding.
                Discuss the significance of the results and their implications.
            Case Uses ({zz} pages):

                Provide real-world examples and case studies where the service has been applied.
                Detail the benefits and impacts observed in each case.
                Discuss any challenges faced and how they were overcome.
                Include testimonials or quotes from users or stakeholders if available.
            Ensure that the content is well-organized, coherent, and flows logically from one section to the next. Use appropriate headings and subheadings to enhance readability. The final document should be informative, engaging, and professional.

            Outline/Table of Contents:

            Generate a detailed outline or table of contents for the document, including:

            Chapter 1: Analysis ({xx} pages):

                Introduction
                Data Collection Methods
                Key Insights and Trends
                Methodology
                Detailed Data Analysis
                Interpretation of Data
                
            Chapter 2: Results ({yy} pages):
                Summary of Findings
                Quantitative Results
                Qualitative Results
                Charts and Graphs
                Significance and Implications
                
            Chapter 3: Case Uses ({zz} pages):
                Case Study 1: [Case Name]
                Case Study 2: [Case Name]
                Case Study 3: [Case Name]
                Benefits and Impacts
                Challenges and Solutions
                Testimonials
            Note: Replace 'xx', 'yy', and 'zz' with the appropriate number of pages based on the total document length of 70 pages and write the number of pages for each section next to the section and heading title. Please write page numbers for each paragraph, section, chapter next to the title. Refer to the uploaded files for all necessary data and information to be included in the document. The final outline/table of contents should clearly indicate the chapters and sections.

            You are also an assistant that generates structured content. 
            I want you to create a book table of contents in JSON format. The structure should include the book title, and a list of chapters. Each chapter should have a chapter number, chapter title, start page, and total pages. Each chapter should also have a list of sections. Each section should have a section number, section title, start page, and total pages.

            The output structure must be a valid JSON object with a structure like this example format:
            
            {
            "title": "Sample Book Title",
            "chapters": [
                {
                "chapter_number": 1,
                "chapter_title": "Introduction",
                "start_page": 1,
                "total_pages": 10,
                "sections": [
                    {
                    "section_number": 1.1,
                    "section_title": "Background",
                    "start_page": 1,
                    "total_pages": 5
                    },
                    {
                    "section_number": 1.2,
                    "section_title": "Objective",
                    "start_page": 6,
                    "total_pages": 5
                    }
                ]
                }
                // Add more chapters as needed
                ]
            }
            
            JSON output with no extraneous text or wrappers:
            """
        # Replace placeholders with actual page numbers
        prompt = outline_system_prompt.replace('xx', str(pageAnalysis)) \
                            .replace('yy', str(pageResult)) \
                            .replace('zz', str(pageUseCase)) \
                            .replace('****', str(service))

        # Create Assistant
        assistant = self.client.beta.assistants.create(
            name="Business Analysis Assistant",
            instructions=prompt,
            model="gpt-4o",
        )
        print("create new thread")
        
        # Create new thread
        thread = self.client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": f"Please generated outline according to below: {promptText} {key_information}",
                }
            ]
        )
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant.id
        )
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text
        print(message_content.value)
        
        # Use regular expression to find text between triple backticks
        outline_object = {}
        match = re.search(r'```json(.*?)```', message_content.value, re.DOTALL)
        print(match)
        if match:
            json_string = match.group(1).strip()
            outline_object = json.loads(json_string)
        else:
            outline_object = json.loads(message_content.value)
        print(outline_object)
        
        
        # print("update assistant")
        # assistant = self.client.beta.assistants.update(
        #     assistant_id=assistant.id,
        #     instructions=f"""
        #                 You are an expert business analyst assistant tasked with generating comprehensive and tailored sections of a business analysis document.
        #                 Your objective is to produce detailed, non-repetitive content that aligns closely with the client’s goals and provides actionable insights.

        #                 Key Requirements:
        #                 1. **Content Structure and Depth**:
        #                     - Ensure that all content is tightly correlated with the main objectives of the consultancy.
        #                     - Each section should logically build upon the previous one, enhancing coherence and flow.
        #                     - Expand paragraphs by including detailed and specific content relevant to the client’s business environment, addressing their unique challenges.

        #                 2. **Use of Real Examples and Tools**:
        #                     - Incorporate practical, real-world examples, including relevant software tools, AI technologies, and case studies.
        #                     - Provide detailed explanations and guidance on the implementation of these tools, including links to demonstrations or tutorials where applicable.

        #                 3. **In-Depth Research and Data Analysis**:
        #                     - Include industry-specific benchmarks, trends, and data to contextualize recommendations.
        #                     - Conduct comparative analysis to highlight the advantages of proposed AI strategies over traditional methods, with a focus on potential ROI.

        #                 4. **Tailored Case Studies and Scenarios**:
        #                     - Develop hypothetical scenarios and case studies that directly address the client’s challenges, demonstrating how proposed solutions would function in their environment.
        #                     - Include success stories from similar companies or industries that have effectively implemented recommended strategies.

        #                 5. **Actionable Steps with Timelines**:
        #                     - Provide a detailed, step-by-step implementation plan with clear timelines.
        #                     - Define key milestones and KPIs for each stage to help the client track progress and measure success.

        #                 6. **Enhanced Visual Aids**:
        #                     - Utilize infographics, flowcharts, and diagrams to simplify complex concepts and enhance engagement.
        #                     - Incorporate advanced data visualizations or interactive elements to allow for deeper exploration of data.

        #                 7. **Interactive and Adaptive Content**:
        #                     - Design sections that can be customized based on the client’s inputs, such as goals, constraints, or budget.
        #                     - Include scenario modeling tools that allow the client to adjust variables and see potential outcomes.

        #                 Reference information:
        #                 {key_information}
        #                 You should meet these requirement at least:
        #                 {requirement}
        #                 Instructions:
        #                 - The content should be delivered in HTML format, excluding body and head tags, for easy integration into existing HTML documents.
        #                 - Conclusions are only needed at the end of each chapter, not for every section.
        #                 - Ensure all content is unique, detailed, and specifically tailored to the client’s needs, avoiding any duplication.
        #                 """,
        # )        
        
        # print(f"Title: {outline_object['title']}")
        # with open("temp.html", 'w', encoding="utf-8") as file:
        #     # Write the beginning of the HTML document
        #     file.write(""""
        #                <html>\n<head>\n<title>Document</title>\n
        #                <meta charset="utf-8" />\n
        #                </head>\n<body>\n
        #                """)
        #     for chapter in outline_object['chapters']:
        #         print(f"Chapter: {chapter['chapter_title']}")
        #         st_ch_time = time.time()
        #         file.write(f"<h1>Chapter {chapter['chapter_number']} {chapter['chapter_title']}</h1>\n")
                
        #         chapter_title = chapter['chapter_title']
        #         for section in chapter['sections']:
        #             st_sc_time = time.time()
        #             section_title = section["section_title"]
        #             total_pages = section["total_pages"]
                    
        #             #generate section description
        #             message = self.client.beta.threads.messages.create(
        #                 thread_id=thread.id,
        #                 role="user",
        #                 content=f"{section_title} of {chapter_title} in {total_pages * 500} words"
        #             )
        #             run = self.client.beta.threads.runs.create_and_poll(
        #                 thread_id=thread.id, assistant_id=assistant.id
        #             )
        #             messages = self.client.beta.threads.messages.list(
        #                 thread_id=thread.id
        #             )
        #             run_messages = [msg for msg in messages if msg.run_id == run.id]
                    
        #             if run.status == 'completed':
        #                 for msg in run_messages:
        #                     if msg.role == 'assistant':  # Assuming the assistant's role is labeled as 'assistant'
        #                         print(f"Response for section '{section_title}':")
        #                         description = ''
        #                         match = re.search(r'```html(.*?)```', msg.content[0].text.value, re.DOTALL)
        #                         if match:
        #                             description = match.group(1).strip()
        #                         else:
        #                             description = msg.content[0].text.value
        #                         section['description'] = description
        #                         print(len(description))
        #                         response = self.client.images.generate(
        #                             model="dall-e-3",
        #                             prompt=f"{outline_object['title']} {chapter['chapter_title']} {section['section_title']}",
        #                             size="1024x1024",
        #                             quality="standard",
        #                             n=1
        #                         )
        #                         section['image_url'] = response.data[0].url
        #                         file.write(f"<h2>Section {section['section_number']} {section['section_title']}</h2>")
        #                         # Add image
        #                         file.write(f"<img src='{section['image_url']}' alt='{section['section_title']} image'>")
        #                         # Add paragraph
        #                         file.write(f"{section['description']}")
        #                 print(run.status)
        #         #     break
        #         # break
        #     file.write('</body>\n</html>')
            
        # # create docx file from html
        # with open("temp.html", encoding='utf-8') as fp:
        #     html = fp.read()

        # # html2docx() returns an io.BytesIO() object. The HTML must be valid.
        # buf = html2docx(html, title=f"{service}") 
        
        # now = datetime.now()
        # formatted_date = now.strftime("%Y-%m-%d-%H-%M_%S")
        # save_directory = f'public/doc/'
        # # Ensure the directory exists
        # os.makedirs(save_directory, exist_ok=True)
        # file_path =os.path.join(save_directory, f"{formatted_date}.docx") 
        # print(file_path)
        # with open(f"{file_path}", "wb") as fp:
        #     fp.write(buf.getvalue())
            
        # # create pdf file from html
        # html_file_path = "temp.html"
        # output_pdf_path = f"public/pdf/{formatted_date}.pdf"
        # with open(f"{output_pdf_path}", "wb") as fp:
        #     try:
        #         pdfkit.from_file(html_file_path, output_pdf_path,  options={'enable-local-file-access': '', 'quiet': ''})
        #     except IOError as e:
        #         # Log the specific error
        #         print(f"IOError occurred: {e}")
        
        # # print(f"PDF created: {output_pdf_path}")
        # return {"file_url": f"/{file_path}", "pdf_url": f"/{output_pdf_path}", "success": True}
        return ''
    