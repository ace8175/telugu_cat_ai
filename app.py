import streamlit as st
import asyncio
import os
from datetime import datetime
import base64
import io
from gtts import gTTS
import tempfile
import uuid
import sys
from config import SUPABASE_URL, SUPABASE_KEY

from database import Database
from ai_services import TeluguAI
from news_service import NewsService
from utils import *

# Page configuration
st.set_page_config(
    page_title="Telugu AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    try:
        db = Database(SUPABASE_URL, SUPABASE_KEY)
        ai = TeluguAI()  # or pass keys if needed
        news = NewsService()
        return db, ai, news
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None

def generate_tts_fixed(text, lang='te'):
    """Generate Text-to-Speech audio with better error handling"""
    try:
        if not text or len(text.strip()) == 0:
            return None
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Use BytesIO instead of temp file to avoid file access issues
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.getvalue()
        
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        st.warning("వాయిస్ ఔట్‌పుట్ ప్రస్తుతం అందుబాటులో లేదు.")
        return None

def chat_interface(db, ai):
    st.title("💬 Telugu Chat Assistant")
    st.write("Telugu మరియు English రెండు భాషలలో టైప్ చేయండి - AI తెలుగులో జవాబిస్తుంది")
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        if hasattr(st.session_state, 'save_history') and st.session_state.save_history:
            # Load chat history from database
            try:
                history = db.get_chat_history(st.session_state.user_id)
                st.session_state.messages = history
            except:
                st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("audio_file"):
                try:
                    st.audio(message["audio_file"])
                except:
                    pass  # Skip audio if there's an issue
    
    # Chat input with better handling
    prompt = st.chat_input("Telugu లేదా English లో టైప్ చేయండి...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("ఆలోచిస్తున్నాను..."):
                try:
                    response = ai.generate_response(prompt)
                    st.markdown(response)
                    
                    # Generate TTS audio if voice output is enabled
                    audio_file = None
                    if hasattr(st.session_state, 'voice_output') and st.session_state.get('voice_output', True):
                        audio_file = generate_tts_fixed(response, lang='te')
                        if audio_file:
                            st.audio(audio_file)
                    
                    # Add assistant response
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "audio_file": audio_file
                    })
                    
                    # Save to database if enabled
                    if hasattr(st.session_state, 'save_history') and st.session_state.save_history:
                        try:
                            db.save_chat_message(
                                st.session_state.user_id,
                                prompt,
                                response,
                                base64.b64encode(audio_file).decode() if audio_file else None
                            )
                        except Exception as e:
                            print(f"Error saving chat: {e}")
                
                except Exception as e:
                    error_response = "క్షమించండి, ప్రస్తుతం సమస్య ఉంది. దయచేసి మళ్లీ ప్రయత్నించండి."
                    st.markdown(error_response)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_response
                    })

def news_interface(news):
    st.title("📰 Telugu News Summary")
    st.write("తెలుగు వార్తల సంక్షిప్త సమాచారం")
    
    # Create columns for refresh button and status
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Refresh News", type="primary"):
            st.session_state.news_loading = True
    
    # Load news
    if st.button("📥 Load Latest News", type="secondary") or 'news_data' not in st.session_state:
        with st.spinner("వార్తలు తెస్తున్నాము..."):
            try:
                news_data = news.get_telugu_news()
                st.session_state.news_data = news_data
                st.success(f"✅ {len(news_data)} వార్తలు లోడ్ అయ్యాయి")
            except Exception as e:
                st.error(f"వార్తలు లోడ్ చేయడంలో సమస్య: {e}")
                st.session_state.news_data = []
    
    # Display news
    if 'news_data' in st.session_state and st.session_state.news_data:
        st.subheader(f"📈 తాజా వార్తలు ({len(st.session_state.news_data)})")
        
        for idx, article in enumerate(st.session_state.news_data[:8]):  # Show top 8 articles
            with st.expander(f"📰 {article['title'][:80]}..."):
                
                # Article content
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**సారాంశం:** {article['summary']}")
                    st.write(f"**మూలం:** {article['source']}")
                    st.write(f"**సమయం:** {article['published']}")
                
                with col2:
                    # Listen button for TTS
                    if st.button(f"🔊 వినండి", key=f"listen_{idx}"):
                        with st.spinner("ఆడియో తయారు చేస్తున్నాం..."):
                            audio_file = generate_tts_fixed(article['summary'], lang='te')
                            if audio_file:
                                st.audio(audio_file)
                            else:
                                st.warning("ఆడియో తయారు చేయడంలో సమస్య")
                    
                    # Read more link
                    if article.get('link') and article['link'] != '#':
                        st.markdown(f"[📖 పూర్తిగా చదవండి]({article['link']})")
    
    else:
        st.info("వార్తలు లోడ్ చేయడానికి 'Load Latest News' బటన్ నొక్కండి")

def main():
    # Load custom CSS
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap');
    
    .telugu-text, .stMarkdown, .stTextInput input, .stChatMessage {
        font-family: 'Noto Sans Telugu', sans-serif !important;
        font-size: 16px !important;
        line-height: 1.6;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize services
    db, ai, news = init_services()
    
    if not db or not ai or not news:
        st.error("🚫 సేవలు లోడ్ కాలేదు. దయచేసి పేజీ రిఫ్రెష్ చేయండి.")
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 Telugu AI Assistant")
        st.markdown("---")
        
        # User Authentication
        if 'user_id' not in st.session_state:
            st.subheader("🔐 Login / Sign Up")
            
            # Toggle between login and signup
            auth_mode = st.radio("Choose Action:", ["Login", "Sign Up"])
            
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Password", type="password")
            
            if auth_mode == "Login":
                if st.button("🚀 Login", type="primary", use_container_width=True):
                    if email and password:
                        try:
                            user = db.authenticate_user(email, password)
                            if user:
                                st.session_state.user_id = user['id']
                                st.session_state.user_email = email
                                st.session_state.save_history = True
                                st.session_state.voice_output = True
                                st.success("✅ లాగిన్ విజయవంతం!")
                                st.rerun()
                            else:
                                st.error("❌ తప్పు ఇమెయిల్ లేదా పాస్‌వర్డ్")
                        except Exception as e:
                            st.error(f"లాగిన్ ఎర్రర్: {e}")
                    else:
                        st.warning("దయచేసి ఇమెయిల్ మరియు పాస్‌వర్డ్ ఎంటర్ చేయండి")
            
            else:  # Sign Up
                if st.button("📝 Create Account", type="primary", use_container_width=True):
                    if email and password:
                        if len(password) < 6:
                            st.error("పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి")
                        else:
                            try:
                                user_id = db.create_user(email, password)
                                if user_id:
                                    st.session_state.user_id = user_id
                                    st.session_state.user_email = email
                                    st.session_state.save_history = True
                                    st.session_state.voice_output = True
                                    st.success("✅ అకౌంట్ సృష్టించబడింది!")
                                    st.rerun()
                                else:
                                    st.error("❌ ఈ ఇమెయిల్ ఇప్పటికే ఉపయోగంలో ఉంది")
                            except Exception as e:
                                st.error(f"సైన్అప్ ఎర్రర్: {e}")
                    else:
                        st.warning("దయచేసి ఇమెయిల్ మరియు పాస్‌వర్డ్ ఎంటర్ చేయండి")
            
        else:
            # User is logged in
            st.success(f"🙏 స్వాగతం!\n**{st.session_state.user_email}**")
            st.markdown("---")
            
            # Settings
            st.subheader("⚙️ Settings")
            
            # Chat history toggle
            save_history = st.toggle(
                "💾 Save Chat History", 
                value=st.session_state.get('save_history', True),
                help="చాట్ చరిత్రను డేటాబేస్‌లో సేవ్ చేయాలా?"
            )
            st.session_state.save_history = save_history
            
            # Voice settings
            st.subheader("🔊 Voice Settings")
            
            voice_output = st.toggle(
                "🔊 Voice Output", 
                value=st.session_state.get('voice_output', True),
                help="AI సమాధానాలను వాయిస్‌లో వినాలా?"
            )
            st.session_state.voice_output = voice_output
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Main content
    if 'user_id' in st.session_state:
        # Create tabs for different features
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📰 News", "👤 Profile"])
        
        with tab1:
            chat_interface(db, ai)
        
        with tab2:
            news_interface(news)
        
        with tab3:
            profile_interface(db)
    
    else:
        # Welcome screen for non-logged-in users
        st.markdown("""
        # 🤖 Telugu AI Assistant కి స్వాగతం!
        
        ### ✨ Features:
        - **💬 Telugu & English Chat** - రెండు భాషలలో మాట్లాడండి
        - **🔊 Voice Output** - తెలుగులో వినండి  
        - **📰 Telugu News** - తాజా తెలుగు వార్తలు
        - **🔒 Secure** - మీ డేటా సురక్షితం
        - **📱 Mobile Friendly** - అన్ని పరికరాలలో వాడండి
        
        ### 🚀 ప్రారంభించడానికి:
        1. **సైడ్‌బార్‌లో లాగిన్ చేయండి** లేదా **కొత్త అకౌంట్ సృష్టించండి**
        2. **Chat టాబ్‌లో** తెలుగు లేదా ఇంగ్లీష్‌లో టైప్ చేయండి
        3. **News టాబ్‌లో** తాజా వార్తలు చూడండి
        
        ---
        *Made with ❤️ for Telugu speakers*
        """)
        
        # Demo section
        st.subheader("🎯 Demo Conversation:")
        
        demo_messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "నమస్కారం! నేను బాగానే ఉన్నాను, ధన్యవాదాలు! మీరు ఎలా ఉన్నారు? నేను మీకు ఎలా సహాయం చేయగలను?"},
            {"role": "user", "content": "మీరు ఏమి చేయగలరు?"},
            {"role": "assistant", "content": "నేను మీకు అనేక విధాలుగా సహాయం చేయగలను:\n- తెలుగు మరియు ఇంగ్లీష్ రెండు భాషలలో మాట్లాడగలను\n- తాజా తెలుగు వార్తలు చెప్పగలను\n- మీ ప్రశ్నలకు జవాబులు ఇవ్వగలను\n- సలహాలు మరియు సహాయం అందించగలను"}
        ]
        
        for message in demo_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

def profile_interface(db):
    st.title("👤 User Profile")
    
    try:
        user_stats = db.get_user_stats(st.session_state.user_id)
        
        # Display stats in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="💬 Total Messages", 
                value=user_stats.get('total_messages', 0)
            )
        
        with col2:
            st.metric(
                label="📅 Days Active", 
                value=user_stats.get('days_active', 0)
            )
        
        with col3:
            st.metric(
                label="📰 News Read", 
                value=user_stats.get('news_read', 0)
            )
        
        st.markdown("---")
        
        # Account management
        st.subheader("🔧 Account Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat History", type="secondary"):
                try:
                    db.clear_chat_history(st.session_state.user_id)
                    st.session_state.messages = []
                    st.success("✅ చాట్ చరిత్ర క్లియర్ అయింది!")
                except Exception as e:
                    st.error(f"❌ ఎర్రర్: {e}")
        
        with col2:
            if st.button("📁 Export Chat Data", type="secondary"):
                st.info("ఈ ఫీచర్ త్వరలో అందుబాటులో ఉంటుంది")
        
        # User preferences
        st.subheader("⚙️ Preferences")
        
        st.write("**Current Settings:**")
        st.write(f"- Save Chat History: {'✅ Yes' if st.session_state.get('save_history', True) else '❌ No'}")
        st.write(f"- Voice Output: {'🔊 Enabled' if st.session_state.get('voice_output', True) else '🔇 Disabled'}")
        st.write(f"- Account: {st.session_state.user_email}")
        
    except Exception as e:
        st.error(f"प్రొఫైల్ లోడ్ చేయడంలో ఎర్రర్: {e}")

if __name__ == "__main__":
    main()