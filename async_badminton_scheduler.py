import streamlit as st
import random
import itertools
from collections import defaultdict

st.set_page_config(page_title="非同期バドミントンスケジューラー", layout="centered")

DEFAULT_PLAYERS = [f"Player {i+1}" for i in range(20)]
DEFAULT_COURTS = 3

st.title("🏸 非同期型バドミントンダブルススケジューラー（各コート独立）")

players_input = st.text_area("プレイヤー名（1人1行）", "\n".join(DEFAULT_PLAYERS))
court_count = st.number_input("使用するコート数", min_value=1, max_value=10, value=DEFAULT_COURTS, step=1)

players = [p.strip() for p in players_input.split("\n") if p.strip()]

# セッション状態の初期化
if 'history' not in st.session_state:
    st.session_state.history = defaultdict(int)
if 'match_log' not in st.session_state:
    st.session_state.match_log = []
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = {i: None for i in range(court_count)}

# ペア履歴取得
def get_play_count(p1, p2):
    return st.session_state.history[frozenset([p1, p2])]

# 使用中プレイヤー取得
def get_busy_players():
    busy = set()
    for match in st.session_state.current_matches.values():
        if match:
            team1, team2 = match
            busy.update(team1)
            busy.update(team2)
    return busy

# マッチ生成（そのコートに空きができたときのみ）
def generate_match(court_id):
    busy = get_busy_players()
    available_players = [p for p in players if p not in busy]
    if len(available_players) < 4:
        return None

    candidates = list(itertools.combinations(available_players, 4))

    def score(group):
        p1, p2, p3, p4 = group
        return get_play_count(p1, p2) + get_play_count(p3, p4)

    for group in sorted(candidates, key=score):
        p1, p2, p3, p4 = group
        return ((p1, p2), (p3, p4))
    return None

# 各コートごとに操作UIを表示
for court_id in range(court_count):
    st.subheader(f"🟩 コート {court_id + 1}")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button(f"試合開始（コート {court_id + 1}）", key=f"start_{court_id}"):
            match = generate_match(court_id)
            if match:
                team1, team2 = match
                st.session_state.current_matches[court_id] = match
                st.session_state.history[frozenset(team1)] += 1
                st.session_state.history[frozenset(team2)] += 1
                st.session_state.match_log.append((court_id + 1, team1, team2))
            else:
                st.warning("利用可能なプレイヤーが足りません。")

    with col2:
        match = st.session_state.current_matches.get(court_id)
        if match:
            team1, team2 = match
            st.markdown(f"✅ **{team1[0]} & {team1[1]}** vs **{team2[0]} & {team2[1]}**")
        else:
            st.markdown("⏸️ 試合未開始")

# 試合履歴表示
with st.expander("📜 試合履歴を見る"):
    for i, (court, team1, team2) in enumerate(st.session_state.match_log, 1):
        st.write(f"{i}. コート{court}: {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")

# リセット
if st.button("🔄 全リセット"):
    st.session_state.history = defaultdict(int)
    st.session_state.match_log = []
    st.session_state.current_matches = {i: None for i in range(court_count)}
    st.success("履歴と試合状況をリセットしました。")
