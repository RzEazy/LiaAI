# LiaAI Architecture

## Overview
LiaAI is a comprehensive AI system designed to assist with various tasks. It consists of a Python backend and a React frontend, orchestrated via Docker.

## Components

### Backend (`backend/`)
- **API**: FastAPI/Flask server handling requests.
- **RAG System**: Vector database (ChromaDB) for document retrieval.
- **Core**: Main orchestrator, memory management, and safety modules.
- **Chains**: Processing chains for different tasks.

### Frontend (`frontend/`)
- **Framework**: Next.js (React).
- **Styling**: Tailwind CSS.
- **Components**: UI components including chat interface and dashboards.

### Infrastructure
- **Docker**: Containerization for both frontend and backend.
- **Scripts**: Utility scripts for setup and deployment.
