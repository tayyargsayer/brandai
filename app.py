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
from datetime import datetime
from datetime import time
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
pd.set_option('display.max_colwidth', 4)

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
        st.text("Son Güncelleme: 23.04.2024")

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

            col1, col2 = st.columns([0.6, 1])


            with col1:
                start_date = st.date_input("Kampanya Başlangıç Tarihi Seçin")
                end_date = st.date_input("Kampanya Bitiş Tarihi Seçin")

                # Convert the dates to datetime at midnight
                from datetime import datetime, time, timezone

                # Convert the dates to datetime at midnight
                start_datetime = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc)
                end_datetime = datetime.combine(end_date, time(23, 59, 59), tzinfo=timezone.utc)

            #use start_datetime and filter camp_start_date on user_photos
            # Convert the camp_start_date from string to datetime
            for photo in user_photos:
                photo['camp_start_date'] = datetime.strptime(photo['camp_start_date'], "%Y-%m-%dT%H:%M:%S.%f%z")

            # Filter the user_photos based on the camp_start_date
            filtered_photos = [photo for photo in user_photos if
                               start_datetime <= photo['camp_start_date'] <= end_datetime]

            st.write(f"Seçilen tarih aralığında {len(filtered_photos)} adet fotoğraf bulunmaktadır.")

            with col2:
                brands = [photo['brands'] for photo in filtered_photos]
                unique_brands = list(set(brands))
                brand_counts = collections.Counter(brands)

                selected_brands = st.multiselect("Markaları Seçin", unique_brands)

                st.write(f"Seçilen markaların sayısı: {len(selected_brands)}")

            brand_counts = {brand: count for brand, count in brand_counts.items() if brand in selected_brands}


            # Define selected_location before the if block
            selected_location = None
            # Ask the user if they want to filter by location
            filter_by_location = st.sidebar.checkbox('Lokasyon ile filtrelemek ister misiniz?')

            if filter_by_location:
                # Create a set of tuples where each tuple contains the latitude and longitude of a location
                unique_locations = set(
                    (photo['location']['latitude'], photo['location']['longitude']) for photo in filtered_photos if
                    photo['brands'] in selected_brands)
                unique_locations = list(unique_locations)

                selected_location = st.sidebar.selectbox("Lokasyonları Seçin", unique_locations, index=0)

            st.divider()



            col41, col42, col43 = st.columns([1, 1, 1])

            with col41:
                import matplotlib.pyplot as plt

                if selected_location is not None:
                    # Create a DataFrame from the brand_counts dictionary
                    # Count the brands at the selected location
                    brand_counts = collections.Counter(photo['brands'] for photo in filtered_photos if
                                                       photo['brands'] in selected_brands and (
                                                       photo['location']['latitude'],
                                                       photo['location']['longitude']) == selected_location)

                    # Create a DataFrame from the brand_counts dictionary
                    df = pd.DataFrame(list(brand_counts.items()), columns=['Brand', 'Count'])

                    # Display the DataFrame
                    st.write(df)



                else:
                    # Create a DataFrame from the brand_counts dictionary
                    df = pd.DataFrame(list(brand_counts.items()), columns=['Brand', 'Count'])

                    # Display the DataFrame
                    st.write(df)


            with col42:
                if selected_location is not None:
                    # Create a list of dictionaries where each dictionary contains the brand name and its unit
                    data = [{'Brand': photo['brands'], 'Unit': photo['unit']} for photo in filtered_photos if
                            photo['brands'] in selected_brands and (
                            photo['location']['latitude'], photo['location']['longitude']) == selected_location]

                    # Create a DataFrame from the data
                    df = pd.DataFrame(data)

                    # Display the DataFrame
                    st.write(df)
                else:
                    # Create a list of dictionaries where each dictionary contains the brand name and its unit
                    data = [{'Brand': photo['brands'], 'Unit': photo['unit']} for photo in filtered_photos if
                            photo['brands'] in selected_brands]

                    # Create a DataFrame from the data
                    df = pd.DataFrame(data)

                    # Display the DataFrame
                    st.write(df)

            with col43:

                if selected_location is not None:
                    # Create a list of dictionaries where each dictionary contains the brand name, its unit, and its product
                    data = [{'Brand': photo['brands'], 'Unit': photo['unit'], 'Product': photo['product']} for photo in
                            filtered_photos if photo['brands'] in selected_brands and (
                            photo['location']['latitude'], photo['location']['longitude']) == selected_location]

                    # Create a DataFrame from the data
                    df = pd.DataFrame(data)

                    # Display the DataFrame
                    st.write(df)
                else:
                    # Create a list of dictionaries where each dictionary contains the brand name, its unit, and its product
                    data = [{'Brand': photo['brands'], 'Unit': photo['unit'], 'Product': photo['product']} for photo in
                            filtered_photos if photo['brands'] in selected_brands]

                    # Create a DataFrame from the data
                    df = pd.DataFrame(data)

                    # Display the DataFrame
                    st.write(df)

        st.divider()

        import matplotlib.pyplot as plt

        # Create separate columns for brands, units, and products
        col51, col52, col53 = st.columns([1, 1, 1])

        if selected_location is not None:
            # Count the brands, units, and products at the selected location
            brand_counts = collections.Counter(photo['brands'] for photo in filtered_photos if
                                               photo['brands'] in selected_brands and (
                                                   photo['location']['latitude'],
                                                   photo['location']['longitude']) == selected_location)
            unit_counts = collections.Counter(photo['unit'] for photo in filtered_photos if
                                              photo['brands'] in selected_brands and (
                                                  photo['location']['latitude'],
                                                  photo['location']['longitude']) == selected_location)
            product_counts = collections.Counter(photo['product'] for photo in filtered_photos if
                                                 photo['brands'] in selected_brands and (
                                                     photo['location']['latitude'],
                                                     photo['location']['longitude']) == selected_location)

            # Create DataFrames from the count dictionaries
            brand_df = pd.DataFrame(list(brand_counts.items()), columns=['Brand', 'Count'])
            unit_df = pd.DataFrame(list(unit_counts.items()), columns=['Unit', 'Count'])
            product_df = pd.DataFrame(list(product_counts.items()), columns=['Product', 'Count'])

            # Create pie charts in the corresponding columns
            with col51:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(brand_df['Count'], labels=brand_df['Brand'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)

            with col52:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(unit_df['Count'], labels=unit_df['Unit'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)

            with col53:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(product_df['Count'], labels=product_df['Product'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)

        else:
            # Count the brands, units, and products
            brand_counts = collections.Counter(photo['brands'] for photo in filtered_photos if
                                               photo['brands'] in selected_brands)
            unit_counts = collections.Counter(photo['unit'] for photo in filtered_photos if
                                              photo['brands'] in selected_brands)
            product_counts = collections.Counter(photo['product'] for photo in filtered_photos if
                                                 photo['brands'] in selected_brands)

            # Create DataFrames from the count dictionaries
            brand_df = pd.DataFrame(list(brand_counts.items()), columns=['Brand', 'Count'])
            unit_df = pd.DataFrame(list(unit_counts.items()), columns=['Unit', 'Count'])
            product_df = pd.DataFrame(list(product_counts.items()), columns=['Product', 'Count'])

            # Create pie charts in the corresponding columns
            with col51:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(brand_df['Count'], labels=brand_df['Brand'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)

            with col52:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(unit_df['Count'], labels=unit_df['Unit'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)

            with col53:
                fig, ax = plt.subplots(figsize=(4, 4))
                ax.pie(product_df['Count'], labels=product_df['Product'], autopct='%1.1f%%', textprops={'fontsize': 8})
                st.pyplot(fig)



        import matplotlib.pyplot as plt
        import io

        # Create a single figure with three subplots
        fig, axs = plt.subplots(1, 3, figsize=(12, 4))

        # Create the pie charts in the subplots
        axs[0].pie(brand_df['Count'], labels=brand_df['Brand'], autopct='%1.1f%%', textprops={'fontsize': 8})
        axs[1].pie(unit_df['Count'], labels=unit_df['Unit'], autopct='%1.1f%%', textprops={'fontsize': 8})
        axs[2].pie(product_df['Count'], labels=product_df['Product'], autopct='%1.1f%%', textprops={'fontsize': 8})

        # Set the titles for the subplots
        axs[0].set_title('Brands')
        axs[1].set_title('Units')
        axs[2].set_title('Products')

        # Adjust the layout
        plt.tight_layout()

        # Save the figure to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Use st.download_button to download the figure
        st.download_button(
            label="Tabloları İndir",
            data=buf,
            file_name='pie_charts.png',
            mime='image/png'
        )



    elif st.session_state["authentication_status"] is False:
        st.sidebar.error('Kullanıcı adı/şifre yanlış')
    elif st.session_state["authentication_status"] is None:
        st.sidebar.warning('Lütfen sisteme erişebilmek için giriş yapın.')


    # Saving config file
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)


except CredentialsError as e:
    st.error(e)


















