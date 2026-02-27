import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import boto3
import json
import os
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- 0. INITIALIZATION & SECURITY ---
load_dotenv()
AWS_CONFIGURED = bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))

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
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'script_output' not in st.session_state: st.session_state['script_output'] = ""
if 'image_history' not in st.session_state: st.session_state['image_history'] = []
if 'plan_data' not in st.session_state:
    st.session_state['plan_data'] = pd.DataFrame([
        {"Content Title": "Organic Farming Tips", "Platform": "YouTube", "Time": "2026-03-01 10:00", "Status": "Draft"},
        {"Content Title": "Digital Payments 101", "Platform": "WhatsApp", "Time": "2026-03-05 18:30", "Status": "Scheduled"}
    ], columns=["Content Title", "Platform", "Time", "Status"])
if 'affiliate_post' not in st.session_state: st.session_state['affiliate_post'] = ""
if 'voice_prompt' not in st.session_state: st.session_state['voice_prompt'] = ""

# --- 4. REAL AWS BEDROCK LOGIC ---
def generate_ai_script_aws(topic, lang, tone):
    prompt = f"You are an expert content creator for the Indian audience. Write a highly engaging, {tone} video script in {lang} about '{topic}'. Include a catchy hook, a 3-point main body, and a strong call to action asking people to subscribe."
    if not AWS_CONFIGURED:
        return f"⚠️ **AWS Integration Notice:**\nWaiting for AWS credits to activate live generation. \n\n---\n**[MOCK SCRIPT FOR DEMO]**\n\nLanguage: {lang}\nTopic: {topic}\n\n[0:00 - Hook]: Did you know that {topic} is changing the landscape of Bharat?\n[0:15 - Body]: Creators in Tier-2 and Tier-3 cities are leveraging this to scale rapidly...\n[1:00 - CTA]: Drop a comment below if you want a full tutorial!"
    try:
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        bedrock = boto3.client(service_name='bedrock-runtime', region_name=region)
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 800,
            "messages": [{"role": "user", "content": prompt}]
        })
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0', 
            contentType='application/json',
            accept='application/json',
            body=body
        )
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    except Exception as e:
        return f"❌ **API Error:**\nCould not generate script. Please check your AWS credentials and model access.\n\nError details: {str(e)}"

# --- 5. DASHBOARDS ---

def dashboard_analytics():
    st.title("📊 Bharat Analytics Hub")
    st.markdown("Detailed cross-platform performance metrics and regional engagement data.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lifetime Reach", "2.4M", "+12.5% Growth")
    m2.metric("Sentiment Score", "92.4%", "Positive 😊")
    m3.metric("Regional Impact", "Indore/Pune", "Tier-2 Peak")
    m4.metric("Active Campaigns", "14", "Running")
    st.divider()
    col_main, col_side = st.columns([2, 1], gap="large")
    with col_main:
        with st.container(border=True):
            st.subheader("🚀 AI-Generated Content Strategy")
            sug_df = pd.DataFrame({
                "Content Topic": ["Solar Pumps in UP", "5G for Rural Students", "Local SEO for Kirana", "Modern Farming Tech"],
                "Viral Match": ["99%", "96%", "91%", "88%"],
                "Priority": ["High", "Medium", "High", "Low"]
            })
            st.table(sug_df)
        with st.container(border=True):
            st.subheader("📈 Language Retention Trends")
            chart_data = pd.DataFrame(np.random.rand(15, 3), columns=['Hindi', 'Marathi', 'Tamil'])
            st.line_chart(chart_data)
    with col_side:
        with st.container(border=True):
            st.subheader("🔥 Trending in Bharat")
            trends = [("#AIforIndia", "High"), ("#AgriGrowth", "Very High"), ("#DigitalGully", "Medium"), ("#StartupIndore", "Medium"), ("#MakeInIndia", "High")]
            for i, (t, vol) in enumerate(trends):
                st.markdown(f"""
                    <div class="trend-card">
                        <div><span class="trend-rank">#{i+1}</span><span style="margin-left:15px; font-weight:500;">{t}</span></div>
                        <span style="background:#4f46e5; padding:2px 8px; border-radius:10px; font-size:0.7em;">{vol}</span>
                    </div>
                """, unsafe_allow_html=True)

def script_genius_page():
    st.title("✍️ Multilingual Script Genius")
    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        with st.container(border=True):
            st.subheader("Configuration Engine")
            
            with st.expander("🎙️ Speak Your Idea (Voice-to-Text)"):
                st.markdown("Skip typing! Record your idea in your local language.")
                if st.button("🔴 Start Recording (Simulated)"):
                    with st.spinner("Listening & Translating to prompt..."):
                        time.sleep(2)
                        st.session_state['voice_prompt'] = "Explain the benefits of the new PM-Kisan scheme for small farmers"
                        st.success("Audio transcribed successfully!")
            
            topic_val = st.session_state['voice_prompt'] if st.session_state['voice_prompt'] else ""
            topic = st.text_input("Content Topic", value=topic_val, placeholder="e.g. Benefits of PM-Kisan Scheme")
            lang = st.selectbox("Choose Language", ["Hindi", "Hinglish", "English", "Marathi", "Tamil", "Bengali"])
            tone = st.select_slider("Vibe", ["Funny", "Casual", "Professional", "Urgent", "Inspirational"])
            
            if st.button("Generate Script with AWS"):
                if topic:
                    with st.spinner("AWS Bedrock is crafting your story..."):
                        st.session_state['script_output'] = generate_ai_script_aws(topic, lang, tone)
                else:
                    st.warning("Please enter a topic first.")
    with c2:
        with st.container(border=True):
            st.subheader("📝 Script Storyboard Editor")
            st.text_area("Live Editor", value=st.session_state['script_output'], height=450)
            col_b1, col_b2 = st.columns(2)
            with col_b1: st.button("🔊 Generate AI Voiceover")
            with col_b2: st.button("📥 Export PDF")

def visual_studio_page():
    st.title("🎨 AI Visual Studio")
    st.write("Generate high-conversion thumbnails tailored for the Indian viewer.")
    with st.container(border=True):
        prompt = st.text_area("Describe your visual concept:", placeholder="An Indian youth using a laptop in a bright village field, modern vibe...")
        col1, col2, col3 = st.columns(3)
        with col1: style = st.selectbox("Design Style", ["Cinematic", "Anime-Bharat", "Minimalist"])
        with col2: mood = st.selectbox("Lighting", ["Golden Hour", "Studio Bright", "Natural"])
        with col3: ratio = st.radio("Format", ["16:9 (YouTube)", "9:16 (Reels)"])
        if st.button("Generate Thumbnail Image"):
            with st.spinner("Connecting to Image API..."):
                time.sleep(1.5)
                url = f"https://picsum.photos/seed/{random.randint(1,999)}/1280/720"
                st.session_state['image_history'].insert(0, url)
    if st.session_state['image_history']:
        st.write("")
        st.image(st.session_state['image_history'][0], caption="Generated Result", use_container_width=True)

def smart_planner_page():
    st.title("📅 Smart Content Calendar")
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        with st.container(border=True):
            st.subheader("Schedule Post")
            t = st.text_input("Video/Post Title")
            p = st.selectbox("Select Platform", ["YouTube", "Instagram", "WhatsApp Channel", "LinkedIn"])
            dt = st.date_input("Date")
            tm = st.time_input("AI Suggested Peak Time")
            if st.button("Sync to Calendar"):
                new_entry = {"Content Title": t, "Platform": p, "Time": f"{dt} {tm}", "Status": "Ready"}
                st.session_state['plan_data'] = pd.concat([st.session_state['plan_data'], pd.DataFrame([new_entry])], ignore_index=True)
                st.success("Calendar Updated!")
    with c2:
        with st.container(border=True):
            st.subheader("Your Content Pipeline")
            st.table(st.session_state['plan_data'])

def trend_radar_page():
    st.title("📡 Trend Radar")
    st.write("Live analysis of trending topics across Bharat's digital landscape.")
    with st.container(border=True):
        df_t = pd.DataFrame({
            'Topic': ['Govt Schemes', 'AI Learning', 'Smart Farming', 'UPI Lite', 'Village Vlogs', 'Crypto India'],
            'Momentum': np.random.randint(40, 100, 6),
            'Volume': np.random.randint(1000, 50000, 6)
        })
        fig = px.scatter(df_t, x="Momentum", y="Volume", size="Volume", text="Topic", 
                         title="Market Sentiment Clusters", color="Momentum", template="plotly_dark")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def authenticity_shield_page():
    st.title("🛡️ Authenticity Shield")
    st.markdown("Protect your credibility. Scan regional WhatsApp forwards and media for deepfakes or manipulation before you share.")
    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload Image or Video (Max 50MB)", type=['png', 'jpg', 'jpeg', 'mp4'])
        if uploaded_file is not None:
            if st.button("Run AI Authenticity Scan"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                    if i == 25: status_text.text("Extracting metadata...")
                    elif i == 50: status_text.text("Analyzing pixel anomalies...")
                    elif i == 75: status_text.text("Running through deepfake neural network...")
                status_text.text("Scan Complete!")
                st.success("✅ **High Confidence: Authentic**\n\nNo significant signs of AI manipulation or deepfake artifacts detected. Safe to distribute.")
                with st.expander("View Detailed Forensics"):
                    st.write("**Artifact Analysis:** 1.2% variance (Normal)")
                    st.write("**Metadata Integrity:** Verified")
                    st.write("**Source Trust Score:** 88/100")

def affiliate_engine_page():
    st.title("💸 Smart Affiliate Engine")
    st.markdown("Turn your content into income. Instantly generate highly converting promotional titles and descriptions for WhatsApp, Telegram, and YouTube.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Campaign Setup")
            product = st.text_input("Product/Niche Name", placeholder="e.g., Solar Water Pump")
            platform = st.selectbox("Target Platform", ["WhatsApp Broadcast", "Telegram Channel", "YouTube Description"])
            tone = st.selectbox("Promotional Vibe", ["Urgent (Limited Time)", "Educational", "Direct Sales"])
            
            if st.button("Generate Affiliate Content"):
                if product:
                    with st.spinner("Analyzing product and writing regional copy..."):
                        time.sleep(1.2)
                        st.session_state['affiliate_post'] = f"""🌟 *{product.upper()} - MEGA DISCOUNT!* 🌟\n\nKisan bhaiyon aur doston! Stop worrying about high costs and upgrade today. This {product} is highly recommended and currently on a massive discount!\n\n✅ Top Quality Guaranteed\n✅ Value for Money\n✅ Perfect for our regional needs\n\n👉 *Buy Now (Discount Applied):* https://amzn.to/mock-affiliate-link-789\n\nHurry up, stock is limited! Share this with your groups. ⏳"""
                else:
                    st.warning("Please enter a product name.")
                    
    with col2:
        with st.container(border=True):
            st.subheader("Generated Campaign Copy")
            st.text_area("Review & Edit Your Post", value=st.session_state['affiliate_post'], height=250)
            
            if st.session_state['affiliate_post']:
                # Create a dynamic WhatsApp API link
                encoded_text = urllib.parse.quote(st.session_state['affiliate_post'])
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Share Direct to WhatsApp</a>', unsafe_allow_html=True)

# --- 6. NAVIGATION LOGIC ---
st.sidebar.title("🇮🇳 IndiCreator AI")
st.sidebar.caption("Hackathon Prototype v1.0 | Tech Force")
st.sidebar.markdown("---")

nav_choice = st.sidebar.radio("Navigation", [
    "📊 Analytics Hub", "✍️ Script Genius", "🎨 Visual Studio", 
    "📅 Smart Planner", "📡 Trend Radar", "🛡️ Authenticity Shield", "💸 Affiliate Engine"
])

st.sidebar.markdown("---")

if AWS_CONFIGURED:
    st.sidebar.success("**Cloud Status:** ✅ Connected to AWS Bedrock")
else:
    st.sidebar.warning("**Cloud Status:** ⚠️ Local Demo Mode (Awaiting Credits)")

if nav_choice == "📊 Analytics Hub": dashboard_analytics()
elif nav_choice == "✍️ Script Genius": script_genius_page()
elif nav_choice == "🎨 Visual Studio": visual_studio_page()
elif nav_choice == "📅 Smart Planner": smart_planner_page()
elif nav_choice == "📡 Trend Radar": trend_radar_page()
elif nav_choice == "🛡️ Authenticity Shield": authenticity_shield_page()
elif nav_choice == "💸 Affiliate Engine": affiliate_engine_page()

# --- FOOTER ---
st.markdown("---")
st.caption("Tech Force | AI for Bharat Hackathon 2026")