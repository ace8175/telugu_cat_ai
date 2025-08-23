import streamlit as st
from supabase import create_client, Client
import bcrypt
from datetime import datetime
import json
from config import SUPABASE_URL, SUPABASE_KEY

class Database:
    def __init__(self, url=SUPABASE_URL, key=SUPABASE_KEY):
        self.client = create_client(url, key)
    
    def create_user(self, email: str, password: str) -> str:
        """Create a new user"""
        try:
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insert user
            result = self.client.table('users').insert({
                'email': email,
                'password': hashed_password.decode('utf-8'),
                'created_at': datetime.now().isoformat()
            }).execute()
            
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """Authenticate user login"""
        try:
            result = self.client.table('users').select('*').eq('email', email).execute()
            
            if result.data:
                user = result.data[0]
                if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    return user
            return None
        except Exception as e:
            st.error(f"Error authenticating user: {str(e)}")
            return None
    
    def save_chat_message(self, user_id: str, user_message: str, ai_response: str, audio_file=None):
        """Save chat message to database"""
        try:
            self.client.table('chat_history').insert({
                'user_id': user_id,
                'user_message': user_message,
                'ai_response': ai_response,
                'audio_file': audio_file,
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            st.error(f"Error saving chat: {str(e)}")
    
    def get_chat_history(self, user_id: str) -> list:
        """Retrieve chat history for user"""
        try:
            result = self.client.table('chat_history')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp')\
                .execute()
            
            messages = []
            for row in result.data:
                messages.append({"role": "user", "content": row['user_message']})
                messages.append({
                    "role": "assistant", 
                    "content": row['ai_response'],
                    "audio_file": row.get('audio_file')
                })
            
            return messages
        except Exception as e:
            st.error(f"Error fetching chat history: {str(e)}")
            return []
    
    def clear_chat_history(self, user_id: str):
        """Clear chat history for user"""
        try:
            self.client.table('chat_history').delete().eq('user_id', user_id).execute()
        except Exception as e:
            st.error(f"Error clearing chat history: {str(e)}")
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user statistics"""
        try:
            # Get total messages
            messages_result = self.client.table('chat_history')\
                .select('*', count='exact')\
                .eq('user_id', user_id)\
                .execute()
            
            total_messages = len(messages_result.data) if messages_result.data else 0
            
            # Calculate days active (simplified)
            user_result = self.client.table('users')\
                .select('created_at')\
                .eq('id', user_id)\
                .execute()
            
            days_active = 1  # Simplified calculation
            
            return {
                'total_messages': total_messages,
                'days_active': days_active,
                'news_read': 0  # Placeholder
            }
        except Exception as e:
            st.error(f"Error fetching user stats: {str(e)}")
            return {'total_messages': 0, 'days_active': 0, 'news_read': 0}