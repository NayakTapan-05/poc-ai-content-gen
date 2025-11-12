"""
Streamlit AI Content Generator POC
Fast, local-first with HF Inference API integration
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

sys.path.append(str(Path(__file__).parent.parent / "backend"))

st.set_page_config(
    page_title="AI Content Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Floating Action Button */
    .fab {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        z-index: 9999;
        transition: transform 0.2s;
    }
    
    .fab:hover {
        transform: scale(1.1);
    }
    
    .fab-icon {
        color: white;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background-color: #2b313e;
    }
    
    .assistant-message {
        background-color: #1e2530;
    }
    
    /* Template card */
    .template-card {
        background: #1e2530;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #2b313e;
        margin-bottom: 1rem;
    }
    
    .template-card:hover {
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_template_picker" not in st.session_state:
    st.session_state.show_template_picker = False
if "generation_type" not in st.session_state:
    st.session_state.generation_type = None
if "selected_brand" not in st.session_state:
    st.session_state.selected_brand = None

with st.sidebar:
    st.title("🎨 AI Content Generator")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["💬 Chat", "📁 Brand Data", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.caption("Powered by Hugging Face")

if st.button("➕", key="fab", help="Create new content"):
    st.session_state.show_template_picker = True

if st.session_state.show_template_picker:
    with st.container():
        st.markdown("### 🎯 Create Content")
        
        tab1, tab2 = st.tabs(["🖼️ Image", "🎬 Video"])
        
        with tab1:
            st.markdown("#### Image Generation")
            
            try:
                response = requests.get(f"{API_URL}/api/templates?type=image")
                if response.status_code == 200:
                    templates = response.json()
                    
                    template_choice = st.selectbox(
                        "Select Template",
                        options=[t["id"] for t in templates],
                        format_func=lambda x: next(t["label"] for t in templates if t["id"] == x)
                    )
                    
                    if template_choice:
                        template = next(t for t in templates if t["id"] == template_choice)
                        st.markdown(f"**{template['label']}**")
                        st.caption(template.get("description", ""))
                        
                        field_values = {}
                        for field in template.get("fields", []):
                            field_values[field["name"]] = st.text_input(
                                field["label"],
                                placeholder=field.get("placeholder", "")
                            )
                        
                        brands_response = requests.get(f"{API_URL}/api/brand/list")
                        if brands_response.status_code == 200:
                            brands = brands_response.json().get("brands", [])
                            if brands:
                                selected_brand = st.selectbox("Brand (optional)", ["None"] + brands)
                                if selected_brand != "None":
                                    field_values["brand"] = selected_brand
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Generate Image", type="primary"):
                                prompt = template["compose"]
                                for key, value in field_values.items():
                                    prompt = prompt.replace(f"{{{key}}}", value)
                                
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": f"Generate image: {prompt}"
                                })
                                
                                with st.spinner("Generating image..."):
                                    data = {
                                        "type": "image",
                                        "prompt": prompt,
                                        "model_id": "sd-turbo"
                                    }
                                    if field_values.get("brand"):
                                        data["brand_name"] = field_values.get("brand")
                                    
                                    gen_response = requests.post(
                                        f"{API_URL}/api/generate",
                                        data=data
                                    )
                                    
                                    if gen_response.status_code == 200:
                                        result = gen_response.json()
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "Generated image successfully!",
                                            "media_url": result.get("media_url"),
                                            "media_type": "image"
                                        })
                                        st.session_state.show_template_picker = False
                                        st.rerun()
                                    else:
                                        st.error(f"Generation failed: {gen_response.text}")
                        
                        with col2:
                            if st.button("Cancel"):
                                st.session_state.show_template_picker = False
                                st.rerun()
                else:
                    st.error("Failed to load templates")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab2:
            st.markdown("#### Video Generation")
            
            try:
                response = requests.get(f"{API_URL}/api/templates?type=video")
                if response.status_code == 200:
                    templates = response.json()
                    
                    template_choice = st.selectbox(
                        "Select Template",
                        options=[t["id"] for t in templates],
                        format_func=lambda x: next(t["label"] for t in templates if t["id"] == x),
                        key="video_template"
                    )
                    
                    if template_choice:
                        template = next(t for t in templates if t["id"] == template_choice)
                        st.markdown(f"**{template['label']}**")
                        st.caption(template.get("description", ""))
                        
                        field_values = {}
                        for field in template.get("fields", []):
                            field_values[field["name"]] = st.text_input(
                                field["label"],
                                placeholder=field.get("placeholder", ""),
                                key=f"video_{field['name']}"
                            )
                        
                        uploaded_image = st.file_uploader("Starting Image (optional)", type=["png", "jpg", "jpeg"])
                        
                        brands_response = requests.get(f"{API_URL}/api/brand/list")
                        if brands_response.status_code == 200:
                            brands = brands_response.json().get("brands", [])
                            if brands:
                                selected_brand = st.selectbox("Brand (optional)", ["None"] + brands, key="video_brand")
                                if selected_brand != "None":
                                    field_values["brand"] = selected_brand
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("Generate Video", type="primary"):
                                prompt = template["compose"]
                                for key, value in field_values.items():
                                    prompt = prompt.replace(f"{{{key}}}", value)
                                
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": f"Generate video: {prompt}"
                                })
                                
                                with st.spinner("Generating video..."):
                                    data = {
                                        "type": "video",
                                        "prompt": prompt,
                                        "model_id": "svd-img2vid"
                                    }
                                    if field_values.get("brand"):
                                        data["brand_name"] = field_values.get("brand")
                                    
                                    files = {}
                                    if uploaded_image:
                                        files["image"] = ("image.png", uploaded_image.getvalue(), "image/png")
                                    
                                    gen_response = requests.post(
                                        f"{API_URL}/api/generate",
                                        data=data,
                                        files=files if files else None
                                    )
                                    
                                    if gen_response.status_code == 200:
                                        result = gen_response.json()
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "Generated video successfully!",
                                            "media_url": result.get("media_url"),
                                            "media_type": "video"
                                        })
                                        st.session_state.show_template_picker = False
                                        st.rerun()
                                    else:
                                        st.error(f"Generation failed: {gen_response.text}")
                        
                        with col2:
                            if st.button("Cancel", key="video_cancel"):
                                st.session_state.show_template_picker = False
                                st.rerun()
                else:
                    st.error("Failed to load templates")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if page == "💬 Chat":
    st.title("💬 Chat")
    st.caption("Ask me to generate images or videos for your brand")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if "media_url" in message and message.get("media_type"):
                media_url = f"{API_URL}{message['media_url']}"
                if message["media_type"] == "image":
                    st.image(media_url)
                elif message["media_type"] == "video":
                    st.video(media_url)
                
                st.download_button(
                    label=f"Download {message['media_type']}",
                    data=requests.get(media_url).content,
                    file_name=f"generated_{message['media_type']}.{'png' if message['media_type'] == 'image' else 'mp4'}",
                    mime=f"{'image/png' if message['media_type'] == 'image' else 'video/mp4'}"
                )
    
    if prompt := st.chat_input("Describe what you want to create..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["image", "picture", "photo", "poster", "banner"]):
            st.session_state.generation_type = "image"
            st.session_state.show_template_picker = True
            st.rerun()
        elif any(word in prompt_lower for word in ["video", "clip", "animate", "animation", "movie"]):
            st.session_state.generation_type = "video"
            st.session_state.show_template_picker = True
            st.rerun()
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I can help you generate images or videos! Please specify what type of content you'd like to create, or click the ➕ button to use the template picker."
            })
            st.rerun()

elif page == "📁 Brand Data":
    st.title("📁 Brand Data Management")
    st.caption("Upload brand metadata to enhance AI generation")
    
    st.markdown("### Upload Brand Data")
    
    upload_type = st.radio("File Type", ["CSV/XLSX", "PDF", "TXT"])
    
    if upload_type == "CSV/XLSX":
        uploaded_file = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx"])
        
        if uploaded_file:
            st.info("Preview and map columns to brand metadata fields")
            
            import pandas as pd
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.dataframe(df.head())
            
            st.markdown("#### Map Columns")
            col1, col2 = st.columns(2)
            with col1:
                brand_col = st.selectbox("Brand Column", df.columns)
            with col2:
                text_col = st.selectbox("Text/Details Column", df.columns)
            
            if st.button("Upload and Ingest"):
                with st.spinner("Ingesting brand data..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    data = {"brand_col": brand_col, "text_col": text_col}
                    
                    response = requests.post(
                        f"{API_URL}/api/brand/upload",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Successfully ingested {result.get('records_ingested', 0)} records for {result.get('brands_count', 0)} brands")
                    else:
                        st.error(f"Upload failed: {response.text}")
    
    elif upload_type == "PDF":
        uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
        brand_name = st.text_input("Brand Name")
        
        if uploaded_file and brand_name and st.button("Upload and Ingest"):
            with st.spinner("Processing PDF..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"brand_name": brand_name}
                
                response = requests.post(
                    f"{API_URL}/api/brand/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Successfully ingested PDF for {brand_name}")
                else:
                    st.error(f"Upload failed: {response.text}")
    
    else:  # TXT
        uploaded_file = st.file_uploader("Upload TXT file", type=["txt"])
        brand_name = st.text_input("Brand Name", key="txt_brand")
        
        if uploaded_file and brand_name and st.button("Upload and Ingest", key="txt_upload"):
            with st.spinner("Processing text file..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"brand_name": brand_name}
                
                response = requests.post(
                    f"{API_URL}/api/brand/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Successfully ingested text for {brand_name}")
                else:
                    st.error(f"Upload failed: {response.text}")
    
    st.markdown("---")
    st.markdown("### Brand Statistics")
    
    try:
        response = requests.get(f"{API_URL}/api/brand/list")
        if response.status_code == 200:
            brands = response.json().get("brands", [])
            
            if brands:
                for brand in brands:
                    with st.expander(f"📊 {brand}"):
                        stats_response = requests.get(f"{API_URL}/api/rag/stats?brandId={brand}")
                        if stats_response.status_code == 200:
                            stats = stats_response.json()
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Documents", stats.get("document_count", 0))
                            with col2:
                                st.metric("Vectors", stats.get("vector_count", 0))
                            with col3:
                                st.metric("Last Updated", stats.get("last_updated", "N/A"))
            else:
                st.info("No brands uploaded yet. Upload brand data to get started.")
    except Exception as e:
        st.error(f"Error loading brand stats: {str(e)}")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.markdown("### Model Configuration")
    
    try:
        response = requests.get(f"{API_URL}/api/models")
        if response.status_code == 200:
            models_config = response.json()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Image Models")
                for model in models_config.get("image", []):
                    st.markdown(f"- **{model['label']}** (`{model['id']}`)")
                
                default_image = models_config.get("defaults", {}).get("imageId", "sd-turbo")
                st.info(f"Default: {default_image}")
            
            with col2:
                st.markdown("#### Video Models")
                for model in models_config.get("video", []):
                    st.markdown(f"- **{model['label']}** (`{model['id']}`)")
                
                default_video = models_config.get("defaults", {}).get("videoId", "svd-img2vid")
                st.info(f"Default: {default_video}")
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("### Generation Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Image Size", value=768, min_value=256, max_value=1024, step=64)
        st.number_input("Image Steps", value=4, min_value=1, max_value=50)
    
    with col2:
        st.number_input("Video Resolution", value=512, min_value=256, max_value=1024, step=64)
        st.number_input("Video Frames", value=12, min_value=8, max_value=24)
    
    st.markdown("---")
    
    st.markdown("### Environment Configuration")
    st.caption("Read-only view of environment variables")
    
    env_vars = {
        "HF_TOKEN": "***" if os.getenv("HF_TOKEN") else "Not set",
        "ENGINE_IMAGE": os.getenv("ENGINE_IMAGE", "hf"),
        "ENGINE_VIDEO": os.getenv("ENGINE_VIDEO", "hf"),
        "IMAGE_MODEL": os.getenv("IMAGE_MODEL", "sd-turbo"),
        "VIDEO_MODEL": os.getenv("VIDEO_MODEL", "svd-img2vid"),
        "API_PORT": os.getenv("API_PORT", "8000")
    }
    
    for key, value in env_vars.items():
        st.text(f"{key}: {value}")
    
    st.info("💡 To update these values, edit the `.env` file in the backend directory")

st.markdown("---")
st.caption("🎨 AI Content Generator POC | Powered by Hugging Face")
