import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.modules.main_agent import get_main_agent_response
from app.modules.scheduling_advisor import init_db

# אתחול DB
init_db()

# הגדרות עמוד
st.set_page_config(
    page_title="Python Developer Recruitment Bot",
    page_icon="💼",
    layout="centered"
)

# CSS לסימולציית SMS
st.markdown("""
<style>
    .candidate-msg {
        background-color: #DCF8C6;
        color: #000000;
        padding: 10px 15px;
        border-radius: 15px 15px 0px 15px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }
    .bot-msg {
        background-color: #FFFFFF;
        color: #000000;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
        border: 1px solid #E0E0E0;
    }
    .chat-container {
    padding: 20px;
    background-color: #ECE5DD;
    border-radius: 10px;
    min-height: 50px;
    margin-bottom: 20px;
    }   
    .clearfix { clear: both; }
</style>
""", unsafe_allow_html=True)

# כותרת
st.title("💼 Python Developer Recruitment Bot")
st.caption("SMS Simulation - Powered by Multi-Agent AI")
st.divider()

# אתחול session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False
if "decision_log" not in st.session_state:
    st.session_state.decision_log = []

# הודעת פתיחה
if not st.session_state.chat_history:
    opening = "Hi! Thanks for applying to our Python Developer position. Could you tell me a bit about your Python experience?"
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": opening
    })

# הצגת השיחה
chat_html = '<div class="chat-container">'

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        chat_html += f'<div class="candidate-msg">👤 {msg["content"]}</div><div class="clearfix"></div>'
    else:
        chat_html += f'<div class="bot-msg">🤖 {msg["content"]}</div><div class="clearfix"></div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)


# Decision log בצד
with st.expander("🧠 Agent Decisions Log"):
    if st.session_state.decision_log:
        for log in st.session_state.decision_log:
            st.write(log)
    else:
        st.write("No decisions yet...")

# Input area
if not st.session_state.conversation_ended:
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        # הוספת הודעת המשתמש
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        with st.spinner("🤔 Thinking..."):
            result = get_main_agent_response(
                st.session_state.chat_history[:-1],
                user_input
            )
        
        # הוספת תשובת הבוט
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"]
        })
        
        # לוג החלטות
        st.session_state.decision_log.append(
            f"Turn {len(st.session_state.decision_log)+1}: '{user_input[:30]}...' → {result['decision'].upper()}"
        )
        
        # בדיקה אם השיחה נסתיימה
        if result["decision"] == "end":
            st.session_state.conversation_ended = True
        
        st.rerun()

else:
    st.error("🔚 Conversation ended")
    if st.button("🔄 Start New Conversation"):
        st.session_state.chat_history = []
        st.session_state.conversation_ended = False
        st.session_state.decision_log = []
        st.rerun()