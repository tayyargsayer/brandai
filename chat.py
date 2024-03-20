
def chat_app():
    import os
    import random

    import PyPDF2
    import google.generativeai as genai
    import pandas as pd
    import streamlit as st
    from docx import Document
    from dotenv import load_dotenv
    from google.generativeai import GenerationConfig


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

    ##Function to load Gemini model and get response
    names = ["Ceyda", "Müge", "Filiz", "Alev", "Ceren", "Rüya", "Hande"]
    model = genai.GenerativeModel(model_name="gemini-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings,
                                  )



    prompt = """Sen Machinho firmasının iş makinesi eksperti ve müşteri asistanısın. 
                      "Eğer direkt olarak soru sorulursa kendini bütün konuşma boyunca sadece 1 kere tanıt ve daha sonra soruyu cevapla. "
                      "İnsanların bu sektör ve iş makineleri ile ilgili sorularından yola çıkarak tahminlerde bulunabilirsin."
                      "Fiyat, makine ismi, makine ve marka önerisi gibi sorular ağırlıklı olacaktır. Çok doğru sonuçlar vermeni bekliyorum."
                      "Dosyada olmayan konular, başlıklar ve içerikler hakkında bilgi verme."""

    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": [
                "Eğer iş makineleri dışında bilgi almak istenirse, bu konu hakkında bilgin olmadığı belirt. "
                "Benzer cevaba yönelik kendi yönlendirmelerini ve cevaplarını arttırabilirsin."]
        },
        {
            "role": "model",
            "parts": [
                "Maalesef bu konu hakkında bilgi sahibi değilim. İş makineleri hakkında herhangi bir sorunuz varsa, size yardımcı olmak isterim. "
                "\n\nÖrneğin: Toprak kazma ve yükleme çalışmalarınız için en iyi makine hangisidir?"]
        },
        {
            "role": "user",
            "parts": [f"Eğer kullanıcı önceki, mevcut veya sonraki soruda senden kıyaslama veya karşılaştırma yapmanı isterse sonuçları daima tablo şeklinde göstermeni istiyorum."
                      "Karşılaştırma yaparken mutlaka kazma derinliği, yükleme kapasitesi, koç gücü, ağırlık, yakıt verimliliği, güvenilirlik, konfor ve fiyat gibi kriterleri kullanarak karşılaştırma yap."
                      "Fiyatlar daima Euro cinsinden ve 2024 piyasa fiyatları olmalıdır. "
                      "Yakıt verimliliği, güvenilirlik ve konfor gibi kriterlerde, 1-10 arasında bir puanlama yapmanı istiyorum. "
                      f"Örneğin: İş makineleri markalarını karşılaştırma yapabilir misin?"]

        },
        {
            "role": "model",
            "parts": ["Elbette, karşılaştırma sonuçlarını aşağıdaki tabloda bulabilirsiniz: \n\n"
                      "st.table"
            ]
        }

    ])

    def get_gemini_response(question, excel_content=None):
        if excel_content is not None:
            response = chat.send_message(prompt + question + excel_content, stream=False)
        else:
            response = chat.send_message(prompt + question, stream=False)
        return response


    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    st.subheader("Machinho Live Assistant")

    uploaded_file = st.sidebar.file_uploader("Dosyayı Yükleyin:", type=["xlsx", "xls", "csv", "pdf", "docx"],
                                             key="uploader1")

    if uploaded_file is not None:
        st.sidebar.write("Dosya Başarıyla Yüklendi")

        def input_file_setup(uploaded_file):
            if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith(
                    '.xls') or uploaded_file.name.endswith('.csv'):
                file_content = pd.read_excel(uploaded_file)
                file_content = file_content.to_string()
            elif uploaded_file.name.endswith('.pdf'):
                reader = PyPDF2.PdfReader(uploaded_file)
                file_content = ""
                for page in reader.pages:
                    file_content += page.extract_text()
            elif uploaded_file.name.endswith('.docx'):
                doc = Document(uploaded_file)
                file_content = " ".join([paragraph.text for paragraph in doc.paragraphs])
            return file_content

        file_content = input_file_setup(uploaded_file)
    else:
        file_content = None

    input = st.chat_input("Haydi sohbet edelim?")
    if input:
        status_placeholder = st.empty()
        status_placeholder.status("Assistant is typing...")
        # Check if a file has been uploaded
        if file_content is not None:
            response = get_gemini_response(prompt + input + file_content)
        else:
            response = get_gemini_response(prompt + input)

        # User message
        with st.chat_message("User"):
            st.write(input)
        st.session_state['chat_history'].append(("User: ", input))

        st.subheader("The answer is:")
        for chunk in response:
            # Assistant message
            with st.chat_message("Assistant"):
                st.write(chunk.text)
            st.session_state['chat_history'].append(("Assistant: ", chunk.text))
        status_placeholder.empty()

