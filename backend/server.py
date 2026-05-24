from fastapi import FastAPI, HTTPException
from langserve import add_routes
from chains import role_templates, create_chat_chain, get_tools
from tools import calculator, get_current_time, weather_query
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(title="角色扮演AI助手 - LangServe", version="1.0")

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

@app.get("/tools")
async def list_tools():
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
    try:
        result = calculator.invoke({"expression": expression})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tool/time")
async def call_get_current_time():
    try:
        result = get_current_time.invoke({})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tool/weather")
async def call_weather_query(city: str):
    try:
        result = weather_query.invoke({"city": city})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        print(f"Registered chain: /{role_id}")
    except Exception as e:
        print(f"Failed to register chain {role_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)