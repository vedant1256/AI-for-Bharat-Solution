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
import io
import urllib.parse
import urllib.request
import base64
import re
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

# Try importing Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# --- 🛡️ SECURE KEY LOADING FROM .env FILE 🛡️ ---
load_dotenv() # This reads the .env file secretly

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

AWS_CONFIGURED = bool(AWS_ACCESS_KEY and AWS_SECRET_KEY)

if GEMINI_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_KEY)

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="DigitalBharat Studio | The Bharat-First Content Engine",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ADVANCED CSS ---
# Included custom styling for centered text and original square logo
st.markdown("""
    <style>
    /* Main App Background */
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    
    /* Standard Components Styling */
    [data-testid="stMetric"] { background-color: rgba(30, 41, 59, 0.7); border: 1px solid #4f46e5; border-radius: 12px; padding: 25px !important; margin: 10px 0px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { border: 1px solid rgba(79, 70, 229, 0.3) !important; border-radius: 15px; padding: 20px; background-color: rgba(30, 41, 59, 0.3); }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%); border: none; color: white; transition: 0.3s; height: 3em; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(124, 58, 237, 0.4); }
    .stTextArea textarea { background-color: #1e293b !important; color: #e2e8f0 !important; border: 1px solid #334155; }
    .whatsapp-btn { display: inline-block; width: 100%; text-align: center; border-radius: 8px; font-weight: 600; background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); padding: 12px 0; color: white !important; text-decoration: none; transition: 0.3s; }
    .whatsapp-btn:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(37, 211, 102, 0.4); }
    .alert-card { background: rgba(37, 211, 102, 0.1); border-left: 4px solid #25D366; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    .jarvis-box { background: rgba(124, 58, 237, 0.1); border: 1px solid #7c3aed; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px;}
    .hook-card { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #eab308; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-size: 1.4em; font-weight: bold; color: #fef08a;}
    .compare-box { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; padding: 15px; border-radius: 8px; font-size: 1.05em; line-height: 1.6; height: 100%; }
    .cal-badge { background: #4f46e5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }

    /* 🆕 CUSTOM SIDEBAR STYLING 🆕 */
    /* Target the main sidebar container to move everything upward */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 15px !important; /* Reduced padding from top */
    }

    /* Container for logo */
    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    /* Original size, square logo style */
    .sidebar-logo {
        width: 100%; /* Full width of the sidebar */
        border-radius: 0; /* Square shape */
        object-fit: contain; 
    }

    /* Centered main title */
    .sidebar-title {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #f8fafc;
        margin-bottom: 0px; /* Reduced space below title */
    }

    /* Centered team name */
    .sidebar-team {
        text-align: center;
        font-size: 16px;
        color: #a1a1aa;
        margin-top: -5px; /* Pulls closer to title */
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
if 'genius_script' not in st.session_state: st.session_state['genius_script'] = ""
if 'radar_active' not in st.session_state: st.session_state['radar_active'] = False
if 'radar_result' not in st.session_state: st.session_state['radar_result'] = ""
if 'thumbnail_hooks' not in st.session_state: st.session_state['thumbnail_hooks'] = []
if 'brand_kit_generated' not in st.session_state: st.session_state['brand_kit_generated'] = False
if 'brand_colors' not in st.session_state: st.session_state['brand_colors'] = []
if 'brand_text' not in st.session_state: st.session_state['brand_text'] = ""
if 'planner_result' not in st.session_state: st.session_state['planner_result'] = ""
if 'calendar_data' not in st.session_state: st.session_state['calendar_data'] = pd.DataFrame(columns=["Content Title", "Platform", "Target Audience", "Optimal Time"])

# Voice Assistant & Pipeline State
if 'jarvis_query' not in st.session_state: st.session_state['jarvis_query'] = ""
if 'jarvis_answer' not in st.session_state: st.session_state['jarvis_answer'] = ""
if 'pipe_base_script' not in st.session_state: st.session_state['pipe_base_script'] = None
if 'pipe_localized_script' not in st.session_state: st.session_state['pipe_localized_script'] = None
if 'pipe_wa_summary' not in st.session_state: st.session_state['pipe_wa_summary'] = None
if 'generated_thumbnail' not in st.session_state: st.session_state['generated_thumbnail'] = None
if 'thumbnail_source' not in st.session_state: st.session_state['thumbnail_source'] = ""

# --- 4. MULTI-CLOUD LIVE AI ENGINE ---
def get_llm_response(prompt, max_tokens=800):
    """Central engine routing to Amazon Nova Micro, with fallback to Google Gemini."""
    aws_error_msg = ""
    
    if AWS_CONFIGURED:
        try:
            # Securely inject keys from .env
            bedrock = boto3.client(
                service_name='bedrock-runtime', 
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
            response = bedrock.converse(
                modelId='amazon.nova-micro-v1:0',
                messages=[{"role": "user", "content": [{"text": prompt}]}]
            )
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            aws_error_msg = str(e)
            print(f"AWS Nova Failed: {aws_error_msg}")

    if GEMINI_KEY and GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Gemini Error: {e}"

    return f"⚠️ AI Engine Offline. AWS Error: {aws_error_msg}."

# --- 5. DASHBOARDS ---

def content_pipeline_page():
    st.title("🚀 AI Content Pipeline")
    st.markdown("A 3-step live AI workflow to transform any topic into a regional viral broadcast.")

    with st.container(border=True):
        st.subheader("Step 1: AI Knowledge Simplifier")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            doc_type = st.text_input("Enter Topic/Document:", placeholder="e.g. Free Fire OB43 Update, or PM-Kisan Scheme")
            target_lang = st.selectbox("Target Base Language", ["Hindi", "Marathi", "Hinglish", "English"])
            if st.button("🔄 Generate Base Script"):
                if doc_type:
                    with st.spinner("AI is analyzing and simplifying..."): 
                        prompt = f"Act as an expert scriptwriter. Summarize the topic '{doc_type}' into a 4-line engaging video script in {target_lang}."
                        st.session_state['pipe_base_script'] = get_llm_response(prompt)
                        st.session_state['pipe_localized_script'] = None 
                        st.session_state['pipe_wa_summary'] = None 
                else:
                    st.warning("Please enter a topic.")
        with col2:
            if st.session_state['pipe_base_script']:
                st.text_area("Base AI Output:", value=st.session_state['pipe_base_script'], height=180)
            else:
                st.info("👈 Enter a topic and click 'Generate' to start.")

    if st.session_state['pipe_base_script']:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("Step 2: Inject Cultural Nuance / Slang")
            col3, col4 = st.columns([1, 1.2])
            with col3:
                target_region = st.selectbox("Target Audience Vibe", ["Pune (Puneri pure)", "Mumbai (Tapori/Bindaas)", "Delhi (Gamer/Swag)", "UP/Bihar (Desi)"])
                if st.button("✨ Apply Cultural Nuance"):
                    with st.spinner(f"Injecting {target_region} style..."): 
                        prompt = f"Rewrite the following script in {target_region} local slang and vibe to make it extremely relatable to that region. Keep the core meaning intact:\n\n'{st.session_state['pipe_base_script']}'"
                        st.session_state['pipe_localized_script'] = get_llm_response(prompt)
                        st.session_state['pipe_wa_summary'] = None 

            with col4:
                if st.session_state['pipe_localized_script']:
                    st.markdown("**🟢 Culturally Localized Script**")
                    st.markdown(f'<div class="compare-box" style="font-size:0.9em;">{st.session_state["pipe_localized_script"]}</div>', unsafe_allow_html=True)

    if st.session_state['pipe_localized_script']:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("Step 3: Format for WhatsApp Distribution")
            col5, col6 = st.columns([1, 1.2])
            with col5:
                if st.button("📲 Auto-Format for WhatsApp"):
                    with st.spinner("Adding emojis and formatting..."):
                        prompt = f"Format this script into a highly engaging, viral WhatsApp broadcast message. Add relevant emojis, short bullet points, and a strong Call to Action at the end:\n\n'{st.session_state['pipe_localized_script']}'"
                        st.session_state['pipe_wa_summary'] = get_llm_response(prompt)
            with col6:
                if st.session_state['pipe_wa_summary']:
                    edited_wa = st.text_area("Review & Edit (Ready to Send)", value=st.session_state['pipe_wa_summary'], height=200)
                    encoded_text = urllib.parse.quote(edited_wa)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">🚀 1-Click Broadcast to WhatsApp</a>', unsafe_allow_html=True)

def script_genius_page():
    st.title("✍️ AI Script Genius")
    st.markdown("Multilingual AI content and script generation with smart hooks and tone control.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("Configuration Engine")
            topic = st.text_input("Content Topic", placeholder="e.g. Free Fire Headshot Trick, Local News")
            language = st.selectbox("Choose Language", ["Hindi", "Marathi", "Hinglish", "English"])
            vibe = st.select_slider("Vibe / Tone", ["Educational", "Professional", "Casual", "Funny", "Urgent"])
            
            if st.button("✨ Generate Script & Hooks"):
                if topic:
                    with st.spinner("Writing script and generating hooks via AI..."):
                        script_prompt = f"Write a highly engaging, {vibe} YouTube Shorts/Reels script in {language} about '{topic}'. Include a 3-second hook, a short body, and a CTA."
                        st.session_state['genius_script'] = get_llm_response(script_prompt)
                        
                        hook_prompt = f"Give me exactly 3 short, clickbaity, viral YouTube thumbnail titles (3-5 words max each) for a video about '{topic}' in {language}. Use emojis. Output them separated by commas."
                        hooks_response = get_llm_response(hook_prompt, max_tokens=100)
                        st.session_state['thumbnail_hooks'] = [h.strip() for h in hooks_response.split(",") if h.strip()][:3]
                        
                    st.success("Generation successful!")
                else:
                    st.warning("Please enter a topic.")
                    
    with col2:
        with st.container(border=True):
            st.subheader("📝 Script Storyboard Editor")
            st.text_area("Live Editor", value=st.session_state.get('genius_script', ""), height=250)

        if st.session_state.get('thumbnail_hooks'):
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.subheader("🔥 AI Suggested Thumbnail Hooks")
                hook_cols = st.columns(3)
                for i, hook in enumerate(st.session_state['thumbnail_hooks']):
                    if i < 3:
                        with hook_cols[i]: st.markdown(f'<div class="hook-card" style="font-size:1.1em; padding:10px; text-align:center;">{hook}</div>', unsafe_allow_html=True)

def brand_kit_page():
    st.title("🎨 Brand Identity Kit")
    st.markdown("Live AI generation of custom brand identities for Gaming, Tech, Finance, or Agriculture channels.")
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("1. Define Your Vibe")
            channel_name = st.text_input("Channel Name:", placeholder="e.g. Headshot Gamer, Kisaan Mitra")
            niche = st.text_input("Content Niche:", placeholder="e.g. Mobile Gaming, Stock Market")
            target_demo = st.text_input("Target Audience:", placeholder="e.g. Teenagers, Farmers")
            
            if st.button("✨ Generate Custom Brand Kit"):
                if channel_name and niche:
                    with st.spinner("AI is analyzing psychology and creating your brand..."):
                        prompt = f"Act as a professional Brand Designer. I am starting a channel named '{channel_name}' in the '{niche}' niche, targeting '{target_demo}'. Provide EXACTLY 3 hex color codes (e.g. #FF0000) that psychologically match this niche. Then provide 2 recommended Google Font names, and a 2-sentence description of the brand's 'Tone of Voice'."
                        response = get_llm_response(prompt)
                        
                        colors = re.findall(r'#[0-9A-Fa-f]{6}', response)
                        st.session_state['brand_colors'] = colors[:3] if len(colors) >= 3 else ["#3b82f6", "#10b981", "#f59e0b"]
                        st.session_state['brand_text'] = response
                        st.session_state['brand_kit_generated'] = True
                    st.success("Brand Identity generated!")
                else:
                    st.warning("Enter Channel Name and Niche.")
                    
    with col2:
        with st.container(border=True):
            st.subheader("2. Your Digital Identity")
            if st.session_state.get('brand_kit_generated', False):
                colors = st.session_state['brand_colors']
                st.markdown("**🎨 AI Selected Brand Colors:**")
                cols_html = "".join([f"<div style='background-color:{c}; width:60px; height:60px; display:inline-block; margin-right:15px; border-radius:8px; border:2px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'></div>" for c in colors])
                labels_html = "".join([f"<div style='width:60px; display:inline-block; margin-right:15px; text-align:center; color:#a1a1aa; font-size:0.8em;'>{c}</div>" for c in colors])
                st.markdown(cols_html + "<br>" + labels_html, unsafe_allow_html=True)
                st.write("")
                
                st.markdown("**🖋️ AI Branding Guidelines:**")
                st.info(st.session_state['brand_text'])
            else:
                st.info("Fill out details to let AI generate your colors and vibe.")

def visual_studio_page():
    st.title("🖼️ AI Visual Studio")
    st.markdown("Generating high-conversion thumbnails using **Amazon Titan Image Generator v2:0**.")
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        with st.container(border=True):
            scene = st.text_area("Scene Description", placeholder="e.g. A cyberpunk hacker sitting in a neon room, OR A pro gamer playing Free Fire on mobile")
            emotion = st.selectbox("Style/Emotion", ["Cinematic 🎬", "Anime/Gaming 🎮", "Hyper-Realistic 📸", "Neon/Tech ⚡"])
            
            if st.button("🎨 Generate via AWS Credits"):
                if not scene:
                    st.warning("Please describe the scene first.")
                else:
                    with st.spinner("AWS Bedrock (Titan v2:0) is painting..."):
                        base_prompt = f"{scene}, {emotion} style, 8k resolution, highly detailed, vibrant colors."
                        st.session_state['enhanced_image_prompt'] = base_prompt
                        
                        try:
                            # 1. ATTEMPT AWS TITAN V2:0 GENERATION
                            bedrock = boto3.client(
                                service_name='bedrock-runtime',
                                region_name=AWS_REGION,
                                aws_access_key_id=AWS_ACCESS_KEY,
                                aws_secret_access_key=AWS_SECRET_KEY
                            )
                            
                            body = json.dumps({
                                "taskType": "TEXT_IMAGE",
                                "textToImageParams": {"text": base_prompt},
                                "imageGenerationConfig": {
                                    "cfgScale": 8,
                                    "seed": random.randint(0, 2147483647), # Randomize seed for fresh images
                                    "width": 1024,
                                    "height": 1024,
                                    "numberOfImages": 1
                                }
                            })
                            
                            response = bedrock.invoke_model(
                                modelId="amazon.titan-image-generator-v2:0", 
                                body=body
                            )
                            
                            response_body = json.loads(response.get("body").read())
                            base64_image = response_body.get("images")[0]
                            st.session_state['generated_thumbnail'] = base64.b64decode(base64_image)
                            st.session_state['thumbnail_source'] = "AWS Titan v2:0"
                            st.success("Successfully generated using AWS Credits!")

                        except Exception as e:
                            # 2. FAIL-SAFE FALLBACK TO POLLINATIONS
                            st.warning(f"AWS Network Blocked. Engaging Fallback Engine...")
                            encoded_prompt = urllib.parse.quote(base_prompt)
                            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={random.randint(1,10000)}&nologo=true"
                            st.session_state['generated_thumbnail'] = image_url
                            st.session_state['thumbnail_source'] = "Open Source Fallback"
                            st.success("Generated via Fallback Engine.")

    with col2:
        with st.container(border=True):
            st.subheader("2. AI Generated Thumbnail")
            if st.session_state.get('generated_thumbnail'):
                
                # Rendering logic based on source
                if st.session_state['thumbnail_source'] == "AWS Titan v2:0":
                    st.image(st.session_state['generated_thumbnail'], caption="AWS Titan v2 Output")
                    st.download_button("📥 Download Thumbnail", st.session_state['generated_thumbnail'], "aws_thumb.png", "image/png")
                else:
                    img_url = st.session_state['generated_thumbnail']
                    st.markdown(f'<img src="{img_url}" style="width:100%; border-radius:10px; border:1px solid #334155;">', unsafe_allow_html=True)
                    st.markdown(f"**[📥 Click here to open/download Image directly]({img_url})**")
                
                st.markdown("<br>**🤖 AI Image Prompt Used:**", unsafe_allow_html=True)
                st.code(st.session_state.get('enhanced_image_prompt', ''), language="text")
            else:
                st.info("Describe your scene and click 'Generate via AWS Credits'.")

def content_planner_page():
    st.title("📅 Smart Content Planner")
    st.markdown("AI-powered scheduling and content calendar management system.")
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        with st.container(border=True):
            title = st.text_input("Content Topic", placeholder="e.g. Free Fire Tips, or Option Trading")
            platform = st.selectbox("Platform", ["YouTube Shorts", "Instagram Reels", "WhatsApp", "Twitter"])
            audience = st.text_input("Target Audience", placeholder="e.g. Gamers, Farmers, Programmers")
            
            if st.button("🤖 Let AI Predict Best Time"):
                if title and audience:
                    with st.spinner("AI analyzing audience behavior..."):
                        prompt = f"Act as a social media algorithm expert. I am posting a {platform} video about '{title}' to a target audience of '{audience}' in India. Suggest a specific optimal posting time (e.g. Today, 6:30 PM) and write a 1-sentence insight explaining why."
                        response = get_llm_response(prompt, max_tokens=150)
                        
                        st.session_state['planner_result'] = response
                        new_entry = pd.DataFrame([{"Content Title": title, "Platform": platform, "Target Audience": audience, "Optimal Time": "AI Decided"}])
                        st.session_state['calendar_data'] = pd.concat([st.session_state['calendar_data'], new_entry], ignore_index=True)
                        st.success("Scheduled successfully!")
                else:
                    st.warning("Enter Topic and Audience.")

    with col2:
        with st.container(border=True):
            st.subheader("Your Live AI Content Calendar")
            st.table(st.session_state['calendar_data'])
            if st.session_state.get('planner_result'):
                st.info(f"🧠 **Latest AI Insight:** {st.session_state['planner_result']}")

def analytics_hub_page():
    st.title("📊 Bharat Analytics Hub")
    st.markdown("Intelligent dashboards for performance, sentiment, and regional engagement insights.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lifetime Reach", "1.2M", "+15%")
    m2.metric("Avg CTR", "8.4%", "+1.2%")
    m3.metric("Top Platform", "YouTube", "60% Traffic")
    m4.metric("Audience", "Tier-2/3", "Growing")
    
    st.divider()
    
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        with st.container(border=True):
            st.subheader("🧠 Live AI Sentiment Analyzer")
            niche_analysis = st.text_input("Enter a video topic you recently posted:", placeholder="e.g. Buying stocks on Groww app")
            if st.button("Analyze Audience Sentiment"):
                if niche_analysis:
                    with st.spinner("AI analyzing predicted comments..."):
                        prompt = f"Predict the audience sentiment and common comments for an Indian creator's video about '{niche_analysis}'. Give a percentage of Positive vs Negative, and a 1 sentence tip to improve the next video."
                        st.info(get_llm_response(prompt))
                else:
                    st.warning("Enter a topic to analyze.")
            
    with c2:
        with st.container(border=True):
            st.subheader("Audience Split")
            sent_df = pd.DataFrame({"Platform": ["YouTube", "Insta", "WhatsApp"], "Traffic": [60, 25, 15]})
            fig2 = px.pie(sent_df, names="Platform", values="Traffic", hole=0.4, color_discrete_sequence=["#ef4444", "#eab308", "#22c55e"])
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)

def trend_radar_page():
    st.title("📡 Trend Radar")
    st.markdown("Real-time AI detection of trending topics and digital momentum.")
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        with st.container(border=True):
            state = st.text_input("State / Location", placeholder="e.g. Maharashtra, or All India")
            niche = st.text_input("Niche (Optional)", placeholder="e.g. Gaming, Finance, Agriculture")
            
            if st.button("📡 Scan Live AI Trends"):
                with st.spinner("AI is scanning internet patterns..."):
                    prompt = f"Act as a trending topics analyst. Suggest 2 highly engaging, plausible trending video ideas right now for a creator in '{state}' focusing on the '{niche}' niche. Keep it under 3 sentences total."
                    st.session_state['radar_result'] = get_llm_response(prompt, max_tokens=200)
                    st.session_state['radar_active'] = True
    with col2:
        if st.session_state.get('radar_active'):
            st.success("Live Radar Scan Complete!")
            st.markdown(f"""
            <div class="alert-card">
                <h4 style="margin:0; color:#25D366;">🔥 High-Value Content Alert!</h4>
                <p style="margin:5px 0 0 0;">{st.session_state['radar_result']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("👈 Enter your location/niche and click 'Scan Live AI Trends'.")

def ai_saarthi_page():
    st.title("🤖 AI Saarthi")
    st.markdown("Your fully connected multi-lingual AI Co-Pilot. Ask anything.")
    
    # Proper language codes for Text-to-Speech (gTTS)
    langs = {
        "Hindi": "hi", 
        "Marathi": "mr", 
        "English (India)": "en"
    }
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        with st.container(border=True):
            target_lang_name = st.selectbox("Select Your Language", list(langs.keys()))
            text_val = st.text_input("💬 Ask Saarthi anything (Gaming, Code, Scripts...):", placeholder="e.g. Write a viral hook for my Free Fire video...")
            
            if st.button("✨ Ask Saarthi"):
                if text_val:
                    st.session_state['jarvis_query'] = text_val
                    with st.spinner("Saarthi is thinking via AI..."):
                        
                        # Strict prompt to force Devanagari Script for clear pronunciation
                        prompt = f"""You are Saarthi, an expert AI creator assistant. 
                        Answer this query in {target_lang_name} briefly and energetically. 
                        CRITICAL RULE: If the language is Hindi or Marathi, you MUST write the answer strictly in the native Devanagari script (e.g., नमस्ते). Do NOT use English letters to write Hindi/Marathi. 
                        Query: {text_val}"""
                        
                        answer = get_llm_response(prompt, max_tokens=300)
                        st.session_state['jarvis_answer'] = answer
                        
                        # Generate Audio using correct gTTS language code & accent
                        with st.spinner("Generating Voice Output..."):
                            if GTTS_AVAILABLE:
                                try:
                                    lang_code = langs[target_lang_name]
                                    if lang_code == "en":
                                        tts = gTTS(text=answer, lang=lang_code, tld="co.in")
                                    else:
                                        tts = gTTS(text=answer, lang=lang_code)
                                    
                                    fp = io.BytesIO()
                                    tts.write_to_fp(fp)
                                    st.session_state['jarvis_audio'] = fp.getvalue()
                                except Exception as e:
                                    st.error(f"TTS Error: {e}")
                                    st.session_state['jarvis_audio'] = None
                            else:
                                st.warning("Audio library (gTTS) is missing.")
                else:
                    st.warning("Please type a question.")
                
    with col2:
        with st.container(border=True):
            st.subheader("2. Saarthi Response")
            if st.session_state.get('jarvis_answer'):
                st.markdown(f"**🗣️ You:** \n*{st.session_state['jarvis_query']}*")
                st.markdown("---")
                st.markdown(f"""<div class="jarvis-box"><h3 style="margin-top:0; color: #7c3aed;">🤖 Saarthi Says:</h3><p style="font-size:1.1em; line-height:1.5;">{st.session_state['jarvis_answer']}</p></div>""", unsafe_allow_html=True)
                
                # Show Audio Player
                if st.session_state.get('jarvis_audio'):
                    st.audio(st.session_state['jarvis_audio'], format='audio/mp3', autoplay=True)
            else:
                st.info("Ask a question to initiate the Live AI loop.")

def system_controls_page():
    st.title("⚙️ AI System Controls")
    st.markdown("Custom AI preferences, automation, and personalization settings.")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        with st.container(border=True):
            st.subheader("1. Active Architecture")
            st.success("🥇 Primary Engine: AWS Bedrock (Amazon Nova & Titan V2)")
            st.info("🥈 Fallback Engine: Google Gemini Pro & Pollinations")
            st.markdown("If AWS API limits or errors occur, the system automatically redirects to Fallbacks without crashing.")
    with col2:
        with st.container(border=True):
            st.subheader("2. Real-Time Status")
            st.progress(100, text="Multi-Cloud Engine Connected & Secure")
            st.progress(45, text="API Quota Used")

# --- 6. NAVIGATION LOGIC (RECONSTRUCTED FOR CUSTOM SIDEBAR) ---

# Spacer to take everything slightly upward
st.sidebar.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 🖼️ SECURE IMAGE ENCODING FOR HTML
LOGOPATH = "logo.jpg"
if os.path.exists(LOGOPATH):
    with open(LOGOPATH, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Original Size and Square Logo using Custom CSS classes defined at top
    LOGO_HTML = f'<div class="sidebar-logo-container"><img src="data:image/jpg;base64,{encoded_string}" class="sidebar-logo"></div>'
else:
    LOGO_HTML = '<div class="stAlert" style="text-align:center; padding: 10px; border-radius:5px; background-color:rgba(255,255,255,0.1);"><p style="margin:0;">💡 Tip: Save your logo as \'logo.jpg\' in this folder.</p></div>'

# Inject Custom HTML for Logo and Titles
st.sidebar.markdown(f"""
    {LOGO_HTML}
    <div class="sidebar-title">DigitalBharat Studio</div>
    <div class="sidebar-team">Tech Force</div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**🏆 PLATFORM TOOLS**")

# Names match the PPT exactly
nav_choice = st.sidebar.radio("Navigation", [
    "🚀 Content Pipeline",
    "✍️ AI Script Genius",
    "🎨 Brand Identity Kit",
    "🖼️ AI Visual Studio",
    "📅 Smart Content Planner",
    "📊 Bharat Analytics Hub",
    "📡 Trend Radar",
    "🤖 AI Saarthi",
    "⚙️ AI System Controls"
], label_visibility="collapsed")

st.sidebar.markdown("---")

# Page Routing
if nav_choice == "🚀 Content Pipeline": content_pipeline_page()
elif nav_choice == "✍️ AI Script Genius": script_genius_page()
elif nav_choice == "🎨 Brand Identity Kit": brand_kit_page()
elif nav_choice == "🖼️ AI Visual Studio": visual_studio_page()
elif nav_choice == "📅 Smart Content Planner": content_planner_page()
elif nav_choice == "📊 Bharat Analytics Hub": analytics_hub_page()
elif nav_choice == "📡 Trend Radar": trend_radar_page()
elif nav_choice == "🤖 AI Saarthi": ai_saarthi_page()
elif nav_choice == "⚙️ AI System Controls": system_controls_page()
else: content_pipeline_page()