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
    st.set_page_config(page_title="角色扮演AI助手", page_icon="🎭", layout="wide")
    
    st.title("🎭 角色扮演AI助手")
    st.subheader("选择一个角色开始对话")
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    roles = get_roles()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 角色选择")
        for role in roles:
            if st.button(role["name"], key=role["id"], use_container_width=True):
                st.session_state.selected_role = role
                st.session_state.messages = []
        
        if st.session_state.selected_role:
            st.markdown(f"**当前角色:** {st.session_state.selected_role['name']}")
            st.markdown(f"*描述:* {st.session_state.selected_role['description']}")
            
            if st.button("🔄 切换角色", use_container_width=True):
                st.session_state.selected_role = None
                st.session_state.messages = []
    
    with col2:
        st.markdown("### 对话区域")
        
        if not st.session_state.selected_role:
            st.info("请从左侧选择一个角色开始对话")
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if prompt := st.chat_input("请输入你的消息..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("AI思考中..."):
                        response = send_message(
                            st.session_state.user_id,
                            st.session_state.selected_role["id"],
                            prompt
                        )
                    
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()