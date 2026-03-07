# 🇮🇳 DigitalBharat Studio 
**The Bharat-First Content Ecosystem | Tech Force | AI for Bharat Hackathon 2026**

[![Live Prototype](https://img.shields.io/badge/Live_Prototype-Click_Here-4f46e5?style=for-the-badge)](YOUR_WORKING_LINK_HERE)
[![Demo Video](https://img.shields.io/badge/Demo_Video-Watch_Now-FF0000?style=for-the-badge)](YOUR_YOUTUBE_LINK_HERE)

---

## 🎯 Problem Statement
Content creators across diverse regions in India (Tier-2, Tier-3, and rural) struggle with accessibility, personalization, and effective distribution of digital content. Existing tools are fragmented, heavily English-biased, and lack a regional, "Bharat-First" focus. 

## 💡 Solution Overview
**DigitalBharat Studio** is a unified, AI-driven content workflow ecosystem. It integrates ideation, creation, personalization, scheduling, and analytics into a single intelligent platform. Designed specifically for Indian creators, it features deep multilingual support, native voice generation, and cultural localization to bridge the digital divide.

---

## 🧠 Enterprise-Grade Architecture (Multi-Cloud Fallback)
To ensure 100% uptime and cost-efficiency, the platform is built on a highly resilient dual-cloud system:
* **🥇 Primary Engine (AWS):** Utilizes **Amazon Nova Micro** for text/logic and **Amazon Titan Image Generator v2:0** for enterprise-grade visuals.
* **🥈 Fail-Safe Engine (Google/Open Source):** Automatically routes requests to **Google Gemini Pro** and **Pollinations AI** if AWS API limits, network blocks, or entitlement errors occur.
* **🛡️ Security Layer:** Complete API key protection via environment variables (`.env`), keeping $100 AWS Hackathon credits and Google keys strictly confidential.

---

## 🚀 Platform Tools & Features

1. **🚀 AI Content Pipeline:** A 3-step workflow that simplifies complex documents (like govt. schemes), injects regional cultural slangs (e.g., Puneri, Bhojpuri), and auto-formats the text for viral WhatsApp broadcasts.
2. **✍️ AI Script Genius:** Multilingual script generation (Hindi, Marathi, English) featuring AI-driven, high-retention thumbnail hooks and tone control.
3. **🎨 Brand Identity Kit:** Automatically synthesizes channel niches into professional brand identities (HEX color palettes, typography, and brand voice guidelines).
4. **🖼️ AI Visual Studio:** High-conversion thumbnail generation powered by AWS Titan v2:0, explicitly tuned for high-quality, culturally relevant Indian aesthetics.
5. **📅 Smart Content Planner:** AI-powered calendar that predicts optimal cross-platform posting times based on Indian demographic behavior.
6. **📊 Bharat Analytics Hub:** A comprehensive dashboard featuring live AI sentiment analysis of regional audiences and cross-platform performance metrics.
7. **📡 Trend Radar:** Real-time AI detection of hyper-local trending topics and digital momentum to guide content strategy.
8. **🤖 AI Saarthi (Voice Co-Pilot):** A multilingual Voice AI assistant. It is strictly prompted to use native Devanagari scripts for Hindi/Marathi to ensure crystal clear Indian text-to-speech (gTTS) pronunciation.
9. **⚙️ AI System Controls:** A live dashboard to monitor active API routing, multi-cloud status, and system security.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit, Custom CSS
* **Data & Analytics:** Pandas, NumPy, Plotly
* **Primary AI Engine:** AWS Bedrock (Amazon Nova Micro, Amazon Titan v2:0)
* **Fallback AI Engine:** Google Gemini API, Pollinations AI
* **Voice Processing:** SpeechRecognition, gTTS (Google Text-to-Speech)
* **Security & Infrastructure:** Python 3.9+, python-dotenv, boto3

---

## 💻 Local Installation & Setup

To run this prototype locally, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME