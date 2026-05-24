import streamlit as st
import requests
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def get_roles():
    try:
        response = requests.get(f"{API_BASE_URL}/roles")
        response.raise_for_status()
        return response.json()["roles"]
    except Exception as e:
        st.error(f"无法获取角色列表: {e}")
        return []

def get_personas():
    try:
        response = requests.get(f"{API_BASE_URL}/personas")
        response.raise_for_status()
        return response.json()["personas"]
    except Exception as e:
        st.error(f"无法获取人物列表: {e}")
        return []

def send_message(user_id, role, message):
    try:
        payload = {
            "input": {"input": message},
            "config": {}
        }
        response = requests.post(f"{API_BASE_URL}/{role}/invoke", json=payload)
        response.raise_for_status()
        result = response.json()
        return result["output"]
    except Exception as e:
        st.error(f"发送消息失败: {e}")
        return None

def main():
    st.set_page_config(page_title="AI角色扮演助手", page_icon="🎭", layout="wide")
    
    st.title("🎭 AI角色扮演助手")
    st.markdown("**与知名人物对话 - 穿越时空的智能问答**")
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = None
    
    if "selected_persona" not in st.session_state:
        st.session_state.selected_persona = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_mode" not in st.session_state:
        st.session_state.chat_mode = "famous_person"
    
    # 模式选择
    st.markdown("### 💬 选择对话模式")
    col_mode1, col_mode2 = st.columns(2)
    
    with col_mode1:
        if st.button("🌟 与知名人物对话", 
                    use_container_width=True,
                    type="primary" if st.session_state.chat_mode == "famous_person" else "secondary"):
            st.session_state.chat_mode = "famous_person"
            st.session_state.selected_role = None
            st.session_state.selected_persona = None
            st.session_state.messages = []
            st.rerun()
    
    with col_mode2:
        if st.button("💼 与职业角色对话", 
                    use_container_width=True,
                    type="primary" if st.session_state.chat_mode == "professional" else "secondary"):
            st.session_state.chat_mode = "professional"
            st.session_state.selected_role = None
            st.session_state.selected_persona = None
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    if st.session_state.chat_mode == "famous_person":
        render_famous_person_chat()
    else:
        render_professional_chat()

def render_famous_person_chat():
    """知名人物对话界面"""
    st.markdown("### 🌟 选择知名人物")
    
    personas = get_personas()
    
    if not personas:
        personas = [
            {"id": "shakespeare", "name": "� 莎士比亚", "description": "英国文学巨匠"},
            {"id": "kobe", "name": "� 科比", "description": "NBA传奇球星"},
            {"id": "curie", "name": "� 居里夫人", "description": "两次诺贝尔奖得主"}
        ]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 分两列显示人物选择
        cols = st.columns(2)
        for idx, persona in enumerate(personas):
            with cols[idx % 2]:
                if st.button(
                    f"{persona['name']}\n*{persona['description']}*",
                    key=f"persona_{persona['id']}",
                    use_container_width=True,
                    help=f"选择与{persona['name']}对话"
                ):
                    st.session_state.selected_persona = persona
                    st.session_state.selected_role = None
                    st.session_state.messages = []
        
        if st.session_state.selected_persona:
            st.markdown(f"""
            **当前人物:** {st.session_state.selected_persona['name']}
            
            *{st.session_state.selected_persona['description']}*
            """)
            
            if st.button("🔄 切换人物", use_container_width=True):
                st.session_state.selected_persona = None
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        render_chat_area()

def render_professional_chat():
    """职业角色对话界面"""
    st.markdown("### 💼 选择职业角色")
    
    roles = get_roles()
    
    if not roles:
        roles = [
            {"id": "tech_teacher", "name": "🖥️ 编程导师", "description": "帮助你学习编程"},
            {"id": "travel_guide", "name": "✈️ 旅行向导", "description": "提供旅行建议"},
            {"id": "psychologist", "name": "🧠 心理咨询师", "description": "倾听你的烦恼"},
            {"id": "story_teller", "name": "📖 故事作家", "description": "创作有趣的故事"},
            {"id": "career_coach", "name": "💼 职业规划师", "description": "帮助你规划职业"}
        ]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        for role in roles:
            if st.button(
                f"{role['name']}\n*{role['description']}*",
                key=f"role_{role['id']}",
                use_container_width=True
            ):
                st.session_state.selected_role = role
                st.session_state.selected_persona = None
                st.session_state.messages = []
        
        if st.session_state.selected_role:
            st.markdown(f"""
            **当前角色:** {st.session_state.selected_role['name']}
            
            *{st.session_state.selected_role['description']}*
            """)
            
            if st.button("🔄 切换角色", use_container_width=True):
                st.session_state.selected_role = None
                st.session_state.messages = []
                st.rerun()
    
    with col2:
        render_chat_area()

def render_chat_area():
    """通用对话区域"""
    current_role = st.session_state.selected_role or st.session_state.selected_persona
    
    if not current_role:
        st.info("👈 请从左侧选择一个角色开始对话")
        st.markdown("""
        **使用说明：**
        1. 选择对话模式（知名人物/职业角色）
        2. 从左侧选择一个角色
        3. 在下方输入你的问题
        4. 开始有趣的对话！
        """)
        return
    
    role_name = current_role.get('name', current_role.get('name', 'AI'))
    
    for msg in st.session_state.messages:
        avatar = role_name.split()[0] if ' ' in role_name else role_name[0]
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input(f"向 {role_name} 提问...", key=f"input_{current_role['id']}"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        avatar = role_name.split()[0] if ' ' in role_name else role_name[0]
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=avatar):
            with st.spinner(f"{role_name}思考中..."):
                response = send_message(
                    st.session_state.user_id,
                    current_role["id"],
                    prompt
                )
            
            if response:
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("消息发送失败，请检查后端服务是否运行")

if __name__ == "__main__":
    main()
