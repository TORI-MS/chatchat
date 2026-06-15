import streamlit as st
import datetime

st.title("💬 우리들의 익명 메시지 보드")
st.write("다양한 의견이나 인사를 자유롭게 남겨주세요!")

# 1. 메시지 저장소 초기화 (실제 서비스에서는 DB 연결 필요)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"user": "관리자", "text": "환영합니다! 첫 메시지를 남겨보세요.", "time": "09:00"}
    ]

# 2. 기존 메시지들 보여주기
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.write(f"**{msg['user']}** ({msg['time']})")
        st.write(msg['text'])

# 3. 사용자 입력 받기
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # 현재 시간 구하기
    now = datetime.datetime.now().strftime("%H:%M")
    
    # 새로운 메시지 추가
    new_msg = {"user": "익명 사용자", "text": user_input, "time": now}
    st.session_state.messages.append(new_msg)
    
    # 화면 새로고침하여 즉시 반영
    st.rerun()
