import base64
import os
import tempfile
import requests
import streamlit as st
from PIL import Image
from gtts import gTTS


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llava"


st.set_page_config(
    page_title="SoundSight",
    page_icon="👁️",
    layout="centered"
)


st.markdown("""
# 👁️ SoundSight

Assistente de visão por IA para descrição sonora de cenas.

Capture uma imagem pela câmera. O sistema descreve a cena em português e gera áudio para auxiliar pessoas com Retinose Pigmentar.
""")


def image_to_base64(image: Image.Image) -> str:
    temp_path = os.path.join(tempfile.gettempdir(), "soundsight_capture.jpg")
    image.save(temp_path, format="JPEG")

    with open(temp_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def describe_scene(image: Image.Image) -> str:
    image_b64 = image_to_base64(image)

    prompt = """
Descreva a cena da imagem em português do Brasil.
A descrição deve ser objetiva, curta e útil para uma pessoa com deficiência visual.

Informe:
- principais objetos visíveis;
- posição aproximada dos objetos;
- possíveis obstáculos;
- se o caminho parece livre ou bloqueado.

Não invente informações que não estejam visíveis.
Use no máximo 4 frases.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "Não consegui descrever a cena.")


def generate_audio(text: str) -> str:
    audio_path = os.path.join(tempfile.gettempdir(), "soundsight_audio.mp3")
    tts = gTTS(text=text, lang="pt-br")
    tts.save(audio_path)
    return audio_path


st.info("Protótipo acadêmico. Não substitui bengala, cão-guia ou tecnologias assistivas profissionais.")

camera_image = st.camera_input("📷 Capture uma imagem da cena")

if camera_image:
    image = Image.open(camera_image).convert("RGB")
    st.image(image, caption="Imagem capturada", use_container_width=True)

    if st.button("🔊 Descrever cena"):
        with st.spinner("Analisando a cena..."):
            try:
                description = describe_scene(image)

                st.subheader("Descrição da cena")
                st.success(description)

                audio_path = generate_audio(description)
                st.audio(audio_path, format="audio/mp3", autoplay=True)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Não consegui conectar ao Ollama. "
                    "Verifique se o Ollama está aberto no computador e se o modelo llava foi instalado."
                )

            except Exception as e:
                st.error(f"Erro ao descrever a cena: {e}")
