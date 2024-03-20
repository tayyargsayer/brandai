import os
import random
import time
import PyPDF2
import google.generativeai as genai
import pandas as pd
import streamlit as st
from docx import Document
from dotenv import load_dotenv
from google.generativeai import GenerationConfig
from chat import chat_app
from curator import *

load_dotenv()

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the model
generation_config = GenerationConfig(
    temperature=1,
    top_p=1,
    top_k=1,
    max_output_tokens=2048,
)


safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

PAGES = {
    "Chat": "chat.app",
    "Curator": "curator",
}

# streamlit setup
st.set_page_config(page_title="Machinho")
st.header("Machinho Hosgeldiniz")

#add tabs


# tab1, tab2, tab3 = st.tabs(["Tablo", "Liste", "Grafik"])


# with tab1:
#
# with tab2:
#
# with tab3:


st.sidebar.title("Machinho Assistans")
st.sidebar.subheader("Datalarin yuklenmesi biraz zaman alabilir. Lutfen bekleyin.")


machine_names = [""] + machines()
selected_machine = st.sidebar.selectbox("Hangi Makine Grubunu İstiyorsun?", machine_names)
machine_data = machine_datas(selected_machine)

selected_specs = st.sidebar.multiselect("Hangi Özellikleri İstiyorsun?", machine_data.columns)

# Check if more than 5 items are selected
if len(selected_specs) > 10:
    # Display a warning message
    st.sidebar.warning("En fazla 10 özellik seçebilirsiniz.")
    # Reset the selection to the first 5 items
    selected_specs = selected_specs[:5]

@st.cache_data
def get_machine_data(machine_name):
    return machine_datas(machine_name)

@st.cache_data
def get_brand_names(machine_data):
    return machine_data["Manufacturer"].unique()

if selected_machine:
    user_input = st.text_input("Sorunu gonder gelsin")
    start_button = st.button("Başla")


    data_specs = machine_data.columns
    machine_data = get_machine_data(selected_machine)
    brand_names = get_brand_names(machine_data)

    selected_brands = st.sidebar.multiselect("Hangi Markayı İstiyorsun?", brand_names)

    if selected_brands:
        filtered_data = machine_data[machine_data["Manufacturer"].isin(selected_brands)]
        if selected_specs:
            filtered_data = filtered_data[selected_specs]

    else:
        filtered_data = machine_data
        if selected_specs:
            filtered_data = filtered_data[selected_specs]


    prompt_2 = [f"""
        You are an expert in work machines. Please provide an answer for {user_input}. Note that there are some restrictions:
            1. Response should always be in the form of a table with the first row containing the column names {selected_specs}the subsequent rows containing the data.
            2. The data of table should only contain the {filtered_data} data.
            3. While doing that, the main goal is answering the user question {user_input}.
            4. Output should be in Turkish.
            
            
        Please note that the output will later be converted into a PDF, so make your edits accordingly. The output should be in Turkish.
        """]


    import io

    if user_input and start_button:
        status_placeholder = st.empty()
        status_placeholder.status("Kağıt Oluşturuluyor...")
        response = model.generate_content(prompt_2)


        # Write the response to the screen
        st.write(response.text)
        status_placeholder.success("Kağıt Oluşturuldu")

    else:
        st.warning("Lütfen bir soru girin ve başlamak için butona basın.")

# st.sidebar.checkbox("Asistanım inisiyatif alabilsin ve harici makineleri ekleyebilsin.", key="inisiyatif")















