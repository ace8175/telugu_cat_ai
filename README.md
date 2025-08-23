# Telugu AI Chat Assistant 🤖

A modern AI-powered chat assistant that supports Telugu language with voice capabilities and news summarization.

## Features

✅ **Telugu Text & Voice Chat** - Type or speak in Telugu, get AI responses
✅ **Telugu News Summarizer** - Latest news from Telugu sources  
✅ **AI Companion Mode** - Friendly conversational AI
✅ **User Authentication** - Secure login with chat history
✅ **Voice Output** - Text-to-speech in Telugu
✅ **Mobile Responsive** - Works on all devices

## Technology Stack

- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **AI Models**: Transformers, DialoGPT
- **Speech**: gTTS, SpeechRecognition
- **News**: RSS Feeds from Telugu sources

## Quick Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd telugu-ai-chat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Supabase Database

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Run these SQL commands in SQL Editor:

```sql
-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat history table
CREATE TABLE chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    audio_file BYTEA,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (true);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view own chat history" ON chat_history FOR SELECT USING (true);
CREATE POLICY "Users can insert own chat history" ON chat_history FOR INSERT WITH CHECK (true);
```

### 4. Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in your Supabase credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 5. Run Application
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Add environment variables in "Advanced settings"
5. Deploy!

## Project Structure

```
telugu-ai-chat/
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── config.py          # Configuration
├── database.py        # Database operations
├── ai_services.py     # AI model services
├── news_service.py    # News fetching
├── utils.py           # Utilities
├── .streamlit/
│   └── config.toml    # Streamlit config
├── assets/
│   └── style.css      # Styling
└── README.md          # Documentation
```

## Usage

1. **Sign Up/Login** - Create account or login
2. **Chat** - Type in Telugu or English, get Telugu responses
3. **Voice** - Toggle voice input/output in sidebar
4. **News** - Check latest Telugu news summaries
5. **Settings** - Control chat history saving

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create GitHub issue
- Email: support@teluguai.com

## Roadmap

**Phase 2 Features:**
- Advanced Telugu NLP models
- Image input for news scanning  
- Personalized daily briefings
- End-to-end encryption
- More AI skills (jokes, study help)