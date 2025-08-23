import streamlit as st
import requests
import json
from langdetect import detect, DetectorFactory
import re
import random
from config import HUGGINGFACE_TOKEN

# Set seed for consistent language detection
DetectorFactory.seed = 0

class TeluguAI:
    def __init__(self):
        self.hf_token = HUGGINGFACE_TOKEN
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        # Fallback responses
        self.telugu_responses = {
            "greeting": [
                "నమస్కారం! మీరు ఎలా ఉన్నారు? నేను మీకు ఎలా సహాయం చేయగలను?",
                "హలో! చాలా సంతోషం మిమ్మల్ని కలవడం. మీకు ఏమి కావాలి?",
                "వందనలు! నేను మీ తెలుగు AI అసిస్టెంట్. నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను."
            ],
            "howaru": [
                "నేను బాగానే ఉన్నాను, ధన్యవాదాలు! మీరు ఎలా ఉన్నారు?",
                "చాలా బాగున్నాను! మీ సంగతేంటి?",
                "అద్భుతంగా ఉన్నాను! మీతో మాట్లాడడం చాలా సంతోషంగా ఉంది."
            ],
            "help": [
                "అవును, నేను మీకు సహాయం చేస్తాను! మీకు ఏమి కావాలి?",
                "నేను ఇక్కడ మీకు సహాయం చేయడానికే ఉన్నాను. ఏదైనా అడగండి.",
                "మీకు ఎలాంటి సహాయం కావాలి? నేను చేయగలిగిన వరకు సహాయం చేస్తాను."
            ],
            "thanks": [
                "మీకు స్వాగతం! ఇంకా ఏదైనా కావాలా?",
                "పర్వాలేదు! ఎల్లప్పుడూ సహాయం చేయడానికి సిద్ధంగా ఉన్నాను.",
                "సంతోషం! మరేదైనా అడగండి."
            ],
            "default": [
                "మీ మాట చాలా ఆసక్తికరంగా ఉంది. మరింత వివరంగా చెప్పగలరా?",
                "బాగుంది! దీని గురించి మరింత మాట్లాడుదాం.",
                "ఆసక్తికరమైన విషయం. మీరు ఇంకా ఏమైనా చెప్పాలనుకుంటున్నారా?",
                "అర్థమైంది. మీకు ఇంకేమైనా తెలుసుకోవాలనుకుంటున్నారా?",
                "మంచి ప్రశ్న! నేను దీని గురించి ఆలోచిస్తున్నాను."
            ]
        }
        
        self.english_to_telugu = {
            "hello": "greeting",
            "hi": "greeting", 
            "hey": "greeting",
            "namaste": "greeting",
            "namaskar": "greeting",
            "how are you": "howaru",
            "how r u": "howaru",
            "what's up": "howaru",
            "help": "help",
            "can you help": "help",
            "assist": "help",
            "support": "help",
            "thank you": "thanks",
            "thanks": "thanks",
            "thank u": "thanks"
        }
    
    def detect_language(self, text):
        """Detect if text is Telugu, English, or mixed"""
        # Check for Telugu script
        telugu_pattern = re.compile(r'[\u0C00-\u0C7F]')
        has_telugu = bool(telugu_pattern.search(text))
        
        # Check for English
        english_pattern = re.compile(r'[a-zA-Z]')
        has_english = bool(english_pattern.search(text))
        
        if has_telugu and has_english:
            return "mixed"
        elif has_telugu:
            return "telugu"
        elif has_english:
            return "english"
        else:
            return "unknown"
    
    def query_huggingface(self, text):
        """Query Hugging Face API"""
        if not self.hf_token or self.hf_token == "":
            return None
            
        try:
            payload = {"inputs": text}
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').replace(text, '').strip()
            return None
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return None
    
    def get_telugu_response_category(self, text):
        """Determine response category based on input"""
        text_lower = text.lower()
        
        # Telugu keyword patterns
        telugu_greetings = ["నమస్కారం", "హలో", "హాయ్", "వందనలు"]
        telugu_howaru = ["ఎలా ఉన్నారు", "ఎలా ఉన్నావు", "సంగతేంటి"]
        telugu_help = ["సహాయం", "హెల్ప్", "సపోర్ట్"]
        telugu_thanks = ["ధన్యవాదాలు", "థాంక్ యు", "కృతజ్ఞతలు"]
        
        # Check Telugu patterns
        for greeting in telugu_greetings:
            if greeting in text:
                return "greeting"
        
        for howaru in telugu_howaru:
            if howaru in text:
                return "howaru"
                
        for help_word in telugu_help:
            if help_word in text:
                return "help"
                
        for thanks in telugu_thanks:
            if thanks in text:
                return "thanks"
        
        # Check English patterns
        for eng_phrase, category in self.english_to_telugu.items():
            if eng_phrase in text_lower:
                return category
        
        return "default"
    
    def generate_response(self, user_input: str) -> str:
        """Generate AI response supporting both English and Telugu"""
        try:
            if not user_input.strip():
                return "దయచేసి ఏదైనా టైప్ చేయండి."
            
            # Clean input
            user_input = user_input.strip()
            
            # Detect language
            lang = self.detect_language(user_input)
            
            # Try Hugging Face API first if available
            if self.hf_token:
                hf_response = self.query_huggingface(user_input)
                if hf_response and len(hf_response) > 10:
                    # If HF gives English response but user prefers Telugu, translate concept
                    if lang in ["telugu", "mixed"]:
                        return self.adapt_response_to_telugu(hf_response, user_input)
                    return hf_response
            
            # Fallback to rule-based responses
            category = self.get_telugu_response_category(user_input)
            
            if category in self.telugu_responses:
                responses = self.telugu_responses[category]
                return random.choice(responses)
            else:
                return random.choice(self.telugu_responses["default"])
                
        except Exception as e:
            print(f"Error in generate_response: {e}")
            return "క్షమించండి, ప్రస్తుతం నేను సరిగ్గా జవాబు ఇవ్వలేకపోతున్నాను. దయచేసి మళ్లీ ప్రయత్నించండి."
    
    def adapt_response_to_telugu(self, english_response, original_input):
        """Adapt English response to Telugu context"""
        # Simple adaptation - in production, use proper translation
        adaptations = {
            "hello": "నమస్కారం",
            "hi": "హాయ్",
            "how are you": "మీరు ఎలా ఉన్నారు",
            "good": "బాగుంది",
            "great": "అద్భుతం",
            "thank you": "ధన్యవాదాలు",
            "welcome": "స్వాగతం",
            "yes": "అవును",
            "no": "లేదు",
            "sorry": "క్షమించండి",
            "please": "దయచేసి"
        }
        
        adapted_response = english_response.lower()
        for eng, tel in adaptations.items():
            adapted_response = adapted_response.replace(eng, tel)
        
        # If adaptation didn't work well, use fallback
        if len(adapted_response) < 10 or adapted_response == english_response.lower():
            category = self.get_telugu_response_category(original_input)
            return random.choice(self.telugu_responses.get(category, self.telugu_responses["default"]))
        
        return adapted_response.capitalize()