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
    {"이름": "고덕중학교", "start": 26100001, "end": 26100600},
    {"이름": "둔촌고등학교", "start": 26100601, "end": 26101350},
    {"이름": "오금중학교", "start": 26101351, "end": 26102025},
    {"이름": "오주중학교", "start": 26102026, "end": 26102675},
    {"이름": "석촌중학교", "start": 26102676, "end": 26103250},
    {"이름": "용마중학교", "start": 26103251, "end": 26103650},
    {"이름": "하계중학교", "start": 26103651, "end": 26104275},
    {"이름": "숭곡중학교", "start": 26104276, "end": 26104875},
    {"이름": "용산철도고등학교", "start": 26104876, "end": 26105675},
    {"이름": "선린중학교", "start": 26105676, "end": 26106195},
    {"이름": "증산중학교", "start": 26106196, "end": 26106720},
    {"이름": "성동공업고등학교", "start": 26106721, "end": 26107360},
    {"이름": "성서중학교", "start": 26107361, "end": 26107860},
    {"이름": "등촌고등학교", "start": 26107861, "end": 26108610},
    {"이름": "장승중학교", "start": 26108611, "end": 26109210},
    {"이름": "성남고등학교", "start": 26109211, "end": 26109760},
    {"이름": "봉영여자중학교", "start": 26109761, "end": 26110260},
    {"이름": "여의도고등학교", "start": 26110261, "end": 26110780},
    {"이름": "서초고등학교", "start": 26110781, "end": 26111511},
    {"이름": "금융감독원 연수원", "start": 26111512, "end": 26111517}
]

# WITTY_BUJUKS 리스트는 생략 (기존 리스트 그대로 사용하시면 됩니다)
WITTY_BUJUKS = [
    "🦅 이루매: '상대(시험지) 잘하는 친구다. 거의 기출 끝판왕급이야.'",
    "🌸 내년 이맘때는 전농로 벚꽃 대신 여의도 파크원 벚꽃 보며 퇴근하는 운명!",
    "✨ 오늘 스트레스 많이 받을 거야. 근데 그런 스트레스도 합격엔 필요하다.",
    "🧮 쌀집 계산기 두드리는 거, 이거 손가락 운동 많이 된다.",
    "🏢 삼일, 삼정, 안진, 한영: '아니 이 인재는 우리랑 대화가 되는 시립대생?!'",
    "📈 정부회계 5문제 다 맞히기? 이거 예술이다 예술.",
    "⚖️ 상법 지문이랑 나랑 지금 '대화가 된다'. 엄대엄 승부 중!",
    "☕ 전농관 커피, 진짜 도움 많이 되고 있어. 마시자마자 뇌 풀가동!",
    "🛑 한판 쉴래? 근데 남들은 안 쉬어.",
    "🔥 말 안 하지만 지금 스트레스 되게 받는다. 그래도 중꺾마 가야지.",
    "🧧 재무회계 대차차액이 0원으로 딱 떨어질 때의 그 도파민... 예술이다!",
    "✍️ 마킹은 기술적으로 부드럽게. 결국은 체력전으로 가야지 끝까지.",
    "🎯 헷갈리는 4번 지문? 상대 세게 나온다. 하지만 내가 더 세죠?",
    "🦅 장산곶매 맑눈광으로 지문 째려보기. 이거 예술이다 예술.",
    "🏢 중도 계단 타던 하체 근력으로 3교시까지 버티는 무적 피지컬!",
    "💼 법인 웰컴키트 언박싱 브이로그 찍는 상상, 오늘 자기 전에 생각 많이 날 거야.",
    "🔍 지문 속 '포함한다'와 '제외한다'가 형광펜 칠한 것처럼 잘 보이는 눈!",
    "🍀 오늘만큼은 우주가 나를 자산(Asset)으로 취급하고 운을 배당해 주는 날!",
    "📏 계산기 GT 눌렀을 때 내 합격 점수가 총계로 나오는 예지력!",
    "🏢 여의도 법인 사원증? 굿 파트너. 내년에 꼭 만나자.",
    "📉 내가 제낀 파트는 중요성 미달로 출제 제외! 이거 완전 럭키비키잔앙!🍀",
    "⚡ 법인세 세무조정? 대화가 된다. 숫자랑 나랑 티키타카 예술이야.",
    "🎯 킬러 문항? 상대 세게 나온다. 난 기술적으로 부드럽게 스킵!",
    "🦆 배봉탕 연못 오리들: '이 친구 여기서 제일 잘하는 친구야. 꽥!'",
    "🎉 합격 후 에타에 '전농동 탈출 수기' 쓰고 따봉 100개 받는 미래!",
    "🛡️ 내 옆자리 빌런의 다리 떨기? 그런 스트레스도 합격엔 필요하다.",
    "👔 여의도 출근룩 입은 내 모습? 예술이다 예술. 폼 미쳤다.",
    "🚀 1차 합격 후 에타 실시간 핫게 가기. 이거 진짜 도움 많이 된다.",
    "🦅 이루매: '상대 스트롱 스트롱! 하지만 우리 학우가 더 스트롱!'",
    "🏢 안진/한영 법인 분위기? 예술이다 예술. 내 자리가 저기네.",
    "🚲 킥보드 타고 쪽문 통과하듯, 함정 지문도 킹받게 잘 피함!",
    "🌟 내 합격 가능성? 거의 OOO급이야. 압도적이라는 뜻이지.",
    "🎊 올해는 시대의 자랑, 내년엔 법인의 보물!",
    "🦅 장산곶매: '한판 쉴래? 근데 남들은 안 쉬어. 그러니까 더 해!'",
    "🏰 경영학 암기 내용이 노래 가사처럼 머릿속에서 재생되는 기적!",
    "🧘 시험장 소음? 그런 스트레스도 필요하다. 덕분에 더 초집중됨.",
    "📈 국기법? 대화가 된다. 암기한 대로 툭툭 나오네.",
    "📏 계산기 뚜껑 여는 소리, 상대 세게 나올 때 내는 선전포고!",
    "🌸 오늘 자기 전에 정답들 생각 많이 날 거야. 기분 좋게 자자.",
    "🏢 삼일회계법인: '우리랑 대화가 되는 인재네. 합격!'",
    "✍️ 종료 5분 전 검토? 기술적으로 부드럽게. 실수 싹 잡아내자.",
    "🗂️ 경제학 그래프가 3D로 보여서 균형점이 그냥 보이는 천리안!",
    "🧧 재무관리 공식 암기? 오늘 자기 전에 생각 많이 날 거야.",
    "🏙️ 여의도 IFC몰 점심 산책? 이거 진짜 도움 많이 되고 있어.",
    "🎓 100배 설레는 '최종합격' 문자 받는 전율!",
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
    "🏙️ 하늘은 높고 말은 살찌는데, 네 점수는 수직 상승 중.",
    "🍀 오늘만큼은 지구가 나를 중심으로 돌고, 이루매가 내 답안지를 지킨다!",
    "🎊 전농동에서 흘린 땀방울이 여의도의 야경으로 바뀔 운명!",
    "🏛️ 인문학관 옆 지름길처럼 정답으로 가는 최단 경로가 눈에 보이는 마법!",
    "🦅 이루매: '중도 언덕 오르던 패기로 경영학 암기 다 씹어먹자.'",
    "🚲 정문에서 중도까지 자전거로 쏘는 속도로 문제 푸는 쾌감!",
    "🏞️ 자작마루 앞 산책로처럼 평온한 멘탈 유지하기. 이거 도움 많이 된다.",
    "🏢 조형관 전시물처럼 예술적인 오답 소거법! 예술이다 예술.",
    "📚 법학관 고시반의 기운을 받아 상법 조문이 내 손바닥 안!",
    "✨ 오늘 네 뇌는 '손상차손' 없이 **'수익'**만 인식함.",
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

# 3. 메인 화면
st.title("🚕 시립대 CPA 커넥트")

d_day = (datetime.date(2026, 3, 1) - datetime.date.today()).days
st.markdown(f"<div class='countdown-box'><span>61회 1차 시험까지 D-{d_day}</span></div>", unsafe_allow_html=True)
st.markdown(f"<div class='bujuk-card'>{random.choice(WITTY_BUJUKS)}</div>", unsafe_allow_html=True)

# --- [최상단 배치] 실시간 대시보드 ---
if not df.empty:
    # 닉네임에 '취소됨'이 포함되지 않은 정상 신청자만 필터링
    active_only = df[~df['닉네임'].str.contains("취소됨", na=False)]
    loc_counts = active_only['고사장'].value_counts()
    
    # 가로 스크롤 형태의 상단 대시보드 시작 (기존 스타일 코드 유지)
    st.markdown("""
        <style>
        .top-dash-container { 
            display: flex; overflow-x: auto; gap: 12px; padding: 10px 5px; 
            scrollbar-width: none; -ms-overflow-style: none;
        }
        .top-dash-container::-webkit-scrollbar { display: none; }
        .top-card {
            min-width: 140px; background: white; border-radius: 15px; padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #eee;
            text-align: center; position: relative;
        }
        .top-loc-name { font-size: 0.85em; font-weight: bold; color: #002758; margin-bottom: 5px; }
        .top-count { font-size: 1.2em; font-weight: 800; color: #333; }
        .status-dot {
            height: 8px; width: 8px; background-color: #00c853; border-radius: 50%;
            display: inline-block; margin-right: 5px; animation: blink 1.5s infinite;
        }
        @keyframes blink { 0% { opacity: 0.3; } 50% { opacity: 1; } 100% { opacity: 0.3; } }
        </style>
    """, unsafe_allow_html=True)

    dash_html = "<div class='top-dash-container'>"
    for loc, count in loc_counts.items():
        dash_html += f"""
            <div class='top-card'>
                <div class='top-loc-name'>{loc}</div>
                <div class='top-count'><span class='status-dot'></span>{count}명</div>
                <div style='font-size: 0.7em; color: #888; margin-top: 5px;'>실시간 매칭 중</div>
            </div>
        """
    dash_html += "</div>"
    st.markdown(dash_html, unsafe_allow_html=True)

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
            # 1. 고사장 정보 미리 찾기
            tgt = next((c for c in TEST_CENTERS if c["start"] <= int(u_no_f) <= c["end"]), None)
            loc_name = tgt["이름"] if tgt else "기타"
            
            # 2. 중복 여부 확인
            is_existing = not df.empty and u_no_f in df['응시번호'].values
            
            if is_existing:
                # [수정 모드] 이미 등록된 번호라면 해당 행의 정보를 업데이트
                idx = df[df['응시번호'] == u_no_f].index[0]
                df.at[idx, '왕복여부'] = uw  # 컬럼명 주의 (원본 컬럼명이 '왕복여부'인지 확인)
                df.at[idx, '매너스타일'] = um
                df.at[idx, '등록시간'] = datetime.datetime.now()
                save_data(df, DB_FILE)
                st.info(f"♻️ 이미 등록된 번호입니다. 신청 정보를 업데이트했습니다! ({loc_name})")
            else:
                # [신규 모드] 새로운 데이터 추가
                new_d = pd.DataFrame([{
                    "닉네임": random.choice(ANIMALS), 
                    "응시번호": u_no_f, 
                    "고사장": loc_name, 
                    "왕복여부": uw, 
                    "오픈채팅링크": "", 
                    "등록시간": datetime.datetime.now(), 
                    "매칭완료": "N", 
                    "매너스타일": um
                }])
                df = pd.concat([df, new_d], ignore_index=True)
                save_data(df, DB_FILE)
                st.success(f"✅ {loc_name} 고사장 신청 완료! 아래에서 팀 정보를 확인하세요.")
                st.balloons()
            
            time.sleep(1)
            st.rerun()
        else:
            st.error("응시번호 8자리를 정확히 입력해주세요.")
    
# --- 섹션 2: 내 매칭 상황 확인 ---
st.markdown("<div class='section-title'>2. 내 매칭 상황 확인</div>", unsafe_allow_html=True)
v_no = st.text_input("🔐 신청한 응시번호 입력하여 조회", type="password")

if v_no:
    v_no_c = re.sub(r'[^0-9]', '', str(v_no))
    # 취소된 데이터까지 포함해서 전체 순서를 잡아야 호차가 안 바뀜
    my_data = df[df["응시번호"].str.contains(v_no_c, na=False)]
    
    if not my_data.empty:
        me = my_data.iloc[-1]
        # 해당 고사장/여정의 전체 명단을 등록시간 순으로 가져옴 (순번 고정)
        team_all = df[(df["고사장"] == me["고사장"]) & (df["왕복여부"] == me["왕복여부"])].sort_values("등록시간")
        
        # 내 현재 위치(index) 확인
        my_idx = list(team_all["응시번호"]).index(me["응시번호"])
        car_no = (my_idx // 4) + 1
        current_team = team_all.iloc[(car_no-1)*4 : car_no*4]

        st.info(f"📍 {me['고사장']} - {car_no}호차 팀")
        
        # 팀원 카드 출력 (들여쓰기 주의)
        t_cols = st.columns(4)
        for i in range(4):
            with t_cols[i]:
                if i < len(current_team):
                    m = current_team.iloc[i]
                    if "취소됨" in str(m['닉네임']):
                        st.markdown("<div class='main-card' style='text-align:center; color:#999; background:#eee; min-height:100px; display:flex; align-items:center; justify-content:center;'>🈳 빈자리</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='main-card' style='text-align:center; min-height:100px;'><b>{m['닉네임']}</b><br><span class='manner-tag'>{m['매너스타일']}</span></div>", unsafe_allow_html=True)
                else: 
                    st.markdown("<div class='main-card' style='text-align:center; color:#ccc; min-height:100px; display:flex; align-items:center; justify-content:center;'>모집중</div>", unsafe_allow_html=True)
        
        # 방장/입장 버튼 로직
        if my_idx % 4 == 0 and "취소됨" not in me['닉네임']:
            st.success("👑 학우님은 방장입니다. 팀원들을 위해 오픈채팅 링크를 등록해주세요.")
            new_l = st.text_input("오픈채팅 링크 등록", value=me['오픈채팅링크'])
            if st.button("링크 저장"):
                df.loc[df["응시번호"] == me["응시번호"], "오픈채팅링크"] = new_l
                save_data(df, DB_FILE)
                st.success("저장되었습니다.")
                time.sleep(1)
                st.rerun()
        elif "취소됨" not in me['닉네임']:
            link = current_team.iloc[0]['오픈채팅링크']
            if pd.notna(link) and link != "": 
                st.link_button("🚀 팀 오픈채팅방 입장", str(link), use_container_width=True)
            else: 
                st.warning("방장님이 링크를 등록 중입니다.")

        # 취소 버튼 (데이터 삭제 대신 상태만 변경)
        if "취소됨" not in me['닉네임']:
            st.divider()
            with st.expander("신청을 취소하시겠습니까?"):
                st.write("취소 시 해당 자리는 빈자리로 표시되며 호차 순서는 유지됩니다.")
                if st.button("❌ 매칭 신청 취소하기", type="primary", use_container_width=True):
                    idx = df[df["응시번호"] == me["응시번호"]].index[0]
                    df.at[idx, '닉네임'] = "❌ 취소됨"
                    df.at[idx, '매너스타일'] = "-"
                    df.at[idx, '응시번호'] = f"canceled_{v_no_c}_{int(time.time())}"
                    save_data(df, DB_FILE)
                    st.success("취소되었습니다.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.error("신청 내역이 없거나 이미 취소된 번호입니다.")

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
        •  시험을 앞둔 학우들에게 힘이 되는 따뜻한 한마디를 남겨주세요.<br>
        •  얼마나 간절했는지, 얼마나 견뎠는지 서로는 알기에. 우리의 합격을 응원합니다. 🦅
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
            • 노쇼 금지: 취소 시 최소 12시간 전 공유,약속 시간 5분 전 대기<br>
            • 하차 즉시 송금: 택시비 정산은 매너입니다.<br>
            • 경로 준수: 개인 경유지 추가 불가
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

# --- 관리자 전용 기능 섹션 ---
with st.expander("🛠️ 시스템 관리"):
    admin_pw = st.text_input("관리자 암호", type="password")
    if admin_pw == "uos1234":  
        st.write("### 🔓 관리자 모드 활성화됨")
        
        # 1. 데이터 백업
        st.download_button("📂 전체 매칭 데이터(CSV) 다운로드", df.to_csv(index=False).encode('utf-8-sig'), "cpa_db_backup.csv")
        
        # 2. 매칭 명단 직접 관리
        st.markdown("---")
        st.subheader("👥 실시간 매칭 명단 관리")
        if not df.empty:
            active_df = df[~df['닉네임'].str.contains("취소됨", na=False)]
            if active_df.empty:
                st.write("현재 매칭된 인원이 없습니다.")
            else:
                for idx, row in active_df.iterrows():
                    c1, c2 = st.columns([0.8, 0.2])
                    c1.write(f"**[{row['고사장']}]** {row['닉네임']} ({row['응시번호']})")
                    if c2.button("제외", key=f"admin_user_del_{idx}"):
                        df.at[idx, '닉네임'] = "❌ 취소됨"
                        df.at[idx, '매너스타일'] = "-"
                        df.at[idx, '응시번호'] = f"admin_cancel_{row['응시번호']}"
                        save_data(df, DB_FILE)
                        st.error(f"{row['닉네임']}님을 제외 처리했습니다.")
                        time.sleep(0.5)
                        st.rerun()

        # 3. 게시글 통합 관리
        st.markdown("---")
        st.subheader("🗑️ 게시글 관리")
        
        if not board_df.empty:
            st.write("**자유 모집 게시판**")
            for idx, row in board_df.iterrows():
                col_txt, col_btn = st.columns([0.8, 0.2])
                col_txt.write(f"[{row['고사장']}] {row['제목']} ({row['작성자']})")
                if col_btn.button(f"삭제", key=f"del_brd_{idx}"):
                    board_df = board_df.drop(idx)
                    save_data(board_df, BOARD_FILE)
                    st.rerun()
        
        if not cheer_df.empty:
            st.write("**응원 게시판**")
            for idx, row in cheer_df.iterrows():
                col_txt, col_btn = st.columns([0.8, 0.2])
                col_txt.write(f"{row['메시지']} ({row['닉네임']})")
                if col_btn.button(f"삭제", key=f"del_chr_{idx}"):
                    cheer_df = cheer_df.drop(idx)
                    save_data(cheer_df, CHEER_FILE)
                    st.rerun()

        # 4. 데이터 초기화 (배포 직전용)
        st.markdown("---")
        st.subheader("⚠️ 데이터 전체 초기화")
        st.warning("이 작업은 되돌릴 수 없습니다. 배포 직전에만 사용하세요.")
        if st.button("🚨 모든 데이터 초기화 실행"):
            # 컬럼 구조에 맞춰 빈 데이터 생성
            empty_df = pd.DataFrame(columns=["닉네임", "응시번호", "고사장", "왕복여부", "오픈채팅링크", "등록시간", "매칭완료", "매너스타일"])
            empty_board = pd.DataFrame(columns=["제목", "고사장", "오픈채팅", "모집인원", "작성자", "작성시간", "상태"])
            empty_cheer = pd.DataFrame(columns=["닉네임", "메시지", "시간"])
            
            save_data(empty_df, DB_FILE)
            save_data(empty_board, BOARD_FILE)
            save_data(empty_cheer, CHEER_FILE)
            
            st.success("모든 데이터가 초기화되었습니다.")
            time.sleep(1)
            st.rerun()
