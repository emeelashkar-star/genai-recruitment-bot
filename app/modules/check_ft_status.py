import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

job_id = "ftjob-HLwarbtOqcP91LAzggDmJDoZ"

job = client.fine_tuning.jobs.retrieve(job_id)

print(f"Status: {job.status}")
print(f"Model: {job.fine_tuned_model}")
print(f"Created at: {job.created_at}")

if job.status == "succeeded":
    print(f"\n✅ Fine-Tuned Model ID: {job.fine_tuned_model}")
    print("⚠️ Save this Model ID - you'll need it for Exit Advisor!")
elif job.status == "failed":
    print(f"\n❌ Failed: {job.error}")
else:
    print(f"\n⏳ Still running... check again in a few minutes")