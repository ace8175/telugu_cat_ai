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
import json
import http.client
from config import SUPABASE_URL, SUPABASE_KEY

from database import Database
from ai_services import TeluguAI
from news_service import NewsService
from utils import *

# Swecha API Integration Class
class SwechaAPI:
    """
    Swecha Corpus API Integration for Telugu AI Chat
    Handles authentication, user management, and data contributions
    """
    
    def __init__(self):
        self.base_url = "api.corpus.swecha.org"
        self.conn = http.client.HTTPSConnection(self.base_url)
        self.headers = {"content-type": "application/json"}
        self.auth_token = None
    
    def _make_request(self, method, endpoint, payload=None):
        """Make HTTP request to Swecha API"""
        try:
            if payload:
                self.conn.request(method, endpoint, payload, self.headers)
            else:
                self.conn.request(method, endpoint, headers=self.headers)
            
            res = self.conn.getresponse()
            data = res.read()
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            st.error(f"API Error: {e}")
            return None
    
    # Authentication Methods
    def send_signup_otp(self, phone_number):
        """Send OTP for signup"""
        payload = json.dumps({"phone_number": phone_number})
        return self._make_request("POST", "/api/v1/auth/signup/send-otp", payload)
    
    def verify_signup_otp(self, phone_number, otp_code, name, email, password):
        """Verify OTP and complete signup"""
        payload = json.dumps({
            "phone_number": phone_number,
            "otp_code": otp_code,
            "name": name,
            "email": email,
            "password": password,
            "has_given_consent": True
        })
        return self._make_request("POST", "/api/v1/auth/signup/verify-otp", payload)
    
    def resend_signup_otp(self, phone_number):
        """Resend signup OTP"""
        payload = json.dumps({"phone_number": phone_number})
        return self._make_request("POST", "/api/v1/auth/signup/resend-otp", payload)
    
    def send_login_otp(self, phone_number):
        """Send OTP for login"""
        payload = json.dumps({"phone_number": phone_number})
        return self._make_request("POST", "/api/v1/auth/login/send-otp", payload)
    
    def verify_login_otp(self, phone_number, otp_code):
        """Verify login OTP"""
        payload = json.dumps({
            "phone_number": phone_number,
            "otp_code": otp_code
        })
        return self._make_request("POST", "/api/v1/auth/login/verify-otp", payload)
    
    def resend_login_otp(self, phone_number):
        """Resend login OTP"""
        payload = json.dumps({"phone_number": phone_number})
        return self._make_request("POST", "/api/v1/auth/login/resend-otp", payload)
    
    def get_user_profile(self):
        """Get current user profile"""
        return self._make_request("GET", "/api/v1/auth/me")
    
    def change_password(self, current_password, new_password):
        """Change user password"""
        payload = json.dumps({
            "current_password": current_password,
            "new_password": new_password
        })
        return self._make_request("POST", "/api/v1/auth/change-password", payload)
    
    def reset_password(self, phone, new_password):
        """Reset password"""
        payload = json.dumps({
            "phone": phone,
            "new_password": new_password
        })
        return self._make_request("POST", "/api/v1/auth/reset-password", payload)
    
    def forgot_password_init(self, phone_number):
        """Initialize forgot password process"""
        payload = json.dumps({"phone_number": phone_number})
        return self._make_request("POST", "/api/v1/auth/forgot-password/init", payload)
    
    def forgot_password_confirm(self, phone_number, otp_code, new_password, confirm_password):
        """Confirm forgot password with OTP"""
        payload = json.dumps({
            "phone_number": phone_number,
            "otp_code": otp_code,
            "new_password": new_password,
            "confirm_password": confirm_password
        })
        return self._make_request("POST", "/api/v1/auth/forgot-password/confirm", payload)
    
    # User Management Methods
    def get_users(self):
        """Get all users"""
        return self._make_request("GET", "/api/v1/users/")
    
    def create_user(self, phone, name, email, gender, date_of_birth, place, password, role_ids):
        """Create new user"""
        payload = json.dumps({
            "phone": phone,
            "name": name,
            "email": email,
            "gender": gender,
            "date_of_birth": date_of_birth,
            "place": place,
            "password": password,
            "role_ids": role_ids,
            "has_given_consent": True
        })
        return self._make_request("POST", "/api/v1/users/", payload)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self._make_request("GET", f"/api/v1/users/{user_id}")
    
    def update_user(self, user_id, name, email, gender, date_of_birth, place, is_active):
        """Update user information"""
        payload = json.dumps({
            "name": name,
            "email": email,
            "gender": gender,
            "date_of_birth": date_of_birth,
            "place": place,
            "is_active": is_active,
            "has_given_consent": True
        })
        return self._make_request("PUT", f"/api/v1/users/{user_id}", payload)
    
    def get_user_with_roles(self, user_id):
        """Get user with roles"""
        return self._make_request("GET", f"/api/v1/users/{user_id}/with-roles")
    
    def get_user_by_phone(self, phone):
        """Get user by phone number"""
        return self._make_request("GET", f"/api/v1/users/phone/{phone}")
    
    def get_user_contributions(self, user_id):
        """Get user contributions"""
        return self._make_request("GET", f"/api/v1/users/{user_id}/contributions")
    
    def get_user_contributions_by_type(self, user_id, media_type):
        """Get user contributions by media type"""
        return self._make_request("GET", f"/api/v1/users/{user_id}/contributions/{media_type}")
    
    # Role Management Methods
    def get_roles(self):
        """Get all roles"""
        return self._make_request("GET", "/api/v1/roles/")
    
    def create_role(self, name, description):
        """Create new role"""
        payload = json.dumps({
            "name": name,
            "description": description
        })
        return self._make_request("POST", "/api/v1/roles/", payload)
    
    def get_role_by_id(self, role_id):
        """Get role by ID"""
        return self._make_request("GET", f"/api/v1/roles/{role_id}")
    
    def get_user_roles(self, user_id):
        """Get user roles"""
        return self._make_request("GET", f"/api/v1/users/{user_id}/roles")
    
    def assign_user_roles(self, user_id, role_ids):
        """Assign roles to user"""
        payload = json.dumps(role_ids)
        return self._make_request("POST", f"/api/v1/users/{user_id}/roles", payload)
    
    # Category Management Methods
    def get_categories(self):
        """Get all categories"""
        return self._make_request("GET", "/api/v1/categories/")
    
    def create_category(self, name, title, description, published, rank):
        """Create new category"""
        payload = json.dumps({
            "name": name,
            "title": title,
            "description": description,
            "published": published,
            "rank": rank
        })
        return self._make_request("POST", "/api/v1/categories/", payload)
    
    def get_category_by_id(self, category_id):
        """Get category by ID"""
        return self._make_request("GET", f"/api/v1/categories/{category_id}")
    
    def delete_category(self, category_id):
        """Delete category"""
        return self._make_request("DELETE", f"/api/v1/categories/{category_id}")
    
    # Records Management Methods
    def get_records(self):
        """Get all records"""
        return self._make_request("GET", "/api/v1/records/")
    
    def create_record(self, title, description, media_type, file_url, file_name, 
                     file_size, location, release_rights, language, user_id, category_id):
        """Create new record"""
        payload = json.dumps({
            "title": title,
            "description": description,
            "media_type": media_type,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "status": "pending",
            "location": location,
            "reviewed": False,
            "release_rights": release_rights,
            "language": language,
            "user_id": user_id,
            "category_id": category_id
        })
        return self._make_request("POST", "/api/v1/records/", payload)
    
    def get_record_by_id(self, record_id):
        """Get record by ID"""
        return self._make_request("GET", f"/api/v1/records/{record_id}")
    
    def update_record(self, record_id, title, description, media_type, file_url, 
                     file_name, file_size, status, location, reviewed, reviewed_by, 
                     release_rights, language):
        """Update record"""
        payload = json.dumps({
            "title": title,
            "description": description,
            "media_type": media_type,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "status": status,
            "location": location,
            "reviewed": reviewed,
            "reviewed_by": reviewed_by,
            "release_rights": release_rights,
            "language": language
        })
        return self._make_request("PATCH", f"/api/v1/records/{record_id}", payload)
    
    def upload_record(self, title, description, media_type, file_url, file_name, 
                     file_size, location, release_rights, language, user_id, category_id):
        """Upload record"""
        payload = json.dumps({
            "title": title,
            "description": description,
            "media_type": media_type,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "status": "pending",
            "location": location,
            "reviewed": False,
            "release_rights": release_rights,
            "language": language,
            "user_id": user_id,
            "category_id": category_id
        })
        return self._make_request("POST", "/api/v1/records/upload", payload)
    
    def search_nearby_records(self, latitude, longitude, radius):
        """Search records nearby"""
        return self._make_request("GET", "/api/v1/records/search/nearby")
    
    def search_records_by_bbox(self, min_lat, min_lon, max_lat, max_lon):
        """Search records by bounding box"""
        return self._make_request("GET", "/api/v1/records/search/bbox")
    
    def get_record_url(self, record_id):
        """Get record URL"""
        return self._make_request("GET", f"/api/v1/records/{record_id}/record-url")
    
    # Task Management Methods
    def export_data(self, task_name):
        """Export data task"""
        payload = json.dumps({
            "task_id": str(uuid.uuid4()),
            "task_name": task_name,
            "status": "pending",
            "message": "Export task initiated"
        })
        return self._make_request("POST", "/api/v1/tasks/export-data", payload)


# Page configuration
st.set_page_config(
    page_title="Telugu AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize services
@st.cache_resource
def init_services():
    try:
        # Check if environment variables are loaded
        if not SUPABASE_URL:
            st.warning("⚠️ SUPABASE_URL is not set. Database features will be limited.")
            db = None
        else:
            try:
                db = Database(SUPABASE_URL, SUPABASE_KEY)
                # Test connection
                db.client.table('users').select('count', count='exact').limit(1).execute()
                st.success("✅ Supabase connected successfully!")
            except Exception as e:
                st.warning(f"⚠️ Supabase connection failed: {e}. Using local session only.")
                db = None
        
        ai = TeluguAI()
        news = NewsService()
        swecha_api = SwechaAPI()
        
        return db, ai, news, swecha_api
    except Exception as e:
        st.error(f"❌ Error initializing services: {e}")
        return None, None, None, None


def generate_tts_fixed(text, lang="te"):
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


def chat_interface(db, ai, swecha_api):
    st.title("💬 Telugu Chat Assistant")
    st.write("Telugu మరియు English రెండు భాషలలో టైప్ చేయండి - AI తెల���గులో జవాబిస్తుంది")

    # Initialize session ID for conversation tracking
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        if hasattr(st.session_state, "save_history") and st.session_state.save_history:
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
            with st.spinner("ఆలోచ���స్తున్నాను..."):
                try:
                    response = ai.generate_response(prompt)
                    st.markdown(response)

                    # Generate TTS audio if voice output is enabled
                    audio_file = None
                    if hasattr(
                        st.session_state, "voice_output"
                    ) and st.session_state.get("voice_output", True):
                        audio_file = generate_tts_fixed(response, lang="te")
                        if audio_file:
                            st.audio(audio_file)

                    # Add assistant response
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                            "audio_file": audio_file,
                        }
                    )

                    # Save to database if enabled
                    if (
                        hasattr(st.session_state, "save_history")
                        and st.session_state.save_history
                    ):
                        try:
                            db.save_chat_message(
                                st.session_state.user_id,
                                prompt,
                                response,
                                base64.b64encode(audio_file).decode()
                                if audio_file
                                else None,
                            )
                        except Exception as e:
                            print(f"Error saving chat: {e}")

                    # Enhanced Swecha API integration for corpus building
                    if st.session_state.get("contribute_to_swecha", False) and st.session_state.get("swecha_authenticated", False):
                        try:
                            # Detect language of the conversation
                            user_lang = ai.detect_language(prompt)
                            response_lang = ai.detect_language(response)
                            
                            # Create structured conversation data for LLM training
                            conversation_data = {
                                "conversation_id": str(uuid.uuid4()),
                                "timestamp": datetime.now().isoformat(),
                                "user_input": {
                                    "text": prompt,
                                    "language": user_lang,
                                    "length": len(prompt)
                                },
                                "ai_response": {
                                    "text": response,
                                    "language": response_lang,
                                    "length": len(response)
                                },
                                "context": {
                                    "conversation_turn": len(st.session_state.messages) // 2,
                                    "session_id": st.session_state.get("session_id", str(uuid.uuid4())),
                                    "user_id": st.session_state.get("swecha_user_id", "anonymous")
                                },
                                "metadata": {
                                    "domain": "conversational_ai",
                                    "quality": "human_verified",
                                    "source": "telugu_ai_chat",
                                    "version": "1.0"
                                }
                            }
                            
                            # Determine primary language for categorization
                            primary_language = "telugu" if user_lang in ["telugu", "mixed"] or response_lang in ["telugu", "mixed"] else "english"
                            
                            # Create record in Swecha corpus
                            swecha_api.create_record(
                                title=f"Telugu AI Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                description=json.dumps(conversation_data, ensure_ascii=False, indent=2),
                                media_type="text",
                                file_url="",
                                file_name=f"conversation_{conversation_data['conversation_id']}.json",
                                file_size=len(json.dumps(conversation_data)),
                                location=st.session_state.get("user_location", {"latitude": 17.385, "longitude": 78.4867}),
                                release_rights="creator",
                                language=primary_language,
                                user_id=st.session_state.get("swecha_user_id", ""),
                                category_id=st.session_state.get("swecha_category_id", "")
                            )
                            
                            # Update contribution counter
                            if "swecha_contributions" not in st.session_state:
                                st.session_state.swecha_contributions = 0
                            st.session_state.swecha_contributions += 1
                            
                        except Exception as e:
                            print(f"Error contributing to Swecha: {e}")
                            # Don't show error to user to avoid interrupting chat flow

                except Exception as e:
                    error_response = "క్షమించండి, ప్రస్తుతం సమస్య ఉంది. దయచేసి మళ్లీ ప్రయత్నించండి."
                    st.markdown(error_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_response}
                    )


def news_interface(news):
    st.title("📰 Telugu News Summary")
    st.write("తెలుగు వార్తల సంక్షిప్త సమాచారం")

    # Create columns for refresh button and status
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔄 Refresh News", type="primary"):
            st.session_state.news_loading = True

    # Load news
    if (
        st.button("📥 Load Latest News", type="secondary")
        or "news_data" not in st.session_state
    ):
        with st.spinner("వార్తలు తెస్తున్నాము..."):
            try:
                news_data = news.get_telugu_news()
                st.session_state.news_data = news_data
                st.success(f"✅ {len(news_data)} వార్తలు లోడ్ అయ్యాయి")
            except Exception as e:
                st.error(f"వార్తలు లోడ్ చేయడంలో సమస్య: {e}")
                st.session_state.news_data = []

    # Display news
    if "news_data" in st.session_state and st.session_state.news_data:
        st.subheader(f"📈 తాజా వార్తలు ({len(st.session_state.news_data)})")

        for idx, article in enumerate(
            st.session_state.news_data[:8]
        ):  # Show top 8 articles
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
                            audio_file = generate_tts_fixed(
                                article["summary"], lang="te"
                            )
                            if audio_file:
                                st.audio(audio_file)
                            else:
                                st.warning("ఆడియో తయారు చేయడంలో సమస్య")

                    # Read more link
                    if article.get("link") and article["link"] != "#":
                        st.markdown(f"[📖 పూర్తిగా చదవండి]({article['link']})")

    else:
        st.info("వార్తలు లోడ్ చేయడానికి 'Load Latest News' బటన్ నొక్కండి")


def swecha_integration_interface(swecha_api):
    """Swecha API Integration Interface"""
    st.title("🌐 Swecha Corpus Integration")
    st.write("తెలుగు భాష డేటా సేకరణ మరియు సహకారం")
    
    # Create tabs for different Swecha features
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Authentication", "👥 User Management", "📊 Contributions", "📁 Categories"])
    
    with tab1:
        st.subheader("🔐 Swecha Authentication")
        
        # Phone-based authentication
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Sign Up with Phone**")
            phone_signup = st.text_input("📱 Phone Number", key="phone_signup")
            
            if st.button("📤 Send Signup OTP", key="send_signup_otp"):
                if phone_signup:
                    result = swecha_api.send_signup_otp(phone_signup)
                    if result:
                        st.success("✅ OTP sent successfully!")
                        st.session_state.signup_phone = phone_signup
                    else:
                        st.error("❌ Failed to send OTP")
            
            if "signup_phone" in st.session_state:
                otp_code = st.text_input("🔢 Enter OTP", key="signup_otp")
                name = st.text_input("👤 Name", key="signup_name")
                email = st.text_input("📧 Email", key="signup_email")
                password = st.text_input("🔒 Password", type="password", key="signup_password")
                
                if st.button("✅ Verify & Sign Up", key="verify_signup"):
                    if all([otp_code, name, email, password]):
                        result = swecha_api.verify_signup_otp(
                            st.session_state.signup_phone, otp_code, name, email, password
                        )
                        if result:
                            st.success("✅ Account created successfully!")
                            st.session_state.swecha_authenticated = True
                        else:
                            st.error("❌ Verification failed")
        
        with col2:
            st.write("**Login with Phone**")
            phone_login = st.text_input("📱 Phone Number", key="phone_login")
            
            if st.button("📤 Send Login OTP", key="send_login_otp"):
                if phone_login:
                    result = swecha_api.send_login_otp(phone_login)
                    if result:
                        st.success("✅ OTP sent successfully!")
                        st.session_state.login_phone = phone_login
                    else:
                        st.error("❌ Failed to send OTP")
            
            if "login_phone" in st.session_state:
                login_otp = st.text_input("🔢 Enter OTP", key="login_otp")
                
                if st.button("🚀 Verify & Login", key="verify_login"):
                    if login_otp:
                        result = swecha_api.verify_login_otp(
                            st.session_state.login_phone, login_otp
                        )
                        if result:
                            st.success("✅ Login successful!")
                            st.session_state.swecha_authenticated = True
                        else:
                            st.error("❌ Login failed")
    
    with tab2:
        st.subheader("👥 User Management")
        
        if st.session_state.get("swecha_authenticated", False):
            # Get user profile
            if st.button("👤 Get My Profile"):
                profile = swecha_api.get_user_profile()
                if profile:
                    st.json(profile)
                else:
                    st.error("Failed to fetch profile")
            
            # Get all users (admin feature)
            if st.button("👥 Get All Users"):
                users = swecha_api.get_users()
                if users:
                    st.json(users)
                else:
                    st.error("Failed to fetch users")
            
            # User search by phone
            search_phone = st.text_input("🔍 Search User by Phone")
            if st.button("🔍 Search") and search_phone:
                user = swecha_api.get_user_by_phone(search_phone)
                if user:
                    st.json(user)
                else:
                    st.error("User not found")
        else:
            st.warning("Please authenticate first to access user management features.")
    
    with tab3:
        st.subheader("📊 Data Contributions")
        
        if st.session_state.get("swecha_authenticated", False):
            # Contribution form
            st.write("**Contribute Data**")
            
            contrib_title = st.text_input("📝 Title")
            contrib_description = st.text_area("📄 Description")
            contrib_type = st.selectbox("📁 Media Type", ["text", "audio", "video", "image", "document"])
            contrib_language = st.selectbox("🌐 Language", ["telugu", "hindi", "english", "tamil", "kannada"])
            
            if st.button("📤 Submit Contribution"):
                if contrib_title and contrib_description:
                    result = swecha_api.create_record(
                        title=contrib_title,
                        description=contrib_description,
                        media_type=contrib_type,
                        file_url="",
                        file_name=f"{contrib_title}.txt",
                        file_size=len(contrib_description),
                        location={"latitude": 17.385, "longitude": 78.4867},
                        release_rights="creator",
                        language=contrib_language,
                        user_id=st.session_state.get("swecha_user_id", ""),
                        category_id=""
                    )
                    if result:
                        st.success("✅ Contribution submitted successfully!")
                    else:
                        st.error("❌ Failed to submit contribution")
            
            # View contributions
            if st.button("📊 View My Contributions"):
                user_id = st.session_state.get("swecha_user_id", "")
                if user_id:
                    contributions = swecha_api.get_user_contributions(user_id)
                    if contributions:
                        st.json(contributions)
                    else:
                        st.error("Failed to fetch contributions")
            
            # View all records
            if st.button("📋 View All Records"):
                records = swecha_api.get_records()
                if records:
                    st.json(records)
                else:
                    st.error("Failed to fetch records")
        else:
            st.warning("Please authenticate first to access contribution features.")
    
    with tab4:
        st.subheader("📁 Categories Management")
        
        if st.session_state.get("swecha_authenticated", False):
            # View categories
            if st.button("📋 View Categories"):
                categories = swecha_api.get_categories()
                if categories:
                    st.json(categories)
                else:
                    st.error("Failed to fetch categories")
            
            # Create category
            st.write("**Create New Category**")
            cat_name = st.text_input("📝 Category Name")
            cat_title = st.text_input("📰 Category Title")
            cat_description = st.text_area("📄 Category Description")
            cat_published = st.checkbox("📢 Published")
            cat_rank = st.number_input("🔢 Rank", min_value=0, value=0)
            
            if st.button("➕ Create Category"):
                if cat_name and cat_title:
                    result = swecha_api.create_category(
                        name=cat_name,
                        title=cat_title,
                        description=cat_description,
                        published=cat_published,
                        rank=cat_rank
                    )
                    if result:
                        st.success("✅ Category created successfully!")
                    else:
                        st.error("❌ Failed to create category")
        else:
            st.warning("Please authenticate first to access category management.")


def main():
    # Load custom CSS
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    # Initialize services
    db, ai, news, swecha_api = init_services()

    if not ai or not news or not swecha_api:
        st.error("🚫 కొన్ని సేవలు లోడ్ కాలేదు. దయచేసి పేజీ రిఫ్రెష్ చేయండి.")
        return

    # Sidebar
    with st.sidebar:
        st.title("🤖 Telugu AI Assistant")
        st.markdown("---")

        # User Authentication
        if "user_id" not in st.session_state:
            st.subheader("🔐 Login / Sign Up")

            if db is None:
                # Local session mode when database is not available
                st.info("🔄 Database not connected. Using local session mode.")
                
                email = st.text_input("���� Email (for session only)")
                
                if st.button("🚀 Start Session", type="primary", use_container_width=True):
                    if email:
                        st.session_state.user_id = str(uuid.uuid4())
                        st.session_state.user_email = email
                        st.session_state.save_history = False  # Can't save without DB
                        st.session_state.voice_output = True
                        st.success("✅ సెషన్ ప్రారంభమైంది!")
                        st.rerun()
                    else:
                        st.warning("దయచేసి ఇమెయిల్ ఎంటర్ చేయండి")
            else:
                # Database mode
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
                                    st.session_state.user_id = user["id"]
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
                    if st.button(
                        "📝 Create Account", type="primary", use_container_width=True
                    ):
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
                value=st.session_state.get("save_history", True),
                help="చాట్ చరిత్రను డేటాబేస్‌లో సేవ్ చేయాలా?",
            )
            st.session_state.save_history = save_history

            # Voice settings
            st.subheader("🔊 Voice Settings")

            voice_output = st.toggle(
                "🔊 Voice Output",
                value=st.session_state.get("voice_output", True),
                help="AI సమాధానాలను వాయిస్‌లో వినాలా?",
            )
            st.session_state.voice_output = voice_output

            # Swecha integration settings
            st.subheader("🌐 Swecha Integration")
            
            contribute_to_swecha = st.toggle(
                "🤝 Contribute to Swecha",
                value=st.session_state.get("contribute_to_swecha", False),
                help="చాట్ సంభాషణలను Swecha కార్పస్‌కు సహకరించాలా?",
            )
            st.session_state.contribute_to_swecha = contribute_to_swecha
            
            # Show contribution statistics if enabled
            if contribute_to_swecha and st.session_state.get("swecha_authenticated", False):
                contributions_count = st.session_state.get("swecha_contributions", 0)
                st.metric("🤝 Contributions Made", contributions_count)
                
                if contributions_count > 0:
                    st.success(f"✅ మీరు {contributions_count} సంభాషణలను కార్పస్‌కు సహకరించారు!")
            elif contribute_to_swecha and not st.session_state.get("swecha_authenticated", False):
                st.warning("⚠️ Swecha లో లాగిన్ చేయండి")
                st.info("Swecha టాబ్‌లో వెళ్లి ఆథెంటికేట్ చేయండి")

            st.markdown("---")

            # Logout button
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    # Main content
    if "user_id" in st.session_state:
        # Create tabs for different features
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📰 News", "🌐 Swecha", "👤 Profile"])

        with tab1:
            chat_interface(db, ai, swecha_api)

        with tab2:
            news_interface(news)

        with tab3:
            swecha_integration_interface(swecha_api)

        with tab4:
            profile_interface(db)

    else:
        # Welcome screen for non-logged-in users
        st.markdown("""
        # 🤖 Telugu AI Assistant కి స్వాగతం!
        
        ### ✨ Features:
        - **💬 Telugu & English Chat** - రెండు భాషలలో మాట్లాడండి
        - **🔊 Voice Output** - తెలుగులో వినండి  
        - **📰 Telugu News** - తాజా తెలుగు వార్తలు
        - **🌐 Swecha Integration** - తెలుగు భాష డేటా సహకారం
        - **🔒 Secure** - మీ డేటా సురక్షితం
        - **📱 Mobile Friendly** - అన్ని పరికరాలలో వాడండి
        
        ### 🚀 ప్రారంభించడానికి:
        1. **సైడ్‌బార్‌లో లాగిన్ చేయండి** లేదా **కొత్త అకౌంట్ సృష్టించండి**
        2. **Chat టాబ్‌లో** తెలుగు లేదా ఇంగ్లీష్‌లో టైప్ చేయండి
        3. **News టాబ్‌లో** తాజా వార్తలు చూడండి
        4. **Swecha టాబ్‌లో** తెలుగు భాష డేటా సహకారం చేయండి
        
        ---
        *Made with ❤️ for Telugu speakers*
        """)

        # Demo section
        st.subheader("🎯 Demo Conversation:")

        demo_messages = [
            {"role": "user", "content": "Hello, how are you?"},
            {
                "role": "assistant",
                "content": "నమస్కారం! నేను బాగానే ఉన్నాను, ధన్యవాదాలు! మీరు ఎలా ఉన్నారు? నేను మీకు ఎలా సహాయం చేయగలను?",
            },
            {"role": "user", "content": "మీరు ఏమి చేయగలరు?"},
            {
                "role": "assistant",
                "content": "నేను మీకు అనేక విధాలుగా సహాయం చేయగలను:\n- తెలుగు మరియు ఇంగ్లీష్ రెండు భాషలలో మాట్లాడగలను\n- తాజా తెలుగు వార్తలు చెప్పగలను\n- మీ ప్రశ్నలకు జవాబులు ఇవ్వగలను\n- సలహాలు మరియు సహాయం అందించగలను\n- Swecha కార్పస్‌కు డేటా సహకారం చేయగలను",
            },
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
                label="💬 Total Messages", value=user_stats.get("total_messages", 0)
            )

        with col2:
            st.metric(label="📅 Days Active", value=user_stats.get("days_active", 0))

        with col3:
            st.metric(label="📰 News Read", value=user_stats.get("news_read", 0))

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
        st.write(
            f"- Save Chat History: {'✅ Yes' if st.session_state.get('save_history', True) else '❌ No'}"
        )
        st.write(
            f"- Voice Output: {'🔊 Enabled' if st.session_state.get('voice_output', True) else '🔇 Disabled'}"
        )
        st.write(
            f"- Swecha Contribution: {'🤝 Enabled' if st.session_state.get('contribute_to_swecha', False) else '❌ Disabled'}"
        )
        st.write(f"- Account: {st.session_state.user_email}")

        # Swecha integration status
        st.subheader("🌐 Swecha Integration Status")
        if st.session_state.get("swecha_authenticated", False):
            st.success("✅ Connected to Swecha Corpus")
        else:
            st.warning("⚠️ Not connected to Swecha Corpus")
            st.info("Go to the Swecha tab to authenticate and start contributing to Telugu language data collection.")

    except Exception as e:
        st.error(f"ప్రొఫైల్ ���ోడ్ చేయడంలో ఎర్రర్: {e}")


if __name__ == "__main__":
    main()
