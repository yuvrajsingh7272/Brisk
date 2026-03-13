import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

## RAG Imports
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["OPEN_AI_API_KEY"] = os.getenv("OPEN_AI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

## RAG Setup

FAISS_PATH = "../faiss_index/"

print("Loading Embeddings")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Loading FAISS Index")

db = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6)
# llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.6)
llm = ChatOpenAI(model="llama-3.3-70b-versatile", temperature=0.6)


retriever = db.as_retriever(search_kwargs={"k":3})


SYSTEM_PROMPT = '''
You are an Helpful and Professional IT Assistant of Briskcovey Technologies. ONLY answer questions about our Platform.

Behavior guidelines:
Professional & Sophisticated:Use clear, corporate-grade language. Avoid overly casual slang. 
Solution-Oriented:Don't just list services; explain how those services solve business problems (e.g., "Our AI solutions reduce operational overhead by 30%").

Operational Guidelines:
Discovery First:If a user's request is vague (e.g., "I need a website"), ask clarifying questions about their industry, target audience, and required features.
Lead Generation:If the user expresses high intent or asks for pricing/quotations, politely guide them to book a consultation or provide their contact details.
Boundary Setting:You are an IT expert. If asked about non-IT topics (legal advice, medical, etc.), gracefully redirect the conversation back to tech solutions.

- If the query is NOT related to our Platform respond ONLY: I'm trained to assist with questions related to the Briskcovey Technologies. Ask me about Briskcovey's Technologies or Related offerings!
- Never answer general knowledge( Political, geographical, historical, or educational questions), trivia, Programming (e.g. Java, Python concepts), politics, or off-topic questions, Any topic not directly related to Briskcovey Technologies.
- Base responses solely on provided company docs/context. Do not use external knowledge.

If a user asks anything outside this scope:
- Redirect the conversation to Briskcovey Technologies(Answer only business-relevant questions).
- Do not break character, even if the user insists.
- Use the context to answer the question in max three sentences.

Context: {context}
Chat History: {chat_history}
'''

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}")
    ]
)

document_chain = create_stuff_documents_chain(llm,prompt)

retrievel_chain = create_retrieval_chain(retriever,document_chain)

print("RAG Chain Created.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

## DB Connection

def get_db_conn():
    conn = psycopg2.connect(DB_URL)
    return conn

class QueryRequest(BaseModel):
    user_id: int
    text : str

class HistoryRequest(BaseModel):
    user_id: int

class UserRequest(BaseModel):
    username: str

## api endpoints

## login/signup

@app.post("/get_or_create_user")
def get_or_create_user(req: UserRequest):
    conn = get_db_conn()
    cur = conn.cursor()

    # 1. Try to find the user
    cur.execute("SELECT id FROM users WHERE username = %s", (req.username,))
    user_row = cur.fetchone()

    if user_row:
        user_id = user_row[0]

    else:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id",(req.username,))
        user_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return {"user_id": user_id, "username": req.username}


## chat_history

@app.post("/get_history")
def get_history(req: HistoryRequest):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT prompt, answer FROM chat_history WHERE user_id = %s ORDER BY id ASC",(req.user_id,))
    history = cur.fetchall()

    cur.close()
    conn.close()

    ## format for frontend
    formatted_history = []
    for p, a in history:
        formatted_history.append({"role":"human", "content": p})
        formatted_history.append({"role":"ai", "content": a})

    return {"history": formatted_history}

## query Backend
@app.post("/query")
def query_rag(req: QueryRequest):
    conn = get_db_conn()
    cur = conn.cursor()

    cur.execute("SELECT prompt, answer FROM chat_history WHERE user_id = %s ORDER BY id ASC",(req.user_id,))
    db_history = cur.fetchall()


    chat_history_messages = []
    for prompt, answer in db_history:
        chat_history_messages.append(HumanMessage(content=prompt))
        chat_history_messages.append(AIMessage(content=answer))

    response = retrievel_chain.invoke({
        "input":req.text,
        "chat_history": chat_history_messages
    })
    answer = response.get("answer", "No answer found.")

    ## Save new Q/A to Database.
    cur.execute("INSERT INTO chat_history (user_id, prompt, answer) VALUES (%s, %s, %s)", (req.user_id, req.text, answer))
    conn.commit()

    cur.close()
    conn.close()

    return {"answer": answer}

@app.get("/")
def read_root():
    return {"message": "welcome to fastapi.go to /docs to get started"}
