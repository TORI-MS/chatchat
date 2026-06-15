import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("💬 실시간 보관되는 메시지 보드")

# 1. 구글 시트 연결 설정 (여기에 복사한 구글 시트 링크를 넣으세요)
# 주의: 링크 끝부분이 /edit?usp=sharing 이라면 /edit#gid=0 등으로 끝날 수 있습니다. URL 그대로 넣으시면 됩니다.
GSHEETS_URL = "여기에_복사한_구글_시트_링크를_넣으세요"

conn = st.connection("gsheets", type=GSheetsConnection)

# 2. 구글 시트에서 기존 데이터 읽어오기
try:
    df = conn.read(spreadsheet=GSHEETS_URL, ttl="0") # ttl="0"은 캐시 없이 항상 새로고침하겠다는 뜻
except Exception:
    # 시트가 비어있을 때를 위한 예외 처리
    df = pd.DataFrame(columns=["name", "text", "time"])

# 3. 기존 메시지 화면에 출력하기
for index, row in df.iterrows():
    with st.chat_message("user"):
        st.write(f"**{row['name']}** ({row['time']})")
        st.write(row['text'])

# 4. 사용자 입력 받기
user_input = st.chat_input("메시지를 입력하고 엔터를 누르세요...")

if user_input:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 새 메시지 데이터 생성
    new_data = pd.DataFrame([{"name": "익명 사용자", "text": user_input, "time": now}])
    
    # 기존 데이터에 새 데이터 합치기
    updated_df = pd.concat([df, new_data], ignore_index=True)
    
    # 구글 시트에 업데이트(저장)하기
    conn.update(spreadsheet=GSHEETS_URL, data=updated_df)
    
    # 화면 즉시 반영
    st.rerun()
