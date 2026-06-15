import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("💬 실시간 보관되는 메시지 보드")

SPREADSHEET_ID = "1pmjIfXlPGWniRXlKShpPtYPZliOdlfaqMvBaqlW-jyU"
WORKSHEET_NAME = "시트1"

# [수정] st.connection이 오작동하지 않도록 딕셔너리 구조를 명확히 정의합니다.
service_account_info = {
    "type": "service_account",
    "project_id": "여기에_project_id_입력",
    "private_key": """-----BEGIN PRIVATE KEY-----
여기에_다운로드한_JSON의_private_key_전체_붙여넣기
-----END PRIVATE KEY-----""",
    "client_email": "여기에_client_email_입력",
}

# [핵심 수정] ** 인증 정보를 직접 풀지 않고, 지정된 형식(credentials)으로 포장해서 넘겨줍니다.
conn = st.connection(
    "gsheets", 
    type=GSheetsConnection, 
    credentials=service_account_info
)

try:
    df = conn.read(spreadsheet=SPREADSHEET_ID, worksheet=WORKSHEET_NAME, ttl=0)
except Exception as e:
    df = pd.DataFrame(columns=["name", "text", "time"])

if not df.empty:
    df = df.fillna("")
    for index, row in df.iterrows():
        with st.chat_message("user"):
            st.write(f"**{row['name']}** ({row['time']})")
            st.write(row['text'])

user_input = st.chat_input("메시지를 입력하고 엔터를 누르세요...")

if user_input:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_data = pd.DataFrame([{"name": "익명 사용자", "text": user_input, "time": now}])
    
    if not df.empty:
        updated_df = pd.concat([df, new_data], ignore_index=True)
    else:
        updated_df = new_data
    
    try:
        conn.update(spreadsheet=SPREADSHEET_ID, worksheet=WORKSHEET_NAME, data=updated_df)
        st.toast("메시지가 성공적으로 등록되었습니다! 🎉")
        st.rerun()
    except Exception as e:
        st.error(f"저장 실패! 에러 내용: {e}")
