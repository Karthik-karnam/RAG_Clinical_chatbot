# 🧠 Clinical RAG Assistant

A **Retrieval-Augmented Generation (RAG)** chatbot designed for clinical and healthcare use cases. It supports answering user queries based on **internal documents** (PDF, Word, etc.) and **external web search**. Built using LangChain, Streamlit, ChromaDB, and optionally local LLMs via Ollama.

---

## 🚀 Features

- 🔍 Ingest and vectorize clinical documents (PDF, DOCX, TXT, etc.)
- 💬 Ask natural language questions and receive contextual answers
- 📚 Displays sources and references alongside each response
- 🌐 Optional web search fallback for out-of-domain questions
- 🧠 Powered by LangChain with OpenAI or local Ollama models
- 📦 Dockerized for easy deployment
- 🧾 Chat history and document inspection

---

## 🗂️ Project Structure

├── app.py # Main Streamlit UI

├── ingest.py # Document loader & vector store

├── rag_chain.py # RAG chain definition

├── requirements.txt # Python dependencies

├── Dockerfile # For containerized setup

├── .env # API keys and environment variables

└── data/ # Directory to place your source documents



---

## ⚙️ Local Setup (Recommended for Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Karthik-karnam/RAG_Clinical_chatbot.git
cd clinical-rag-assistant
```


### 2. (Option A) Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (Option B) Set up with Docker (Recommended for Deployment)

```bash
docker build -t clinical-rag .
docker run -p 8501:8501 -v $(pwd)/data:/app/data clinical-rag
```

# 🤖 Using a Local Model with Ollama (Optional)
If you don’t want to use OpenAI and prefer local models like mistral, install Ollama:

### Step 1: Install Ollama

Follow instructions for your platform: https://ollama.com/download


### Step 2: Pull a model
```bash
ollama pull mistral
```

### Step 3: Run Ollama (auto-starts)
```bash
ollama run mistral
```

Ensure that ```ollama``` is running on ```http://localhost:11434.```

# 🔐 Environment Variables

Create a ```.env``` file in the project root:


```bash
OPENAI_API_KEY=your_openai_key_here
USE_OLLAMA=true         # set to false if using OpenAI
OLLAMA_MODEL=mistral
```


# 📁 Add Documents for Ingestion

Place your documents (PDF, Word, Excel, TXT) inside the ```/data``` folder. The app will parse and embed these on startup.


# ▶️ Run the App

If installed locally:


```bash
streamlit run app.py
```

# 💬 Demo UI Walkthrough

<img width="1911" height="884" alt="Screenshot 2025-07-21 at 6 02 42 PM" src="https://github.com/user-attachments/assets/55adde74-c3af-4211-a2e1-a95ddbfc4407" />

- Upload documents from the sidebar

- Click “Process Documents” to embed

- Ask a question in the chat box

- View answers, sources, and metrics

- Export chat history as needed


# 🧪 Test Sample Documents

You can use any dummy clinical documents, or public medical reports (e.g., from WHO, CDC) in ```.pdf``` or ```.docx``` format.


# 🙋‍♂️ Author
Developed by ```Karthik Karnam``` — Graduate Researcher at University of Florida
For inquiries or collaboration, please reach out via LinkedIn or email.







