import streamlit as st
import pandas as pd
import datetime
import os
import random
import urllib.parse
import re
import time

# 1. 앱 설정 및 스타일
st.set_page_config(page_title="시립대 CPA 커넥트", page_icon="🚕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-card { border: 1px solid #e1e4e8; border-radius: 12px; padding: 18px; background-color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 15px; }
    .countdown-box { background: #002758; color: white; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 15px; display: flex; align-items: center; justify-content: center; gap: 20px; }
    .d-day-text { font-size: 1.8em; font-weight: 800; }
    .bujuk-card { 
        background: linear-gradient(135deg, #fff9c4 0%, #fbc02d 100%); 
        border: 2px solid #f9a825; padding: 20px; border-radius: 15px; 
        text-align: center; margin-bottom: 20px; font-weight: bold; 
        color: #5f4b00; font-size: 1.1em; box-shadow: 0 6px 15px rgba(0,0,0,0.1); line-height: 1.6;
    }
    .manner-tag { display: inline-block; padding: 2px 8px; border-radius: 15px; font-size: 0.8em; background: #e0e7ff; color: #4338ca; margin-top: 5px; }
    .cheer-bubble { background: #ffffff; border: 1px solid #dee2e6; padding: 12px 16px; border-radius: 18px 18px 18px 2px; margin-bottom: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); }
    .guide-box { background: #f1f3f5; padding: 15px; border-radius: 10px; border-left: 5px solid #002758; font-size: 0.85em; color: #333; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 초기화 및 최신 고사장 설정
DB_FILE, BOARD_FILE, CHEER_FILE = "cpa_db.csv", "cpa_board.csv", "cpa_cheer.csv"
ANIMALS = ["이루매 🦅", "아기사자 🦁", "똑똑한쿼카 🐾", "합격판다 🐼", "행운토끼 🐰", "회계사여우 🦊", "정답너구리 🦝", "열공고양이 🐱", "계산하는곰 🐻", "지혜로운부엉이 🦉"]

# 최신 고사장 데이터 (주소 포함)
TEST_CENTERS = [
    {"이름": "경기고", "주소": "서울특별시 강남구 영동대로 643", "start": 25100001, "end": 25101100},
    {"이름": "둔촌중", "주소": "서울특별시 강동구 진황도로61길 25-30", "start": 25101101, "end": 25101625},
    {"이름": "명일중", "주소": "서울특별시 강동구 양재대로156길 57", "start": 25101626, "end": 25102400},
    {"이름": "등촌고", "주소": "서울특별시 강서구 공항대로39길 115", "start": 25102401, "end": 25103150},
    {"이름": "경인중", "주소": "서울특별시 구로구 경인로 301", "start": 25103151, "end": 25103656},
    {"이름": "광운인공지능고", "주소": "서울특별시 노원구 광운로1길 24", "start": 25103657, "end": 25104056},
    {"이름": "녹천중", "주소": "서울특별시 노원구 월계로 376", "start": 25104057, "end": 25104456},
    {"이름": "장승중", "주소": "서울특별시 동작구 장승배기로10가길 25", "start": 25104457, "end": 25105056},
    {"이름": "아현중", "주소": "서울특별시 마포구 마포대로 247", "start": 25105057, "end": 25105456},
    {"이름": "연희중", "주소": "서울특별시 서대문구 증가로 170", "start": 25105457, "end": 25106016},
    {"이름": "성수중", "주소": "서울특별시 성동구 서울숲길 18", "start": 25106017, "end": 25106376},
    {"이름": "숭곡중", "주소": "서울특별시 성북구 종암로 208", "start": 25106377, "end": 25106976},
    {"이름": "오주중", "주소": "서울특별시 송파구 동남로 281", "start": 25106977, "end": 25107626},
    {"이름": "오금중", "주소": "서울특별시 송파구 오금로35길 20", "start": 25107627, "end": 25108301},
    {"이름": "봉영여중", "주소": "서울특별시 양천구 목동동로2길 68", "start": 25108302, "end": 25108801},
    {"이름": "신길중", "주소": "서울특별시 영등포구 신길로28길 43", "start": 25108802, "end": 25109476},
    {"이름": "용산철도고", "주소": "서울특별시 용산구 서빙고로 24", "start": 25109477, "end": 25110276},
    {"이름": "선린인터넷고", "주소": "서울특별시 용산구 원효로97길 33-4", "start": 25110277, "end": 25110996},
    {"이름": "은평중", "주소": "서울특별시 은평구 갈현로17나길 12-1", "start": 25110997, "end": 25111416},
    {"이름": "증산중", "주소": "서울특별시 은평구 증산로5길 27-30", "start": 25111417, "end": 25111916},
    {"이름": "중화고", "주소": "서울특별시 중랑구 봉화산로27길 62", "start": 25111917, "end": 25112556},
    {"이름": "면목중", "주소": "서울특별시 중랑구 용마산로70길 37", "start": 25112557, "end": 25113046},
    {"이름": "금융감독원 연수원", "주소": "서울특별시 종로구 효자로 11", "start": 25113047, "end": 25113049}
]

# 부적 문구 ([] 제거 버전)
WITTY_BUJUKS = [
    "🧧 대차차액이 0원으로 소름 돋게 딱 떨어지는 마법!", "🔥 내가 제낀 파트에서는 절대로 출제 안 됨!",
    "🦁 시립대 마스코트 이루매가 정답으로 비상하는 기운!", "🎓 머릿속에서 숫자들이 알아서 정렬되는 몰입력!",
    "✨ 고민 없이 5문제 다 맞고 시작하는 든든함!", "⚖️ 조문 하나하나가 기출 선지로 보이는 천리안!",
    "📈 그래프가 3D로 보여서 정답이 스스로 튀어나옴!", "💬 헷갈리는 선지 2개 중 찍는 것마다 정답!",
    "🏢 내년 이맘때는 전농동 대신 여의도로 출근!", "🧮 쌀집 계산기 소리가 경쾌한 합격의 리듬으로!",
    "✍️ 마킹 실수 0건! 종료 1분 전 기적의 검토 완료!", "🍱 점심 먹고 식곤증 없이 오후 집중력 대폭발!",
    "🧐 출제자의 비열한 함정이 눈에 다 보이는 투시력!", "🍀 모의고사 때 틀린 문제가 똑같이 나오는 기적!",
    "👟 전농동의 정기가 시험장 책상까지 따라가는 행운!", "🤫 감독관 발소리도 안 들리는 역대급 몰입 상태!",
    "☕ 카페인 없이도 뇌가 팽팽 돌아가는 초사이어인 모드!", "🎉 시험 끝나고 에타에 '합격각?' 올리면 'ㅇㅇ'만 달림!",
    "🖋️ 펜 끝에 합격의 신이 깃들어 답만 콕콕 찝는 손길!", "🏥 시험 당일 두통, 복통 zero! 최상의 컨디션!",
    "🥇 가채점 결과가 예상 컷보다 +20점 높게 나옴!"
]

def load_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file, dtype={'응시번호': str})
    return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False, encoding='utf-8-sig')

df = load_data(DB_FILE, ["닉네임", "응시번호", "고사장", "왕복여부", "오픈채팅링크", "등록시간", "매칭완료", "매너스타일"])
board_df = load_data(BOARD_FILE, ["제목", "고사장", "오픈채팅", "모집인원", "작성자", "작성시간", "상태"])
cheer_df = load_data(CHEER_FILE, ["닉네임", "메시지", "시간"])

# 3. 메인 상단
st.title("🚕 시립대 CPA 커넥트")
d_day = (datetime.date(2026, 3, 1) - datetime.date.today()).days
st.markdown(f"<div class='countdown-box'><span class='d-day-text'>D-{d_day}</span> <span>(61회 1차 시험까지)</span></div>", unsafe_allow_html=True)
st.markdown(f"<div class='bujuk-card'>{random.choice(WITTY_BUJUKS)}</div>", unsafe_allow_html=True)

# 4. 실시간 매칭 현황판
if not df.empty:
    with st.expander("📊 실시간 고사장별 매칭 현황", expanded=True):
        loc_counts = df['고사장'].value_counts()
        cols = st.columns(3)
        for i, (loc, count) in enumerate(loc_counts.items()):
            with cols[i % 3]:
                st.write(f"**{loc}** ({count}명)")
                st.progress((count % 4) / 4 if count % 4 != 0 else 1.0)
                st.caption(f"{4 - (count % 4) if count % 4 != 0 else 0}명 추가 시 다음 호차 완성")

# 5. 메인 탭
tab1, tab2, tab3 = st.tabs(["📟 내 상황실", "📢 자율 모집 게시판", "🍀 합격 응원"])

with tab1:
    v_no = st.text_input("🔐 조회용 응시번호 입력", type="password", placeholder="8자리 숫자 입력")
    if v_no:
        v_no_c = re.sub(r'[^0-9]', '', str(v_no))
        my_data = df[df["응시번호"] == v_no_c]
        if not my_data.empty:
            me = my_data.iloc[0]
            # 고사장 정보 찾기 (주소 추출용)
            center_info = next((c for c in TEST_CENTERS if c["이름"] == me["고사장"]), None)
            
            team_all = df[(df["고사장"] == me["고사장"]) & (df["왕복여부"] == me["왕복여부"])].sort_values("등록시간")
            my_idx = list(team_all["응시번호"]).index(v_no_c)
            car_no = (my_idx // 4) + 1
            current_team = team_all.iloc[(car_no-1)*4 : car_no*4]

            st.header(f"📍 {me['고사장']} {car_no}호차")
            # ✨ 주소 표시 기능 추가
            if center_info:
                st.markdown(f"🏠 **고사장 주소**: {center_info['주소']}")
            
            st.link_button("🚕 예상 택시비 확인", f"https://map.naver.com/v5/directions/-/{urllib.parse.quote(me['고사장'])}/-/car", use_container_width=True)
            
            t_cols = st.columns(4)
            for i in range(4):
                with t_cols[i]:
                    if i < len(current_team):
                        m = current_team.iloc[i]
                        st.markdown(f"<div class='main-card' style='text-align:center;'><b>{m['닉네임']}</b><br><span class='manner-tag'>{m['매너스타일']}</span></div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='main-card' style='text-align:center; color:#ccc;'>💺<br>모집중</div>", unsafe_allow_html=True)
            
            st.divider()
            if my_idx % 4 == 0: # 방장
                st.success("🎓 학우님은 이 팀의 방장입니다!")
                with st.expander("📍 방장용 오픈톡 공지 템플릿"):
                    msg = f"[{me['고사장']} {car_no}호차 공지]\n- 모임장소: 학교 정문\n- 출발시간: \n- 주소: {center_info['주소'] if center_info else ''}"
                    st.code(msg, language="text")
                new_l = st.text_input("🔗 오픈채팅 링크 등록", value=me['오픈채팅링크'])
                if st.button("링크 저장"):
                    df.loc[df["응시번호"] == v_no_c, "오픈채팅링크"] = new_l
                    save_data(df, DB_FILE); st.success("저장되었습니다!"); st.rerun()
            elif me['오픈채팅링크']:
                st.link_button("🚀 팀 오픈채팅방 입장", str(me['오픈채팅링크']), use_container_width=True)
        else: st.warning("신청 내역이 없습니다.")

# (tab2, tab3, 사이드바 신청 로직은 이전과 동일하므로 생략하거나 기존 코드 유지)
# ... [생략된 부분은 이전 최종본의 Tab2, Tab3, Sidebar 코드를 그대로 붙여넣으시면 됩니다] ...

with tab2:
    st.header("📢 자율 모집 게시판")
    col_l, col_r = st.columns([0.4, 0.6])
    with col_l:
        with st.form("b_form", clear_on_submit=True):
            st.write("✨ **새 모집글 작성**")
            bt = st.text_input("제목", placeholder="예: [경기고] 7시 정문 정각 출발")
            bp = st.selectbox("고사장 선택", [c["이름"] for c in TEST_CENTERS])
            bl = st.text_input("오픈톡 링크")
            if st.form_submit_button("등록"):
                if bt and bl:
                    new_b = pd.DataFrame([{"제목": bt, "고사장": bp, "오픈채팅": bl, "모집인원": 1, "작성자": random.choice(ANIMALS), "작성시간": datetime.datetime.now(), "상태": "모집중"}])
                    board_df = pd.concat([board_df, new_b], ignore_index=True); save_data(board_df, BOARD_FILE); st.rerun()
    with col_r:
        for idx, r in board_df[board_df['상태'] != "완료"].sort_values("작성시간", ascending=False).iterrows():
            st.markdown(f"<div class='main-card'><b>[{r['고사장']}] {r['제목']}</b><br><small>{r['작성자']} | {str(r['작성시간'])[5:16]}</small></div>", unsafe_allow_html=True)
            bc1, bc2 = st.columns([0.7, 0.3])
            bc1.link_button("🔗 입장", str(r['오픈채팅']), use_container_width=True)
            if bc2.button("✅ 완료", key=f"bd_{idx}"):
                board_df.at[idx, '상태'] = "완료"; save_data(board_df, BOARD_FILE); st.rerun()

with tab3:
    st.header("🍀 응원 타임라인")
    with st.form("cheer_form", clear_on_submit=True):
        cm = st.text_input("메시지", placeholder="학우들에게 따뜻한 응원을 남겨주세요!")
        if st.form_submit_button("등록"):
            if cm:
                new_c = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "메시지": cm, "시간": datetime.datetime.now()}])
                cheer_df = pd.concat([cheer_df, new_c], ignore_index=True); save_data(cheer_df, CHEER_FILE); st.rerun()
    for i in range(0, len(cheer_df), 2):
        c_cols = st.columns(2)
        for j in range(2):
            if i + j < len(cheer_df):
                row = cheer_df.sort_values("시간", ascending=False).iloc[i + j]
                c_cols[j].markdown(f"<div class='cheer-bubble'><b>{row['메시지']}</b><br><small>- {row['닉네임']}</small></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🚕 카풀 신청")
    with st.form("join"):
        u_no = st.text_input("응시번호 (8자리)", placeholder="2510XXXX")
        uw = st.selectbox("여정", ["편도 (학교→고사장)", "왕복"])
        um = st.radio("탑승 스타일", ["🔇 조용히 가고 싶어요", "💬 대화 환영", "💡 함께 퀴즈 내며 가요"], index=1)
        if st.form_submit_button("익명으로 신청 완료"):
            u_no_f = re.sub(r'[^0-9]', '', str(u_no))
            if len(u_no_f) == 8:
                if u_no_f in df['응시번호'].values:
                    st.warning("⚠️ 이미 신청된 번호입니다.")
                else:
                    tgt = next((c for c in TEST_CENTERS if c["start"] <= int(u_no_f) <= c["end"]), None)
                    new_d = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "응시번호": u_no_f, "고사장": tgt["이름"] if tgt else "기타", "왕복여부": uw, "오픈채팅링크": "", "등록시간": datetime.datetime.now(), "매칭완료": "N", "매너스타일": um}])
                    df = pd.concat([df, new_d], ignore_index=True); save_data(df, DB_FILE)
                    st.success("✅ 신청 완료!"); st.balloons(); time.sleep(1); st.rerun()
            else: st.error("응시번호 8자리를 확인해주세요.")
    st.markdown("---")
    st.markdown("### 📖 이용 가이드")

    st.markdown("<div class='guide-box'>응시번호를 입력하면 고사장이 자동 배정됩니다. 팀원들과 오픈톡에서 만나요!</div>", unsafe_allow_html=True)

st.markdown("---")
with st.expander("🛠️ 관리자 전용"):
    admin_code = st.text_input("관리자 코드", type="password")
    if admin_code == "uos1234": # 비밀번호는 원하시는 대로 수정하세요!
        st.success("인증 성공")
        
        # 1. 카풀 메인 데이터 백업
        st.write("**카풀 신청 현황**")
        csv1 = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("카풀 데이터 다운로드", data=csv1, file_name="cpa_db_backup.csv")
        
        # 2. 자율 게시판 데이터 백업
        st.write("**자율 게시판 현황**")
        csv2 = board_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("게시판 데이터 다운로드", data=csv2, file_name="board_backup.csv")
        
        st.info("💡 장난으로 지워진 글이 있다면 위 데이터를 확인해 보세요.")
