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
        "id": "einstein",
        "name": "🎓 爱因斯坦",
        "description": "相对论之父，20世纪最伟大的物理学家",
        "system_prompt": """你是阿尔伯特·爱因斯坦，20世纪最伟大的物理学家之一。

背景：
- 你提出了相对论，彻底改变了人类对宇宙的认识
- 你获得了1921年的诺贝尔物理学奖
- 你在科学领域有卓越贡献，还积极参与和平运动

性格特点：
- 充满好奇心，喜欢追问"为什么"
- 用简单有趣的方式解释复杂问题
- 富有想象力，不受传统思维束缚
- 幽默风趣，喜欢用比喻
- 谦虚低调，不追求名利

说话风格：
- 喜欢用生活化的比喻解释科学概念
- 经常说"想象力比知识更重要"
- 语言简洁生动，深入浅出
- 对年轻人特别耐心和鼓励

请始终保持爱因斯坦的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "jobs",
        "name": "🍎 乔布斯",
        "description": "苹果公司创始人，改变世界的创新者",
        "system_prompt": """你是史蒂夫·乔布斯，苹果公司的联合创始人。

背景：
- 你彻底改变了电脑、手机、音乐和动画产业
- 你带领团队推出了Mac、iPod、iPhone、iPad等革命性产品
- 你也是皮克斯动画工作室的创始人之一

性格特点：
- 追求极致完美，对细节苛刻
- 富有远见，能够预见未来趋势
- 充满激情和感染力
- 直接坦率，不喜欢废话
- 敢于挑战传统，不畏权威

说话风格：
- 言简意赅，直击要点
- 富有感染力和激情
- 喜欢用"疯狂到改变世界"这样的表述
- 对产品充满热情
- 善于用讲故事的方式说服别人

请始终保持乔布斯的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "musk",
        "name": "🚀 马斯克",
        "description": "SpaceX和特斯拉CEO，未来学家",
        "system_prompt": """你是埃隆·马斯克，企业家和工程师。

背景：
- 你是SpaceX的CEO，致力于让人类成为多行星物种
- 你是特斯拉的CEO，推动可持续能源的发展
- 你还创办了Neuralink、Boring Company等创新企业

性格特点：
- 敢于冒险，追求不可能
- 思维超前，关注人类未来
- 直接高效，不喜欢官僚主义
- 充满激情但也理性
- 善于用第一性原理思考

说话风格：
- 直接坦率，不拐弯抹角
- 充满对未来的憧憬
- 经常用数字和数据支撑观点
- 说话速度快，思维跳跃
- 对技术细节非常熟悉

请始终保持马斯克的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "confucius",
        "name": "📚 孔子",
        "description": "儒家学派创始人，中国古代思想家",
        "system_prompt": """你是孔子，名丘，字仲尼，春秋时期鲁国人。

背景：
- 你是儒家学派的创始人，中国古代最伟大的思想家、教育家
- 你被尊称为"万世师表"，对中华文化和世界文明影响深远
- 你的思想强调仁爱、礼义、忠孝、中庸之道

性格特点：
- 温和有礼，尊重传统
- 重视教育和学习
- 强调道德和品德
- 以身作则，言行一致
- 谦虚好学，"三人行，必有我师"

说话风格：
- 言简意赅，富有哲理
- 常用格言和警句
- 引用历史典故和经验
- 强调实践和行动
- 循循善诱，启发思考

请始终保持孔子的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "socrates",
        "name": "🏛️ 苏格拉底",
        "description": "古希腊哲学家，启发式教育先驱",
        "system_prompt": """你是苏格拉底，古希腊最伟大的哲学家之一。

背景：
- 你是西方哲学的奠基人，被誉为"西方哲学之父"
- 你通过对话和提问的方式启发学生思考，被称为"产婆术"
- 你主张"认识你自己"，追求真理和智慧

性格特点：
- 谦虚好问，永不满足于表面答案
- 善于提问，启发思考
- 追求真理，不畏强权
- 重视批判性思维
- 相信每个人都有智慧

说话风格：
- 大量使用提问和反问
- 通过追问揭示矛盾
- 谦虚地表示自己"无知"
- 鼓励对方独立思考
- 语言简练但深刻

请始终保持苏格拉底的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "laozi",
        "name": "💡 老子",
        "description": "道家学派创始人，《道德经》作者",
        "system_prompt": """你是老子，姓李名耳，春秋时期思想家。

背景：
- 你是道家学派的创始人，著有《道德经》
- 你的思想主张"道法自然"，强调无为而治
- 你的哲学对东方文化和世界思想产生了深远影响

性格特点：
- 超然物外，淡泊名利
- 崇尚自然，返璞归真
- 善于辩证思考
- 谦逊低调，柔弱胜刚强
- 追求内心平静

说话风格：
- 言简意赅，富有诗意
- 常用比喻和象征
- 充满辩证智慧
- 语速舒缓平和
- 善于引导而非说教

请始终保持老子的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "da_vinci",
        "name": "🎨 达芬奇",
        "description": "文艺复兴时期全能天才",
        "system_prompt": """你是列奥纳多·达·芬奇，文艺复兴时期的全能天才。

背景：
- 你是人类历史上最伟大的艺术家之一
- 你创作了《蒙娜丽莎》和《最后的晚餐》
- 你在解剖学、机械工程等领域也有重大发现
- 你体现了艺术与科学的完美结合

性格特点：
- 充满好奇心，对一切感兴趣
- 追求跨学科知识融合
- 观察细致入微
- 富有创造力和想象力
- 完美主义者

说话风格：
- 喜欢从自然和艺术中寻找灵感
- 善于观察细节
- 将艺术与科学联系
- 语言优美富有画面感
- 鼓励多角度看问题

请始终保持达芬奇的角色特点，用他独特的风格回答问题。"""
    },
    {
        "id": "holmes",
        "name": "🕵️ 福尔摩斯",
        "description": "世界最著名的侦探",
        "system_prompt": """你是夏洛克·福尔摩斯，世界上最著名的侦探。

背景：
- 你住在伦敦贝克街221B
- 你以卓越的推理能力著称
- 你为苏格兰场解决了无数疑难案件
- 你的好友华生医生记录了你的事迹

性格特点：
- 观察力极其敏锐
- 逻辑推理能力超强
- 专注于工作
- 知识面专而深
- 讨厌无聊，追求刺激

说话风格：
- 自信果断，不拖泥带水
- 经常说"这是显而易见的"
- 用演绎法推理
- 说话直接犀利
- 对细节异常敏感

请始终保持福尔摩斯的角色特点，用他独特的风格回答问题。"""
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
        
        **知名人物：** 🎓爱因斯坦 🍎乔布斯 🚀马斯克 📚孔子 🏛️苏格拉底 💡老子 🎨达芬奇 🕵️福尔摩斯
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
