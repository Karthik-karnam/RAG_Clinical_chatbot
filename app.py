import streamlit as st
from rag_chain import ClinicalRAG
import json
import datetime
import time

st.set_page_config(page_title="Clinical RAG Assistant", page_icon="🩺")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "rag" not in st.session_state:
    st.session_state.rag = ClinicalRAG()

# Sidebar for document upload
with st.sidebar:
    st.header("Clinical Documents")
    uploaded_files = st.file_uploader(
        "Upload medical documents", 
        type=["pdf", "docx", "txt", "xlsx"],
        accept_multiple_files=True
    )
    if uploaded_files:
        for file in uploaded_files:
            with open(f"docs/{file.name}", "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} files")
        if st.button("Process Documents"):
            with st.spinner("Indexing documents..."):
                import ingest
                ingest.ingest_documents()
                st.session_state.rag = ClinicalRAG()
                st.rerun()
    st.divider()
    st.header("System Metrics")
    if "metrics" in st.session_state:
        st.metric("Avg. Response Time", f"{st.session_state.metrics['avg_latency']:.2f}s")
        st.metric("Total Questions", st.session_state.metrics["total_questions"])
        st.metric("Hallucination Rate", f"{st.session_state.metrics['hallucination_rate']:.1%}")

# Initialize metrics
if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "total_questions": 0,
        "total_latency": 0,
        "avg_latency": 0,
        "hallucination_count": 0,
        "hallucination_rate": 0
    }

# Main chat interface
st.title("🩺 Clinical RAG Assistant")
st.caption("Powered by medical documents + web search")

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                st.markdown("\n".join(f"- {src}" for src in message["sources"]))
        if message.get("metrics"):
            with st.expander("Performance Metrics"):
                st.write(f"⏱️ Response time: {message['metrics']['latency']:.2f}s")
                st.write(f"📊 Word count: {message['metrics']['word_count']}")
                if message['metrics'].get('hallucination_detected'):
                    st.warning("⚠️ Potential hallucination detected")

if query := st.chat_input("Ask a clinical question:"):
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Consulting knowledge base..."):
            start_time = time.time()
            chat_history = [(h["content"], "") for h in st.session_state.history[:-1]]
            response = st.session_state.rag.get_response(query, chat_history)
            latency = time.time() - start_time
            
            # Update metrics
            st.session_state.metrics["total_questions"] += 1
            st.session_state.metrics["total_latency"] += latency
            st.session_state.metrics["avg_latency"] = (
                st.session_state.metrics["total_latency"] / 
                st.session_state.metrics["total_questions"]
            )
            
            if response.get("hallucination_detected"):
                st.session_state.metrics["hallucination_count"] += 1
                st.session_state.metrics["hallucination_rate"] = (
                    st.session_state.metrics["hallucination_count"] /
                    st.session_state.metrics["total_questions"]
                )
        
        st.markdown(response["answer"])
        
        with st.expander("References"):
            st.markdown("\n".join(f"- {src}" for src in response["sources"]))
    # Add assistant response to history
    st.session_state.history.append({
        "role": "assistant",
        "content": response["answer"],
        "sources": response["sources"],
        "metrics": {
            "latency": latency,
            "word_count": response["metrics"]["word_count"],
            "hallucination_detected": response.get("hallucination_detected", False)
        }
    })
    # # Add assistant response to history
    # st.session_state.history.append({
    #     "role": "assistant",
    #     "content": response["answer"],
    #     "sources": response["sources"]
    # })

# Export chat history
# Export chat history
if st.button("Export Chat"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"clinical_chat_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(st.session_state.history, f)
    st.success(f"Chat exported to {filename}")
    st.download_button(
        label="Download Chat",
        data=json.dumps(st.session_state.history, indent=2),
        file_name=filename,
        mime="application/json"
    )