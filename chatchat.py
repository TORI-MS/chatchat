import streamlit as st
import datetime
import pandas as pd
import gspread

st.title("💬 실시간 보관되는 메시지 보드")

SPREADSHEET_ID = "1pmjIfXlPGWniRXlKShpPtYPZliOdlfaqMvBaqlW-jyU"
WORKSHEET_NAME = "시트1"  # ⚠️ 구글 시트 맨 아래 탭 이름과 정확히 일치해야 합니다!

# 1. 구글 서비스 계정 자격증명 설정
service_account_info = {
    "type": "service_account",
    "project_id": "여기에_project_id_입력",
    "private_key": """-----BEGIN PRIVATE KEY-----
여기에_다운로드한_JSON의_private_key_전체_붙여넣기
-----END PRIVATE KEY-----""",
    "client_email": "여기에_client_email_입력",
}

@st.cache_resource
def get_gspread_client():
    return gspread.service_account_from_dict(service_account_info)

# 변수 초기화
worksheet = None
df = pd.DataFrame(columns=["name", "text", "time"])

# 2. 구글 시트 연결 및 데이터 읽기
try:
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.worksheet(WORKSHEET_NAME)
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except gspread.exceptions.WorksheetNotFound:
    st.error(f"❌ 구글 시트 안에서 '{WORKSHEET_NAME}'이라는 이름의 탭을 찾을 수 없습니다. 탭 이름을 다시 확인해 주세요.")
except Exception as e:
    st.error(f"❌ 구글 시트 연결 중 오류 발생: {e}")
    st.info("💡 서비스 계정 이메일이 구글 시트에 '편집자'로 공유되어 있는지 꼭 확인해 주세요.")

# 3. 기존 메시지 화면에 출력하기
if not df.empty:
    df = df.fillna("")
    for index, row in df.iterrows():
        with st.chat_message("user"):
            st.write(f"**{row.get('name', '익명')}** ({row.get('time', '')})")
            st.write(row.get('text', ''))

# 4. 사용자 입력 받기
user_input = st.chat_input("메시지를 입력하고 엔터를 누르세요...")

if user_input:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # worksheet 변수가 정상적으로 생성되었는지 검사
    if worksheet is not None:
        try:
            new_row = ["익명 사용자", user_input, now]
            worksheet.append_row(new_row)
            
            st.toast("메시지가 성공적으로 등록되었습니다! 🎉")
            st.rerun()
        except Exception as e:
            st.error(f"저장 실패! 에러 내용: {e}")
    else:
        st.error("❌ 구글 시트와 연결되지 않아 메시지를 저장할 수 없습니다. 상단의 에러 메시지를 확인해 주세요.")
