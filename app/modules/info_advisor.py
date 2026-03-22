import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

def get_info_advisor_response(chat_history: list, user_message: str) -> str:
    
    # טוען את ה-ChromaDB הקיים
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    
    # מחפש מידע רלוונטי מה-PDF
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(user_message)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # בונה את ה-prompt
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    messages = [
        {
            "role": "system",
            "content": f"""You are an Info Advisor in a recruitment chatbot for a Python Developer position.
Your job is to answer candidate questions about the position using the information below.
Always be helpful, professional, and guide the candidate toward scheduling an interview.

Job Description Context:
{context}"""
        }
    ]
    
    # מוסיף את היסטוריית השיחה
    for msg in chat_history:
        messages.append(msg)
    
    # מוסיף את ההודעה הנוכחית
    messages.append({"role": "user", "content": user_message})
    
    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
    # בדיקה פשוטה
    test_history = []
    test_message = "What are the requirements for this Python Developer position?"
    
    print("Testing Info Advisor...")
    response = get_info_advisor_response(test_history, test_message)
    print(f"Response: {response}")