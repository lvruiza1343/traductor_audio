import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# Crear carpeta temporal
try:
    os.mkdir("temp")
except:
    pass

# Función de limpiar archivos viejos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

remove_files(7)

# Función Text to Speech
def text_to_speech(input_language, output_language, text, tld):
    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

# --- ESTILOS --- 
st.markdown("""
    <style>
    .title {
        color: #4CAF50;
        text-align: center;
        font-size: 50px;
    }
    .subtitle {
        color: #2196F3;
        text-align: center;
        font-size: 30px;
    }
    .section {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .sidebar-title {
        font-size: 22px;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# --- INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="title">Reconocimiento Óptico de Caracteres</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="subtitle">Elige la fuente de la imagen 📸 o 📁</h2>', unsafe_allow_html=True)

cam_ = st.checkbox("📷 Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.markdown('<h2 class="sidebar-title">📸 Procesamiento de Imagen</h2>', unsafe_allow_html=True)
    filtro = st.radio("¿Aplicar filtro de inversión de colores?", ('Sí', 'No'))

bg_image = st.file_uploader("📤 Cargar Imagen:", type=["png", "jpg"])

text = " "  # Variable global

# --- PROCESAMIENTO DE IMAGEN ---
if bg_image is not None:
    with st.spinner('Procesando imagen...'):
        uploaded_file = bg_image
        st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
        
        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.read())
        
        st.success(f"✅ Imagen guardada como {uploaded_file.name}")
        img_cv = cv2.imread(uploaded_file.name)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)

st.write("### Texto detectado:")
st.write(text)

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    st.write("### Texto detectado desde cámara:")
    st.write(text)

# --- SIDEBAR PARA TRADUCCIÓN Y AUDIO ---
with st.sidebar:
    st.markdown('<h2 class="sidebar-title">🗣️ Parámetros de Traducción</h2>', unsafe_allow_html=True)

    translator = Translator()

    in_lang = st.selectbox(
        "🌎 Lenguaje de Entrada",
        ("Ingles", "Español", "Bengali", "Koreano", "Mandarin", "Japones"),
    )
    input_language = {"Ingles": "en", "Español": "es", "Bengali": "bn", 
                      "Koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}[in_lang]

    out_lang = st.selectbox(
        "🌎 Lenguaje de Salida",
        ("Ingles", "Español", "Bengali", "Koreano", "Mandarin", "Japones"),
    )
    output_language = {"Ingles": "en", "Español": "es", "Bengali": "bn", 
                       "Koreano": "ko", "Mandarin": "zh-cn", "Japones": "ja"}[out_lang]

    english_accent = st.selectbox(
        "🇬🇧 Acento (solo en Inglés)",
        ("Default", "India", "United Kingdom", "United States", "Canada", "Australia", "Ireland", "South Africa"),
    )
    tld = {"Default": "com", "India": "co.in", "United Kingdom": "co.uk", "United States": "com",
           "Canada": "ca", "Australia": "com.au", "Ireland": "ie", "South Africa": "co.za"}[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("🎵 Convertir Texto a Audio"):
        with st.spinner('Convirtiendo... 🎶'):
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown(f"## 🎧 Tu Audio:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)

            if display_output_text:
                st.markdown(f"## 📝 Texto Traducido:")
                st.write(output_text)

    
    
