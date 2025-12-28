import streamlit as st
import google.generativeai as genai

# 1. 页面基本配置
st.set_page_config(page_title="AI 助手 (BYOK版)", page_icon="🤖")
st.title("🤖 跟我制作的 AI 聊聊")

# 2. 侧边栏：让朋友输入自己的 API Key
with st.sidebar:
    st.header("🔑 身份验证")
    st.markdown("""
    为了使用此工具，你需要输入自己的 Google API Key。
    
    [👉 点击这里免费获取 Key](https://aistudio.google.com/app/apikey)
    """)
    # type="password" 可以让输入的字符变成圆点，保护隐私
    user_api_key = st.text_input("请输入你的 API Key", type="password")

# 3. 检查是否输入了 Key
if not user_api_key:
    st.info("👈 请先在左侧输入你的 Google API Key 才能开始对话。")
    st.stop() # 停止运行下面的代码，直到用户输入 Key

# 4. 配置 Google Gemini (使用朋友的 Key)
try:
    genai.configure(api_key=user_api_key)
    # 简单测试一下 Key 是否有效
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"API Key 设置有误，请检查: {e}")
    st.stop()

# --- 以下是聊天逻辑 (和之前一样) ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("输入你想说的话..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            chat = model.start_chat(history=[
                {"role": m["role"], "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            response = chat.send_message(prompt, stream=True)
            
            # 简单的流式输出效果
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "model", "content": full_response})
        except Exception as e:
            st.error(f"发生错误 (可能是网络或Key的问题): {e}")
