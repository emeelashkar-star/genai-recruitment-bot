import os
import sqlite3
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def init_db():
    """יוצר SQLite database עם slots פנויים"""
    conn = sqlite3.connect("data/db_Tech.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Schedule (
            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            time TIME NOT NULL,
            position VARCHAR(20) NOT NULL,
            available INTEGER NOT NULL
        )
    """)
    
    # בודק אם כבר יש נתונים
    cursor.execute("SELECT COUNT(*) FROM Schedule")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # יוצר slots לשנה הנוכחית
        start_date = date.today()
        end_date = date(date.today().year, 12, 31)
        current = start_date
        hours = ["09:00", "10:00", "11:00", "12:00", "13:00", 
                 "14:00", "15:00", "16:00", "17:00"]
        
        slots = []
        while current <= end_date:
            # רק ימים ראשון-חמישי (לא שבת ושישי)
            if current.weekday() not in [4, 5]:  # 4=Friday, 5=Saturday
                for hour in hours:
                    slots.append((
                        current.strftime("%Y-%m-%d"),
                        hour,
                        "Python Developer",
                        1
                    ))
            current += timedelta(days=1)
        
        cursor.executemany(
            "INSERT INTO Schedule (date, time, position, available) VALUES (?, ?, ?, ?)",
            slots
        )
        print(f"✅ Created {len(slots)} available slots")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def get_available_slots() -> list:
    """מחזיר את הזמנים הפנויים הקרובים"""
    conn = sqlite3.connect("data/db_Tech.db")
    cursor = conn.cursor()
    
    today = date.today().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT date, time, position 
        FROM Schedule 
        WHERE available = 1 
        AND date >= ?
        ORDER BY date, time
        LIMIT 10
    """, (today,))
    
    slots = cursor.fetchall()
    conn.close()
    return slots

def get_scheduling_advisor_response(chat_history: list, user_message: str) -> str:
    
    try:
        slots = get_available_slots()
    except Exception:
        init_db()
        slots = get_available_slots()
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    slots_text = "\n".join([
        f"Date: {slot[0]}, Time: {slot[1]}, Position: {slot[2]}" 
        for slot in slots[:3]
    ])
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a Scheduling Advisor in a recruitment chatbot for a Python Developer position.
Your job is to help candidates schedule an interview with the recruiter.
Today's date is {current_date}.

The 3 nearest available interview slots are:
{slots_text}

Suggest these slots to the candidate and confirm their preference.
Be friendly and professional."""
        }
    ]
    
    for msg in chat_history:
        messages.append(msg)
    
    messages.append({"role": "user", "content": user_message})
    
    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    
    print("\nTesting Scheduling Advisor...")
    test_message = "I'd like to schedule an interview, what times are available?"
    response = get_scheduling_advisor_response([], test_message)
    print(f"Response: {response}")