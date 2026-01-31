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
    .guide-box { background: #f1f3f5; padding: 15px; border-radius: 10px; border-left: 5px solid #002758; font-size: 0.85em; color: #333; line-height: 1.6; margin-bottom: 20px; }

    /* 여기서부터 추가: 모바일 화살표 텍스트 버그 방지 */
    [data-testid="stSidebarCollapseIcon"] {
        font-size: 0px !important;
    }
    [data-testid="stSidebarCollapseIcon"]::before {
        content: "☰"; /* 지저분한 영어 대신 삼선 아이콘 노출 */
        font-size: 24px !important;
        color: #002758;
        visibility: visible;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 함수 및 설정
DB_FILE, BOARD_FILE, CHEER_FILE = "cpa_db.csv", "cpa_board.csv", "cpa_cheer.csv"
ANIMALS = ["이루매 🦅", "아기사자 🦁", "똑똑한쿼카 🐾", "합격판다 🐼", "행운토끼 🐰", "회계사여우 🦊", "정답너구리 🦝", "열공고양이 🐱", "계산하는곰 🐻", "지혜로운부엉이 🦉"]

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

WITTY_BUJUKS = [
    "🦅 이루매: '상대(시험지) 잘하는 친구다. 거의 기출 끝판왕급이야.'",
    "🌸 내년 이맘때는 전농로 벚꽃 대신 여의도 파크원 벚꽃 보며 퇴근하는 운명!",
    "✨ 오늘 스트레스 많이 받을 거야. 근데 그런 스트레스도 합격엔 필요하다.",
    "🧮 쌀집 계산기 두드리는 거, 이거 손가락 운동 많이 된다.",
    "🏢 삼일, 삼정, 안진, 한영: '아니 이 인재는 우리랑 대화가 되는 시립대생?!'",
    "📈 정부회계 10문제 다 맞히기? 이거 예술이다 예술.",
    "⚖️ 상법 지문이랑 나랑 지금 '대화가 된다'. 엄대엄 승부 중!",
    "☕ 중도 매점 커피, 진짜 도움 많이 되고 있어. 마시자마자 뇌 풀가동!",
    "🛑 한판 쉴래? 근데 남들은 안 쉬어.",
    "🔥 말 안 하지만 지금 스트레스 되게 받는다. 그래도 중꺾마 가야지.",
    "🧧 재무회계 대차차액이 0원으로 딱 떨어질 때의 그 도파민... 예술이다!",
    "✍️ 마킹은 기술적으로 부드럽게. 결국은 체력전으로 가야지 끝까지.",
    "🎯 헷갈리는 4번 지문? 상대 세게 나온다. 하지만 내가 더 세죠?",
    "🦅 장산곶매 맑눈광으로 지문 째려보기. 이거 예술이다 예술.",
    "🏢 미래관 계단 타던 하체 근력으로 3교시까지 버티는 무적 피지컬!",
    "💼 법인 웰컴키트 언박싱 브이로그 찍는 상상, 오늘 자기 전에 생각 많이 날 거야.",
    "🔍 지문 속 '포함한다'와 '제외한다'가 형광펜 칠한 것처럼 잘 보이는 눈!",
    "🍀 오늘만큼은 우주가 나를 자산(Asset)으로 취급하고 운을 배당해 주는 날!",
    "📏 계산기 GT 눌렀을 때 내 합격 점수가 총계로 나오는 예지력!",
    "🏢 여의도 법인 사원증? 굿 파트너. 내년에 꼭 만나자.",
    "📉 내가 제낀 파트는 중요성 미달로 출제 제외! 이거 완전 럭키비키잔앙!🍀",
    "⚡ 법인세 세무조정? 대화가 된다. 숫자랑 나랑 티키타카 예술이야.",
    "🎯 킬러 문항? 상대 세게 나온다. 난 기술적으로 부드럽게 스킵!",
    "🦆 전농관 연못 오리들: '이 친구 여기서 제일 잘하는 친구야. 꽥!'",
    "🎉 합격 후 에타에 '전농동 탈출 수기' 쓰고 따봉 100개 받는 미래!",
    "🛡️ 내 옆자리 빌런의 다리 떨기? 그런 스트레스도 합격엔 필요하다.",
    "👔 여의도 출근룩 입은 내 모습? 예술이다 예술. 폼 미쳤다.",
    "🚀 1차 합격 후 에타 실시간 핫게 가기. 이거 진짜 도움 많이 된다.",
    "🦅 이루매: '상대 스트롱 스트롱! 하지만 우리 학우가 더 스트롱!'",
    "🏢 안진/한영 법인 분위기? 예술이다 예술. 내 자리가 저기네.",
    "🚲 시대 자전거 타고 쪽문 통과하듯, 함정 지문도 킹받게 잘 피함!",
    "🌟 내 합격 가능성? 거의 OOO급이야. 압도적이라는 뜻이지.",
    "🎊 올해는 시대의 자랑, 내년엔 법인의 보물!",
    "🦅 장산곶매: '한판 쉴래? 근데 남들은 안 쉬어. 그러니까 더 해!'",
    "🏰 경영학 암기 내용이 노래 가사처럼 머릿속에서 재생되는 기적!",
    "🧘 시험장 소음? 그런 스트레스도 필요하다. 덕분에 더 초집중됨.",
    "📈 국기법/국징법? 대화가 된다. 암기한 대로 툭툭 나오네.",
    "📏 계산기 뚜껑 여는 소리, 상대 세게 나올 때 내는 선전포고!",
    "🌸 오늘 자기 전에 정답들 생각 많이 날 거야. 기분 좋게 자자.",
    "🏢 삼일회계법인: '우리랑 대화가 되는 인재네. 합격!'",
    "✍️ 종료 5분 전 검토? 기술적으로 부드럽게. 실수 싹 잡아내자.",
    "🗂️ 경제학 그래프가 3D로 보여서 균형점이 그냥 보이는 천리안!",
    "🧧 재무관리 공식 암기? 오늘 자기 전에 생각 많이 날 거야.",
    "🏙️ 여의도 IFC몰 점심 산책? 이거 진짜 도움 많이 되고 있어.",
    "🎓 학위수여식보다 100배 설레는 '최종합격' 문자 받는 전율!",
    "🦅 장산곶매의 시력으로 답안지 오타까지 싹 잡아내는 완벽한 검토!",
    "🏢 백주년기념관의 적막함이 시험장까지 이어지는 역대급 몰입도!",
    "📉 정부회계가 초등학교 산수 수준으로 나오는 '대혜자' 시험지!",
    "🍞 시험장 앞 간식? 이거 진짜 도움 많이 되고 있어. 에너지 뿜뿜!",
    "✨ 헷갈리던 개념이 시험지 펼치자마자 번뜩 생각나는 영감!",
    "🥊 원가회계? 체력전으로 가야지. 끝까지 물고 늘어지면 네가 이겨.",
    "🥇 찍기 운도 실력! 헷갈리는 지문 중 고르는 것마다 정답 행진!",
    "🦅 이루매: '이 친구 잘하는 친구다. 여의도 금방 가겠어.'",
    "👔 면접 정장 맞출 때 '내 돈 내산' 아니고 '법인 돈'으로 사는 상상!",
    "📜 회계학 시험지 첫 장부터 아는 문제만 쏟아지는 축복!",
    "☕ 1교시 전 마신 커피가 뇌세포 전수조사급 집중력 전달!",
    "🏙️ 내년엔 시대 과잠 대신 법인 웰컴키트 언박싱 브이로그!",
    "🍀 오늘만큼은 지구가 나를 중심으로 돌고, 이루매가 내 답안지를 지킨다!",
    "🎊 전농동에서 흘린 땀방울이 여의도의 야경으로 바뀔 운명!",
    "🏛️ 인문학관 옆 지름길처럼 정답으로 가는 최단 경로가 눈에 보이는 마법!",
    "🦅 이루매: '음악관 언덕 오르던 패기로 경영학 암기 다 씹어먹자.'",
    "🚲 정문에서 중도까지 자전거로 쏘는 속도로 문제 푸는 쾌감!",
    "🏞️ 자작마루 앞 산책로처럼 평온한 멘탈 유지하기. 이거 도움 많이 된다.",
    "🏢 조형관 전시물처럼 예술적인 오답 소거법! 예술이다 예술.",
    "📚 법학관 도서관의 기운을 받아 상법 조문이 내 손바닥 안!",
    "🦅 이루매: '정보기술관에서 코딩하듯 세무조정도 로직으로 풀어버려.'",
    "🚶 후문 쪽 떡볶이 골목 가는 가벼운 발걸음으로 시험장 퇴근하기!",
    "🌲 대강당 앞 소나무처럼 흔들리지 않는 뿌리 깊은 재무회계 실력!",
    "🦅 시립대 CPA 커넥트: '학우님, 여기서 제일 잘하는 사람이야!'"
]

def load_data(file, cols):
    if os.path.exists(file): return pd.read_csv(file, dtype={'응시번호': str})
    return pd.DataFrame(columns=cols)

def save_data(df, file): df.to_csv(file, index=False, encoding='utf-8-sig')

df = load_data(DB_FILE, ["닉네임", "응시번호", "고사장", "왕복여부", "오픈채팅링크", "등록시간", "매칭완료", "매너스타일"])
board_df = load_data(BOARD_FILE, ["제목", "고사장", "오픈채팅", "모집인원", "작성자", "작성시간", "상태"])
cheer_df = load_data(CHEER_FILE, ["닉네임", "메시지", "시간"])

# 3. 메인 상단 UI
st.title("🚕 시립대 CPA 커넥트")
d_day = (datetime.date(2026, 3, 1) - datetime.date.today()).days
st.markdown(f"<div class='countdown-box'><span class='d-day-text'>D-{d_day}</span> <span>(61회 1차 시험까지)</span></div>", unsafe_allow_html=True)
st.markdown(f"<div class='bujuk-card'>{random.choice(WITTY_BUJUKS)}</div>", unsafe_allow_html=True)

# 4. 실시간 현황
if not df.empty:
    with st.expander("📊 실시간 고사장별 매칭 현황", expanded=True):
        loc_counts = df['고사장'].value_counts()
        cols = st.columns(3)
        for i, (loc, count) in enumerate(loc_counts.items()):
            with cols[i % 3]:
                st.write(f"**{loc}** ({count}명)")
                st.progress((count % 4) / 4 if count % 4 != 0 else 1.0)
                st.caption(f"{4 - (count % 4) if count % 4 != 0 else 0}명 추가 시 다음 호차 완성")

tab1, tab2, tab3 = st.tabs(["📟 내 상황실", "📢 자율 모집 게시판", "🍀 합격 응원"])

# --- TAB 1 ---
with tab1:
    st.markdown("""
        <div class='guide-box'>
            <b>📌 이용 안내</b><br>
            • <b>모바일 사용자</b>: 왼쪽 상단의 <b>'>'</b> 화살표를 눌러 사이드바를 열고 신청해 주세요!<br>
            • <b>등록 필수</b>: 사이드바에서 응시번호 등록 후 조회가 가능합니다.<br>
            • <b>자동 매칭</b>: 고사장별 선착순 4명씩 자동으로 호차가 배정됩니다.<br>
            • <b>방장 역할</b>: <b>1번 입석자</b>가 오픈톡 방을 만들고 링크를 게시해주세요.
        </div>
    """, unsafe_allow_html=True)
    v_no = st.text_input("🔐 조회용 응시번호 입력 (8자리)", type="password", key="v_no")
    if v_no:
        v_no_c = re.sub(r'[^0-9]', '', str(v_no))
        my_data = df[df["응시번호"] == v_no_c]
        if not my_data.empty:
            me = my_data.iloc[-1]
            center_info = next((c for c in TEST_CENTERS if c["이름"] == me["고사장"]), None)
            team_all = df[(df["고사장"] == me["고사장"]) & (df["왕복여부"] == me["왕복여부"])].sort_values("등록시간")
            my_idx_in_list = list(team_all["응시번호"]).index(v_no_c)
            car_no = (my_idx_in_list // 4) + 1
            current_team = team_all.iloc[(car_no-1)*4 : car_no*4]

            st.header(f"📍 {me['고사장']} {car_no}호차")
            st.link_button("🚕 예상 택시비 확인", f"https://map.naver.com/v5/directions/-/{urllib.parse.quote(me['고사장'])}/-/car", use_container_width=True)
            t_cols = st.columns(4)
            for i in range(4):
                with t_cols[i]:
                    if i < len(current_team):
                        m = current_team.iloc[i]
                        st.markdown(f"<div class='main-card' style='text-align:center;'><b>{m['닉네임']}</b><br><span class='manner-tag'>{m['매너스타일']}</span></div>", unsafe_allow_html=True)
                    else: st.markdown("<div class='main-card' style='text-align:center; color:#ccc;'>💺<br>모집중</div>", unsafe_allow_html=True)
            
            st.divider()
            if my_idx_in_list % 4 == 0:
                st.success("🎓 학우님은 이 팀의 방장입니다!")
                new_l = st.text_input("🔗 우리 팀 오픈채팅 링크 등록", value=me['오픈채팅링크'])
                if st.button("링크 업데이트"):
                    df.loc[df["응시번호"] == v_no_c, "오픈채팅링크"] = new_l
                    save_data(df, DB_FILE); st.success("등록 완료!"); time.sleep(1); st.rerun()
            else:
                leader_link = current_team.iloc[0]['오픈채팅링크']
                if pd.notna(leader_link) and leader_link != "": st.link_button("🚀 팀 오픈채팅방 입장", str(leader_link), use_container_width=True)
                else: st.warning("아직 방장님이 링크를 등록하지 않았습니다.")
        else: st.warning("신청 내역이 없습니다.")

# --- TAB 2 ---
with tab2:
    st.markdown("""
        <div class='guide-box' style='background-color: #f1f3f5; border-left: 5px solid #002758;'>
            <b>📢 게시판 이용 가이드</b><br>
            • <b>글 작성</b>: 고사장과 오픈톡 링크를 포함해 자유롭게 팀을 모집해 주세요.<br>
            • <b>완료 처리</b>: 모집이 끝나면 오픈톡 제목을 <b>[완료]</b>로 바꿔주세요.<br>
            • <b>신뢰 형성</b>: 삭제 기능은 운영자가 관리합니다.
        </div>
    """, unsafe_allow_html=True)
    col_l, col_r = st.columns([0.4, 0.6])
    with col_l:
        with st.form("b_form", clear_on_submit=True):
            bt = st.text_input("제목")
            bp = st.selectbox("고사장", [c["이름"] for c in TEST_CENTERS])
            bl = st.text_input("오픈톡 링크")
            if st.form_submit_button("모집 시작"):
                if bt and bl:
                    new_b = pd.DataFrame([{"제목": bt, "고사장": bp, "오픈채팅": bl, "모집인원": 1, "작성자": random.choice(ANIMALS), "작성시간": datetime.datetime.now(), "상태": "모집중"}])
                    board_df = pd.concat([board_df, new_b], ignore_index=True); save_data(board_df, BOARD_FILE); st.rerun()
    with col_r:
        active_board = board_df[board_df['상태'] != "완료"].sort_values("작성시간", ascending=False)
        for idx, r in active_board.iterrows():
            st.markdown(f"<div class='main-card'><b>[{r['고사장']}] {r['제목']}</b></div>", unsafe_allow_html=True)
            st.link_button("🔗 입장하기", str(r['오픈채팅']), use_container_width=True)

# --- TAB 3 ---
with tab3:
    st.header("🍀 응원 타임라인")
    st.markdown("""
        <div class='guide-box' style='background-color: #fdfcf0; border-left: 5px solid #fbc02d;'>
            • 시험을 앞둔 학우들에게 힘이 되는 따뜻한 한마디를 남겨주세요.<br>
            • 전농동에서 흘린 땀방울이 여의도의 야경으로 바뀔 그날을 함께 응원합니다. 🦅
        </div>
    """, unsafe_allow_html=True)
    with st.form("cheer_form", clear_on_submit=True):
        cm = st.text_input("메시지")
        if st.form_submit_button("응원 등록"):
            if cm:
                new_c = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "메시지": cm, "시간": datetime.datetime.now()}])
                cheer_df = pd.concat([cheer_df, new_c], ignore_index=True); save_data(cheer_df, CHEER_FILE); st.rerun()
    for i in range(0, len(cheer_df), 2):
        c_cols = st.columns(2)
        for j in range(2):
            if i+j < len(cheer_df):
                row = cheer_df.iloc[-(i+j+1)]
                c_cols[j].markdown(f"<div class='cheer-bubble'><b>{row['메시지']}</b><br><small>- {row['닉네임']}</small></div>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🚕 카풀 자동 매칭")
    with st.form("join"):
        u_no = st.text_input("응시번호 (8자리)")
        uw = st.selectbox("여정", ["편도 (학교→고사장)", "왕복"])
        um = st.radio("탑승 스타일", ["🔇 조용히", "💬 대화 환영", "💡 퀴즈 내며"], index=1)
        if st.form_submit_button("신청"):
            u_no_f = re.sub(r'[^0-9]', '', str(u_no))
            if len(u_no_f) == 8:
                tgt = next((c for c in TEST_CENTERS if c["start"] <= int(u_no_f) <= c["end"]), None)
                new_d = pd.DataFrame([{"닉네임": random.choice(ANIMALS), "응시번호": u_no_f, "고사장": tgt["이름"] if tgt else "기타", "왕복여부": uw, "오픈채팅링크": "", "등록시간": datetime.datetime.now(), "매칭완료": "N", "매너스타일": um}])
                df = pd.concat([df, new_d], ignore_index=True); save_data(df, DB_FILE); st.success("신청 완료!"); st.balloons(); time.sleep(1); st.rerun()

    with st.expander("⚠️ 이용 에티켓 (필독)"):
        st.markdown("""
            * **노쇼 금지**: 취소 시 최소 12시간 전 공유
            * **5분 전 대기**: 약속 시간 엄수
            * **즉시 정산**: 하차 직후 송금
            * **경로 준수**: 개인 경유지 추가 불가
        """)
    
    st.markdown("---")
    with st.expander("🛠️ 관리자"):
        if st.text_input("암호", type="password") == "uos1234":
            st.download_button("DB 다운로드", df.to_csv(index=False).encode('utf-8-sig'), "cpa_db.csv")

