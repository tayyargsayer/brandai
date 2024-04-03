import os
from pathlib import Path
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 0.4,
    "top_p": 0.90,
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



st.header("Eye Authentic Hoşgeldiniz")
st.text("Son Güncelleme: 03.04.2024")

st.sidebar.title("Eye Authentic Assistant")
st.sidebar.subheader("Görselinizin yüklenmesi biraz zaman alabilir. Lütfen bekleyin.")

uploaded_image = st.sidebar.file_uploader("Lütfen sadece belirtilen formatlarda yükleme yapın", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    st.sidebar.image(uploaded_image, caption="Yüklenen Görsel", use_column_width=True)
    original_image_parts = [{"mime_type": "image/jpeg",
                             "data": uploaded_image.read()}]

    start_button = st.button("Analiz et")


    prompt = [original_image_parts[0],
              f"""
        I want you to inspect the file above and detect the brands on it with high accuracy. While doing that, please follow these steps:
            1- If there is any deformation on the image, or billboards or any other objects that are not related to the brands:
            Note: Some images may contain elements that seem like anomalies but are actually part of the design or marketing strategy. For example, a billboard for a window brand might include an image of a glass crack. These should not be considered as anomalies.
               If you not sure about the anomaly, you can say:
                "Görüntüde deformasyon olabilir - Reklam Panosunda yırtık olabildiği için marka teşhisi yapamıyorum"
                "Görüntüde deformasyon olabilir - Billboard'da efekt olduğu için marka teşhisi yapamıyorum"
               
               If you detect a real anomaly, stop the process and report the category of the deformation in Turkish. For example:

                "Görüntüde deformasyon var - Reklam Panosunda yırtık var"
                "Görüntüde deformasyon var - Billboard'da yırtık var"
                'Görüntüde deformasyon var - Bir nesne görünüyor ama marka değil'
                
            
                
            2- While giving output, give the brand name, it's category and sub-category in Turkish.For example:
                "Nike - Giyim - Spor Ayakkabı"
                "Eti - Yiyecek - Bisküvi"
            3- The results should be seen on a table.
            4- If you can't see any brand on image, for example "car" image has been taken but there is no brand or amblem on it, don't write anything.
            5- You should be careful about spelling, for example "Adıdas" instead of "Adidas" is not acceptable. You should check the spelling from the internet.
        """
              ]


    if uploaded_image and start_button:
        status_placeholder = st.empty()
        status_placeholder.status("Görsel Analiz Ediliyor..")
        response = model.generate_content(prompt)


        st.write(response.text)
        complete_message = status_placeholder.success("Analiz Tamamlandı")

        if complete_message:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                download_button = st.markdown(
                    f'<a href="data:text/plain;charset=utf-8,{response.text}" download="response.txt">'
                    '<button class="streamlit-button-outlined" style="margin:10px;padding:10px;color:white;background-color:#FF6347;box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);border-radius: 10px;">İndir</button>'
                    '</a>',
                    unsafe_allow_html=True,
                )




    else:
        st.warning("Lütfen tekrar başlamak için butona basın.")









# streamlit run c.py --server.runOnSave=True







