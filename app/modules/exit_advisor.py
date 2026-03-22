import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

FINE_TUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:personal::DHs6JwPC"

def should_end_conversation(chat_history: list, user_message: str) -> bool:
    
    llm = ChatOpenAI(
        model=FINE_TUNED_MODEL,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    history_text = ""
    for msg in chat_history:
        role = "Recruiter" if msg["role"] == "assistant" else "Candidate"
        history_text += f"{role}: {msg['content']}\n"
    
    messages = [
        {
            "role": "system",
            "content": """You are an Exit Advisor for a recruitment chatbot for a Python Developer position.
Your job is to detect if the conversation should END.

End the conversation if the candidate:
- Already found another job
- Is not interested in the position
- Explicitly says goodbye or wants to stop
- Is very evasive or unresponsive

Do NOT end if the candidate:
- Has questions about the position
- Wants to schedule an interview
- Is engaged and responding positively
- Is unsure but still open

Reply with ONLY one word: 'end' or 'continue'."""
        },
        {
            "role": "user",
            "content": f"Conversation so far:\n{history_text}\nLatest message: {user_message}\nShould the conversation end?"
        }
    ]
    
    response = llm.invoke(messages).content.strip().lower()
    print(f"🚪 Exit Advisor decision: {response}")
    
    return "end" in response


def get_exit_advisor_response(chat_history: list, user_message: str) -> dict:
    
    should_end = should_end_conversation(chat_history, user_message)
    
    if should_end:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        messages = [
            {
                "role": "system",
                "content": """You are an Exit Advisor for a recruitment chatbot.
Write a short, polite and professional closing message.
Wish the candidate well and leave the door open for future opportunities."""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        closing_message = llm.invoke(messages).content
        return {
            "should_end": True,
            "response": closing_message
        }
    
    return {
        "should_end": False,
        "response": None
    }


if __name__ == "__main__":
    print("Testing Exit Advisor with Fine-Tuned model...\n")
    
    print("Test 1 - Not interested:")
    result = get_exit_advisor_response(
        [], 
        "I already found another job, I'm not interested anymore."
    )
    print(f"Should end: {result['should_end']}")
    print(f"Response: {result['response']}\n")
    
    print("Test 2 - Still interested:")
    result = get_exit_advisor_response(
        [],
        "That sounds great, tell me more about the position."
    )
    print(f"Should end: {result['should_end']}")
    print(f"Response: {result['response']}\n")
    
    print("Test 3 - Evasive candidate:")
    result = get_exit_advisor_response(
        [],
        "I'm not sure, maybe another time, I'm very busy right now."
    )
    print(f"Should end: {result['should_end']}")
    print(f"Response: {result['response']}\n")