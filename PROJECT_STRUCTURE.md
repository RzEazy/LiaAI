# LiaAI Project Structure

```
LiaAI-2/
├── 📁 backend/                      # Python FastAPI Backend
│   ├── 📁 chains/                   # LangChain implementations
│   ├── 📁 core/                     # Core functionality
│   │   ├── lia_main.py             # Main LIA AI logic
│   │   └── ...
│   ├── 📁 models/                   # Data models
│   ├── 📁 rag/                      # RAG (Retrieval Augmented Generation)
│   ├── 📁 services/                 # Business logic services
│   ├── 📁 utils/                    # Utility functions
│   ├── app.py                       # FastAPI application entry point
│   ├── requirements.txt             # Python dependencies
│   └── ...
│
├── 📁 frontend/                     # Next.js 14 Frontend
│   ├── 📁 public/                   # Static assets
│   ├── 📁 src/
│   │   ├── 📁 app/                  # Next.js App Router
│   │   │   ├── favicon.ico
│   │   │   ├── globals.css          # Global styles with Tailwind
│   │   │   ├── layout.tsx           # Root layout
│   │   │   └── page.tsx             # Home page
│   │   │
│   │   └── 📁 components/           # React components
│   │       ├── 📁 chat/
│   │       │   └── ChatInterface.tsx # Main chat interface
│   │       └── 📁 ui/               # Reusable UI components
│   │           └── alert.tsx
│   │
│   ├── .eslintrc.json
│   ├── .gitignore
│   ├── next.config.js               # Next.js configuration
│   ├── package.json                 # Node dependencies
│   ├── postcss.config.js            # PostCSS configuration
│   ├── tailwind.config.ts           # Tailwind CSS configuration
│   └── tsconfig.json                # TypeScript configuration
│
├── 📁 docker/                       # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── 📁 scripts/                      # Utility scripts
│   ├── setup.sh
│   ├── run_backend.sh
│   ├── run_frontend.sh
│   └── ...
│
├── 📁 tests/                        # Test files
│   ├── 📁 backend/
│   ├── 📁 frontend/
│   └── ...
│
├── 📁 Docs/                         # Documentation
│   ├── API.md
│   └── SETUP.md
│
├── .env.example                     # Environment variables template
├── .gitignore
├── ARCHITECTURE.md                  # Architecture documentation
├── README.md                        # Project README
└── shell.nix                        # Nix shell configuration
```

## 📦 Key Technologies

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **UI**: Custom components with glassmorphism

### Backend
- **Framework**: FastAPI (Python)
- **AI**: LangChain
- **RAG**: Custom implementation
- **Database**: (To be configured)

## 🚀 Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
# API runs on http://localhost:8000
```

## 📝 Important Files

### Frontend Configuration
- `frontend/src/app/globals.css` - Global styles with CSS variables
- `frontend/tailwind.config.ts` - Tailwind configuration
- `frontend/next.config.js` - Next.js settings

### Backend Configuration
- `backend/app.py` - FastAPI application
- `backend/requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## 🎨 Design System

The frontend uses a dark theme with:
- **Glassmorphism** effects
- **Gradient** backgrounds
- **Custom** CSS variables
- **Smooth** animations
- **Responsive** design

## 🔧 Development

### Frontend Development
- Hot reload enabled
- TypeScript strict mode
- ESLint configured
- Tailwind JIT mode

### Backend Development
- FastAPI auto-reload
- API documentation at `/docs`
- CORS enabled for development
