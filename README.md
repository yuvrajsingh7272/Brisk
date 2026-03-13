## Brisk_Bot 
Advanced Gen AI chatbot assistant system

Brisk_Bot is a futuristic and advanced Generative AI chatbot designed to assist clients and provide accurate information about an organization.  
The chatbot leverages cutting-edge AI technologies including Retrieval-Augmented Generation (RAG), Large Language Models, and Vector Databases to deliver reliable and context-aware responses.

The system is built to minimize hallucination and ensure responses are generated based on verified company knowledge bases.

---

# Features

- AI-powered conversational assistant for clients
- Provides detailed information about the organization
- Explains company portfolio, services, and achievements
- Knowledge-based responses using RAG
- Reduces hallucination with contextual retrieval
- Fast and scalable API backend
- Interactive chatbot interface
- Real-time information retrieval from vector database

---

# Technologies Used

- Python
- LangChain
- Retrieval-Augmented Generation (RAG)
- Large Language Models (LLMs)
- Gemini API
- Groq LLM
- FastAPI
- FAISS Vector Database
- PostgreSQL
- SQL
- Streamlit

---

# System Architecture

1. User sends a query through the Streamlit chatbot interface.
2. FastAPI handles backend processing.
3. LangChain orchestrates the LLM pipeline.
4. RAG retrieves relevant knowledge from the FAISS vector database.
5. Context is passed to LLMs (Gemini / Groq).
6. The LLM generates accurate and context-aware responses.
7. Response is delivered to the user through the chatbot interface.

---

# Use Cases

- Client support automation
- Organization knowledge assistant
- Portfolio and services explanation
- Company achievements and information retrieval
- Internal knowledge base chatbot

---
