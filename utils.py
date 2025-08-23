import streamlit as st
import base64
import io
import tempfile
import os

def encode_audio_to_base64(audio_bytes):
    """Encode audio bytes to base64 string"""
    if audio_bytes:
        return base64.b64encode(audio_bytes).decode()
    return None

def create_download_link(file_content, filename, text="Download"):
    """Create a download link for file content"""
    b64 = base64.b64encode(file_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove any potential harmful characters
    sanitized = text.replace("<", "&lt;").replace(">", "&gt;")
    return sanitized.strip()

def format_chat_message(message, is_user=True):
    """Format chat message for display"""
    role = "user" if is_user else "assistant"
    timestamp = message.get("timestamp", "")
    content = sanitize_input(message.get("content", ""))
    
    return {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }

@st.cache_data
def load_telugu_font():
    """Load Telugu font for better text rendering"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap');
    
    .telugu-text {
        font-family: 'Noto Sans Telugu', sans-serif;
        line-height: 1.6;
    }
    </style>
    """

def create_chat_container():
    """Create a styled chat container"""
    return st.container()