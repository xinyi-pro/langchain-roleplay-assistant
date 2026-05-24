"""
AI角色扮演助手 - Streamlit Cloud 部署版本
支持知名人物对话和职业角色对话
"""
import streamlit as st
import uuid
import os

# LangChain 导入
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# ==================== 知名人物配置 ====================
PERSONAS = [
    {
        "id": "shakespeare",
        "name": "📜 莎士比亚",
        "description": "英国文学巨匠，戏剧之王",
        "system_prompt": """你是威廉·莎士比亚，英国文艺复兴时期最伟大的戏剧家和诗人。

背景：
- 你创作了《哈姆雷特》《罗密欧与朱丽叶》《麦克白》等不朽名著
- 你的作品深刻揭示了人性的复杂与命运的无常
- 你的文字跨越四百年，至今仍在世界各地被演绎和研究

性格特点：
- 对人性有极其深刻的洞察
- 语言华丽且富有诗意
- 幽默与深沉并存
- 善于塑造鲜明的角色
- 热爱戏剧和舞台艺术

说话风格：
- 用诗意的语言表达观点
- 善用比喻和排比
- 偶尔引用自己的经典台词
- 充满戏剧性和感染力
- 能从平凡中发现深刻的哲理

请始终保持莎士比亚的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "kobe",
        "name": "🏀 科比·布莱恩特",
        "description": "NBA传奇球星，黑曼巴精神代表",
        "system_prompt": """你是科比·布莱恩特，NBA历史上最伟大的球员之一。

背景：
- 你效力于洛杉矶湖人队20年，赢得了5座NBA总冠军
- 你以"黑曼巴精神"著称，代表着极致的勤奋和对完美的追求
- 退役后你投身于投资、影视创作和青少年篮球教育

性格特点：
- 极度自律和勤奋
- 永不满足，追求极致
- 自信坚韧，不惧竞争
- 认真专注，对细节苛刻
- 勇于承担领袖责任

说话风格：
- 简短有力，直击要点
- 充满斗志和能量
- 常用篮球比喻人生
- 强调努力和态度
- 激励他人追求卓越

请始终保持科比的角色特点，用黑曼巴精神回答问题。"""
    },
    {
        "id": "curie",
        "name": "🔬 居里夫人",
        "description": "两次诺贝尔奖得主，放射性研究先驱",
        "system_prompt": """你是玛丽·居里，历史上最伟大的女性科学家之一。

背景：
- 你发现了放射性元素镭和钋，开创了放射性研究领域
- 你是第一个获得诺贝尔奖的女性，也是唯一获得两次诺贝尔奖的科学家
- 你在极其艰苦的条件下坚持科研，最终为科学献身

性格特点：
- 严谨认真，一丝不苟
- 坚韧不拔，不畏困难
- 淡泊名利，专注科研
- 富有责任感和使命感
- 谦虚谨慎，不张扬

说话风格：
- 用事实和数据说话
- 逻辑严密，条理清晰
- 温和但坚定
- 强调实验和实践的重要性
- 鼓励女性追求科学梦想

请始终保持居里夫人的角色特点，用她严谨而温和的风格回答问题。"""
    }
]

# ==================== 职业角色配置 ====================
ROLE_TEMPLATES = {
    "tech_teacher": """你是一位耐心的编程技术导师。
    你的任务是帮助用户学习编程知识，解答技术问题。
    请用简洁明了的语言解释复杂概念。""",
    "travel_guide": """你是一位专业的旅行向导。
    你的任务是为用户提供旅行建议、目的地推荐和行程规划。
    请提供详细有用的旅行信息。""",
    "psychologist": """你是一位友善的心理咨询师。
    你的任务是倾听用户的烦恼，给予安慰和建议。
    请保持同理心和专业态度。""",
    "story_teller": """你是一位富有想象力的故事作家。
    你的任务是根据用户的要求创作有趣的故事。
    请发挥创造力，让故事生动有趣。""",
    "career_coach": """你是一位资深的职业规划师。
    你的任务是帮助用户规划职业发展，提供求职建议。
    请给出专业实用的建议。"""
}

ROLES = [
    {"id": "tech_teacher", "name": "🖥️ 编程导师", "description": "帮助你学习编程"},
    {"id": "travel_guide", "name": "✈️ 旅行向导", "description": "提供旅行建议"},
    {"id": "psychologist", "name": "🧠 心理咨询师", "description": "倾听你的烦恼"},
    {"id": "story_teller", "name": "📖 故事作家", "description": "创作有趣的故事"},
    {"id": "career_coach", "name": "💼 职业规划师", "description": "帮助你规划职业"}
]

# ==================== LLM 配置 ====================
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

def create_chain(role_type: str, role_id: str):
    """创建对话链"""
    llm = get_llm()
    
    if role_type == "persona":
        # 知名人物
        persona = next((p for p in PERSONAS if p["id"] == role_id), None)
        if not persona:
            raise ValueError(f"未知人物: {role_id}")
        system_prompt = persona["system_prompt"]
    else:
        # 职业角色
        if role_id not in ROLE_TEMPLATES:
            raise ValueError(f"未知角色: {role_id}")
        system_prompt = ROLE_TEMPLATES[role_id]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain

# ==================== Streamlit 应用 ====================
def main():
    st.set_page_config(page_title="AI角色扮演助手", page_icon="🎭", layout="wide")
    
    st.title("🎭 AI角色扮演助手")
    st.markdown("**与知名人物对话 | 穿越时空的智能问答**")
    
    # 初始化会话状态
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "selected_role_type" not in st.session_state:
        st.session_state.selected_role_type = None
    
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chain" not in st.session_state:
        st.session_state.chain = None
    
    # 模式选择
    st.markdown("### 💬 选择对话模式")
    
    col_mode1, col_mode2 = st.columns(2)
    
    with col_mode1:
        mode1_clicked = st.button(
            "🌟 与知名人物对话",
            use_container_width=True,
            type="primary"
        )
    
    with col_mode2:
        mode2_clicked = st.button(
            "💼 与职业角色对话",
            use_container_width=True,
            type="secondary"
        )
    
    if mode1_clicked:
        st.session_state.selected_role_type = "persona"
        st.session_state.selected_role = None
        st.session_state.messages = []
        st.session_state.chain = None
        st.rerun()
    
    if mode2_clicked:
        st.session_state.selected_role_type = "role"
        st.session_state.selected_role = None
        st.session_state.messages = []
        st.session_state.chain = None
        st.rerun()
    
    st.divider()
    
    if st.session_state.selected_role_type == "persona":
        render_persona_selection()
    else:
        render_role_selection()

def render_persona_selection():
    """知名人物选择界面"""
    st.markdown("### 🌟 选择知名人物")
    
    # 显示人物网格
    cols = st.columns(4)
    for idx, persona in enumerate(PERSONAS):
        with cols[idx % 4]:
            if st.button(
                f"{persona['name']}\n*{persona['description']}*",
                key=f"persona_{persona['id']}",
                use_container_width=True,
                help=f"与{persona['name']}对话"
            ):
                st.session_state.selected_role = persona
                st.session_state.messages = []
                try:
                    st.session_state.chain = create_chain("persona", persona["id"])
                    st.success(f"已选择 {persona['name']}")
                except Exception as e:
                    st.error(f"初始化失败: {e}")
    
    if st.session_state.selected_role:
        st.markdown(f"""
        **当前人物:** {st.session_state.selected_role['name']}
        
        *{st.session_state.selected_role['description']}*
        """)
        
        if st.button("🔄 切换人物", use_container_width=True):
            st.session_state.selected_role = None
            st.session_state.messages = []
            st.session_state.chain = None
            st.rerun()
    
    st.divider()
    render_chat_area()

def render_role_selection():
    """职业角色选择界面"""
    st.markdown("### 💼 选择职业角色")
    
    cols = st.columns(5)
    for idx, role in enumerate(ROLES):
        with cols[idx % 5]:
            if st.button(
                f"{role['name']}\n*{role['description']}*",
                key=f"role_{role['id']}",
                use_container_width=True,
                help=f"与{role['name']}对话"
            ):
                st.session_state.selected_role = role
                st.session_state.messages = []
                try:
                    st.session_state.chain = create_chain("role", role["id"])
                    st.success(f"已选择 {role['name']}")
                except Exception as e:
                    st.error(f"初始化失败: {e}")
    
    if st.session_state.selected_role:
        st.markdown(f"""
        **当前角色:** {st.session_state.selected_role['name']}
        
        *{st.session_state.selected_role['description']}*
        """)
        
        if st.button("🔄 切换角色", use_container_width=True):
            st.session_state.selected_role = None
            st.session_state.messages = []
            st.session_state.chain = None
            st.rerun()
    
    st.divider()
    render_chat_area()

def render_chat_area():
    """对话区域"""
    if not st.session_state.selected_role:
        st.info("👈 请先选择一个角色开始对话")
        st.markdown("""
        **使用说明:**
        1. 选择对话模式（知名人物/职业角色）
        2. 从上方选择一个角色
        3. 在下方输入你的问题
        4. 开始有趣的对话！
        
        **知名人物：** 📜莎士比亚 🏀科比·布莱恩特 🔬居里夫人
        **职业角色：** 🖥️编程导师 ✈️旅行向导 🧠心理咨询师 📖故事作家 💼职业规划师
        """)
        return
    
    role_name = st.session_state.selected_role['name']
    avatar = role_name.split()[0] if ' ' in role_name else role_name[0]
    
    # 显示对话历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=avatar if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
    
    # 输入新消息
    if prompt := st.chat_input(f"向 {role_name} 提问..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=avatar):
            with st.spinner(f"{role_name}思考中..."):
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

# ==================== 部署说明 ====================
# Streamlit Cloud 部署步骤：
# 1. 将此文件保存为 app.py
# 2. 在 Streamlit Cloud 创建新项目
# 3. 设置环境变量:
#    - API_PROVIDER: deepseek 或 openai
#    - DEEPSEEK_API_KEY: 你的 DeepSeek API Key
# 4. 部署应用
