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
from datetime import datetime, timezone
import json

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


st.set_page_config(layout="wide",
                     page_title="Eye Authentic",
                     page_icon="👁️",
                     initial_sidebar_state="auto")



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
    config['pre-authorized']
)

# Creating a login widget
# Creating a login widget in the sidebar
try:
    if not st.session_state.get("authentication_status", False):
        with st.sidebar:
            with st.expander("Giriş Yap", expanded=False):
                try:
                    authenticator.login(max_login_attempts=5)
                except LoginError as e:
                    st.error(str(e))

            with st.expander("Kayıt Ol", expanded=False):
                try:
                    (email_of_registered_user,
                     username_of_registered_user,
                     name_of_registered_user) = authenticator.register_user(pre_authorization=True)
                    if email_of_registered_user:
                        st.success('Kullanıcı başarıyla kaydedildi')
                except RegisterError as e:
                    st.error(e)

    if st.session_state["authentication_status"]:
        authenticator.logout()
        st.sidebar.write(f'Hoşgeldin *{st.session_state["name"]}*')

        st.header("Eye Authentic Hoşgeldiniz")
        st.text("Son Güncelleme: 20.04.2024")

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
            # db = firestore.Client.from_service_account_json("firestore-key.json")
            user_id = "YYfdk8Dd5NXgf7zriJgff9Xsh0i1"
            # user_photos_ref = db.collection('users').document(user_id).collection('user_photos')
            # user_photos = user_photos_ref.get()

            with open('user_photos.json', 'r', encoding='utf-8') as f:
                user_photos = json.load(f)

            unique_brands = set()
            unique_locations = set()


            for photo in user_photos:
                # unique_brands.add(photo.to_dict()['brands'])

                location = photo['location']
                unique_locations.add((location['latitude'], location['longitude']))

            if user_id:

                col1, col2, col3 = st.columns([0.4, 1.2, 0.3])

                from datetime import datetime

                with col1:
                    start_date = st.date_input("Kampanya Başlangıç Tarihi Seçin")
                    end_date = st.date_input("Kampanya Bitiş Tarihi Seçin")

                    # Convert the dates to datetime at midnight
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                    end_datetime = datetime.combine(end_date, datetime.min.time())

                    # Attach the timezone information
                    start_datetime = start_datetime.replace(tzinfo=timezone.utc)
                    end_datetime = end_datetime.replace(tzinfo=timezone.utc)

                    filtered_photos = []

                    from datetime import datetime

                    for photo in user_photos:
                        photo_start_date = datetime.strptime(photo['camp_start_date'], "%Y-%m-%dT%H:%M:%S.%f%z")
                        photo_end_date = datetime.strptime(photo['camp_end_date'], "%Y-%m-%dT%H:%M:%S.%f%z")

                        if photo_start_date >= start_datetime and photo_end_date <= end_datetime:
                            filtered_photos.append(photo)


                with col2:
                    brands = set()
                    for photo in filtered_photos:
                        brands.add(photo['brands'])

                    brand_selection = st.multiselect("Lütfen marka seçin", [brand for brand in brands])
                    st.write(f"Çalışılmış toplam marka sayısı {len(brands)}.")
                    st.write(f"Seçilen marka sayısı {len(brand_selection)}.")


                with col3:
                    location_selection = st.selectbox("Lütfen lokasyon seçin", [location for location in unique_locations])

                st.divider()

                st.write(f"Seçilen tarih aralığı ve markalara ait toplamda {len(brands)} adet döküman bulundu.")









            else:
                st.warning("Lütfen kullanıcı ID'sini girin.")










    elif st.session_state["authentication_status"] is False:
        st.sidebar.error('Kullanıcı adı/şifre yanlış')
    elif st.session_state["authentication_status"] is None:
        st.sidebar.warning('Lütfen sisteme erişebilmek için giriş yapın.')


    # Saving config file
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)


except CredentialsError as e:
    st.error(e)


















