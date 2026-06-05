import time
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from src.audio.tts import TTSService
from src.utils.cooldown import AudioCooldown
from src.vision.detector import ObjectDetector

st.set_page_config(
    page_title="SoundSight — Visão Sonora",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --primary: #2563eb; --muted: #64748b; --bg: #f8fafc; --card: #ffffff; }
html, body, [class*="css"] { font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: var(--bg); }
section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: #ffffff !important; }
section[data-testid="stSidebar"] * { color: #0f172a !important; }
.block-container { padding-top: 2rem; }
.main-title { font-size: 2.5rem; font-weight: 800; color: #1e3a8a; line-height: 1.1; margin-bottom: .25rem; }
.subtitle { color: var(--muted); font-size: 1.1rem; margin-bottom: 1.5rem; }
.card { background: var(--card); border: 1px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 8px 28px rgba(15, 23, 42, .06); margin-bottom: 18px; }
.notice { background: #eff6ff; border-left: 5px solid #2563eb; padding: 14px 18px; border-radius: 12px; color: #1e3a8a; }
.big-result { font-size: 1.35rem; font-weight: 700; color: #0f172a; }
.small-muted { color: #64748b; font-size: .95rem; }
.stButton > button { background: #2563eb !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 700 !important; padding: .75rem 1rem !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_detector(confidence: float, only_important: bool):
    return ObjectDetector(confidence_threshold=confidence, only_important=only_important)

@st.cache_resource
def get_tts():
    return TTSService()

if "cooldown" not in st.session_state:
    st.session_state.cooldown = AudioCooldown(seconds=5)

st.sidebar.markdown("## 👁️ SoundSight")
st.sidebar.caption("Câmera + detecção de objetos + feedback sonoro")

confidence = st.sidebar.slider("Confiança mínima", 0.30, 0.95, 0.70, 0.05)
only_important = st.sidebar.checkbox("Priorizar objetos úteis no cotidiano", value=True)
play_audio = st.sidebar.checkbox("Gerar áudio", value=True)
st.sidebar.info("Protótipo acadêmico. Não substitui bengala, cão-guia ou tecnologias assistivas profissionais.")

st.markdown('<div class="main-title">SoundSight — Visão em Tempo Real</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Use a câmera para identificar objetos e ouvir uma descrição simples do ambiente.</div>', unsafe_allow_html=True)
st.markdown('<div class="notice">Fluxo atual: câmera → detecção com YOLOv8 pré-treinado em COCO → tradução dos rótulos → áudio em português.</div>', unsafe_allow_html=True)

col_cam, col_result = st.columns([1.35, 1], gap="large")

with col_cam:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📷 Captura pela câmera")
    st.caption("Aponte a câmera para o ambiente ou objeto e clique para capturar.")
    camera_file = st.camera_input("Capturar imagem")
    st.markdown('</div>', unsafe_allow_html=True)

with col_result:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔊 Resultado sonoro")
    result_placeholder = st.empty()
    audio_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

if camera_file:
    image = Image.open(camera_file).convert("RGB")
    detector = get_detector(confidence, only_important)
    tts = get_tts()

    with st.spinner("Identificando objetos..."):
        started = time.time()
        detections = detector.detect(image)
        annotated = detector.draw_detections(image, detections)
        elapsed = (time.time() - started) * 1000

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Imagem analisada")
        st.image(annotated, caption=f"Tempo de inferência: {elapsed:.0f} ms", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Objetos detectados")
        if detections:
            rows = [{"Objeto": d["label_pt"], "Confiança": f'{d["confidence"]*100:.1f}%'} for d in detections]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            labels = [d["label_pt"] for d in detections]
            sentence = tts.build_sentence(labels)
            st.markdown(f'<div class="big-result">{sentence}</div>', unsafe_allow_html=True)
            if play_audio and st.session_state.cooldown.can_speak(sentence):
                audio_path = tts.save_to_file(sentence, "soundsight_feedback.mp3")
                if audio_path and Path(audio_path).exists():
                    st.audio(audio_path, autoplay=True)
                else:
                    st.warning("Não consegui gerar o áudio neste ambiente. O texto foi exibido acima.")
        else:
            st.warning("Nenhum objeto foi detectado com a confiança mínima configurada.")
            st.caption("Tente melhorar a iluminação, aproximar a câmera ou reduzir a confiança mínima.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Como testar")
    st.write("1. Aponte a câmera para objetos como pessoa, cadeira, copo, garrafa, celular, livro ou notebook.")
    st.write("2. Capture a imagem.")
    st.write("3. O sistema exibirá caixas nos objetos e gerará uma frase em áudio.")
    st.markdown('</div>', unsafe_allow_html=True)
