import streamlit as st
import random
import itertools
from collections import defaultdict

st.set_page_config(page_title="非同期バドミントンスケジューラー", layout="centered")

DEFAULT_PLAYERS = [f"Player {i+1}" for i in range(20)]
DEFAULT_COURTS = 3

st.title("🏸 非同期ダブルススケジューラー（コート別試合開始）")

players_input = st.text_area("プレイヤー名（1人1行）", "\n".join(DEFAULT_PLAYERS))
court_count = st.number_input("コート数", min_value=1, max_value=10, value=DEFAULT_COURTS)

players = [p.strip() for p in players_input.split("\n") if p.strip()]

# セッション管理
if 'history' not in st.session_state:
    st.session_state.history = defaultdict(int)
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = {i: None for i in range(court_count)}
if 'match_log' not in st.session_state:
    st.session_state.match_log = []

def get_play_count(p1, p2):
    return st.session_state.history[frozenset([p1, p2])]

def get_busy_players():
    busy = set()
    for match in st.session_state.current_matches.values():
        if match:
            team1, team2 = match
            busy.update(team1)
            busy.update(team2)
    return busy

def generate_match():
    available = [p for p in players if p not in get_busy_players()]
    if len(available) < 4:
        return None
    candidates = list(itertools.combinations(available, 4))
    for group in sorted(candidates, key=lambda g: get_play_count(g[0], g[1]) + get_play_count(g[2], g[3])):
        return ((group[0], group[1]), (group[2], group[3]))
    return None

# 各コートごとに表示
for court_id in range(court_count):
    st.subheader(f"🟩 コート {court_id + 1}")
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button(f"試合開始（コート {court_id + 1}）", key=f"start_{court_id}"):
            match = generate_match()
            if match:
                team1, team2 = match
                st.session_state.current_matches[court_id] = match
                st.session_state.history[frozenset(team1)] += 1
                st.session_state.history[frozenset(team2)] += 1
                st.session_state.match_log.append((court_id + 1, team1, team2))
            else:
                st.warning("プレイ可能な人数が足りません")

    with col2:
        match = st.session_state.current_matches[court_id]
        if match:
            t1, t2 = match
            st.markdown(f"🎮 **{t1[0]} & {t1[1]}** vs **{t2[0]} & {t2[1]}**")
        else:
            st.markdown("⏸️ 試合未実施")

# 履歴表示
with st.expander("📜 試合履歴"):
    for i, (court, team1, team2) in enumerate(st.session_state.match_log, 1):
        st.write(f"{i}. コート{court}: {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")

# リセット
if st.button("🔄 リセット（全履歴＋試合状態）"):
    st.session_state.history = defaultdict(int)
    st.session_state.current_matches = {i: None for i in range(court_count)}
    st.session_state.match_log = []
    st.success("すべてリセットされました")
