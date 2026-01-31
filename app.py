import streamlit as st
import pandas as pd
import datetime
import os
import random
import urllib.parse
import re
import time

# 1. 앱 설정 및 원페이지 최적화
st.set_page_config(page_title="시립대 CPA 커넥트", page_icon="🚕", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stSidebarCollapseIcon"] {display: none !important;}
    .stDeployButton {display: none !important;}
    footer {display: none !important;}
    header {visibility: hidden !important;}

    .stApp { background-color: #f8f9fa; }
    .main-card { border: 1px solid #e1e4e8; border-radius: 12px; padding: 18px; background-color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 15px; }
    .countdown-box { background: #002758; color: white; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: bold; }
    .bujuk-card { 
        background: linear-gradient(135deg, #fff9c4 0%, #fbc02d 100%); 
        border: 2px solid #f9a825; padding: 20px; border-radius: 15px; 
        text-align: center; margin-bottom: 25px; font-weight: bold; 
        color: #5f4b00; font-size: 1.1em; line-height: 1.6;
    }
    .section-title { font-size: 1.4em; font-weight: bold; color: #002758; margin: 35px 0 10px 0; padding-left: 10px; border-left: 5px solid #002758; }
    .guide-box { background: #f1f3f5; padding: 15px; border-radius: 10px; border-left: 5px solid #002758; font-size: 0.85em; color: #333; line-height: 1.6; margin-bottom: 15px; }
    .security-box { background: #fff5f5; padding: 12px; border-radius: 10px; border: 1px solid #feb2b2; font-size: 0.85em; color: #c53030; margin-bottom: 15px; }
    .manner-tag { display: inline-block; padding: 2px 8px; border-radius: 15px; font-size: 0.8em; background: #e0e7ff; color: #4338ca; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 및 고사장 정보
DB_FILE, BOARD_FILE, CHEER_FILE = "cpa_db.csv", "cpa_board.csv", "cpa_cheer.csv"
ANIMALS = ["이루매 🦅", "아기사자 🦁", "똑똑한쿼카 🐾", "합격판다 🐼", "행운토끼 🐰", "회계사여우 🦊", "정답너구리 🦝", "열공고양이 🐱", "계산하는곰 🐻", "지혜로운부엉이 🦉"]

TEST_CENTERS = [
    {"이름": "경기고", "start": 25100001, "end": 25101100}, {"이름": "둔촌중", "start": 25101101, "end": 25101625},
    {"이름": "명일중", "start": 25101626, "end": 25102400}, {"이름": "등촌고", "start": 25102401, "end": 25103150},
    {"이름": "경인중", "start": 25103151, "end": 25103656}, {"이름": "광운인공지능고", "start": 25103657, "end": 25104056},
    {"이름": "녹천중", "start": 25104057, "end": 25104456}, {"이름": "장승중", "start": 25104457, "end": 25105056},
    {"이름": "아현중", "start": 25105057, "end": 25105456}, {"이름": "연희중", "start": 25105457, "end": 25106016},
    {"이름": "성수중", "start": 25106017, "end": 25106376}, {"이름": "숭곡중", "start": 25106377, "end": 25106976},
    {"이름": "오주중", "start": 25106977, "end": 25107626}, {"이름": "오금중", "start": 25107627, "end": 25108301},
    {"이름": "봉영여중", "start": 25108302, "end": 25108801}, {"이름": "신길중", "start": 25108802, "end": 25109476},
    {"이름": "용산철도고", "start": 25109477, "end": 25110276}, {"이름": "선린인터넷고", "start": 25110277, "end": 25110996},
    {"이름": "은평중", "start": 25110997, "end": 25111416}, {"이름": "증산중", "start": 25111417, "end": 25111916},
    {"이름": "중화고", "start": 25111917, "end": 25112556}, {"이름": "면목중", "start": 25112557, "end": 25113046},
    {"이름": "금융감독원 연수원", "start": 25113047, "end": 25113049}
]

# WITTY_BUJUKS 리스트는 생략 (기존 리스트 그대로 사용하시면 됩니다)
WITTY_BUJUKS = [
    "🦅 이루매: '상대(시험지) 잘하는 친구다. 거의 기출 끝판왕급이야.'",
    "🌸 내년 이맘때는 전농로 벚꽃 대신 여의도 파크원 벚꽃 보며 퇴근하는 운명!",
    "✨ 오늘 스트레스 많이 받을 거야. 근데 그런 스트레스도 합격엔 필요하다.",
    "🧮 쌀집 계산기 두드리는 거, 이거 손가락 운동 많이 된다.",
    "🏢 삼일, 삼정, 안진, 한영: '아니 이 인재는 우리랑 대화가 되는 시립대생?!'",
    "🦅 시립대 CPA 커넥트: '학우님, 여기서 제일 잘하는 사람이야!'"
]

def load_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file, dtype={'응시번호': str})
    return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False, encoding='utf-8-sig')

df = load_data(DB_FILE, ["닉네임", "응시번호", "고사장", "왕복여부", "오픈채팅링크", "등록시간", "매칭완료", "매너스타일"])
board_df = load_data(BOARD_FILE, ["제목", "고사장", "오픈채팅", "모집인원", "작성자", "작성시간", "상태"])
cheer_df = load_data(CHEER_FILE, ["닉네임", "메시지", "시간"])

# 3. 메인 화면
st.title("🚕 시립대 CPA 커넥트")

d_day = (datetime.date(2026, 3, 1) - datetime.date.today()).days
st.markdown(f"<div class='countdown-box'><span>61회 1차 시험까지 D-{d_day}</span></div>", unsafe_allow_html=True)
st.markdown(f"<div class='bujuk-card'>{random.choice(WITTY_BUJUKS)}</div>", unsafe_allow_html=True)

# --- 섹션 1: 카풀 매칭 신청 ---
st.markdown("<div class='section-title'>1. 카풀 매칭 신청</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='guide-box'>
        <b>📌 카풀 신청 가이드</b><br>
        • 응시번호를 입력하면 자동으로 해당 고사장 팀에 배정됩니다.<br>
        • 선착순 4명 단위로 호차가 구성되며, <b>1번 신청자가 방장</b>이 되어 오픈톡 링크를 생성합니다.<br>
        • 매칭 현황은 아래 '내 매칭 확인' 섹션에서 응시번호로 조회 가능합니다.
    </div>
""", unsafe_allow_html=True)
st.markdown("""
    <div class='security-box'>
        <b>🔒 보안 유지 주의사항</b><br>
        • 입력하신 응시번호는 고사장 배정 및 본인 확인용으로만 사용되며 외부에 공개되지 않습니다.<br>
        • 매칭된 학우의 응시번호나 개인정보를 캡처하여 유포하는 행위는 절대 금지됩니다.
    </div>
""", unsafe_allow_html=True)

with st.form("join_form"):
    u_no = st.text_input("응시번호 (8자리 숫자)")
    col1, col2 = st.columns(2)
    with col1: uw = st.selectbox("여정 선택", ["편도 (학교→고사장)", "왕복"])
    with col2: um = st.radio("탑승 스타일", ["🔇 조용히", "💬 대화 환영", "💡 퀴즈 내며"], horizontal=True)
    if st.form_submit_button("신청하기"):
        u_no_f = re.sub(r'[^0-9]', '', str(u_no))
        if len(u_no_f) == 8:
            tgt = next((c for c in TEST_CENTERS if c["start"] <= int(u_no_f) <= c["end"]), None)
            new_d = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "응시번호": u_no_f, "고사장": tgt["이름"] if tgt else "기타", "왕복여부": uw, "오픈채팅링크": "", "등록시간": datetime.datetime.now(), "매칭완료": "N", "매너스타일": um}])
            df = pd.concat([df, new_d], ignore_index=True); save_data(df, DB_FILE)
            st.success("신청 완료! 아래에서 팀 정보를 확인하세요."); st.balloons(); time.sleep(1); st.rerun()
        else: st.error("응시번호 8자리를 정확히 입력해주세요.")

# --- 섹션 2: 내 매칭 확인 ---
st.markdown("<div class='section-title'>2. 내 매칭 상황 확인</div>", unsafe_allow_html=True)
v_no = st.text_input("🔐 신청한 응시번호 입력하여 조회", type="password")
if v_no:
    v_no_c = re.sub(r'[^0-9]', '', str(v_no))
    my_data = df[df["응시번호"] == v_no_c]
    if not my_data.empty:
        me = my_data.iloc[-1]
        team_all = df[(df["고사장"] == me["고사장"]) & (df["왕복여부"] == me["왕복여부"])].sort_values("등록시간")
        my_idx = list(team_all["응시번호"]).index(v_no_c)
        car_no = (my_idx // 4) + 1
        current_team = team_all.iloc[(car_no-1)*4 : car_no*4]

        st.info(f"📍 {me['고사장']} - {car_no}호차 팀")
        t_cols = st.columns(4)
        for i in range(4):
            with t_cols[i]:
                if i < len(current_team):
                    m = current_team.iloc[i]
                    st.markdown(f"<div class='main-card' style='text-align:center;'><b>{m['닉네임']}</b><br><span class='manner-tag'>{m['매너스타일']}</span></div>", unsafe_allow_html=True)
                else: st.markdown("<div class='main-card' style='text-align:center; color:#ccc;'>모집중</div>", unsafe_allow_html=True)
        
        if my_idx % 4 == 0:
            st.success("👑 학우님은 방장입니다. 오픈채팅 링크를 등록해주세요.")
            new_l = st.text_input("오픈채팅 링크 등록", value=me['오픈채팅링크'])
            if st.button("링크 저장"):
                df.loc[df["응시번호"] == v_no_c, "오픈채팅링크"] = new_l
                save_data(df, DB_FILE); st.success("저장되었습니다."); time.sleep(1); st.rerun()
        else:
            link = current_team.iloc[0]['오픈채팅링크']
            if pd.notna(link) and link != "": st.link_button("🚀 팀 오픈채팅방 입장", str(link), use_container_width=True)
            else: st.warning("방장님이 링크를 등록 중입니다.")

# --- 섹션 3: 자유 모집 게시판 ---
st.markdown("<div class='section-title'>3. 자유 모집 게시판</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='guide-box'>
        <b>📢 게시판 이용 가이드</b><br>
        • 자동 매칭 외에 직접 출발 시간이나 장소를 정하고 싶을 때 사용하세요.<br>
        • 글 제목에 목적지와 출발 시간을 명시하면 빠른 모집에 도움이 됩니다.<br>
        • 모집이 완료되면 채팅방 제목을 [완료]로 수정해 주세요.
    </div>
""", unsafe_allow_html=True)
col_bl, col_br = st.columns([0.4, 0.6])
with col_bl:
    with st.form("b_form"):
        bt = st.text_input("모집 제목")
        bp = st.selectbox("고사장", [c["is"] for c in TEST_CENTERS] if 'is' in TEST_CENTERS[0] else [c["이름"] for c in TEST_CENTERS])
        bl = st.text_input("오픈톡 링크")
        if st.form_submit_button("글 올리기"):
            if bt and bl:
                new_b = pd.DataFrame([{"제목": bt, "고사장": bp, "오픈채팅": bl, "작성자": random.choice(ANIMALS), "작성시간": datetime.datetime.now(), "상태": "모집중"}])
                board_df = pd.concat([board_df, new_b], ignore_index=True); save_data(board_df, BOARD_FILE); st.rerun()
with col_br:
    for idx, r in board_df.sort_values("작성시간", ascending=False).head(5).iterrows():
        st.markdown(f"<div class='main-card'><b>[{r['고사장']}] {r['제목']}</b></div>", unsafe_allow_html=True)
        st.link_button("🔗 입장하기", str(r['오픈채팅']), use_container_width=True)

# --- 섹션 4: 합격 응원 게시판 ---
st.markdown("<div class='section-title'>4. 합격 응원 게시판</div>", unsafe_allow_html=True)
st.markdown("""
    <div class='guide-box'>
        <b>🍀 응원 가이드</b><br>
        • 얼마나 간절했는지, 얼마나 견뎠는지 서로는 알기에. 따뜻한 한마디를 남겨주세요.<br>
        • 우리는 서로에게 가장 큰 힘이자, 여의도에서 다시 만날 미래의 동료입니다.
    </div>
""", unsafe_allow_html=True)
with st.form("cheer_form", clear_on_submit=True):
    cm = st.text_input("응원 메시지 입력")
    if st.form_submit_button("응원 등록"):
        if cm:
            new_c = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "메시지": cm, "시간": datetime.datetime.now()}])
            cheer_df = pd.concat([cheer_df, new_c], ignore_index=True); save_data(cheer_df, CHEER_FILE); st.rerun()
for i in range(0, min(len(cheer_df), 10), 2):
    c_cols = st.columns(2)
    for j in range(2):
        if i+j < len(cheer_df):
            row = cheer_df.iloc[-(i+j+1)]
            c_cols[j].markdown(f"<div class='main-card'><b>{row['메시지']}</b><br><small>- {row['닉네임']}</small></div>", unsafe_allow_html=True)

# --- 최하단 에티켓 및 보안 ---
st.markdown("<div class='section-title'>🚨 이용 수칙 및 보안</div>", unsafe_allow_html=True)
col_e1, col_e2 = st.columns(2)
with col_e1:
    st.markdown("""
        <div class='guide-box'>
            <b>🚕 카풀 에티켓</b><br>
            • 노쇼 금지: 약속 시간 5분 전 대기<br>
            • 하차 즉시 송금: 택시비 정산은 매너입니다.<br>
            • 정숙 유지: 시험 직전 예민한 시간을 배려해 주세요.
        </div>
    """, unsafe_allow_html=True)
with col_e2:
    st.markdown("""
        <div class='security-box'>
            <b>🛡️ 보안 및 정보 보호</b><br>
            • <b>응시번호 노출 주의</b>: 타인의 정보를 수집하거나 공유하지 마세요.<br>
            • <b>허위 정보 금지</b>: 신뢰를 위해 정확한 응시번호만 입력해 주세요.<br>
            • 규정 위반 시 서비스 이용이 제한될 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

# 관리자
with st.expander("🛠️"):
    if st.text_input("PW", type="password") == "uos1234":
        st.download_button("DB", df.to_csv(index=False).encode('utf-8-sig'), "cpa_db.csv")
