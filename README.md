# 👁️ Olhar Amigo

Assistente de visão inteligente para pessoas com baixa visão e Retinose Pigmentar.

O Olhar Amigo utiliza Inteligência Artificial multimodal para interpretar imagens capturadas pela câmera do celular e transformar o ambiente em descrições sonoras acessíveis.

O objetivo é auxiliar pessoas com deficiência visual na compreensão do ambiente ao seu redor, fornecendo informações sobre obstáculos, objetos, caminhos e elementos importantes da cena.

---

# 📖 Sobre o Projeto

Pessoas com Retinose Pigmentar frequentemente apresentam perda progressiva da visão periférica, resultando em uma condição conhecida como visão em túnel.

Essa limitação dificulta a identificação de obstáculos, objetos e referências espaciais, especialmente em ambientes pouco iluminados.

O Olhar Amigo foi desenvolvido para atuar como um assistente digital capaz de:

* Interpretar cenas capturadas pela câmera.
* Responder perguntas sobre o ambiente.
* Identificar possíveis obstáculos.
* Auxiliar na localização de objetos.
* Converter respostas em áudio acessível.

---

# 🎯 Objetivo

Transformar imagens em informações úteis e acessíveis para aumentar a autonomia e a segurança de pessoas com baixa visão.

---

# 🚀 Funcionalidades

## 📷 Captura do ambiente

O usuário pode utilizar a câmera do celular ou computador para capturar uma imagem do ambiente.

---

## 🚧 Verificação de obstáculos

Pergunta rápida:

```text
Tem obstáculo?
```

O sistema analisa a cena e informa possíveis riscos ou barreiras.

---

## 🚶 Verificação de caminho livre

Pergunta rápida:

```text
O caminho está livre?
```

O sistema verifica se existem objetos que possam dificultar a locomoção.

---

## 🔎 Identificação de objetos próximos

Pergunta rápida:

```text
O que está perto de mim?
```

O sistema informa os principais objetos próximos ao usuário.

---

## 📖 Leitura de textos

Pergunta rápida:

```text
Leia o que aparece.
```

O sistema tenta identificar e interpretar textos presentes na imagem.

---

## 🎙️ Comandos de voz

O usuário pode realizar perguntas utilizando a própria voz.

Exemplos:

```text
O que está à minha frente?
```

```text
Existe alguma cadeira perto?
```

```text
Há algo no chão?
```

```text
Onde está a garrafa?
```

O áudio é transcrito automaticamente e enviado para análise.

---

## 🔊 Resposta por áudio

As respostas geradas pela Inteligência Artificial são convertidas automaticamente em áudio.

Isso permite que o usuário receba as informações sem precisar ler a tela.

---

# 🧠 Tecnologias Utilizadas

## Frontend

* Streamlit

## Processamento de Imagens

* Pillow (PIL)

## Inteligência Artificial

* Groq API
* Llama Vision

## Reconhecimento de Voz

* Whisper Large V3 Turbo

## Conversão Texto → Voz

* gTTS (Google Text-to-Speech)

---

# 🏗️ Arquitetura

```text
Câmera
      ↓
Captura da imagem
      ↓
Groq Vision
      ↓
Interpretação da cena
      ↓
Resposta em linguagem natural
      ↓
gTTS
      ↓
Áudio para o usuário
```

Quando utilizado comando de voz:

```text
Microfone
      ↓
Whisper
      ↓
Transcrição
      ↓
Groq Vision
      ↓
Resposta contextual
      ↓
Áudio
```

---

# ▶️ Execução

```bash
streamlit run app.py
```

---

# 👨‍🏫 Contexto Acadêmico

Este projeto foi desenvolvido como atividade da disciplina de Aprendizado Profundo (Deep Learning).

A proposta utiliza modelos multimodais de visão computacional e linguagem natural para criação de uma tecnologia assistiva voltada para acessibilidade e inclusão digital.

---

# 🔮 Próximos Passos

## Curto Prazo

* Melhorar a leitura de textos.
* Detectar obstáculos com maior precisão.
* Melhorar a descrição espacial dos objetos.
* Implementar captura contínua de imagens.

## Médio Prazo

* Modo de navegação assistida.
* Alertas automáticos de risco.
* Reconhecimento de objetos personalizados.

## Longo Prazo

* Integração com óculos inteligentes.
* Processamento em tempo real.
* Navegação indoor assistida.
* Identificação de pessoas e objetos frequentes.
* Sistema de orientação por áudio espacial.

---

# ⚠️ Aviso Importante

O Olhar Amigo é um protótipo acadêmico.

Não substitui:

* Bengala;
* Cão-guia;
* Tecnologias assistivas certificadas;
* Orientação profissional especializada.

Seu uso deve ser considerado complementar e experimental.

5. Adicionar OCR para leitura de rótulos e textos curtos.
