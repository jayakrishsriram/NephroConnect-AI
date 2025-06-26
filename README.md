# 🏥 NephroConnect AI

A sophisticated multi-agent AI system designed to provide post-discharge support for nephrology patients. This system combines patient database lookups, RAG (Retrieval-Augmented Generation) with medical literature, and intelligent agent routing to provide personalized medical assistance.

## 🌟 Features

### Multi-Agent Architecture
- **Receptionist Agent**: Handles patient identification, administrative queries, and routing
- **Clinical Agent**: Provides evidence-based medical responses using RAG and web search
- **Smart Routing**: Automatically routes queries to appropriate agents based on content analysis

### Core Capabilities
- 📋 Patient discharge report lookup from JSON database
- 📚 RAG-powered medical reference system using comprehensive nephrology literature
- 🔍 Fallback web search when RAG is unavailable
- 💬 Real-time chat interface with session management
- 📊 Interaction logging and session tracking
- ⚠️ Built-in medical disclaimers and safety warnings

### Technical Features
- FastAPI-based REST API backend
- Real-time web interface with modern UI
- Google Gemini integration for LLM capabilities
- FAISS vector store for efficient document retrieval
- Session-based conversation management
- CORS-enabled for cross-origin requests
- **Comprehensive logging system** with file and console output
- **Structured error handling** and monitoring capabilities

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│   FastAPI App    │───▶│  Agent System   │
│  (HTML/JS/CSS)  │    │    (app.py)      │    │   (agent.py)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                         ┌──────────────┐    ┌─────────────────────┐
                         │   Sessions   │    │     Tools Layer    │
                         │   Storage    │    │                     │
                         └──────────────┘    │ ┌─────────────────┐ │
                                             │ │ DatabaseTool    │ │
                                             │ │ (JSON lookup)   │ │
                                             │ └─────────────────┘ │
                                             │ ┌─────────────────┐ │
                                             │ │   RAGTool       │ │
                                             │ │ (Vector Store)  │ │
                                             │ └─────────────────┘ │
                                             │ ┌─────────────────┐ │
                                             │ │  Web Search     │ │
                                             │ │ (DuckDuckGo)    │ │
                                             │ └─────────────────┘ │
                                             └─────────────────────┘
```

## 📁 Project Structure

```
├── agent.py                      # Multi-agent system core with logging
├── app.py                        # FastAPI web application
├── discharge_reports.json        # Patient database
├── requirements.txt              # Python dependencies
├── comprehensive-clinical-nephrology.pdf  # Medical reference
├── rag.ipynb                     # RAG Creation setup notebook
├── nephro_connect.log            # System log file (auto-generated)
├── static/
│   ├── index.html               # Web interface
│   ├── script.js                # Frontend JavaScript
│   └── style.css                # Styling
└── vector_store/
    ├── index.faiss              # FAISS vector index
    └── index.pkl                # Vector store metadata
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API key for Gemini AI
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jayakrishsriram/NephroConnect-AI.git
   cd NephroConnect-AI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Google API key**
   - Get a Google AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Replace the API key in `agent.py` line 19:
   ```python
   os.environ["GOOGLE_API_KEY"] = "your-api-key-here"
   ```

4. **Set up the RAG system (if needed)**
   - Run the `rag.ipynb` notebook to create the vector store from the PDF
   - This will populate the `vector_store/` directory

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:8000`
   - The web interface will be available immediately

## 💬 Usage Guide

### For Patients
1. **Start a conversation** by providing your full name
2. **Ask questions** about your medications, symptoms, or discharge instructions
3. **Get personalized responses** based on your discharge report and medical literature
4. **View interaction logs** to track your session

### Sample Interactions
```
Patient: "John Smith"
Assistant: "Hi John Smith! I found your discharge report from 2024-01-15 for Chronic Kidney Disease Stage 3. How are you feeling today? Are you following your medication schedule?"

Patient: "I'm having some swelling in my legs. Is this normal?"
Assistant: [Clinical Agent provides evidence-based response with RAG citations]

Patient: "When is my next appointment?"
Assistant: [Receptionist Agent handles administrative query]
```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key

### Database Configuration
- Patient data is stored in `discharge_reports.json`
- Add new patients by following the existing JSON structure:
```json
{
  "patient_name": "Patient Name",
  "discharge_date": "YYYY-MM-DD",
  "primary_diagnosis": "Diagnosis",
  "medications": ["Med 1", "Med 2"],
  "dietary_restrictions": "Restrictions",
  "follow_up": "Follow-up instructions",
  "warning_signs": "Signs to watch for",
  "discharge_instructions": "General instructions"
}
```

### RAG System Setup
If the RAG system shows as unavailable:
1. Open and run `rag.ipynb` notebook
2. Ensure `comprehensive-clinical-nephrology.pdf` is in the project directory
3. The notebook will create the vector store in `vector_store/` directory

### Logging Configuration
NephroConnect AI includes comprehensive logging:
- **Log File**: `nephro_connect.log` (auto-created in project directory)
- **Console Output**: Real-time logging to terminal
- **Log Levels**: INFO, WARNING, ERROR with timestamps
- **Coverage**: All system components, patient lookups, agent routing, and API calls

**Sample log entries:**
```
2025-06-26 10:30:15 - __main__ - INFO - Initializing SimpleMultiAgentSystem
2025-06-26 10:30:16 - __main__ - INFO - Successfully loaded 15 patient reports
2025-06-26 10:30:17 - __main__ - INFO - ✅ Found discharge report for John Smith
2025-06-26 10:30:18 - __main__ - INFO - 🏥 Query identified as medical - routing to Clinical Agent
```

## 🛠️ API Endpoints

### Main Endpoints
- `GET /` - Web interface
- `POST /chat` - Chat API endpoint
- `GET /logs/{session_id}` - Session logs
- `GET /health` - Health check

### Chat API Usage
```python
import requests from json

response = requests.post("http://localhost:8000/chat", json={
    "message": "John Smith",
    "session_id": "unique-session-id"
})

data = response.json()
print(data["response"])
```

## 🏥 Medical Safety Features

### Built-in Safeguards
- ⚠️ **Medical disclaimers** on all clinical responses
- 🔄 **Healthcare provider reminders** for all medical advice
- 📚 **Evidence-based responses** using peer-reviewed literature
- 🚫 **No diagnostic claims** - focuses on education and support
- 📝 **Comprehensive interaction logging** for accountability and monitoring
- 🔍 **Error tracking** and system health monitoring

### Limitations
- This system is for **educational and support purposes only**
- **Not a replacement** for professional medical advice
- **Always consult healthcare providers** for medical decisions
- **RAG system requires setup** for full functionality

## 🔍 Troubleshooting

### Common Issues

**RAG System Not Available**
- Run the `rag.ipynb` notebook to create the vector store
- Ensure the PDF file is in the correct location
- Check Google API key configuration

**Patient Not Found**
- Verify patient name spelling matches `discharge_reports.json`
- Names are case-insensitive but must match exactly

**Web Interface Issues**
- Check that the server is running on port 8000
- Ensure static files are in the `static/` directory
- Check browser console for JavaScript errors

**Dependencies Issues**
```bash
pip install --upgrade -r requirements.txt
```

**Log File Issues**
- Check `nephro_connect.log` for detailed error information
- Log file is created automatically in the project directory
- Use log entries to trace system behavior and debug issues

## 🧪 Development

### System Monitoring
- **Log Analysis**: Monitor `nephro_connect.log` for system health
- **Performance Tracking**: Track response times and error rates
- **Usage Analytics**: Analyze patient interaction patterns

### Testing
- Test patient lookup with existing names from `discharge_reports.json`
- Try medical queries like "medication side effects", "dietary restrictions"
- Test both clinical and administrative queries
- Monitor log output for proper agent routing and error handling

### Extending the System
- **Add new agents**: Extend the routing logic in `_handle_medical_query()`
- **New data sources**: Modify `DatabaseTool` for different data formats
- **Enhanced RAG**: Add more medical literature to the vector store
- **Custom UI**: Modify files in the `static/` directory

## 📚 Dependencies

### Core Dependencies
- `fastapi` - Web framework
- `langchain` - LLM orchestration
- `langchain-google-genai` - Google Gemini integration
- `faiss-cpu` - Vector similarity search
- `duckduckgo-search` - Web search fallback

### Full Dependencies
See `requirements.txt` for complete list with versions.

## 📄 License

This project is for educational and research purposes. Please ensure compliance with medical software regulations in your jurisdiction before any clinical use.

## 🤝 Contributing

This is a research/educational project. When extending:
1. Follow medical software best practices
2. Include appropriate disclaimers
3. Test thoroughly with sample data
4. Document any changes to the agent routing logic

## 📞 Support

For technical issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure Google API key is properly configured
4. Check that all required files are present

---

**⚠️ Important Medical Disclaimer**: This AI assistant is for educational and informational purposes only. It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with questions about medical conditions, medications, or treatment plans.
