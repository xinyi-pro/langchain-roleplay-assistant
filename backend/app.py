from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from openai import OpenAI
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="角色扮演AI助手服务", version="1.0")

role_templates = {
    "tech_teacher": """
    你是一位耐心的编程技术导师。
    你的任务是帮助用户学习编程知识，解答技术问题。
    请用简洁明了的语言解释复杂概念。
    """,
    "travel_guide": """
    你是一位专业的旅行向导。
    你的任务是为用户提供旅行建议、目的地推荐和行程规划。
    请提供详细有用的旅行信息。
    """,
    "psychologist": """
    你是一位友善的心理咨询师。
    你的任务是倾听用户的烦恼，给予安慰和建议。
    请保持同理心和专业态度。
    """,
    "story_teller": """
    你是一位富有想象力的故事作家。
    你的任务是根据用户的要求创作有趣的故事。
    请发挥创造力，让故事生动有趣。
    """,
    "career_coach": """
    你是一位资深的职业规划师。
    你的任务是帮助用户规划职业发展，提供求职建议。
    请给出专业实用的建议。
    """
}

store: Dict[str, list] = {}

class ChatRequest(BaseModel):
    user_id: str
    role: str
    message: str

class ChatResponse(BaseModel):
    response: str
    role: str

def get_messages(user_id: str, role: str) -> list:
    if user_id not in store:
        store[user_id] = []
    return store[user_id]

def get_client():
    api_provider = os.getenv("API_PROVIDER", "deepseek").lower()
    
    if api_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY not set")
        
        base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
        
        base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if request.role not in role_templates:
        raise HTTPException(status_code=400, detail=f"Unknown role: {request.role}")
    
    client, model = get_client()
    
    messages = get_messages(request.user_id, request.role)
    system_prompt = role_templates[request.role]
    
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(messages)
    api_messages.append({"role": "user", "content": request.message})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        
        messages.append({"role": "user", "content": request.message})
        messages.append({"role": "assistant", "content": result})
        
        return ChatResponse(response=result, role=request.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/roles")
async def get_roles():
    return {
        "roles": [
            {"id": "tech_teacher", "name": "编程导师", "description": "帮助你学习编程知识"},
            {"id": "travel_guide", "name": "旅行向导", "description": "为你提供旅行建议"},
            {"id": "psychologist", "name": "心理咨询师", "description": "倾听你的烦恼"},
            {"id": "story_teller", "name": "故事作家", "description": "创作有趣的故事"},
            {"id": "career_coach", "name": "职业规划师", "description": "帮助你规划职业"}
        ]
    }

@app.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str):
    if user_id in store:
        del store[user_id]
    return {"message": "Conversation cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)