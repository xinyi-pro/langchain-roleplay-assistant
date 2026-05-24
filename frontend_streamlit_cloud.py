import streamlit as st
import uuid
from dotenv import load_dotenv
import os

# 尝试加载环境变量（本地开发时使用）
try:
    load_dotenv()
except:
    pass

# LangChain 导入
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 角色模板
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

roles = [
    {"id": "tech_teacher", "name": "编程导师", "description": "帮助你学习编程知识"},
    {"id": "travel_guide", "name": "旅行向导", "description": "为你提供旅行建议"},
    {"id": "psychologist", "name": "心理咨询师", "description": "倾听你的烦恼"},
    {"id": "story_teller", "name": "故事作家", "description": "创作有趣的故事"},
    {"id": "career_coach", "name": "职业规划师", "description": "帮助你规划职业"}
]

def get_llm():
    """获取 LLM 实例"""
    api_provider = os.getenv("API_PROVIDER", "deepseek").lower()
    
    if api_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        
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
            raise ValueError("请设置 OPENAI_API_KEY 环境变量")
        
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        return ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key
        )

def create_chain(role_id):
    """创建对话链"""
    if role_id not in role_templates:
        raise ValueError(f"未知角色: {role_id}")
    
    llm = get_llm()
    system_prompt = role_templates[role_id]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain

def main():
    st.set_page_config(page_title="角色扮演AI助手", page_icon="🎭", layout="wide")
    
    st.title("🎭 角色扮演AI助手")
    st.subheader("选择一个角色开始对话")
    
    # 初始化会话状态
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chain" not in st.session_state:
        st.session_state.chain = None
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 角色选择")
        
        # API Key 配置
        with st.expander("🔑 API 配置"):
            api_provider = st.selectbox("API 提供商", ["deepseek", "openai"], index=0)
            os.environ["API_PROVIDER"] = api_provider
            
            if api_provider == "deepseek":
                deepseek_key = st.text_input("DeepSeek API Key", type="password", value=os.getenv("DEEPSEEK_API_KEY", ""))
                os.environ["DEEPSEEK_API_KEY"] = deepseek_key
            else:
                openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
                os.environ["OPENAI_API_KEY"] = openai_key
        
        # 角色选择按钮
        for role in roles:
            if st.button(role["name"], key=role["id"], use_container_width=True):
                st.session_state.selected_role = role
                st.session_state.messages = []
                try:
                    st.session_state.chain = create_chain(role["id"])
                    st.success(f"已切换到 {role['name']}")
                except Exception as e:
                    st.error(f"初始化失败: {e}")
                    st.session_state.selected_role = None
                    st.session_state.chain = None
        
        if st.session_state.selected_role:
            st.markdown(f"**当前角色:** {st.session_state.selected_role['name']}")
            st.markdown(f"*描述:* {st.session_state.selected_role['description']}")
            
            if st.button("🔄 切换角色", use_container_width=True):
                st.session_state.selected_role = None
                st.session_state.messages = []
                st.session_state.chain = None
    
    with col2:
        st.markdown("### 对话区域")
        
        if not st.session_state.selected_role:
            st.info("请从左侧选择一个角色开始对话")
            st.markdown("""
            **使用说明:**
            1. 在左侧展开 API 配置，输入你的 API Key
            2. 选择一个角色开始对话
            3. 在输入框中输入你的问题
            """)
        else:
            # 显示对话历史
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            # 输入新消息
            if prompt := st.chat_input("请输入你的消息..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("AI思考中..."):
                        try:
                            if st.session_state.chain:
                                response = st.session_state.chain.invoke({"input": prompt})
                                st.markdown(response)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            else:
                                st.error("链条未初始化，请重新选择角色")
                        except Exception as e:
                            st.error(f"请求失败: {e}")

if __name__ == "__main__":
    main()

# Streamlit Cloud 部署说明
# 1. 将此文件保存为 app.py
# 2. 在 Streamlit Cloud 中创建新项目
# 3. 设置环境变量:
#    - API_PROVIDER: deepseek 或 openai
#    - DEEPSEEK_API_KEY: 你的 DeepSeek API Key (如果选择 deepseek)
#    - OPENAI_API_KEY: 你的 OpenAI API Key (如果选择 openai)
# 4. 部署应用