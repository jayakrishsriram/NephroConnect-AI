import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import SystemMessage
from langchain_community.tools import DuckDuckGoSearchRun

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nephro_connect.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBlvXS-P2zhMJ3HsXk57H75MXg56__Xwrk"

class AgentState:
    """State shared between agents - using regular class instead of dataclass"""
    def __init__(self):
        self.patient_name = ""
        self.discharge_report = {}
        self.conversation_history = []
        self.current_query = ""
        self.agent_response = ""
        self.interaction_log = []

class DatabaseTool:
    """Tool to retrieve patient discharge reports from JSON database"""
    
    def __init__(self, db_path: str = "discharge_reports.json"):
        self.db_path = db_path
        logger.info(f"Initializing DatabaseTool with path: {db_path}")
        self.reports = self._load_reports()  # Loads JSON data into memory
    
    def _load_reports(self) -> List[Dict]:
        try:
            logger.info(f"Loading patient reports from {self.db_path}")
            with open(self.db_path, 'r') as f:
                reports = json.load(f)  # Reads the JSON file
            logger.info(f"Successfully loaded {len(reports)} patient reports")
            return reports
        except FileNotFoundError:
            logger.error(f"Database file {self.db_path} not found")
            print(f"Database file {self.db_path} not found")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {self.db_path}: {e}")
            print(f"Error parsing JSON from {self.db_path}: {e}")
            return []
    
    def get_patient_report(self, patient_name: str) -> Dict:
        """Retrieve discharge report for a specific patient"""
        logger.info(f"Searching for patient: {patient_name}")
        for report in self.reports:
            if report.get("patient_name", "").lower() == patient_name.lower():
                logger.info(f"Found discharge report for patient: {patient_name}")
                return report  # Returns matching patient data
        logger.warning(f"No discharge report found for patient: {patient_name}")
        return {}

class RAGTool:
    """RAG tool for querying nephrology reference materials"""
    
    def __init__(self):
        self.vector_store_path = "./vector_store"
        logger.info("Initializing RAGTool")
        self.qa_chain = self._setup_rag()
    
    def _setup_rag(self):
        """Set up RAG chain with vector store"""
        try:
            logger.info("Setting up RAG system...")
            print("Setting up RAG system...")
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001"
            )
            logger.info("✅ Embeddings initialized")
            print("✅ Embeddings initialized")
            
            if os.path.exists(self.vector_store_path):
                logger.info(f"✅ Vector store found at {self.vector_store_path}")
                print(f"✅ Vector store found at {self.vector_store_path}")
                try:
                    # Try loading with the parameter first
                    vector_store = FAISS.load_local(
                        self.vector_store_path, 
                        embeddings,
                        allow_dangerous_deserialization=True
                    )
                    logger.info("✅ Vector store loaded successfully")
                    print("✅ Vector store loaded successfully")
                except TypeError:
                    # If parameter not supported, try without it
                    logger.warning("⚠️ Trying to load without deserialization parameter...")
                    print("⚠️ Trying to load without deserialization parameter...")
                    vector_store = FAISS.load_local(
                        self.vector_store_path, 
                        embeddings
                    )
                    logger.info("✅ Vector store loaded successfully")
                    print("✅ Vector store loaded successfully")
                except (KeyError, AttributeError) as compatibility_error:
                    logger.error(f"⚠️ Vector store compatibility issue: {compatibility_error}")
                    print(f"⚠️ Vector store compatibility issue: {compatibility_error}")
                    print("📝 Please recreate your vector store by running the RAG notebook again.")
                    return None
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash", 
                    temperature=0.3,
                    convert_system_message_to_human=True
                )
                logger.info("✅ LLM initialized")
                print("✅ LLM initialized")
                
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
                    return_source_documents=True
                )
                logger.info("✅ RAG chain created successfully")
                print("✅ RAG chain created successfully")
                return qa_chain
            else:
                logger.error(f"❌ Vector store not found at {self.vector_store_path}")
                print(f"❌ Vector store not found at {self.vector_store_path}")
                return None
        except Exception as e:
            logger.error(f"❌ Error setting up RAG: {e}")
            print(f"❌ Error setting up RAG: {e}")
            return None
    
    def query_nephrology_reference(self, query: str) -> str:
        """Query the nephrology reference materials"""
        logger.info(f"Querying RAG system with: {query[:100]}...")
        if not self.qa_chain:
            logger.warning("RAG system not available")
            return "RAG system not available - please recreate the vector store"
        
        try:
            response = self.qa_chain({"query": query})
            answer = response["result"]
            sources = response.get("source_documents", [])
            
            if sources:
                logger.info(f"RAG query successful, found {len(sources)} source documents")
                answer += f"\n\n[Citations: Based on {len(sources)} references from comprehensive clinical nephrology text]"
            else:
                logger.info("RAG query successful, no source documents returned")
            
            return answer
        except Exception as e:
            logger.error(f"Error querying reference materials: {e}")
            return f"Error querying reference materials: {e}"

class SimpleMultiAgentSystem:
    
    def __init__(self):
        logger.info("Initializing SimpleMultiAgentSystem")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.db_tool = DatabaseTool()  # Creates database connection
        self.rag_tool = RAGTool()
        self.web_search = DuckDuckGoSearchRun()
        logger.info("✅ SimpleMultiAgentSystem initialized successfully")
    
    def chat(self, user_input: str, state: Optional[AgentState] = None):
        """Main chat interface"""
        logger.info(f"Chat request received: {user_input[:100]}...")
        if state is None:
            state = AgentState()
            logger.info("Created new AgentState")
        
        # Add to conversation history
        state.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "type": "user_input"
        })
        
        # Determine if we need patient name
        if not state.patient_name:
            logger.info("No patient name found, handling initial interaction")
            # First interaction - ask for name or set name
            if user_input.strip():
                # Check if this looks like a name
                if len(user_input.split()) >= 2 and not any(word in user_input.lower() for word in ['help', 'hello', 'hi']):
                    state.patient_name = user_input
                    logger.info(f"Patient name set to: {state.patient_name}")
                    return self._handle_patient_lookup(state)
                else:
                    logger.info("User input doesn't look like a name, asking for name")
                    state.agent_response = "Hello! Welcome to the nephrology clinic. Could you please provide your full name so I can look up your discharge information?"
            else:
                logger.info("Empty user input, asking for name")
                state.agent_response = "Hello! Welcome to the nephrology clinic. Could you please provide your full name so I can look up your discharge information?"
        
        # If we have patient name but haven't done lookup yet
        elif state.patient_name and not state.discharge_report:
            logger.info(f"Have patient name ({state.patient_name}) but no discharge report, doing lookup")
            return self._handle_patient_lookup(state)
        
        # Handle medical queries
        else:
            logger.info(f"Processing medical query for patient: {state.patient_name}")
            state.current_query = user_input
            return self._handle_medical_query(state)
        
        return state
    
    def _handle_patient_lookup(self, state: AgentState):
        """Handle patient database lookup"""
        logger.info(f"Handling patient lookup for: {state.patient_name}")
        discharge_report = self.db_tool.get_patient_report(state.patient_name)  # Queries database
        
        if discharge_report:
            state.discharge_report = discharge_report
            logger.info(f"✅ Found discharge report for {state.patient_name}")
            
            # Simple, direct greeting
            state.agent_response = f"Hi {state.patient_name}! I found your discharge report from {discharge_report.get('discharge_date', 'N/A')} for {discharge_report.get('primary_diagnosis', 'N/A')}. How are you feeling today? Are you following your medication schedule?"
            
            # Log interaction
            state.interaction_log.append({
                "timestamp": datetime.now().isoformat(),
                "agent": "Receptionist",
                "action": "Retrieved discharge report",
                "patient": state.patient_name
            })
            logger.info(f"Added interaction log entry for successful lookup")
        else:
            logger.warning(f"❌ No discharge report found for {state.patient_name}")
            state.agent_response = f"I apologize, but I couldn't find a discharge report for {state.patient_name}. Could you please verify the spelling of your name?"
        
        return state
    
    def _handle_medical_query(self, state: AgentState):
        """Handle medical questions"""
        logger.info(f"Analyzing query for medical content: {state.current_query[:100]}...")
        
        # Expand medical keywords to catch more medical queries
        medical_keywords = ['pain', 'medication', 'symptoms', 'side effects', 'dosage', 
                          'treatment', 'kidney', 'dialysis', 'blood pressure', 'diet',
                          'swelling', 'worried', 'concern', 'feeling', 'hurt', 'ache',
                          'research', 'study', 'latest', 'new', 'inhibitor', 'drug',
                          'should i', 'what if', 'is it normal', 'help', 'advice']
        
        # Also check for question patterns
        question_patterns = ['?', 'should i', 'what', 'how', 'why', 'when', 'can i']
        
        is_medical_query = (any(keyword in state.current_query.lower() for keyword in medical_keywords) or
                           any(pattern in state.current_query.lower() for pattern in question_patterns))
        
        if is_medical_query:
            logger.info("🏥 Query identified as medical - routing to Clinical Agent")
            # Route to Clinical Agent with notification
            state.agent_response = "This sounds like a medical concern. Let me connect you with our Clinical AI Agent."
            
            # Log the routing
            state.interaction_log.append({
                "timestamp": datetime.now().isoformat(),
                "agent": "Receptionist",
                "action": "Routed to Clinical Agent",
                "query": state.current_query
            })
            
            # Immediately process with clinical agent
            return self._clinical_response(state)
        else:
            logger.info("📋 Query identified as administrative - handling with Receptionist")
            # Use Receptionist logic for non-medical queries
            return self._receptionist_response(state)
    
    def _clinical_response(self, state: AgentState):
        """Generate clinical response using RAG and web search"""
        logger.info(f"🏥 Clinical Agent processing query for {state.patient_name}")
        try:
            # First, try RAG
            logger.info("Attempting RAG query...")
            rag_response = self.rag_tool.query_nephrology_reference(state.current_query)
            
            if "not available" not in rag_response.lower() and "recreate" not in rag_response.lower() and len(rag_response) > 50:
                logger.info("✅ RAG query successful, enhancing with patient context")
                # Enhance with patient context
                if state.discharge_report:
                    enhanced_prompt = f"""
                    Based on the nephrology reference materials: {rag_response}
                    
                    Patient context:
                    - Name: {state.patient_name}
                    - Diagnosis: {state.discharge_report.get('primary_diagnosis', 'N/A')}
                    - Medications: {state.discharge_report.get('medications', [])}
                    - Dietary restrictions: {state.discharge_report.get('dietary_restrictions', 'N/A')}
                    
                    Provide a personalized response considering their specific condition.
                    Always remind them to consult with their healthcare provider.
                    """
                    
                    response = self.llm.invoke(enhanced_prompt)
                    state.agent_response = response.content
                    logger.info("✅ Enhanced response generated with patient context")
                else:
                    state.agent_response = rag_response + "\n\n⚠️ Please consult with your healthcare provider for personalized medical advice."
                    logger.info("✅ RAG response provided without patient context")
            else:
                # Fall back to web search since RAG is not available
                logger.warning("RAG not available, falling back to web search")
                try:
                    logger.info("📡 Using web search as RAG is unavailable...")
                    print("📡 Using web search as RAG is unavailable...")
                    web_results = self.web_search.run(f"nephrology {state.current_query}")
                    
                    web_prompt = f"""
                    Patient asked: "{state.current_query}"
                    Web search results: {web_results}
                    Patient diagnosis: {state.discharge_report.get('primary_diagnosis', 'N/A') if state.discharge_report else 'N/A'}
                    
                    Provide helpful medical response based on web search.
                    Include disclaimers about consulting healthcare providers.
                    Note: This information is from web search as the medical reference system is temporarily unavailable.
                    """
                    
                    response = self.llm.invoke(web_prompt)
                    state.agent_response = response.content + "\n\n[Source: Web search results - Medical reference temporarily unavailable]"
                    logger.info("✅ Web search response generated")
                except Exception as web_error:
                    logger.error(f"Web search error: {web_error}")
                    print(f"Web search error: {web_error}")
                    state.agent_response = "I'm having trouble accessing medical information right now. Please consult with your healthcare provider for this specific question."
            
            # Log interaction
            state.interaction_log.append({
                "timestamp": datetime.now().isoformat(),
                "agent": "Clinical",
                "query": state.current_query,
                "patient": state.patient_name
            })
            logger.info("✅ Clinical interaction logged")
            
        except Exception as e:
            logger.error(f"Error in clinical response: {e}")
            print(f"Error in clinical response: {e}")
            state.agent_response = "I encountered an error processing your request. Please try again or consult with your healthcare provider."
        
        return state
    
    def _receptionist_response(self, state: AgentState):
        """Generate receptionist response for non-medical queries"""
        logger.info(f"📋 Receptionist Agent processing query for {state.patient_name}")
        prompt = f"""You are a medical receptionist. Patient {state.patient_name} is asking: "{state.current_query}"

Their discharge information: {json.dumps(state.discharge_report, indent=2) if state.discharge_report else 'N/A'}

Provide helpful response for administrative/scheduling questions.
If it's medical, direct them to ask medical questions."""
        
        try:
            response = self.llm.invoke(prompt)
            state.agent_response = response.content
            logger.info("✅ Receptionist response generated successfully")
        except Exception as e:
            logger.error(f"Error generating receptionist response: {e}")
            state.agent_response = "I'm having trouble processing your request right now. Please try again or contact our office directly."
        
        return state

    def get_interaction_log(self, state: AgentState):
        """Get interaction log for the session"""
        logger.info(f"Retrieving interaction log for session with {len(state.interaction_log)} entries")
        return state.interaction_log

# Alias for compatibility
MultiAgentSystem = SimpleMultiAgentSystem

