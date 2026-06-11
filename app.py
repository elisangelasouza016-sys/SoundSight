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
    page_title="Olhar Amigo",
    page_icon="👁️",
    layout="centered"
)


st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 22px !important;
    }

    .stApp {
        background: #06111f;
        color: #f8fafc;
    }

    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, p, label, span, div {
        color: #f8fafc !important;
    }

    h1 {
        font-size: 2.7rem !important;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }

    h2 {
        font-size: 1.55rem !important;
        margin-top: 1.2rem;
    }

    .subtitle {
        font-size: 1.15rem;
        color: #dbeafe !important;
        margin-bottom: 1rem;
    }

    .notice {
        background: #172554;
        border-left: 10px solid #38bdf8;
        padding: 18px;
        border-radius: 18px;
        font-size: 1.15rem;
        margin-bottom: 20px;
    }

    .warning {
        background: #451a03;
        border-left: 10px solid #f97316;
        padding: 18px;
        border-radius: 18px;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }

    .result-box {
        background: #022c22;
        border-left: 10px solid #22c55e;
        padding: 22px;
        border-radius: 18px;
        font-size: 1.25rem;
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .stButton > button {
        width: 100%;
        min-height: 78px;
        font-size: 1.3rem !important;
        font-weight: 900;
        border-radius: 22px;
        border: 4px solid #ffffff;
        background: #facc15;
        color: #111827 !important;
        box-shadow: 0 0 0 5px rgba(250, 204, 21, 0.25);
        margin-bottom: 8px;
    }

    .stButton > button:hover {
        background: #fde047;
        border-color: #38bdf8;
        color: #000000 !important;
    }

    .stCameraInput {
        border: 3px dashed #38bdf8;
        border-radius: 22px;
        padding: 18px;
        background: rgba(56, 189, 248, 0.10);
    }

    .stTextInput input {
        min-height: 68px;
        font-size: 1.2rem !important;
        border-radius: 16px;
        border: 3px solid #38bdf8;
        background: #0f172a;
        color: #ffffff;
    }

    .small-text {
        font-size: 1rem;
        color: #cbd5e1 !important;
    }
</style>
""", unsafe_allow_html=True)


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


def build_prompt(user_command: str) -> str:
    return f"""
Você é o Olhar Amigo, um assistente de visão para pessoas com baixa visão ou Retinose Pigmentar.

A pessoa pode ter visão em túnel, dificuldade de enxergar à noite e baixa percepção periférica.

Pedido da pessoa:
"{user_command}"

Analise a imagem e responda em português do Brasil.

Regras:
- Priorize segurança, orientação e bem-estar.
- Se houver obstáculo, risco ou caminho bloqueado, diga isso primeiro.
- Informe posição aproximada: à frente, à esquerda, à direita, perto ou longe.
- Use frases curtas.
- Não invente informações.
- Responda como se estivesse ajudando alguém na rotina.
- Use no máximo 4 frases.
"""


def describe_scene(image: Image.Image, user_command: str) -> str:
    image_b64 = image_to_base64(image)
    prompt = build_prompt(user_command)

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
    audio_path = os.path.join(tempfile.gettempdir(), "resposta_olhar_amigo.mp3")
    tts = gTTS(text=text, lang="pt-br")
    tts.save(audio_path)
    return audio_path


def analyze_and_speak(image: Image.Image, command: str):
    with st.spinner("Analisando a cena..."):
        try:
            description = describe_scene(image, command)

            st.markdown("### Resposta do Olhar Amigo")
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


st.title("👁️ Olhar Amigo")

st.markdown(
    """
    <div class="subtitle">
    Assistente de voz para pessoas com baixa visão.
    Aponte a câmera, escolha uma pergunta e ouça a descrição do ambiente.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="notice">
    Use quando precisar entender o que está à sua frente, procurar objetos ou perceber possíveis obstáculos.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="warning">
    Protótipo acadêmico. Use como apoio. Não substitui bengala, cão-guia, acompanhamento humano ou orientação profissional.
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown("## 1. Aponte a câmera")
camera_image = st.camera_input("📷 Tirar foto do ambiente")


if camera_image:
    image = Image.open(camera_image).convert("RGB")

    st.image(image, caption="Imagem capturada", use_container_width=True)

    st.markdown("## 2. Escolha o que deseja saber")

    if st.button("📷 O QUE ESTOU VENDO?"):
        analyze_and_speak(
            image,
            "Descreva a cena geral. Diga o que aparece à minha frente e se há algum obstáculo."
        )

    if st.button("🚧 TEM OBSTÁCULO?"):
        analyze_and_speak(
            image,
            "Verifique se há obstáculos, riscos de tropeço, objetos no caminho ou algo que possa atrapalhar minha passagem."
        )

    if st.button("🚶 O CAMINHO ESTÁ LIVRE?"):
        analyze_and_speak(
            image,
            "Diga se o caminho à minha frente parece livre ou bloqueado. Seja direto."
        )

    if st.button("🔎 O QUE ESTÁ PERTO DE MIM?"):
        analyze_and_speak(
            image,
            "Identifique os objetos mais próximos de mim e diga a posição aproximada deles."
        )

    if st.button("📖 LEIA O QUE APARECE"):
        analyze_and_speak(
            image,
            "Tente identificar e ler textos visíveis na imagem. Se não houver texto claro, diga que não conseguiu ler."
        )

    st.markdown("## 3. Ou faça uma pergunta por voz")

    st.markdown(
        """
        <div class="small-text">
        Exemplos: “Onde está a garrafa?”, “Tem cadeira na frente?”, “Há algo no chão?”
        </div>
        """,
        unsafe_allow_html=True
    )

    audio = mic_recorder(
        start_prompt="🎙️ FALAR PERGUNTA",
        stop_prompt="⏹️ PARAR GRAVAÇÃO",
        just_once=True,
        use_container_width=True
    )

    manual_command = st.text_input(
        "Ou digite sua pergunta:",
        placeholder="Exemplo: há algo no chão?"
    )

    voice_command = ""

    if audio and "bytes" in audio:
        with st.spinner("Entendendo sua pergunta..."):
            try:
                voice_command = transcribe_audio(audio["bytes"])
                st.success(f"Pergunta reconhecida: {voice_command}")
            except Exception as e:
                st.error(f"Erro ao transcrever áudio: {e}")

    final_command = manual_command.strip() or voice_command.strip()

    if final_command:
        if st.button("🔊 RESPONDER MINHA PERGUNTA"):
            analyze_and_speak(image, final_command)

else:
    st.info("Tire uma foto do ambiente para começar.")
