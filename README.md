# 📚 Study Mate - AI-Powered PDF Learning Assistant

> **Demo Video**: [🎥 Watch Demo]()

**Study Mate** is an intelligent PDF learning companion that transforms how you interact with documents. Upload PDFs and engage with them through voice conversations, generate mind maps, create podcasts, and extract insights—all powered by cutting-edge AI technology.

> 🏆 **Created for TKRES Hackathon 2025** (29th & 30th August 2025)
> An innovative solution showcasing AI-powered document interaction and learning enhancement
> 💡 Competing for ₹15,000 Winner Prize | Team Innovation Challenge

## 🏆 TKRES Hackathon 2025 Submission

This project was developed for the **TKRES Hackathon 2025**, demonstrating innovation in AI-powered educational technology.

### 📅 Hackathon Details
- **Event**: TKRES Hackathon 2025
- **Dates**: 29th & 30th August 2025
- **Bootcamp**: 25th – 28th August 2025
- **Timings**: 9:40 AM – 4:20 PM
- **Prizes**: 🏆 Winner – ₹15,000 | 🥈 Runner – ₹10,000
- **Registration**: [CodeTapasya Hackathon](https://www.codetapasya.com/hackathon)

### 🎯 Innovation Focus
Study Mate addresses the challenge of making document learning more interactive and accessible through:
- **Voice-First Interaction**: Natural conversation with PDFs
- **Page-Specific Queries**: Ask questions about specific pages or sections
- **AI-Powered Insights**: Generate summaries, mind maps, and podcasts
- **Multi-Modal Learning**: Visual, auditory, and text-based learning support

## ✨ Features Overview

### 📚 Document Management
- **PDF Upload & Processing**: Drag-and-drop upload with intelligent text extraction
- **Document Library**: Centralized storage and management of PDF collections
- **Adobe PDF Viewer**: Rich viewing experience with text selection and highlights
- **Semantic Search**: AI-powered search across document content using vector embeddings

### 🤖 AI-Powered Intelligence
- **Enhanced Talk to PDF**: 🆕 RAG-based conversational interface with page-specific queries
  - Ask questions about specific pages: "What's on page 5?"
  - Query page ranges: "Summarize pages 3 to 7"
  - Natural language page targeting: "What does page 10 say about..."
  - Voice and text input support with Azure TTS output
- **Smart Insights**: LLM-generated insights from selected text or document sections
- **Content Recommendations**: AI-suggested related sections and documents
- **Knowledge Graphs**: Visual representation of document relationships

### 🎨 Content Generation
- **Mindmap Creation**: Generate interactive mindmaps in Mermaid and FreeMind formats
- **Podcast Generation**: Convert documents into engaging AI-generated audio discussions
- **Text-to-Speech**: Azure TTS with SSML support and multiple voice options
- **Audio Export**: Download generated podcasts and TTS audio

### 🔍 Advanced Search & Analysis
- **Vector Search**: Semantic similarity search across document collections
- **Section Analysis**: Automatic document structure detection and extraction
- **Multi-document Insights**: Cross-document analysis and recommendations

## 🏅 Technical Achievements (Hackathon Highlights)

### 🆕 Latest Enhancements for TKRES 2025
- **Page-Specific AI Queries**: Revolutionary feature allowing users to ask questions about specific PDF pages
- **Enhanced Chat Intelligence**: Smart query parsing that detects page numbers in natural language
- **Dual Search Architecture**: Page-first search with fallback to semantic section search
- **Real-time Page Indicators**: Visual feedback showing which pages were referenced in responses

### 🔧 Technical Innovation Stack
- **Frontend**: React 19 + Vite + TailwindCSS for modern, responsive UI
- **Backend**: FastAPI + MongoDB for high-performance API and data storage
- **AI Integration**: Google Gemini Pro for LLM capabilities + Azure TTS for voice synthesis
- **Document Processing**: PyMuPDF + PDFMiner for advanced PDF text extraction and page analysis
- **Search Technology**: Sentence Transformers for semantic search + custom text-based fallback

### 🎯 Problem-Solution Fit
**Problem**: Students struggle with large PDF documents, unable to quickly find and discuss specific content
**Solution**: AI-powered conversational interface with precise page targeting and multi-modal interaction

## 🚀 Docker Setup

### Prerequisites
- Docker and Docker Compose installed
- API keys for Google Gemini and Azure TTS
- Adobe Embed API key

### Quick Start
```bash
# 1. Clone the repository
git clone https://github.com/Avinashreddy48/Study-Mate.git
cd Study-Mate

# 2. Configure environment variables (see below)
# Create backend/.env and frontend/.env files

# 3. Start the application
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Commands
```bash
# Production deployment
docker compose up --build

# Stop services
docker compose down


```

## 🔧 Environment Variables

### Backend Configuration (`backend/.env`)
```env
# Database Configuration
MONGO_CONNECTION_STRING=mongodb://mongo:27017
MONGO_DATABASE_NAME=adobe-hackies

# LLM Provider Settings
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=your_google_credentials

# Text-to-Speech Configuration
TTS_PROVIDER=azure
AZURE_TTS_KEY=your_azure_tts_key_here
AZURE_TTS_ENDPOINT=your_azure_tts_endpoint


```

### Frontend Configuration (`frontend/.env`)
```env
# Adobe PDF Viewer
ADOBE_EMBED_API_KEY=2a66854b8d8344dd9823037c42db2295

```

### Required API Keys

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `GOOGLE_API_KEY` in backend/.env

#### Azure Text-to-Speech
1. Create Azure Cognitive Services resource
2. Get subscription key and region
3. Add to `AZURE_TTS_KEY` and `AZURE_TTS_ENDPOINT`

#### Adobe Embed API Key
1. Visit [Adobe Developer Console](https://developer.adobe.com/console)
2. Create new project and add PDF Embed API
3. Add to `ADOBE_EMBED_API_KEY` in frontend/.env

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python), MongoDB, Google Gemini LLM, Azure TTS
- **Frontend**: React 19 + Vite, Adobe Document Cloud SDK, TailwindCSS
- **Infrastructure**: Docker, Docker Compose, Multi-stage builds
- **AI/ML**: Sentence Transformers, Vector Search, RAG Pipeline
- **Database**: MongoDB with Motor async driver

## 📁 Project Structure

```
adobe-hackies-final-v1/
├── backend/                    # FastAPI Python Backend
│   ├── api/v1/endpoints/      # API endpoints for all features
│   ├── services/              # AI services and business logic
│   ├── core/                  # Configuration and settings
│   └── db/                    # Database connections
├── frontend/                  # React + Vite Frontend
│   ├── src/components/        # React components
│   └── src/services/          # API client services
├── docker-compose.yml         # Production deployment
├── docker-compose.dev.yml     # Development environment
└── Dockerfile                # Multi-stage build configuration
```

## 🚨 Troubleshooting

### Common Issues
- **MongoDB Connection**: Ensure MongoDB is running and connection string is correct
- **API Keys**: Verify all required API keys are set in environment files
- **Docker Issues**: Try `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
- **Port Conflicts**: Ensure ports 8000 and 8080/5173 are available

### Support
For detailed implementation guides:
- Backend API documentation: See `backend/README.md`
- Frontend development guide: See `frontend/README.md`

---

## 🏆 TKRES Hackathon 2025

**Study Mate** represents our commitment to innovation in educational technology. This project demonstrates how AI can transform traditional document interaction into an engaging, conversational learning experience.

### 🎯 Hackathon Goals Achieved
✅ **Innovation**: Page-specific AI queries - first of its kind
✅ **User Experience**: Voice-first, intuitive interface
✅ **Technical Excellence**: Robust full-stack architecture
✅ **Problem Solving**: Addresses real student learning challenges

### 🚀 Future Roadmap
- Multi-language document support
- Collaborative study sessions
- Advanced analytics and learning insights
- Mobile application development

**Team**: Passionate developers creating the future of AI-powered learning
**Event**: TKRES Hackathon 2025 | 29th & 30th August 2025
**Registration**: [CodeTapasya Hackathon](https://www.codetapasya.com/hackathon)
