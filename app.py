import base64
import os
import tempfile
from io import BytesIO

import streamlit as st
from PIL import Image
from gtts import gTTS
from groq import Groq
from streamlit_mic_recorder import mic_recorder


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="SoundSight",
    page_icon="👁️",
    layout="centered"
)


# =========================
# ESTILO ACESSÍVEL
# =========================

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 20px !important;
    }

    .stApp {
        background: #07111f;
        color: #f8fafc;
    }

    .block-container {
        max-width: 760px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, p, label, span, div {
        color: #f8fafc !important;
    }

    h1 {
        font-size: 2.5rem !important;
        line-height: 1.2;
        margin-bottom: 0.7rem;
    }

    h2, h3 {
        font-size: 1.6rem !important;
        margin-top: 1.4rem;
    }

    .stButton > button {
        width: 100%;
        min-height: 78px;
        font-size: 1.4rem !important;
        font-weight: 800;
        border-radius: 20px;
        border: 4px solid #ffffff;
        background: #facc15;
        color: #111827 !important;
        box-shadow: 0 0 0 5px rgba(250, 204, 21, 0.25);
    }

    .stButton > button:hover {
        background: #fde047;
        border-color: #38bdf8;
        color: #000000 !important;
    }

    .stTextInput input {
        min-height: 68px;
        font-size: 1.25rem !important;
        border-radius: 16px;
        border: 3px solid #38bdf8;
        background: #0f172a;
        color: #ffffff;
    }

    .stCameraInput {
        border: 3px dashed #38bdf8;
        border-radius: 20px;
        padding: 18px;
        background: rgba(56, 189, 248, 0.10);
    }

    .stAlert {
        border-radius: 18px;
        font-size: 1.1rem;
    }

    .main-instruction {
        background: #172554;
        border-left: 8px solid #38bdf8;
        padding: 18px;
        border-radius: 16px;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }

    .danger-box {
        background: #451a03;
        border-left: 8px solid #f97316;
        padding: 18px;
        border-radius: 16px;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }

    .result-box {
        background: #022c22;
        border-left: 8px solid #22c55e;
        padding: 20px;
        border-radius: 16px;
        font-size: 1.25rem;
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .small-note {
        font-size: 1rem;
        color: #cbd5e1 !important;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# CLIENTE GROQ
# =========================

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# =========================
# FUNÇÕES AUXILIARES
# =========================

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
        user_command = "Descreva o ambiente e diga se há obstáculos."

    prompt = f"""
Você é o SoundSight, um assistente de visão para pessoas com baixa visão ou Retinose Pigmentar.

A pessoa pode ter visão em túnel, dificuldade de enxergar à noite e baixa percepção periférica.

A pergunta ou comando da pessoa foi:
"{user_command}"

Analise a imagem e responda em português do Brasil.

Regras:
- Priorize segurança, orientação e bem-estar.
- Diga primeiro se há obstáculo, risco ou caminho livre.
- Depois descreva os principais objetos.
- Informe posição aproximada: à frente, à esquerda, à direita, perto ou longe.
- Use frases curtas.
- Não invente informações.
- Responda como se estivesse falando com alguém caminhando ou procurando algo.
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


# =========================
# INTERFACE
# =========================

st.title("👁️ SoundSight")

st.markdown("""
<div class="main-instruction">
Aponte a câmera para o ambiente. Depois faça uma pergunta por voz ou toque no botão de análise.
O SoundSight irá descrever a cena em áudio.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="danger-box">
Protótipo acadêmico. Use como apoio. Não substitui bengala, cão-guia, acompanhamento humano ou orientação profissional.
</div>
""", unsafe_allow_html=True)


# =========================
# CAPTURA DA IMAGEM
# =========================

st.markdown("## 1. Capturar ambiente")

camera_image = st.camera_input("📷 Toque para abrir a câmera")


# =========================
# COMANDO DE VOZ
# =========================

st.markdown("## 2. Perguntar por voz")

st.markdown("""
<div class="small-note">
Exemplos: “Tem obstáculo?”, “O caminho está livre?”, “O que está na minha frente?”, “Descreva a mesa”.
</div>
""", unsafe_allow_html=True)

audio = mic_recorder(
    start_prompt="🎙️ FALAR PERGUNTA",
    stop_prompt="⏹️ PARAR GRAVAÇÃO",
    just_once=True,
    use_container_width=True
)

manual_command = st.text_input(
    "Ou digite sua pergunta:",
    placeholder="Exemplo: o caminho está livre?"
)


# =========================
# PROCESSAMENTO
# =========================

if camera_image:
    image = Image.open(camera_image).convert("RGB")

    st.markdown("## 3. Imagem capturada")
    st.image(image, caption="Cena capturada pela câmera", use_container_width=True)

    user_command = manual_command.strip()

    if audio and "bytes" in audio:
        with st.spinner("Transcrevendo comando de voz..."):
            try:
                user_command = transcribe_audio(audio["bytes"])
                st.success(f"Comando reconhecido: {user_command}")
            except Exception as e:
                st.error(f"Erro ao transcrever áudio: {e}")

    st.markdown("## 4. Análise sonora")

    if st.button("🔊 DESCREVER O AMBIENTE"):
        with st.spinner("Analisando a cena..."):
            try:
                description = describe_scene(image, user_command)

                st.markdown("### Resposta do SoundSight")
                st.markdown(
                    f"""
                    <div class="result-box">
                    {description}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                audio_path = generate_audio(description)
                st.audio(audio_path, format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Erro ao analisar a cena: {e}")

else:
    st.info("Capture uma imagem para iniciar a análise.")
