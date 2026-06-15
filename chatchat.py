import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("💬 실시간 보관되는 메시지 보드")

# 1. URL 전체를 넣는 대신, 중간에 있는 '고유 ID'만 추출해서 넣습니다.
# https://docs.google.com/spreadsheets/d/[여기 들어있는 문자열]/edit 에서 중간 ID 부분입니다.
SPREADSHEET_ID = "1pmjIfXlPGWniRXlKShpPtYPZliOdlfaqMvBaqlW-jyU"

# 2. 구글 시트 맨 아래에 있는 탭 이름(워크시트 이름)을 적어줍니다. 기본값은 보통 "시트1" 또는 "Sheet1" 입니다.
WORKSHEET_NAME = "시트1" 

# Secrets 설정을 기반으로 구글 시트 연결 생성
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # URL 대신 spreadsheet_id와 worksheet 이름을 명시합니다.
    df = conn.read(spreadsheet=SPREADSHEET_ID, worksheet=WORKSHEET_NAME, ttl=0)
except Exception as e:
    # 시트가 완전히 비어있거나 오류가 날 경우 구조 강제 생성
    df = pd.DataFrame(columns=["name", "text", "time"])

# 3. 기존 메시지 화면에 출력하기
if not df.empty:
    # 혹시 모를 결측치(NaN) 제거 및 텍스트 변환
    df = df.fillna("")
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
    
    # 기존 데이터가 비어있지 않다면 합치고, 비어있다면 새 데이터가 기준이 됨
    if not df.empty:
        updated_df = pd.concat([df, new_data], ignore_index=True)
    else:
        updated_df = new_data
    
    try:
        # 업데이트할 때도 ID와 워크시트 이름을 명시하여 서비스 계정 권한을 강제로 깨웁니다.
        conn.update(spreadsheet=SPREADSHEET_ID, worksheet=WORKSHEET_NAME, data=updated_df)
        st.toast("메시지가 성공적으로 등록되었습니다! 🎉")
        st.rerun()
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다. 토큰 설정을 다시 확인해주세요. 에러 내용: {e}")
