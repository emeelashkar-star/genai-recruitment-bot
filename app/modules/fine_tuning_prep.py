import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def prepare_fine_tuning_data():
    """ממיר את sms_conversations.json לפורמט Fine-Tuning של OpenAI"""
    
    with open("data/sms_conversations.json", "r") as f:
        conversations = json.load(f)
    
    training_data = []
    
    for conv in conversations:
        turns = conv["turns"]
        
        for i, turn in enumerate(turns):
            # רק turns של recruiter עם label
            if turn["speaker"] == "recruiter" and turn["label"] in ["end", "continue", "schedule"]:
                
                # בונה היסטוריית שיחה עד לנקודה הזו
                history = ""
                for prev in turns[:i]:
                    speaker = "Recruiter" if prev["speaker"] == "recruiter" else "Candidate"
                    history += f"{speaker}: {prev['text']}\n"
                
                # יוצר דוגמת אימון
                sample = {
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an Exit Advisor for a recruitment chatbot.
Analyze the conversation and decide if it should end.
Reply with ONLY one word: 'end' or 'continue'."""
                        },
                        {
                            "role": "user",
                            "content": f"Conversation so far:\n{history}\nLatest message: {turn['text']}\nShould the conversation end?"
                        },
                        {
                            "role": "assistant",
                            "content": "end" if turn["label"] == "end" else "continue"
                        }
                    ]
                }
                training_data.append(sample)
    
    # שומר לקובץ JSONL
    with open("data/fine_tuning_data.jsonl", "w") as f:
        for sample in training_data:
            f.write(json.dumps(sample) + "\n")
    
    print(f"✅ Created {len(training_data)} training samples")
    print(f"Saved to data/fine_tuning_data.jsonl")
    return len(training_data)


def upload_and_train():
    """מעלה את הנתונים ל-OpenAI ומתחיל Fine-Tuning"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("Uploading training file to OpenAI...")
    with open("data/fine_tuning_data.jsonl", "rb") as f:
        response = client.files.create(file=f, purpose="fine-tune")
    
    file_id = response.id
    print(f"✅ File uploaded: {file_id}")
    
    print("Starting Fine-Tuning job...")
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-4o-mini-2024-07-18"
    )
    
    print(f"✅ Fine-Tuning job started: {job.id}")
    print(f"Status: {job.status}")
    print(f"\n⚠️ Save this job ID: {job.id}")
    print("Fine-tuning takes 10-30 minutes. Run check_status.py to monitor.")
    
    return job.id


if __name__ == "__main__":
    print("Step 1: Preparing training data...")
    count = prepare_fine_tuning_data()
    
    if count > 0:
        print("\nStep 2: Upload and start Fine-Tuning? (yes/no)")
        answer = input()
        if answer.lower() == "yes":
            job_id = upload_and_train()