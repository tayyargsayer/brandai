import os
from pathlib import Path
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from google.cloud import firestore
import pydeck as pdk
import pandas as pd
import collections
import streamlit_authenticator as stauth

load_dotenv()

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 0.45,
    "top_p": 0.9,
    "max_output_tokens": 2048,
}

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


model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def get_gemini_repsonse(prompt, original_image):
    model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    response = model.generate_content([prompt, original_image])
    return response.text


st.set_page_config(layout="wide")



import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import (CredentialsError,
                                                          ForgotError,
                                                          LoginError,
                                                          RegisterError,
                                                          ResetError,
                                                          UpdateError)

# Loading config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# Creating a login widget
# Creating a login widget in the sidebar
try:
    with st.sidebar:
        with st.expander("Login", expanded=True):
            authenticator.login()

        with st.expander("Reset Password", expanded=False):
            try:
                (username_of_forgotten_password,
                 email_of_forgotten_password,
                 new_random_password) = authenticator.forgot_password()
                if username_of_forgotten_password:
                    st.success('New password sent securely')
                    # Random password to be transferred to the user securely
                elif not username_of_forgotten_password:
                    st.error('Username not found')
            except ForgotError as e:
                st.error(e)


except LoginError as e:
    st.sidebar.error(e)


    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')


        st.title('Some content')
        st.header("Eye Authentic Hoşgeldiniz")
        st.text("Son Güncelleme: 18.04.2024")

        st.sidebar.title("Eye Authentic Assistant")
        st.sidebar.subheader("Görselinizin yüklenmesi biraz zaman alabilir. Lütfen bekleyin.")

        uploaded_image = st.sidebar.file_uploader("Lütfen sadece belirtilen formatlarda yükleme yapın",
                                                  type=["png", "jpg", "jpeg", "webp"])

        if uploaded_image is not None:
            st.sidebar.image(uploaded_image, caption="Yüklenen Görsel", use_column_width=True)
            original_image_parts = [{"mime_type": "image/jpeg",
                                     "data": uploaded_image.read()}]

        tab1, tab2, tab3 = st.tabs(["Marka Analizi", "Anomali Kontrolü", "Raporlama"])
        st.markdown("""
                <style>
    
                    .stTabs [data-baseweb="tab-list"] {
                        gap: 2px;
                    }
    
                    .stTabs [data-baseweb="tab"] {
                        height: 50px;
                        width: 100%;
                        white-space: pre-wrap;
                        background-color: #F0F2F6;
                        border-radius: 4px 4px 0px 0px;
                        margin-right: 1%;
                    }
    
                    .stTabs [aria-selected="true"] {
                        background-color: brown;
                        color: #FFFFFF;
                    }
    
                </style>""", unsafe_allow_html=True)

        with tab1:
            if uploaded_image is None:
                st.warning("Lütfen bir görsel yükleyin.")
            else:
                start_button = st.button("Marka analizi yap")

                prompt = [original_image_parts[0],
                          f"""
                        I want you to inspect the file above and detect the brands on it with high accuracy. While doing that, please follow these steps:
                            1- While giving output, give the brand name, it's category, sub-category and it's unit like bilboard, pylon, banner etc. in Turkish.For example:
                                "Nike - Giyim - Spor Ayakkabı - Bilboard
                                "Eti - Yiyecek - Bisküvi - Poster"
                            3- The results should be seen on a table.
                            4- If you can't see any brand on image, for example "car" image has been taken but there is no brand or amblem on it, don't write anything.
                            5- You should be careful about spelling, for example "Adıdas" instead of "Adidas" is not acceptable. You should check the spelling from the internet.
                        """
                          ]

                if uploaded_image and start_button:
                    status_placeholder = st.empty()
                    status_placeholder.status("Görsel analiz Ediliyor..")
                    response = model.generate_content(prompt)

                    st.write(response.text)
                    complete_message = status_placeholder.success("Görsel analizi analizi tamamlandı")

                    if complete_message:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            download_button = st.markdown(
                                f'<a href="data:text/plain;charset=utf-8,{response.text}" download="response.txt">'
                                '<button class="streamlit-button-outlined" style="margin:10px;padding:10px;color:white;background-color:#FF6347;box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);border-radius: 10px;">İndir</button>'
                                '</a>',
                                unsafe_allow_html=True,
                            )


                else:
                    st.warning("Lütfen başlamak için butona basın.")

        with tab2:
            if uploaded_image is None:
                st.warning("Lütfen bir görsel yükleyin.")
            else:
                control_button = st.button("Anomali kontrol et")

                prompt_2 = [original_image_parts[0],
                            f"""
                                I want you to inspect the file above and check the anomaly for is it design or image is really parished or damaged. While doing that, please follow these steps:
                                    1- You should consider the image as a paper and paper can have limited deformations. For example, a paper can be crumpled, torn, or have a hole in it.
                                    2-Bilboard or image can be ruptured, ripped, or worn and shattered. These should be considered as anomalies.
                                    3- Some images may contain elements or visual effects like that seem like anomalies but are actually part of the design or marketing strategy. For example, a billboard for a screen brand might include an image of a glass crack. These should be considered as effect.
                                       If the image is really parished or damaged, you should say:
                                        "Efekt yok!"
                                        If the image is not really parished or damaged, it can be effect for example, you should say:
                                        "Efekt var!"
    
    
                                   """
                            ]

                if uploaded_image and control_button:
                    status_placeholder_2 = st.empty()
                    status_placeholder_2.status("Anomali kontrol Ediliyor..")
                    response_2 = model.generate_content(prompt_2)

                    st.write(response_2.text)
                    complete_message_2 = status_placeholder_2.success("Anomali kontrolü Tamamlandı")

                    if complete_message_2:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            download_button = st.markdown(
                                f'<a href="data:text/plain;charset=utf-8,{response_2.text}" download="response.txt">'
                                '<button class="streamlit-button-outlined" style="margin:10px;padding:10px;color:white;background-color:#FF6347;box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);border-radius: 10px;">İndir</button>'
                                '</a>',
                                unsafe_allow_html=True,
                            )


                else:
                    st.warning("Lütfen başlamak için butona basın.")

        with tab3:
            # Authenticate to Firestore with the JSON account key.
            db = firestore.Client.from_service_account_json("firestore-key.json")

            # Specify the user ID
            # user_id = st.text_input("Lütfen kullanıcı ID'sini girin")
            user_id = "YYfdk8Dd5NXgf7zriJgff9Xsh0i1"
            if user_id:

                col1, col2, col3, col4 = st.columns([0.3, 0.4, 1, 0.5])

                with col1:
                    st.selectbox("Lütfen ajans seçin", ["Ajans 1", "Ajans 2", "Ajans 3"])

                with col2:
                    start_date = st.date_input("Kampanya Başlangıç Tarihi Seçin")
                    end_date = st.date_input("Kampanya Bitiş Tarihi Seçin")

                with col3:
                    brand_selection = st.multiselect("Lütfen marka seçin", ["Marka 1", "Marka 2", "Marka 3"])

                with col4:
                    location_selection = st.selectbox("Lütfen lokasyon seçin", ["Lokasyon 1", "Lokasyon 2", "Lokasyon 3"])

                st.divider()

                # Fetch all documents from the 'user_photos' subcollection of the specified user
                user_photos_ref = db.collection('users').document(user_id).collection('user_photos')
                user_photos = user_photos_ref.get()




            else:
                st.warning("Lütfen kullanıcı ID'sini girin.")








    # # streamlit run c.py --server.runOnSave=True


    elif st.session_state["authentication_status"] is False:
        st.sidebar.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.sidebar.warning('Please enter your username and password')


















