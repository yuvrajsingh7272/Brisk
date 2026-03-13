import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/"

st.title("Briskcovey Chatbot")

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []


if st.session_state.user_id is None:
    st.header("Welcome ! Please login to continue to chat ...")
    username = st.text_input("Enter your username : ", key="login_username")

    if st.button("Login/Signup", key="login_button"):
        if username:
            try:
                res = requests.post(f"{API_URL}/get_or_create_user", json= {"username": username})
                res.raise_for_status()
                data = res.json()

                st.session_state.user_id = data["user_id"]
                st.session_state.username = data["username"]

                res_hist = requests.post(f"{API_URL}/get_history", json={"user_id":data["user_id"]})
                st.session_state.messages=res_hist.json()["history"]
                st.rerun()
        
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("please enter a username.")
else:
    st.sidebar.header(f"Logged in as : {st.session_state.username}")
    if st.sidebar.button("logout", key="logout_button"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.messages = []
        st.rerun()

    st.header("Chat Interface")
    st.write("Where should we start?")

    for chat in st.session_state.messages:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    if prompt:=st.chat_input("Ask me Anything ..."):
        st.session_state.messages.append({"role":"human","content":prompt})
        with st.chat_message("human"):
            st.markdown(prompt)
        
        with st.chat_message("ai"):
            with st.spinner("Thinking ..."):

                try:
                    res = requests.post(f"{API_URL}/query", json={"user_id": st.session_state.user_id, "text": prompt})
                    res.raise_for_status()
                    answer = res.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role":"ai", "content": answer})

                except Exception as e:
                    st.error(f"Error: {e}")


