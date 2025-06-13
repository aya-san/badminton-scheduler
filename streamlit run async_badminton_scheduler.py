import streamlit as st
import random
import itertools
from collections import defaultdict

st.set_page_config(page_title="非同期バドミントンスケジューラー", layout="centered")

# 初期設定
DEFAULT_PLAYERS = [f"Player {i+1}" for i in range(20)]
DEFAULT_COURTS = 3

st.title("🏸 非同期型バドミントンダブルススケジューラー")

# プレイヤーリストとコート数の設定
players_input = st.text_area("プレイヤー名（1人1行）", "\n".join(DEFAULT_PLAYERS))
court_count = st.number_input("使用するコート数", min_value=1, max_value=10, value=DEFAULT_COURTS, step=1)

players = [p.strip() for p in players_input.split("\n") if p.strip()]
random.shuffle(players)

# セッションステートで履歴管理
if 'history' not in st.session_state:
    st.session_state.history = defaultdict(int)
if 'match_log' not in st.session_state:
    st.session_state.match_log = []

# ペアごとのプレイ回数を取得
def get_play_count(p1, p2):
    return st.session_state.history[frozenset([p1, p2])]

# マッチを生成するロジック
def generate_matches(players, court_count):
    used = set()
    matches = []
    candidates = list(itertools.combinations(players, 4))

    # ソート：ペアのプレイ回数が少ない順に並べる
    def score(group):
        p1, p2, p3, p4 = group
        team1 = get_play_count(p1, p2)
        team2 = get_play_count(p3, p4)
        return team1 + team2

    for group in sorted(candidates, key=score):
        p1, p2, p3, p4 = group
        if len(matches) >= court_count:
            break
        if not (set([p1, p2, p3, p4]) & used):
            matches.append(((p1, p2), (p3, p4)))
            used.update([p1, p2, p3, p4])

    return matches

# ボタンを押してマッチ生成
if st.button("🎮 試合開始！"):
    matches = generate_matches(players, court_count)

    for (team1, team2) in matches:
        st.write(f"✅ **{team1[0]} & {team1[1]}** vs **{team2[0]} & {team2[1]}**")
        # 履歴更新
        st.session_state.history[frozenset(team1)] += 1
        st.session_state.history[frozenset(team2)] += 1
        st.session_state.match_log.append((team1, team2))

# 試合履歴
with st.expander("📜 試合履歴を見る"):
    for i, (team1, team2) in enumerate(st.session_state.match_log, 1):
        st.write(f"{i}. {team1[0]} & {team1[1]} vs {team2[0]} & {team2[1]}")

# リセットボタン
if st.button("🔄 履歴をリセット"):
    st.session_state.history = defaultdict(int)
    st.session_state.match_log = []
    st.success("履歴をリセットしました。")
