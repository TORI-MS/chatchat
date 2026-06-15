import streamlit as st
import datetime
import pandas as pd
import gspread

st.title("💬 실시간 보관되는 메시지 보드")

SPREADSHEET_ID = "1pmjIfXlPGWniRXlKShpPtYPZliOdlfaqMvBaqlW-jyU"
WORKSHEET_NAME = "시트1"

# 1. 코드 내부에서 직접 구글 서비스 계정 자격증명을 구성합니다.
# 다운로드하신 JSON 파일의 내용을 아래에 그대로 붙여넣으세요.
service_account_info = {
    "type": "service_account",
    "project_id": "여기에_project_id_입력",
    "private_key": """-----BEGIN PRIVATE KEY-----
여기에_다운로드한_JSON의_private_key_전체_붙여넣기
-----END PRIVATE KEY-----""",
    "client_email": "여기에_client_email_입력",
}

# 2. 스트림릿 커넥션 에러를 우회하여, gspread로 직접 구글 시트에 로그인합니다.
@st.cache_resource # 매번 로그인하지 않도록 세션 유지
def get_gspread_client():
    return gspread.service_account_from_dict(service_account_info)

try:
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet(WORKSHEET_NAME)
    
    # 구글 시트에서 전체 데이터를 읽어와 데이터프레임으로 변환
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    # 시트가 비어있거나 첫 연결 시 오류 방지용 구조 생성
    df = pd.DataFrame(columns=["name", "text", "time"])

# 3. 기존 메시지 화면에 출력하기
if not df.empty:
    df = df.fillna("")
    for index, row in df.iterrows():
        with st.chat_message("user"):
            # 컬럼명이 구글 시트 첫 줄과 정확히 일치해야 합니다.
            st.write(f"**{row.get('name', '익명')}** ({row.get('time', '')})")
            st.write(row.get('text', ''))

# 4. 사용자 입력 받기
user_input = st.chat_input("메시지를 입력하고 엔터를 누르세요...")

if user_input:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        # gspread 방식은 한 줄씩 데이터를 바로 아래에 이어붙이기(append)가 가능합니다.
        # 기존 전체 데이터를 덮어쓰지 않아도 되므로 훨씬 빠르고 안전합니다!
        new_row = ["익명 사용자", user_input, now]
        worksheet.append_row(new_row)
        
        st.toast("메시지가 성공적으로 등록되었습니다! 🎉")
        st.rerun()
    except Exception as e:
        st.error(f"저장 실패! 에러 내용: {e}")
