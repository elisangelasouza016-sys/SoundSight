# SoundSight — Visão Sonora

Protótipo acadêmico de tecnologia assistiva para pessoas com Retinose Pigmentar e deficiências visuais correlatas.

O fluxo principal é:

**câmera → detecção de objetos → descrição textual → feedback sonoro**

## Modelo

Esta versão usa **YOLOv8n pré-treinado no dataset COCO**. Isso permite testar o app sem treinar um modelo do zero.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Na primeira execução, o YOLO baixa automaticamente o arquivo `yolov8n.pt`.

## O que o app faz

- Abre a câmera pelo navegador.
- Captura uma imagem do ambiente.
- Detecta objetos comuns.
- Desenha caixas nos objetos identificados.
- Traduz os rótulos para português.
- Gera áudio com uma frase simples, como: `Estou vendo uma pessoa, uma cadeira e uma garrafa.`

## Limitações

- Este MVP usa captura por imagem via `st.camera_input`, não vídeo contínuo.
- Não substitui bengala, cão-guia ou tecnologia assistiva profissional.
- Pode falhar em baixa luminosidade.
- Pode não reconhecer objetos domésticos muito específicos.
- O áudio pode depender do ambiente de execução.

## Próximas evoluções

1. Adicionar vídeo contínuo com `streamlit-webrtc`.
2. Treinar um modelo personalizado com objetos do ambiente do usuário.
3. Exportar para ONNX/TFLite.
4. Criar versão mobile.
5. Adicionar OCR para leitura de rótulos e textos curtos.
