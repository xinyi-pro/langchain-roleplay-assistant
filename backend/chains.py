from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from tools import tools
import os
from dotenv import load_dotenv

load_dotenv()

role_templates = {
    "tech_teacher": """
    你是一位耐心的编程技术导师。
    你的任务是帮助用户学习编程知识，解答技术问题。
    请用简洁明了的语言解释复杂概念。
    
    你可以使用以下工具来辅助回答：
    - calculator: 计算器工具，用于数学计算
    - get_current_time: 获取当前时间
    - weather_query: 查询天气信息
    
    如果需要使用工具，请在回答中明确说明。
    """,
    "travel_guide": """
    你是一位专业的旅行向导。
    你的任务是为用户提供旅行建议、目的地推荐和行程规划。
    请提供详细有用的旅行信息。
    
    你可以使用以下工具来辅助回答：
    - calculator: 计算器工具，用于计算
    - get_current_time: 获取当前时间
    - weather_query: 查询天气信息
    
    如果需要使用工具，请在回答中明确说明。
    """,
    "psychologist": """
    你是一位友善的心理咨询师。
    你的任务是倾听用户的烦恼，给予安慰和建议。
    请保持同理心和专业态度。
    
    你可以使用以下工具来辅助回答：
    - get_current_time: 获取当前时间
    
    如果需要使用工具，请在回答中明确说明。
    """,
    "story_teller": """
    你是一位富有想象力的故事作家。
    你的任务是根据用户的要求创作有趣的故事。
    请发挥创造力，让故事生动有趣。
    
    你可以使用以下工具来辅助回答：
    - get_current_time: 获取当前时间
    
    如果需要使用工具，请在回答中明确说明。
    """,
    "career_coach": """
    你是一位资深的职业规划师。
    你的任务是帮助用户规划职业发展，提供求职建议。
    请给出专业实用的建议。
    
    你可以使用以下工具来辅助回答：
    - calculator: 计算器工具，用于计算
    - get_current_time: 获取当前时间
    
    如果需要使用工具，请在回答中明确说明。
    """
}

def get_llm():
    api_provider = os.getenv("API_PROVIDER", "deepseek").lower()
    
    if api_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        
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
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        return ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key,
            base_url=base_url
        )

def create_chat_chain(role: str):
    if role not in role_templates:
        raise ValueError(f"Unknown role: {role}")
    
    llm = get_llm()
    system_prompt = role_templates[role]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    return chain

def get_tools():
    return tools