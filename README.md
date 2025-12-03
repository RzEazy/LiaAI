# LiaAI — 0.3.0

LiaAI has evolved into a modular, LLM-powered cyber-OS assistant with three core capabilities:

1. **Natural Language Chat** - General conversation and assistance
2. **OS Command Execution** - Safe execution of system commands
3. **Osquery Security Engine** - Security questioning and system forensics

## 🏗️ Architecture

```
lia_ai/
├── core/                  # Core modules (router, memory, safety)
├── chains/                # Processing chains (chat, OS, osquery)
├── tools/                 # Formatting and utility tools
├── engines/               # Execution engines (OS, osquery)
├── utils/                 # Utilities and templates
├── app.py                 # Main application entry point
└── lia_ai.py              # Legacy implementation (deprecated)
```

## 🚀 Features

- **Intent Classification**: Automatically routes requests to the appropriate processor
- **OS Command Execution**: Converts natural language to safe system commands
- **Osquery Integration**: Translates security questions to osquery SQL and executes them
- **Memory Management**: Remembers conversations and previous queries
- **Safety Controls**: Comprehensive protection against dangerous operations
- **Tabular Output**: Clean, readable results formatting

## 🛠️ Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install osquery:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install osquery
   
   # macOS
   brew install osquery
   
   # Windows
   Download from https://osquery.io/downloads
   ```

## ▶️ Usage

Run the application:
```bash
python app.py
```

Then interact with LiaAI using natural language:

### Chat Examples
- "Hello, how are you?"
- "What can you help me with?"

### OS Command Examples
- "Create a folder called projects"
- "List all files in the current directory"
- "Show me the disk usage"

### Osquery Examples
- "Show me all running processes"
- "What network ports are listening?"
- "Are there any suspicious login attempts?"
- "List all users on this system"
- "Show me recently modified files"

## 🛡️ Safety Features

- Blocks dangerous OS commands (`rm -rf`, `format`, etc.)
- Prevents destructive osquery operations (`DROP`, `DELETE`, `INSERT`)
- Protects against SQL injection attacks
- Sanitizes sensitive data from results
- Implements timeouts to prevent hanging operations

## 🧩 Modular Design

The new architecture makes it easy to extend LiaAI with additional capabilities:

- Add new processing chains in `chains/`
- Implement new tools in `tools/`
- Extend execution engines in `engines/`
- Customize core functionality in `core/`

## 🔮 Future Expansion Opportunities

- Anomaly detection
- Persistence scanning
- Real-time monitoring
- Fleet-wide querying
- Self-healing automations
- Threat hunting packs

## 📄 License

MIT