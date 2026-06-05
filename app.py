import base64
import os
import tempfile
from io import BytesIO

import streamlit as st
from PIL import Image
from gtts import gTTS
from groq import Groq


st.set_page_config(
    page_title="SoundSight",
    page_icon="👁️",
    layout="centered"
)



client = Groq(api_key=st.secrets["GROQ_API_KEY"])


def image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def describe_scene(image: Image.Image) -> str:
    image_b64 = image_to_base64(image)

    prompt = """
Descreva a cena da imagem em português do Brasil.

A descrição deve ser curta, objetiva e útil para uma pessoa com deficiência visual.

Informe:
1. principais objetos visíveis;
2. posição aproximada dos objetos;
3. possíveis obstáculos;
4. se o caminho parece livre ou bloqueado.

Não invente informações que não estejam visíveis.
Use no máximo 4 frases.
"""

    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
        max_completion_tokens=300,
    )

    return completion.choices[0].message.content


def generate_audio(text: str) -> str:
    audio_path = os.path.join(tempfile.gettempdir(), "soundsight_audio.mp3")
    tts = gTTS(text=text, lang="pt-br")
    tts.save(audio_path)
    return audio_path


st.title("👁️ SoundSight")
st.write(
    "Assistente de visão por IA para descrição sonora de cenas. "
    "Capture uma imagem pela câmera e ouça uma descrição objetiva do ambiente."
)

st.warning(
    "Protótipo acadêmico. Não substitui bengala, cão-guia ou tecnologias assistivas profissionais."
)

camera_image = st.camera_input("📷 Capturar imagem pela câmera")

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

            except Exception as e:
                st.error(f"Erro ao descrever a cena: {e}")
