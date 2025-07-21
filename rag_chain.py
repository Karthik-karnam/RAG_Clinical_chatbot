import os
import openai
from openai import OpenAIError, RateLimitError

from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.retrievers.web_research import WebResearchRetriever
#from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_community.llms import Ollama
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rag_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)




class ClinicalRAG:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.vector_db = Chroma(
            persist_directory="vector_db",
            embedding_function=self.embedding
        )
        try:
            self.llm = Ollama(model="mistral", base_url="http://host.docker.internal:11434", temperature=0.3, timeout = 90)
            logger.info("Using Ollama Mistral model")
            load_dotenv()
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}. Falling back to OpenAI.")


        self.search = GoogleSearchAPIWrapper(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            google_cse_id=os.getenv("GOOGLE_CSE_ID"),
            k=5
        )

        
        # Web search retriever
       # self.search = DuckDuckGoSearchAPIWrapper()
        self.web_retriever = WebResearchRetriever.from_llm(
            vectorstore=self.vector_db,
            llm=self.llm,
            search=self.search,
            allow_dangerous_requests=True 
        )

    def detect_hallucination(self, answer: str) -> bool:
        """Detect potential hallucinations in the response"""
        hallucination_phrases = [
            "I don't know", "not mentioned in the context", "no information provided",
            "based on my training data", "as an AI language model", "I cannot answer",
            "not specified in the given context", "without specific context"
        ]
        
        # Check for uncertainty phrases
        if any(phrase.lower() in answer.lower() for phrase in hallucination_phrases):
            return True
            
        # Check for vague responses
        vague_phrases = ["it depends", "may vary", "could be", "might be", "possibly"]
        vague_count = sum(phrase in answer.lower() for phrase in vague_phrases)
        
        # More than 2 vague phrases indicates uncertainty
        if vague_count > 2:
            return True
            
        return False
    
    def get_response(self, query, chat_history):
        
        try:
            # Initialize metrics
            metrics = {"word_count": 0}
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.web_retriever,
                return_source_documents=True,
                verbose=True
            )
            result = qa_chain({"question": query, "chat_history": chat_history})
            answer = result["answer"]
            sources = list(set(doc.metadata["source"] for doc in result["source_documents"]))
            
            # Calculate word count
            metrics["word_count"] = len(answer.split())
            
            # Check for hallucinations
            hallucination_detected = self.detect_hallucination(answer)
            if hallucination_detected:
                logger.warning(f"Potential hallucination detected in response: {answer[:100]}...")
                
                # Fallback to direct web search
                web_results = self.search.run(query)
                answer = f"{answer}\n\n⚠️ I detected uncertainty in my response. Here are web search results:\n{web_results}"
                sources.append("Google Search")
            
            return {
                "answer": answer,
                "sources": sources,
                "metrics": metrics,
                "hallucination_detected": hallucination_detected
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "answer": f"⚠️ System error: {str(e)}. Please try again.",
                "sources": [],
                "metrics": {"word_count": 0},
                "hallucination_detected": False
            }
