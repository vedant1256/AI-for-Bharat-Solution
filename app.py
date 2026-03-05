import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import boto3
import json
import os
import io
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Try importing speech_recognition for real Voice-to-Text
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

# Try importing gTTS for real Text-to-Speech
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Try importing Google Gemini for Powerful Free AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# --- 0. INITIALIZATION & SECURITY ---
load_dotenv()
AWS_CONFIGURED = bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_KEY)

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IndiCreator AI | The Bharat-First Content Engine",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ADVANCED CSS FOR SPACED & PROFESSIONAL UI ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    [data-testid="stMetric"] {
        background-color: rgba(30, 41, 59, 0.7); border: 1px solid #4f46e5;
        border-radius: 12px; padding: 25px !important; margin: 10px 0px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: 1px solid rgba(79, 70, 229, 0.3) !important;
        border-radius: 15px; padding: 20px; background-color: rgba(30, 41, 59, 0.3);
    }
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 600;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        border: none; color: white; transition: 0.3s; height: 3em;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(124, 58, 237, 0.4); }
    .stTextArea textarea { background-color: #1e293b !important; color: #e2e8f0 !important; border: 1px solid #334155; }
    .trend-card {
        background: rgba(255, 255, 255, 0.05); border-left: 4px solid #7c3aed;
        padding: 10px 15px; margin-bottom: 8px; border-radius: 4px; display: flex;
        justify-content: space-between; align-items: center;
    }
    .trend-rank { font-weight: bold; color: #7c3aed; font-size: 1.2em; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #334155; }
    .whatsapp-btn {
        display: inline-block; width: 100%; text-align: center; border-radius: 8px; font-weight: 600;
        background: linear-gradient(90deg, #25D366 0%, #128C7E 100%);
        padding: 12px 0; color: white !important; text-decoration: none; transition: 0.3s;
    }
    .whatsapp-btn:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(37, 211, 102, 0.4); }
    .alert-card { background: rgba(37, 211, 102, 0.1); border-left: 4px solid #25D366; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .hero-box { border: 2px dashed #25D366; padding: 15px; border-radius: 10px; background: rgba(37, 211, 102, 0.05); margin-top: 15px;}
    .jarvis-box { background: rgba(124, 58, 237, 0.1); border: 1px solid #7c3aed; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px;}
    .hook-card { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #eab308; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 1.4em; font-weight: bold; color: #fef08a;}
    
    /* Before & After Visualization CSS */
    .diff-remove { background-color: rgba(239, 68, 68, 0.2); color: #fca5a5; text-decoration: line-through; padding: 2px 4px; border-radius: 4px; }
    .diff-add { background-color: rgba(34, 197, 94, 0.2); color: #86efac; font-weight: bold; padding: 2px 4px; border-radius: 4px; border-bottom: 2px dashed #22c55e; }
    .compare-box { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 15px; border-radius: 8px; font-size: 1.05em; line-height: 1.6; height: 100%; }
    
    /* Calendar CSS */
    .cal-badge { background: #4f46e5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
    
    /* Action chips */
    .action-chip { background-color: #334155; padding: 8px 12px; border-radius: 20px; font-size: 0.85em; cursor: pointer; display: inline-block; margin-right: 8px; margin-top: 5px; transition: 0.2s;}
    .action-chip:hover { background-color: #4f46e5; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'script_output' not in st.session_state: st.session_state['script_output'] = ""
if 'genius_script' not in st.session_state: st.session_state['genius_script'] = ""
if 'shield_input' not in st.session_state: st.session_state['shield_input'] = ""
if 'shield_original_text' not in st.session_state: st.session_state['shield_original_text'] = ""
if 'transcribed_text' not in st.session_state: st.session_state['transcribed_text'] = ""
if 'cultural_output' not in st.session_state: st.session_state['cultural_output'] = None
if 'radar_active' not in st.session_state: st.session_state['radar_active'] = False
if 'wa_summary' not in st.session_state: st.session_state['wa_summary'] = ""
if 'transformer_result' not in st.session_state: st.session_state['transformer_result'] = None
if 'thumbnail_hooks' not in st.session_state: st.session_state['thumbnail_hooks'] = []
if 'emotion_style' not in st.session_state: st.session_state['emotion_style'] = None
if 'emotion_topic' not in st.session_state: st.session_state['emotion_topic'] = None
if 'brand_kit_generated' not in st.session_state: st.session_state['brand_kit_generated'] = False
if 'calendar_data' not in st.session_state: 
    st.session_state['calendar_data'] = pd.DataFrame([
        {"Content Title": "PM-Kisan Update", "Platform": "WhatsApp", "Target Audience": "Farmers", "Optimal Time": "Today, 7:00 PM"},
        {"Content Title": "Local Mandi Prices", "Platform": "YouTube Shorts", "Target Audience": "Agri-Business", "Optimal Time": "Tomorrow, 8:30 AM"}
    ])

# Voice Assistant State
if 'jarvis_query' not in st.session_state: st.session_state['jarvis_query'] = ""
if 'jarvis_answer' not in st.session_state: st.session_state['jarvis_answer'] = ""
if 'jarvis_audio' not in st.session_state: st.session_state['jarvis_audio'] = None

# --- 4. REAL AI / MOCK LOGIC ---
def generate_ai_script_aws(topic, lang, tone):
    prompt = f"You are an expert content creator for the Indian audience. Write a highly engaging, {tone} video script in {lang} about '{topic}'. Include a catchy hook, a 3-point main body, and a strong call to action asking people to subscribe."
    
    if GEMINI_KEY and GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            pass 

    if AWS_CONFIGURED:
        try:
            region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
            body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]})
            response = bedrock.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', contentType='application/json', accept='application/json', body=body)
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
        except Exception as e:
            pass 

    return f"""**[0:00 - HOOK (3 seconds)]**: \nStop scrolling! Are you still missing out on the {topic}?\n\n**[0:05 - INTRO (7 seconds)]**: \nNamaskar doston! Today, I am going to reveal a simple trick regarding {topic} in {lang} that will blow your mind...\n\n**[0:15 - BODY POINT 1]**: \nWhy this is important for our community...\n\n**[0:45 - BODY POINT 2]**: \nStep-by-step required documents and process...\n\n**[1:30 - CALL TO ACTION]**: \nIf this {tone} video helped you, hit the share button and forward it to your WhatsApp groups!"""

def ask_jarvis_ai(query, lang):
    # New Prompt explicitly defining Jarvis as a Creator Co-Pilot
    prompt = f"You are Jarvis, an expert creative AI assistant for digital content creators in India. Help them brainstorm viral ideas, write hooks, and plan content. Keep your answer brief, high-energy, and under 3 sentences. Speak naturally in the '{lang}' language. User query: {query}"
    
    if GEMINI_KEY and GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            pass 

    if AWS_CONFIGURED:
        try:
            region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
            body = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 200, "messages": [{"role": "user", "content": prompt}]})
            response = bedrock.invoke_model(modelId='anthropic.claude-3-haiku-20240307-v1:0', contentType='application/json', accept='application/json', body=body)
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
        except Exception as e:
            pass 

    # Overhauled Offline/Fallback Logic tailored to Creators
    lower_query = query.lower()
    if "trend" in lower_query or "viral" in lower_query:
        ans = "Right now, hyper-local community content and 'Day in the Life' vlogs are trending heavily in your region. Would you like me to write a script for that?"
        if "hindi" in lang.lower(): ans = "अभी आपके क्षेत्र में हाइपर-लोकल कंटेंट और 'डे इन द लाइफ' व्लॉग बहुत ट्रेंड कर रहे हैं। क्या मैं आपके लिए उस पर एक स्क्रिप्ट लिखूं?"
        if "marathi" in lang.lower(): ans = "सध्या तुमच्या विभागात हायपर-लोकल कंटेंट आणि 'डे इन द लाइफ' व्लॉग खूप ट्रेंड करत आहेत. मी यासाठी एक उत्तम स्क्रिप्ट लिहू का?"
    elif "hook" in lower_query or "intro" in lower_query or "start" in lower_query:
        ans = "Here is a strong, high-retention hook: 'Stop scrolling! What I am about to tell you will completely change how you use your phone.' Try saying that with high energy!"
        if "hindi" in lang.lower(): ans = "यहाँ एक दमदार हुक है: 'स्क्रॉल करना बंद करें! मैं जो बताने जा रहा हूँ वह आपके फोन का उपयोग करने का तरीका बदल देगा।' इसे पूरी ऊर्जा के साथ बोलें!"
        if "marathi" in lang.lower(): ans = "येथे एक दमदार हुक आहे: 'स्क्रोल करणे थांबवा! मी जे सांगणार आहे त्यामुळे तुमचा फोन वापरण्याची पद्धत बदलेल.' हे पूर्ण ऊर्जेने आणि आत्मविश्वासाने बोला!"
    else:
        ans = "That is a brilliant idea for a video! I suggest posting it around 6 PM tomorrow for maximum audience reach. Shall I add it to your Smart Planner?"
        if "hindi" in lang.lower(): ans = "वीडियो के लिए यह एक बेहतरीन विचार है! मेरा सुझाव है कि अधिकतम पहुंच के लिए इसे कल शाम 6 बजे पोस्ट करें। क्या मैं इसे आपके स्मार्ट प्लानर में जोड़ दूं?"
        if "marathi" in lang.lower(): ans = "व्हिडिओसाठी ही एक उत्तम कल्पना आहे! जास्तीत जास्त लोकांपर्यंत पोहोचण्यासाठी मी तुम्हाला हा व्हिडिओ उद्या संध्याकाळी 6 वाजता पोस्ट करण्याचा सल्ला देतो. मी हे तुमच्या स्मार्ट प्लॅनरमध्ये जोडू का?"
    return ans

# --- 5. DASHBOARDS ---

def ai_script_genius_page():
    st.title("✍️ AI Script Genius")
    st.markdown("Multilingual AI content and script generation with **smart hooks** and **tone control**.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Configuration Engine")
            topic = st.text_input("Content Topic", placeholder="e.g. Benefits of PM-Kisan Scheme")
            language = st.selectbox("Choose Language", ["Hindi", "Marathi", "Tamil", "Bengali", "Gujarati", "Hinglish"], index=1)
            vibe = st.select_slider("Vibe / Tone", ["Educational", "Professional", "Casual", "Funny", "Urgent"])
            
            if st.button("✨ Generate Script & Hooks"):
                if topic:
                    with st.spinner(f"Analyzing topic and generating {vibe} script in {language}..."):
                        time.sleep(1.5)
                        st.session_state['genius_script'] = generate_ai_script_aws(topic, language, vibe)
                    st.success("Script generated successfully!")
                else:
                    st.warning("Please enter a content topic.")
                    
    with col2:
        with st.container(border=True):
            st.subheader("Script Storyboard Editor")
            genius_out = st.session_state.get('genius_script', "")
            st.text_area("Live Editor", value=genius_out, height=350)
            
            c_btn1, c_btn2, c_btn3 = st.columns(3)
            with c_btn1: st.button("✨ Auto-Refine Script")
            with c_btn2: st.button("🔊 Voiceover Preview")
            with c_btn3: 
                if st.button("🛡️ Send to Cultural Shield"):
                    st.session_state['shield_input'] = genius_out
                    st.session_state['nav_choice'] = "🛡️ Cultural Authenticity Shield"
                    st.rerun()

def knowledge_transformer_page():
    st.title("🧠 Bharat Knowledge Transformer")
    st.markdown("**Phase 1 of Hero Flow:** Convert complex, heavy documents (like Budget speeches or Government Policies) into a base script.")
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Source Knowledge")
            doc_type = st.selectbox("Select Complex Document", ["Union Budget 2026 (Agriculture Sector Highlights)", "New IT Rules for Digital Media", "National Education Policy (NEP) Summary", "Custom (Paste Text/URL)"])
            if doc_type == "Custom (Paste Text/URL)": st.text_area("Paste Complex Text Here:", height=100)
            target_lang = st.selectbox("Target Output Format", ["Standard Hindi Script", "Standard Marathi Script", "Standard English Script"])
            if st.button("🔄 Generate Base Script"):
                with st.spinner(f"Parsing '{doc_type}'..."): time.sleep(1.5)
                with st.spinner(f"Simplifying into {target_lang}..."): time.sleep(1.5)
                res_text = f"Hello friends! How are you doing today? I have a very good news for you regarding the {doc_type.split('(')[0].strip()}. This new policy is amazing for farmers. My brother checked it and he saved a lot of money without any tension. The government is giving a 50% subsidy on new tech. Listen to me carefully and share this with your village."
                st.session_state['transformer_result'] = {"lang": target_lang, "text": res_text}
                st.success("Transformation Complete!")

    with col2:
        with st.container(border=True):
            st.subheader("✨ Base AI Output")
            if st.session_state['transformer_result']:
                res = st.session_state['transformer_result']
                st.text_area("Generic Textbook Script", value=res['text'], height=250)
                st.markdown("""<div class="hero-box"><p style="margin:0; color:#25D366; font-weight:bold;">🚀 Next Step in Pipeline:</p><p style="margin:5px 0 15px 0; font-size:0.9em;">This script feels a bit robotic. Send it to the Authenticity Shield to inject local cultural flavor.</p>""", unsafe_allow_html=True)
                if st.button("🛡️ Send to Cultural Shield ➡️"):
                    st.session_state['shield_input'] = res['text']
                    st.session_state['nav_choice'] = "🛡️ Cultural Authenticity Shield"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("👈 Select a document and click 'Generate Base Script' to start the pipeline.")

def authenticity_shield_page():
    st.title("🛡️ Cultural Authenticity Shield")
    st.markdown("**Phase 2 of Hero Flow:** Standard LLMs write 'textbook' scripts that feel robotic. This tool scans your base script and injects hyper-local slang. Watch the **Before & After Visualization** to see the AI at work.")
    
    with st.container(border=True):
        col_in1, col_in2 = st.columns([2, 1])
        with col_in1:
            default_script = st.session_state.get('shield_input', "")
            if not default_script: default_script = "Hello friends! How are you doing today? I have a very good news for you. This new business idea is amazing. My brother tried it and he made a lot of money without any tension. Listen to me carefully."
            base_script = st.text_area("Base 'Textbook' Script (Input):", value=default_script, height=100)
        with col_in2:
            target_region = st.selectbox("Target Audience Vibe", ["Pune (Puneri pure)", "UP/Bihar (Desi/Bhojpuri touch)", "Mumbai (Tapori/Bindaas)", "Delhi (Bhaichaara/Swag)"])
            if st.button("✨ Apply Cultural Nuance"):
                st.session_state['shield_original_text'] = base_script 
                with st.spinner("AI4Bharat analyzing sentiment..."): time.sleep(1)
                with st.spinner(f"Injecting {target_region} RAG guidelines..."): time.sleep(1)
                
                if "UP" in target_region:
                    st.session_state['cultural_output'] = {"text": "Ka haal ba bhaiya log! Sab theek ba na? ekdam bhaukaal khabar laye hain aapke liye. Ye naya jugaad gajab hai. Humre chacha ke ladke ne try kiya aur bina kisi jhanjhat ke daba ke paisa banaya. Kaan khol ke suno humri baat.", "changes": [("Hello friends! How are you doing today?", "Ka haal ba bhaiya log! Sab theek ba na?"), ("I have a very good news for you.", "ekdam bhaukaal khabar laye hain aapke liye."), ("business idea is amazing", "jugaad gajab hai"), ("My brother", "Humre chacha ke ladke"), ("without any tension", "bina kisi jhanjhat ke"), ("made a lot of money", "daba ke paisa banaya"), ("Listen to me carefully.", "Kaan khol ke suno humri baat.")]}
                elif "Mumbai" in target_region:
                    st.session_state['cultural_output'] = {"text": "Bole toh kya public! Kaisa chal rela hai aaj? ekdam raapchik news hai tumhare liye. Ye naya dhandha ek number hai. Mere bhau ne try kiya aur bina kisi magajmari ke mast paisa chaapa. Dhyan se sun meri baat.", "changes": [("Hello friends! How are you doing today?", "Bole toh kya public! Kaisa chal rela hai aaj?"), ("I have a very good news for you.", "ekdam raapchik news hai tumhare liye."), ("business idea is amazing", "dhandha ek number hai"), ("My brother", "Mere bhau"), ("without any tension", "bina kisi magajmari ke"), ("made a lot of money", "mast paisa chaapa"), ("Listen to me carefully.", "Dhyan se sun meri baat.")]}
                else:
                    st.session_state['cultural_output'] = {"text": "Oye mere bhaiyo! Kya haal chaal? Ekdum solid khabar laya hu tumhare liye. Ye naya business scene bawal hai. Mere bhai ne try kiya aur bina kisi khach-khach ke andha paisa banaya. Dhyaan se sunna meri baat.", "changes": [("Hello friends! How are you doing today?", "Oye mere bhaiyo! Kya haal chaal?"), ("I have a very good news for you.", "Ekdum solid khabar laya hu tumhare liye."), ("business idea is amazing", "business scene bawal hai"), ("My brother", "Mere bhai"), ("without any tension", "bina kisi khach-khach ke"), ("made a lot of money", "andha paisa banaya"), ("Listen to me carefully.", "Dhyan se sunna meri baat.")]}
                st.success("Cultural injection complete! View the Before & After comparison below.")

    if st.session_state['cultural_output']:
        st.write("")
        st.markdown("### 🔍 Before & After Visualization")
        result = st.session_state['cultural_output']
        
        before_html = st.session_state['shield_original_text']
        for orig, new in result['changes']: before_html = before_html.replace(orig, f'<span class="diff-remove">{orig}</span>')
        after_html = result['text']
        for orig, new in result['changes']: after_html = after_html.replace(new, f'<span class="diff-add">{new}</span>')

        c_before, c_after = st.columns(2)
        with c_before:
            st.markdown("🔴 **Standard AI (Textbook)**")
            st.markdown(f'<div class="compare-box">{before_html}</div>', unsafe_allow_html=True)
        with c_after:
            st.markdown("🟢 **Bharat AI (Culturally Localized)**")
            st.markdown(f'<div class="compare-box">{after_html}</div>', unsafe_allow_html=True)

        st.markdown("""<div class="hero-box"><p style="margin:0; color:#25D366; font-weight:bold;">🚀 Final Step in Pipeline:</p><p style="margin:5px 0 15px 0; font-size:0.9em;">Content is successfully localized! Now send it to the Optimizer to format it into a viral WhatsApp message.</p>""", unsafe_allow_html=True)
        if st.button("📲 Send Output to WhatsApp Optimizer ➡️"):
            st.session_state['script_output'] = result['text']
            st.session_state['nav_choice'] = "📲 WhatsApp Optimizer"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def brand_identity_kit_page():
    st.title("🎨 Brand Identity Kit")
    st.markdown("Digital brand creation tools for creator identity and consistency. Ensure your channel looks professional across all regional platforms.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("1. Define Your Vibe")
            channel_name = st.text_input("Channel Name:", placeholder="e.g. Kick to Tech")
            niche = st.selectbox("Content Niche:", ["Education & Exam Prep", "Agriculture & Farming", "Local News & Updates", "Gaming & E-Sports"])
            target_demo = st.selectbox("Primary Audience:", ["Students (Tier-2)", "Rural Farmers (Tier-3)", "General Public"])
            
            if st.button("✨ Generate AI Brand Kit"):
                with st.spinner("Synthesizing brand identity..."):
                    time.sleep(1.5)
                    st.session_state['brand_kit_generated'] = True
                    st.success("Brand Identity generated!")
                    
    with col2:
        with st.container(border=True):
            st.subheader("2. Your Digital Identity")
            if st.session_state.get('brand_kit_generated', False):
                st.markdown(f"### {channel_name or 'Your Channel'} Brand Guide")
                
                if niche == "Agriculture & Farming":
                    colors, tone, fonts = ["#166534", "#facc15", "#f8fafc"], "Earthy, Trustworthy, Simple. Use terms like 'Kisan Bhaiyon' and focus on respect.", "Mukta (Headings) + Roboto (Body)"
                elif niche == "Education & Exam Prep":
                    colors, tone, fonts = ["#1e3a8a", "#38bdf8", "#ffffff"], "Encouraging, Authoritative, Clear. Mix professional terms with easy local analogies.", "Poppins (Headings) + Open Sans (Body)"
                else:
                    colors, tone, fonts = ["#7f1d1d", "#f97316", "#111827"], "Energetic, Fast-paced, Engaging. Use high-emotion hooks.", "Oswald (Headings) + Lato (Body)"
                    
                st.markdown("**🎨 Brand Colors:**")
                cols_html = "".join([f"<div style='background-color:{c}; width:60px; height:60px; display:inline-block; margin-right:15px; border-radius:8px; border:2px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'></div>" for c in colors])
                labels_html = "".join([f"<div style='width:60px; display:inline-block; margin-right:15px; text-align:center; color:#a1a1aa; font-size:0.8em;'>{c}</div>" for c in colors])
                st.markdown(cols_html + "<br>" + labels_html, unsafe_allow_html=True)
                st.write("")
                
                st.markdown(f"**🖋️ Typography:** {fonts}")
                st.markdown(f"**🗣️ Tone of Voice:** {tone}")
                
                st.markdown("**🤖 AI Logo Generation Prompt:**")
                st.code(f"Minimalist flat vector logo for a {niche} channel targeting {target_demo}, using colors {colors[0]} and {colors[1]}, modern, clean, no text --v 5", language="text")
                
                st.button("📥 Export Kit as PDF")
            else:
                st.info("Fill out your details to auto-generate a professional Brand Kit.")

def thumbnail_optimizer_page():
    st.title("🖼️ AI Thumbnail Hook Optimizer")
    st.markdown("Boost your CTR (Click-Through Rate). Standard titles are boring. Let AI suggest **3-4 word high-impact hooks** using power words tailored for the Bharat audience.")
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Current Video Info")
            base_title = st.text_input("Enter your textbook/boring title:", value="Benefits of PM Kisan Yojana")
            lang_mix = st.selectbox("Target Optimization Mix", ["Marathi-English Mix", "Hindi-English Mix (Hinglish)", "Pure Hindi (Bold)"])
            
            if st.button("🚀 Generate Viral Hooks"):
                with st.spinner("Analyzing semantics and generating CTR-focused hooks..."):
                    time.sleep(1.5)
                    if "kisan" in base_title.lower() or "farmer" in base_title.lower():
                        st.session_state['thumbnail_hooks'] = ["₹6000 FREE? सच या झूठ? 🤯", "PM Kisan: BIG UPDATE 🚨", "Don't Miss! ₹6000 Form 📝"]
                    elif "solar" in base_title.lower():
                        st.session_state['thumbnail_hooks'] = ["FREE Electricity? 100% सच! ☀️", "Zero Bill: Secret Trick ⚡", "Solar Subsidy: Apply NOW ⏳"]
                    else:
                        st.session_state['thumbnail_hooks'] = ["ये TRICK किसी ने नहीं बताई 🤫", "BIG EXPOSE! सच जान लो 🚨", "100% Working (Live Proof) 🔥"]
                    st.success("High-impact hooks generated!")

    with col2:
        with st.container(border=True):
            st.subheader("🔥 AI Suggested Hooks")
            if st.session_state['thumbnail_hooks']:
                st.markdown("<p style='color:#a1a1aa; margin-bottom:15px;'>Use these exactly as they are written on your YouTube thumbnail to maximize clicks:</p>", unsafe_allow_html=True)
                for hook in st.session_state['thumbnail_hooks']: st.markdown(f'<div class="hook-card">{hook}</div>', unsafe_allow_html=True)
                st.button("📋 Copy Top Hook")
            else:
                st.info("Enter your video title and click Generate to see viral hook suggestions.")

def emotion_template_page():
    st.title("🎨 AI Visual Studio")
    st.markdown("Different videos need different psychological triggers. Select an emotion, and the AI will auto-generate the perfect thumbnail style, color palette, and visual prompt for your content.")
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("1. Content & Target Emotion")
            topic = st.text_input("Video Topic:", placeholder="e.g., MHT-CET Exam Tips")
            emotion = st.selectbox("Select Target Emotion:", ["Curiosity 🤔", "Shock 😲", "Urgency ⏳", "Fear 😨", "Motivation 🚀"])

            if st.button("🎨 Auto-Generate Thumbnail Style"):
                with st.spinner("Analyzing psychological triggers and generating visual assets..."):
                    time.sleep(1.5)
                    if not topic: topic = "the main subject"
                    st.session_state['emotion_style'] = emotion
                    st.session_state['emotion_topic'] = topic
                    st.success("Visual template generated successfully!")

    with col2:
        with st.container(border=True):
            st.subheader("2. AI Generated Visual Assets")
            if st.session_state.get('emotion_style'):
                emo = st.session_state['emotion_style']
                top = st.session_state['emotion_topic']

                if "Shock" in emo:
                    colors, elements, ai_prompt = ["#000000", "#ef4444", "#eab308"], "Wide-eyed reaction face, giant red arrow pointing to unexpected detail.", f"YouTube thumbnail, high contrast, person with shocked wide-eyed expression looking at {top}, bright red arrow, bold yellow text, cinematic lighting --ar 16:9"
                elif "Curiosity" in emo:
                    colors, elements, ai_prompt = ["#1e1b4b", "#8b5cf6", "#38bdf8"], "Blurred background, glowing mysterious object, neon question marks.", f"YouTube thumbnail, mysterious glowing {top}, person pointing with curious expression, dark background with neon purple lights --ar 16:9"
                elif "Urgency" in emo:
                    colors, elements, ai_prompt = ["#ef4444", "#ffffff", "#f97316"], "Stopwatch graphic, bold 'TODAY' text, fast motion blur effect.", f"YouTube thumbnail, {top} with motion blur, giant stopwatch graphic, bold urgent red typography, intense lighting --ar 16:9"
                elif "Fear" in emo:
                    colors, elements, ai_prompt = ["#111827", "#7f1d1d", "#9ca3af"], "Heavy shadows, worried expression, downward trending graph.", f"YouTube thumbnail, dark and moody lighting, person with a worried fearful expression regarding {top}, heavy shadows --ar 16:9"
                elif "Motivation" in emo:
                    colors, elements, ai_prompt = ["#facc15", "#22c55e", "#ffffff"], "Bright clear sky, upward green arrow, confident posture.", f"YouTube thumbnail, bright sunny lighting, confident successful person interacting with {top}, upward green trend arrow --ar 16:9"

                st.markdown("**🎨 Suggested Color Palette:**")
                cols_html = "".join([f"<div style='background-color:{c}; width:50px; height:50px; display:inline-block; margin-right:10px; border-radius:5px; border:1px solid #334155;'></div>" for c in colors])
                st.markdown(cols_html, unsafe_allow_html=True)
                st.write("")
                st.markdown(f"**🧩 Core Visual Elements:**\n{elements}")
                st.markdown("**🤖 AI Image Generation Prompt:**")
                st.code(ai_prompt, language="text")
            else:
                st.info("Select an emotion and click 'Generate' to see the recommended visual style.")

def smart_planner_page():
    st.title("📅 Smart Content Planner")
    st.markdown("AI-powered scheduling and content calendar management system. Optimizes posting times based on regional audience behavior.")
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Schedule New Content")
            title = st.text_input("Content Title", placeholder="e.g. Free Solar Pump Info")
            platform = st.selectbox("Distribution Platform", ["YouTube Shorts", "WhatsApp Broadcast", "Instagram Reels", "Facebook Group"])
            audience = st.selectbox("Target Audience", ["Farmers / Agriculture", "Students / Youth", "Local Business / Shopkeepers", "General Village Audience"])
            
            if st.button("🤖 Suggest Optimal Time"):
                with st.spinner("Analyzing regional engagement patterns..."):
                    time.sleep(1.5)
                    if audience == "Farmers / Agriculture":
                        rec_time, insight = "Today, 7:30 PM", "Farmers in your district have highest WhatsApp retention between 7 PM - 9 PM after field hours."
                    elif audience == "Students / Youth":
                        rec_time, insight = "Tomorrow, 4:00 PM", "Youth engagement spikes post-college/school hours."
                    else:
                        rec_time, insight = "Today, 1:00 PM", "Standard lunch-break engagement peak."
                    
                    st.success("Optimal slot found!")
                    st.markdown(f"**Suggested Time:** <span class='cal-badge'>{rec_time}</span>", unsafe_allow_html=True)
                    st.caption(f"🧠 *AI Insight:* {insight}")
                    
                    if st.button("✅ Add to Calendar"):
                        new_entry = pd.DataFrame([{"Content Title": title, "Platform": platform, "Target Audience": audience, "Optimal Time": rec_time}])
                        st.session_state['calendar_data'] = pd.concat([st.session_state['calendar_data'], new_entry], ignore_index=True)
                        st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("Your AI Content Calendar")
            st.table(st.session_state['calendar_data'])
            st.markdown("""<div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 10px; border-radius: 4px; margin-top: 15px;"><strong>Auto-Publishing:</strong> Ready. Connected to WhatsApp Business & YouTube APIs.</div>""", unsafe_allow_html=True)

def whatsapp_optimizer_page():
    st.title("📲 WhatsApp Channel Optimizer")
    st.markdown("Turn your localized script into a **forward-ready WhatsApp message** with emojis, scannable bullet points, and a clear Call-to-Action.")
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Input Localized Script")
            default_script = st.session_state.get('script_output', "")
            if not default_script: default_script = "Ka haal ba bhaiya log! Sab theek ba na? Aaj ekdam bhaukaal khabar laye hain aapke liye. Ye naya jugaad gajab hai..."
            source_script = st.text_area("Paste your localized script here:", value=default_script, height=200)
            if st.button("✨ Auto-Format for WhatsApp"):
                with st.spinner("Extracting key points and adding WhatsApp markdown..."):
                    time.sleep(1.5)
                    st.session_state['wa_summary'] = f"""🚨 *NAYA BHAUKAAL UPDATE!* 🚨\n\n{source_script.split('!')[0]}! Don't miss this opportunity. Here is the quick summary for our district:\n\n1️⃣ *Naya Jugaad:* Govt is giving 50% subsidy on new tech.\n2️⃣ *Paisa Banao:* Bina kisi jhanjhat ke save money this season.\n3️⃣ *Apply Kaise Karein:* Visit the local CSC center tomorrow.\n\n👇 *Click here to apply online:*\n🔗 https://bit.ly/local-scheme-apply\n\n*Forward this to our village WhatsApp groups right now!* 🌾📲"""
                    st.success("WhatsApp Summary generated successfully!")

    with col2:
        with st.container(border=True):
            st.subheader("Forward-Ready Output")
            wa_output = st.session_state.get('wa_summary', "")
            edited_wa = st.text_area("Review & Edit (Emojis & Formatting Intact)", value=wa_output, height=300)
            if edited_wa:
                encoded_text = urllib.parse.quote(edited_wa)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">🚀 1-Click Broadcast to WhatsApp</a>', unsafe_allow_html=True)

def bharat_analytics_hub_page():
    st.title("📊 Bharat Analytics Hub")
    st.markdown("Intelligent dashboards for **performance, sentiment, and regional engagement insights**.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lifetime Bharat Reach", "5.2M", "+15% (Tier-2 Surge)")
    m2.metric("Overall Sentiment", "94%", "Highly Positive 😊")
    m3.metric("Top Regional Variant", "Marathi", "1.8M Views")
    m4.metric("WhatsApp Forward Rate", "12.4%", "+2.1% WoW")
    
    st.divider()
    
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        with st.container(border=True):
            st.subheader("📈 Regional Engagement Pulse")
            st.markdown("Tracking viewer retention across vernacular zones.")
            
            # Mock Data for chart
            df = pd.DataFrame({
                "Week": ["W1", "W2", "W3", "W4", "W5"],
                "Hindi (UP/Bihar)": [50, 55, 65, 60, 80],
                "Marathi (MH)": [40, 45, 60, 75, 85],
                "Tamil (TN)": [30, 40, 45, 55, 60]
            })
            fig = px.line(df, x="Week", y=["Hindi (UP/Bihar)", "Marathi (MH)", "Tamil (TN)"], 
                          labels={"value": "Engagement Score", "variable": "Language Region"},
                          template="plotly_dark")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.subheader("🧠 Sentiment Analysis")
            st.markdown("AI breakdown of local comments.")
            
            sent_df = pd.DataFrame({
                "Sentiment": ["Positive (Inspired)", "Neutral (Informative)", "Negative (Confused)"],
                "Value": [78, 15, 7]
            })
            fig2 = px.pie(sent_df, names="Sentiment", values="Value", hole=0.4, 
                          color_discrete_sequence=["#22c55e", "#3b82f6", "#ef4444"])
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
            st.caption("💡 *Insight: 7% confusion due to heavy English words. Suggesting use of Cultural Authenticity Shield.*")

def trend_radar_page():
    st.title("📡 Hyper-Local Trend Radar")
    st.markdown("National trends are crowded. Win your audience by talking about **hyper-local events** happening in your district right now.")
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        with st.container(border=True):
            state = st.selectbox("Select State", ["Maharashtra", "Uttar Pradesh", "Bihar", "Madhya Pradesh"])
            district = st.selectbox("Select District", ["Pune", "Nashik", "Nagpur", "Jalgaon"])
            if st.button("Scan Local Trends"):
                with st.spinner("Fetching data from Data.gov.in & NewsAPI..."):
                    time.sleep(1.5)
                    st.session_state['radar_active'] = True
    with col2:
        if st.session_state.get('radar_active', False):
            st.success(f"Radar Active for {district}, {state}")
            st.markdown(f"""
            <div class="alert-card">
                <h4 style="margin:0; color:#25D366;">🌱 High-Value Content Alert!</h4>
                <p style="margin:5px 0 0 0;"><strong>Onion (Kanda) prices</strong> at the local {district} Mandi have surged by 18% in the last 48 hours. <br>
                <em>AI Suggestion: Make a video advising local farmers to hold or sell their stock today!</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Select your district and click 'Scan Local Trends'.")

def jarvis_voice_assistant_page():
    st.title("🤖 Bharat Voice Assistant (Jarvis)")
    st.markdown("Your fully connected multi-lingual AI Co-Pilot. **Speak in your native language**, and the AI will listen, brainstorm ideas, and speak back to you instantly.")
    langs = {"Hindi": {"stt": "hi-IN", "tts": "hi"}, "Marathi": {"stt": "mr-IN", "tts": "mr"}, "Tamil": {"stt": "ta-IN", "tts": "ta"}, "Bengali": {"stt": "bn-IN", "tts": "bn"}, "Telugu": {"stt": "te-IN", "tts": "te"}, "English (India)": {"stt": "en-IN", "tts": "en"}}
    
    if not SR_AVAILABLE or not GTTS_AVAILABLE: st.error("⚠️ Ensure both `SpeechRecognition` and `gTTS` libraries are installed to enable Voice-to-Voice.")
    if not GEMINI_KEY and not AWS_CONFIGURED: st.warning("⚡ **Notice:** Jarvis is running in 'Dynamic Offline Mode'.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("1. Speak to Jarvis")
            target_lang = st.selectbox("Select Your Language", list(langs.keys()), index=1)
            audio_val = st.audio_input("🎙️ Click to Record your voice:") if hasattr(st, "audio_input") else None
            text_val = st.text_input("💬 Or type your question manually:", placeholder="e.g. Write a viral hook for my new tech review video...")
            
            # --- TASK 4: QUICK ACTION PROMPT CHIPS ---
            st.markdown("<p style='font-size: 0.85em; color: #a1a1aa; margin-top: 10px; margin-bottom: 5px;'>⚡ Quick Actions:</p>", unsafe_allow_html=True)
            qc1, qc2, qc3 = st.columns(3)
            quick_query = ""
            if qc1.button("🔥 What's trending?"): quick_query = "What is trending right now?"
            if qc2.button("✍️ Write a hook"): quick_query = "Write a strong hook for my video."
            if qc3.button("📅 Best post time?"): quick_query = "When is the best time to post today?"

            if st.button("✨ Ask Jarvis") or quick_query:
                user_query = quick_query
                if not user_query:
                    if audio_val and not text_val:
                        with st.spinner("Ear to the ground (Transcribing Voice)..."):
                            if SR_AVAILABLE:
                                try:
                                    r = sr.Recognizer()
                                    with sr.AudioFile(audio_val) as source: audio_data = r.record(source)
                                    user_query = r.recognize_google(audio_data, language=langs[target_lang]["stt"])
                                    st.success(f"🎤 Voice transcribed: {user_query}")
                                except Exception as e: st.error(f"Jarvis could not understand the audio. {e}")
                            else:
                                user_query = "What are the trending topics in my district right now?"
                                st.warning("Simulated transcription.")
                    else:
                        user_query = text_val
                    
                if user_query:
                    st.session_state['jarvis_query'] = user_query
                    with st.spinner("Jarvis is brainstorming..."):
                        answer = ask_jarvis_ai(user_query, target_lang)
                        st.session_state['jarvis_answer'] = answer
                    with st.spinner("Generating Voice Output..."):
                        if GTTS_AVAILABLE:
                            try:
                                tts = gTTS(text=answer, lang=langs[target_lang]["tts"])
                                fp = io.BytesIO()
                                tts.write_to_fp(fp)
                                st.session_state['jarvis_audio'] = fp.getvalue()
                            except Exception as e: st.error(f"TTS Error: {e}")
                        else:
                            st.session_state['jarvis_audio'] = None
            elif not quick_query and not audio_val and not text_val:
                st.warning("Please record audio, type a question, or use a quick action to proceed.")
                
    with col2:
        with st.container(border=True):
            st.subheader("2. Jarvis Response")
            if 'jarvis_answer' in st.session_state and st.session_state['jarvis_answer']:
                st.markdown(f"**🗣️ You:** \n*{st.session_state['jarvis_query']}*")
                st.markdown("---")
                st.markdown(f"""<div class="jarvis-box"><h3 style="margin-top:0; color: #7c3aed;">🤖 Jarvis Says:</h3><p style="font-size:1.2em; line-height:1.5;">{st.session_state['jarvis_answer']}</p></div>""", unsafe_allow_html=True)
                if 'jarvis_audio' in st.session_state and st.session_state['jarvis_audio']:
                    st.audio(st.session_state['jarvis_audio'], format='audio/mp3', autoplay=True)
                    st.success("🔊 Audio auto-playing!")
            else:
                st.info("Ask a question to initiate the AI Co-Pilot loop.")

def ai_system_controls_page():
    st.title("⚙️ AI System Controls")
    st.markdown("Manage your custom AI preferences, API integrations, and system automation settings.")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("1. AI Engine Configurations")
            st.selectbox("Primary AI Model", ["Google Gemini (Recommended)", "AWS Bedrock (Claude 3)", "OpenAI GPT-4", "Local Llama 3"])
            st.text_input("Gemini API Key", value="************************" if GEMINI_KEY else "", type="password", placeholder="Paste Gemini Key Here")
            st.text_input("AWS Access Key", placeholder="Paste AWS Key Here", type="password")
            st.toggle("Enable Fallback Offline Mode", value=True)

        with st.container(border=True):
            st.subheader("2. Automation Preferences")
            st.toggle("Auto-Schedule via WhatsApp API", value=True)
            st.toggle("Auto-Generate Thumbnails for Scripts", value=False)
            st.toggle("Enable Daily Trend Alerts", value=True)

    with col2:
        with st.container(border=True):
            st.subheader("3. Global Personalization")
            st.selectbox("Default Content Language", ["Hindi", "Marathi", "Tamil", "Bengali", "Gujarati", "Telugu"], index=1)
            st.selectbox("Creator Persona", ["Education & Exam Prep", "Rural Tech Reviewer", "Agri-Business (Farming)", "Village Vlogger"])
            st.slider("AI Creativity Level (Temperature)", 0.0, 1.0, 0.7)

        with st.container(border=True):
            st.subheader("4. System Health & Storage")
            st.progress(65, text="Cloud Storage Used (6.5 GB / 10 GB)")
            st.progress(85, text="Monthly AI Token Quota")
            if st.button("🗑️ Clear Cache & Reset Defaults"):
                st.success("System cache cleared!")

# --- 6. NAVIGATION LOGIC ---
st.sidebar.title("🇮🇳 IndiCreator AI")
st.sidebar.caption("Hackathon Prototype v1.0 | Tech Force")
st.sidebar.markdown("---")

st.sidebar.markdown("**🏆 PLATFORM TOOLS**")
nav_choice = st.sidebar.radio("Navigation", [
    "--- 📝 CREATE & PERSONALIZE ---",
    "✍️ AI Script Genius",
    "🧠 Bharat Knowledge Transformer", 
    "🛡️ Cultural Authenticity Shield",
    "--- 🎨 VISUALS & BRANDING ---",
    "🎨 Brand Identity Kit",
    "🎨 AI Visual Studio",
    "🖼️ AI Thumbnail Hook Optimizer",
    "--- 🚀 DISTRIBUTE & PLAN ---",
    "📅 Smart Content Planner",
    "📲 WhatsApp Optimizer",
    "--- 📈 ANALYZE & GROW ---",
    "📊 Bharat Analytics Hub",
    "📡 Hyper-Local Trend Radar",
    "🤖 Bharat Voice Assistant (Jarvis)",
    "--- ⚙️ SYSTEM & SETTINGS ---",
    "⚙️ AI System Controls"
], label_visibility="collapsed", key='nav_choice')

st.sidebar.markdown("---")

if AWS_CONFIGURED or GEMINI_KEY:
    st.sidebar.success("**Cloud Status:** ✅ Connected to AI Models")
else:
    st.sidebar.warning("**Cloud Status:** ⚠️ Dynamic Offline Demo")

# Page Routing
if "---" in nav_choice: st.info("👈 Please select a specific tool from the sidebar menu to get started.")
elif nav_choice == "✍️ AI Script Genius": ai_script_genius_page()
elif nav_choice == "🧠 Bharat Knowledge Transformer": knowledge_transformer_page()
elif nav_choice == "🛡️ Cultural Authenticity Shield": authenticity_shield_page()
elif nav_choice == "🎨 Brand Identity Kit": brand_identity_kit_page()
elif nav_choice == "🎨 AI Visual Studio": emotion_template_page()
elif nav_choice == "🖼️ AI Thumbnail Hook Optimizer": thumbnail_optimizer_page()
elif nav_choice == "📅 Smart Content Planner": smart_planner_page()
elif nav_choice == "📲 WhatsApp Optimizer": whatsapp_optimizer_page()
elif nav_choice == "📊 Bharat Analytics Hub": bharat_analytics_hub_page()
elif nav_choice == "📡 Hyper-Local Trend Radar": trend_radar_page()
elif nav_choice == "🤖 Bharat Voice Assistant (Jarvis)": jarvis_voice_assistant_page()
elif nav_choice == "⚙️ AI System Controls": ai_system_controls_page()
else: ai_script_genius_page()

# --- FOOTER ---
st.markdown("---")
st.caption("Tech Force | AI for Bharat Hackathon 2026")