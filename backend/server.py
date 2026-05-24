from fastapi import FastAPI, HTTPException
from langserve import add_routes
import os
import sys
import dotenv

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from chains import role_templates, create_chat_chain, get_tools
from personas import PERSONAS, get_persona_summary, build_system_prompt, get_persona_by_id
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from tools import calculator, get_current_time, weather_query

dotenv.load_dotenv()

app = FastAPI(title="AI角色扮演助手 - LangServe", version="2.0")

# 获取LLM实例
def get_llm():
    api_provider = os.getenv("API_PROVIDER", "deepseek").lower()
    
    if api_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        return ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key,
            base_url=base_url
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        return ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key
        )

# 创建人物对话链
def create_persona_chain(persona_id: str):
    """为知名人物创建对话链"""
    persona = get_persona_by_id(persona_id)
    if not persona:
        raise ValueError(f"未知人物: {persona_id}")
    
    llm = get_llm()
    system_prompt = build_system_prompt(persona)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain

@app.get("/roles")
async def get_roles():
    """获取职业角色列表"""
    return {
        "roles": [
            {"id": "tech_teacher", "name": "🖥️ 编程导师", "description": "帮助你学习编程知识"},
            {"id": "travel_guide", "name": "✈️ 旅行向导", "description": "为你提供旅行建议"},
            {"id": "psychologist", "name": "🧠 心理咨询师", "description": "倾听你的烦恼"},
            {"id": "story_teller", "name": "📖 故事作家", "description": "创作有趣的故事"},
            {"id": "career_coach", "name": "💼 职业规划师", "description": "帮助你规划职业"}
        ]
    }

@app.get("/personas")
async def get_personas():
    """获取知名人物列表"""
    return {
        "personas": get_persona_summary()
    }

@app.get("/tools")
async def list_tools():
    """获取工具列表"""
    tools = get_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "args": tool.args
            } for tool in tools
        ]
    }

@app.post("/tool/calculator")
async def call_calculator(expression: str):
    """调用计算器工具"""
    try:
        result = calculator.invoke({"expression": expression})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tool/time")
async def call_get_current_time():
    """获取当前时间"""
    try:
        result = get_current_time.invoke({})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tool/weather")
async def call_weather_query(city: str):
    """查询天气"""
    try:
        result = weather_query.invoke({"city": city})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 注册职业角色链
for role_id in role_templates.keys():
    try:
        chain = create_chat_chain(role_id)
        add_routes(
            app,
            chain,
            path=f"/{role_id}",
            enable_feedback_endpoint=True,
            enable_public_trace_link_endpoint=True,
        )
        print(f"✓ Registered role chain: /{role_id}")
    except Exception as e:
        print(f"✗ Failed to register role chain {role_id}: {e}")

# 注册知名人物链
for persona in PERSONAS:
    try:
        chain = create_persona_chain(persona["id"])
        add_routes(
            app,
            chain,
            path=f"/{persona['id']}",
            enable_feedback_endpoint=True,
            enable_public_trace_link_endpoint=True,
        )
        print(f"✓ Registered persona chain: /{persona['id']}")
    except Exception as e:
        print(f"✗ Failed to register persona chain {persona['id']}: {e}")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI角色扮演助手 API",
        "version": "2.0",
        "endpoints": {
            "roles": "/roles",
            "personas": "/personas",
            "tools": "/tools"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
