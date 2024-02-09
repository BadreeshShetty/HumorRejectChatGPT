import streamlit as st
import json
import re
import openai
import time
import requests
from streamlit_lottie import st_lottie_spinner

from pdf2image import convert_from_bytes
from PIL import Image

from PyPDF2 import PdfReader

from dotenv import load_dotenv,find_dotenv


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def read_pdf_page(file, page_number):
    pdfReader = PdfReader(file)
    page = pdfReader.pages[page_number]
    return page.extract_text()


def clean_resume(pdf_str):
    applicant_resume = re.sub('\s[,.]', ',', pdf_str)
    applicant_resume = re.sub('[\n]+', '\n', applicant_resume)
    applicant_resume = re.sub('[\s]+', ' ', applicant_resume)

    return applicant_resume


def get_response(prompt, system = '', temperature = 0.5):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt},
                   {"role": "system", "content": system}],
        temperature = temperature
    ) 
    return response['choices'][0]['message']['content']


def on_text_area_change():
    st.session_state.page_text = st.session_state.my_text_area

def extracted_gpt_base(gpt_response_resume_json,extract,text):
    if gpt_response_resume_json['basic_info'][extract]:
        extract=st.text_input(
            text,
            gpt_response_resume_json['basic_info'][extract],
            key=extract)
    else:
        extract=st.text_input(
            text,
            "Enter : "+str(text),
            key=extract)
   
def extracted_gpt_wk_exp(gpt_response_resume_json):
    if gpt_response_resume_json['work_experience']:
        for experience in gpt_response_resume_json['work_experience']:
            for key, value in experience.items():
                if key=="job_summary":
                    key=st.text_area(
                        height=200,
                        label=key.capitalize().replace("_", " "),  # Convert keys to capitalized format
                        value=value,  # Use the value from the JSON
                        key=f"{key}_{experience['job_title']}"  # Use a unique key for each input
                    )
                else:
                    key=st.text_input(
                        label=key.capitalize().replace("_", " "),  # Convert keys to capitalized format
                        value=value,  # Use the value from the JSON
                        key=f"{key}_{experience['job_title']}"  # Use a unique key for each input
                    )
                
    else:
        st.text("No work experience provided.")

def extracted_gpt_prj_exp(gpt_response_resume_json):
    if gpt_response_resume_json['project_experience']:
        for experience in gpt_response_resume_json['project_experience']:
            for key, value in experience.items():
                if key=="project_description":
                    key=st.text_area(
                        height=200,
                        label=key.capitalize().replace("_", " "),  # Convert keys to capitalized format
                        value=value,  # Use the value from the JSON
                        key=f"{key}_{experience['project_name']}"  # Use a unique key for each input
                    )
                else:
                    key=st.text_input(
                        label=key.capitalize().replace("_", " "),  # Convert keys to capitalized format
                        value=value,  # Use the value from the JSON
                        key=f"{key}_{experience['project_name']}"  # Use a unique key for each input
                    )
                
    else:
        st.text("No project experience provided.")

def technical_skills(gpt_response_resume_json):

    skills = ', '.join(map(str, gpt_response_resume_json["technical_skills"])) 
    key=st.text_area(label="Technical Skills",height=200,value=skills)

        

def call_extracted_gpt_base(gpt_response_resume_json):
    st.header("Base Info:")
    extracted_gpt_base(gpt_response_resume_json,"full_name","Full Name:")
    extracted_gpt_base(gpt_response_resume_json,"email","Email:")
    extracted_gpt_base(gpt_response_resume_json,"phone_number","Phone Number:")
    extracted_gpt_base(gpt_response_resume_json,"portfolio_website_url","Portfolio URL:")
    extracted_gpt_base(gpt_response_resume_json,"linkedin_url","Linkedin URL:")
    extracted_gpt_base(gpt_response_resume_json,"github_main_page_url","Github URL:")
    extracted_gpt_base(gpt_response_resume_json,"university","University:")
    extracted_gpt_base(gpt_response_resume_json,"education_level","Highest Education:")
    extracted_gpt_base(gpt_response_resume_json,"graduation_year","Highest Education Graduation Year:")
    extracted_gpt_base(gpt_response_resume_json,"graduation_month","Highest Education Graduation Month:")
    extracted_gpt_base(gpt_response_resume_json,"latest_majors","Highest Education Majors:")
    extracted_gpt_base(gpt_response_resume_json,"total_years_experience_with_months","Total Years of Experience:")


    extracted_gpt_wk_exp(gpt_response_resume_json)

    extracted_gpt_prj_exp(gpt_response_resume_json)

    technical_skills(gpt_response_resume_json)


def main():
    _ = load_dotenv(find_dotenv())

    lottie_url_hand="https://lottie.host/c6d296de-3a71-44bf-b16f-4b72fa0e96a2/tfVAlnaamt.json"
    lottie_download = load_lottieurl(lottie_url_hand)

    st.set_page_config(
    page_title = 'Job Rejection Humor',
    page_icon = '✅',
    layout = 'wide')

    st.title("Add Job Description here:")
    job_descripion=st.text_area(
                            height=100,
                            label="Add the Job Description",
                            key="Job Description"
                        )

    st.title("Please Upload One Page Resume PDF to see the rejection faster than speed of dark")

    # PDF file upload
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf_file:
        # Create a selectbox to choose the page number
        # pdfReader = PdfReader(pdf_file)
        # page_numbers = list(range(1, len(pdfReader.pages)+1))
        # selected_page = st.selectbox("Select a page", page_numbers)
        # selected_page -= 1
        # Convert the selected page to an image
        images = convert_from_bytes(pdf_file.getvalue())
        # image = images[selected_page]
        image = images[0]

        # Create two columns to display the image and text
        # col1, col2 = st.columns(2)
        left_co, cent_co,last_co = st.columns(3)

        # Display the image in the first column
        cent_co.image(image, caption=f"Page {0 + 1}")

        pdf_str=read_pdf_page(pdf_file, 0)

        applicant_resume=clean_resume(pdf_str)

        system_prompt = '''You are a helpful AI Job assistant, provide the answer in a json format.'''

        message_prompt =str(applicant_resume)+'''
        Summarize the text below into a JSON with exactly the following structure 
        {basic_info: {first_name, last_name, full_name, email, phone_number, portfolio_website_url, 
        linkedin_url, github_main_page_url, university, education_level (BS, MS, or PhD), graduation_year, 
        graduation_month, latest_majors, total_years_experience_with_months}, 
        work_experience: [{job_title, company, location, duration, job_summary}], 
        project_experience:[{project_name, project_description}], 
        technical_skills:[elaborate_skills_mentioned_throughout_in_resume],
        intrapersonal_skills: if intrapersonal skills then [extract_skills_mentioned_throughout_in_resume] 
        else null}.'''
        
        ## This code will send the request and display the response
        with st_lottie_spinner(lottie_download, reverse=True, height=400, width=400, speed=1,   loop=True, quality='high', key="download1"):
            gpt_response_resume = get_response(message_prompt,system_prompt)
        # print(gpt_response_resume)
            
          

        
        gpt_response_resume_json = json.loads(gpt_response_resume)

        gpt_response_resume_json['basic_info']['first_name']

        # with last_co:
        # st.toast('Correct! if Extraction is wrong')
        # time.sleep(.5)

        # call_extracted_gpt_base(gpt_response_resume_json)

        
        if job_descripion and gpt_response_resume_json:
            with st_lottie_spinner(lottie_download, reverse=True, height=400, width=400, speed=1,   loop=True, quality='high', key="download2"):
    
                system_prompt = '''You are an ATS Job Assistant for the company mnetioned in the job description, provide the reply email in a humorous way showing 
                he/she/they is being rejected and is not considered for the job role based on the resume even without even giving a chance. Spit Relevant 
                Funny facts based on resume and job description. Additionally give serious suggestions on how the user can improve himself 
                overall and specific changes to the resume based on this job description.'''
                message_prompt ='''
                Based on the details of the user'''+str(gpt_response_resume_json)+'''
                mentioned on the job description here:'''+str(job_descripion)+''' Reject in a very funny way demoralizing,mocking him/her/them and motivating him/her/them at the same time.'''

                gpt_response_jd = get_response(message_prompt,system_prompt)
                st.header(gpt_response_jd)
            


if __name__ == '__main__':
    main()
