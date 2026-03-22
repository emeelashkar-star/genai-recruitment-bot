import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.modules.info_advisor import get_info_advisor_response
from app.modules.scheduling_advisor import get_scheduling_advisor_response, init_db
from app.modules.exit_advisor import get_exit_advisor_response

load_dotenv()

def get_main_agent_response(chat_history: list, user_message: str) -> dict:
    """
    Main Agent - מנהל את השיחה ומחליט בין 3 אפשרויות:
    - continue: להמשיך את השיחה
    - schedule: לתזמן ראיון
    - end: לסיים את השיחה
    """
    
    # שלב 1 - Exit Advisor בודק קודם אם צריך לסיים
    exit_result = get_exit_advisor_response(chat_history, user_message)
    if exit_result["should_end"]:
        return {
            "decision": "end",
            "response": exit_result["response"]
        }
    
    # שלב 2 - Main Agent מחליט בין continue ל-schedule
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    decision_messages = [
        {
            "role": "system",
            "content": """You are the Main Agent of a recruitment chatbot for a Python Developer position.
Analyze the conversation and decide on ONE of these actions:
- continue: candidate wants more info or has questions
- schedule: candidate is ready to schedule an interview

Reply with ONLY one word: 'continue' or 'schedule'."""
        }
    ]
    
    for msg in chat_history:
        decision_messages.append(msg)
    decision_messages.append({"role": "user", "content": user_message})
    
    decision = llm.invoke(decision_messages).content.strip().lower()
    
    if "schedule" in decision:
        decision = "schedule"
    else:
        decision = "continue"
    
    print(f"🤖 Main Agent decision: {decision}")
    
    # שלב 3 - מפנה לAdvisor המתאים
    if decision == "schedule":
        response = get_scheduling_advisor_response(chat_history, user_message)
    else:
        response = get_info_advisor_response(chat_history, user_message)
    
    return {
        "decision": decision,
        "response": response
    }


if __name__ == "__main__":
    init_db()
    
    print("Testing Main Agent with all Advisors...\n")
    
    # בדיקה 1 - שאלה על המשרה
    print("Test 1 - Info question:")
    result = get_main_agent_response([], "What Python frameworks do you require?")
    print(f"Decision: {result['decision']}")
    print(f"Response: {result['response']}\n")
    
    # בדיקה 2 - רצון לתזמן
    print("Test 2 - Schedule request:")
    result = get_main_agent_response([], "I'm interested, can we schedule an interview?")
    print(f"Decision: {result['decision']}")
    print(f"Response: {result['response']}\n")
    
    # בדיקה 3 - סיום שיחה
    print("Test 3 - End conversation:")
    result = get_main_agent_response([], "I already found another job, not interested.")
    print(f"Decision: {result['decision']}")
    print(f"Response: {result['response']}\n")