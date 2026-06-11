import base64
import os
import tempfile
from io import BytesIO

import streamlit as st
from PIL import Image
from gtts import gTTS
from groq import Groq
from streamlit_mic_recorder import mic_recorder


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


def transcribe_audio(audio_bytes: bytes) -> str:
    audio_path = os.path.join(tempfile.gettempdir(), "comando_voz.wav")

    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=("comando_voz.wav", audio_file.read()),
            model="whisper-large-v3-turbo",
            language="pt"
        )

    return transcription.text


def describe_scene(image: Image.Image, user_command: str = "") -> str:
    image_b64 = image_to_base64(image)

    if not user_command:
        user_command = "Descreva a cena para uma pessoa com deficiência visual."

    prompt = f"""
Você é o SoundSight, um assistente de visão para pessoas com Retinose Pigmentar.

A pessoa fez este comando ou pergunta:
"{user_command}"

Analise a imagem e responda em português do Brasil.

Regras:
- Seja objetivo.
- Use frases curtas.
- Informe objetos importantes, posição aproximada e obstáculos.
- Se houver risco de colisão, avise.
- Não invente informações não visíveis.
- Responda como áudio assistivo, sem enrolação.
- Use no máximo 4 frases.
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
                        }
                    }
                ]
            }
        ],
        temperature=0.2,
        max_completion_tokens=400
    )

    return completion.choices[0].message.content


def generate_audio(text: str) -> str:
    audio_path = os.path.join(tempfile.gettempdir(), "resposta_soundsight.mp3")
    tts = gTTS(text=text, lang="pt-br")
    tts.save(audio_path)
    return audio_path


st.title("👁️ SoundSight")
st.write(
    "Assistente de visão por IA para pessoas com Retinose Pigmentar. "
    "Capture uma imagem, faça uma pergunta por voz e receba uma descrição sonora."
)

st.warning(
    "Protótipo acadêmico. Não substitui bengala, cão-guia ou tecnologias assistivas profissionais."
)

st.subheader("1. Capture a cena")

camera_image = st.camera_input("📷 Capturar imagem pela câmera")

st.subheader("2. Faça um comando de voz")

st.caption("Exemplos: 'O que tem à minha frente?', 'Tem obstáculo?', 'Descreva a mesa.', 'O caminho está livre?'")

audio = mic_recorder(
    start_prompt="🎙️ Iniciar gravação",
    stop_prompt="⏹️ Parar gravação",
    just_once=True,
    use_container_width=True
)

manual_command = st.text_input(
    "Ou digite o comando manualmente:",
    placeholder="Exemplo: o que tem à minha frente?"
)

if camera_image:
    image = Image.open(camera_image).convert("RGB")
    st.image(image, caption="Imagem capturada", use_container_width=True)

    user_command = manual_command.strip()

    if audio and "bytes" in audio:
        with st.spinner("Transcrevendo comando de voz..."):
            try:
                user_command = transcribe_audio(audio["bytes"])
                st.success(f"Comando reconhecido: {user_command}")
            except Exception as e:
                st.error(f"Erro ao transcrever áudio: {e}")

    if st.button("🔊 Analisar cena"):
        with st.spinner("Analisando imagem e comando..."):
            try:
                description = describe_scene(image, user_command)

                st.subheader("Resposta do SoundSight")
                st.success(description)

                audio_path = generate_audio(description)
                st.audio(audio_path, format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Erro ao analisar a cena: {e}")
else:
    st.info("Capture uma imagem para iniciar a análise.")
