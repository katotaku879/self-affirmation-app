import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import os
import random
import uuid

# ページの設定
st.set_page_config(
    page_title="目標達成サポート - 自己肯定アプリ",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSSスタイルの定義
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2E7D32;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .goal-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
    }
    .goal-active {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .goal-warning {
        background-color: #FFF9C4;
        border-left: 5px solid #FFC107;
    }
    .goal-danger {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .goal-complete {
        background-color: #E0F7FA;
        border-left: 5px solid #00BCD4;
    }
    .mini-task {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
    }
    .badge-item {
        background-color: #F3E5F5;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .reward-card {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #9C27B0;
    }
    .message-card {
        background-color: #E0F7FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #00BCD4;
    }
    .insight-box {
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
    }
    .problem-item {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #F44336;
    }
    .progress-stat {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .success-memory {
        background-color: #DCEDC8;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #8BC34A;
    }
</style>
""", unsafe_allow_html=True)

# データファイルのパス
GOALS_FILE = "goals.json"
SMART_GOALS_FILE = "smart_goals.json"
TASKS_FILE = "tasks.json"
REWARDS_FILE = "goal_rewards.json"
FUTURE_MESSAGES_FILE = "goal_future_messages.json"
PROBLEMS_FILE = "goal_problems.json"
SUCCESS_MEMORIES_FILE = "success_memories.json"
BADGES_FILE = "badges.json"
POINTS_FILE = "points.json"

# データファイルの初期化
def initialize_goal_files():
    if not os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(SMART_GOALS_FILE):
        with open(SMART_GOALS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(REWARDS_FILE):
        with open(REWARDS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(FUTURE_MESSAGES_FILE):
        with open(FUTURE_MESSAGES_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(PROBLEMS_FILE):
        with open(PROBLEMS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(SUCCESS_MEMORIES_FILE):
        with open(SUCCESS_MEMORIES_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(BADGES_FILE):
        default_badges = {
            "badges": [
                {"id": "first_goal", "name": "ファーストゴール", "description": "最初の目標を設定", "image": "🎯", "earned": False},
                {"id": "first_complete", "name": "初めての達成", "description": "最初の目標を達成", "image": "🏆", "earned": False},
                {"id": "three_goals", "name": "目標マスター", "description": "3つの目標を設定", "image": "🌟", "earned": False},
                {"id": "consistent", "name": "継続の達人", "description": "7日連続でタスクを完了", "image": "📊", "earned": False},
                {"id": "problem_solver", "name": "問題解決者", "description": "3つの問題と解決策を特定", "image": "🔧", "earned": False},
                {"id": "reward_planner", "name": "報酬プランナー", "description": "3つの報酬を設定", "image": "🎁", "earned": False}
            ]
        }
        with open(BADGES_FILE, "w") as f:
            json.dump(default_badges, f)
    
    if not os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "w") as f:
            json.dump({"points": 0}, f)

# 初期化を実行
initialize_goal_files()

# データを読み込む関数
def load_goals():
    with open(GOALS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "name", "description", "category", "deadline", "progress", "created_at", "status"])

def load_smart_goals():
    with open(SMART_GOALS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "goal_id", "specific", "measurable", "achievable", "relevant", "time_bound", "mini_goal", "minimum_criteria"])

def load_tasks():
    with open(TASKS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "goal_id", "description", "status", "deadline", "created_at", "completed_at", "points"])

def load_rewards():
    with open(REWARDS_FILE, "r") as f:
        return json.load(f)

def load_future_messages():
    with open(FUTURE_MESSAGES_FILE, "r") as f:
        return json.load(f)

def load_problems():
    with open(PROBLEMS_FILE, "r") as f:
        return json.load(f)

def load_success_memories():
    with open(SUCCESS_MEMORIES_FILE, "r") as f:
        return json.load(f)

def load_badges():
    with open(BADGES_FILE, "r") as f:
        return json.load(f)

def load_points():
    with open(POINTS_FILE, "r") as f:
        return json.load(f)

# データを保存する関数
def save_goals(df):
    with open(GOALS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_smart_goals(df):
    with open(SMART_GOALS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_tasks(df):
    with open(TASKS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_rewards(data):
    with open(REWARDS_FILE, "w") as f:
        json.dump(data, f)

def save_future_messages(data):
    with open(FUTURE_MESSAGES_FILE, "w") as f:
        json.dump(data, f)

def save_problems(data):
    with open(PROBLEMS_FILE, "w") as f:
        json.dump(data, f)

def save_success_memories(data):
    with open(SUCCESS_MEMORIES_FILE, "w") as f:
        json.dump(data, f)

def save_badges(data):
    with open(BADGES_FILE, "w") as f:
        json.dump(data, f)

def save_points(data):
    with open(POINTS_FILE, "w") as f:
        json.dump(data, f)

# ページタイトルとナビゲーション
st.markdown('<h1 class="main-header">🎯 目標達成サポート</h1>', unsafe_allow_html=True)

# ポイント表示
points_data = load_points()
total_points = points_data["points"]
st.sidebar.markdown(f"### 📊 現在のポイント: {total_points}ポイント")

# バッジ数表示
badges_data = load_badges()
earned_badges = sum(1 for badge in badges_data["badges"] if badge["earned"])
total_badges = len(badges_data["badges"])
st.sidebar.markdown(f"### 🏆 獲得バッジ: {earned_badges}/{total_badges}")

# サイドバーナビゲーション
page = st.sidebar.radio(
    "目標達成メニュー",
    ["目標ダッシュボード", "SMART目標設定", "タスク管理", "報酬設定", "問題と対策", "成功体験の記録", "進捗振り返り"]
)

# 目標ダッシュボードページ
def show_goal_dashboard():
    st.markdown('<h2 class="sub-header">📊 目標ダッシュボード</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    tasks_df = load_tasks()
    
    if goals_df.empty:
        st.info("まだ目標が設定されていません。「SMART目標設定」から最初の目標を設定しましょう！")
        return
    
    # 目標の概要
    st.markdown("### 目標の概要")
    
    # 目標のカテゴリごとに色分けした円グラフ
    if 'category' in goals_df.columns and not goals_df['category'].empty:
        category_counts = goals_df['category'].value_counts()
        
        fig_category = px.pie(
            category_counts.reset_index(),
            values=category_counts.values,
            names=category_counts.index,
            title="目標のカテゴリ分布",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    # 目標の進捗状況グラフ
    if 'progress' in goals_df.columns:
        fig_progress = px.bar(
            goals_df.sort_values('progress', ascending=False),
            x='name',
            y='progress',
            title="目標の進捗状況",
            labels={'name': '目標', 'progress': '進捗 (%)'},
            color='progress',
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[0, 100]
        )
        st.plotly_chart(fig_progress, use_container_width=True)
    
    # 各目標のカード表示
    st.markdown("### 目標一覧")
    
    # 目標のステータス別にグループ化
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    completed_goals = goals_df[goals_df['status'] == 'completed'] if 'status' in goals_df.columns else pd.DataFrame()
    
    # アクティブな目標
    if not active_goals.empty:
        st.markdown("#### 進行中の目標")
        
        for _, goal in active_goals.iterrows():
            # 進捗状況に応じたカードスタイルの決定
            card_class = "goal-card"
            if goal['progress'] >= 80:
                card_class = "goal-card goal-active"
            elif goal['progress'] >= 50:
                card_class = "goal-card goal-warning"
            elif goal['progress'] < 50:
                card_class = "goal-card goal-danger"
            
            # 締め切りまでの日数計算
            days_left = "未設定"
            deadline_warning = ""
            if 'deadline' in goal and goal['deadline']:
                deadline_date = datetime.strptime(goal['deadline'], "%Y-%m-%d").date()
                days_left = (deadline_date - datetime.now().date()).days
                
                if days_left < 0:
                    deadline_warning = f"<span style='color: #F44336;'>締め切りを{abs(days_left)}日過ぎています</span>"
                elif days_left < 7:
                    deadline_warning = f"<span style='color: #FFC107;'>締め切りまであと{days_left}日です</span>"
                else:
                    deadline_warning = f"締め切りまであと{days_left}日です"
            
            # タスクの完了率計算
            task_count = len(tasks_df[tasks_df['goal_id'] == goal['id']]) if not tasks_df.empty else 0
            completed_tasks = len(tasks_df[(tasks_df['goal_id'] == goal['id']) & (tasks_df['status'] == 'completed')]) if not tasks_df.empty else 0
            task_completion = f"{completed_tasks}/{task_count}タスク完了" if task_count > 0 else "タスクなし"
            
            # 目標カードの表示
            st.markdown(f"""
            <div class="{card_class}">
                <h3>{goal['name']}</h3>
                <p>{goal['description']}</p>
                <p>カテゴリ: {goal.get('category', '未分類')}</p>
                <p>進捗: <b>{goal['progress']}%</b></p>
                <div style="background-color: #E0E0E0; border-radius: 5px; height: 10px; width: 100%;">
                    <div style="background-color: {'#4CAF50' if goal['progress'] >= 50 else '#FFC107' if goal['progress'] >= 25 else '#F44336'}; border-radius: 5px; height: 10px; width: {goal['progress']}%;"></div>
                </div>
                <p>{task_completion} | {deadline_warning}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 完了した目標
    if not completed_goals.empty:
        with st.expander("完了した目標", expanded=False):
            for _, goal in completed_goals.iterrows():
                st.markdown(f"""
                <div class="goal-card goal-complete">
                    <h3>{goal['name']} ✅</h3>
                    <p>{goal['description']}</p>
                    <p>カテゴリ: {goal.get('category', '未分類')}</p>
                    <p>完了日: {goal.get('completed_at', '不明')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # やる気が出ないときのサポート
    st.markdown("### やる気サポート")
    
    if st.button("今日やる気が出ない…"):
        micro_tasks = generate_micro_tasks(goals_df, tasks_df)
        
        if micro_tasks:
            st.markdown("""
            <div class="insight-box">
                <h4>大丈夫です！小さな一歩から始めましょう。</h4>
                <p>以下のどれか1つだけでも取り組んでみましょう：</p>
            </div>
            """, unsafe_allow_html=True)
            
            for task in micro_tasks:
                st.markdown(f"""
                <div class="mini-task">
                    <h4>💫 {task['description']}</h4>
                    <p>目標: {task['goal_name']}</p>
                    <p><small>たった1分でもOK！少しでも進めれば素晴らしい成果です。</small></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("アクティブな目標やタスクがありません。新しい目標やタスクを設定してみましょう。")
    
    # 過去の成功体験を表示
    success_memories = load_success_memories()
    if success_memories and len(success_memories) > 0:
        st.markdown("### 成功体験の振り返り")
        
        # ランダムに1つの成功体験を選択
        random_memory = random.choice(success_memories)
        
        st.markdown(f"""
        <div class="success-memory">
            <h4>🌟 過去の成功体験</h4>
            <p>「{random_memory['title']}」</p>
            <p>{random_memory['description']}</p>
            <p><small>成功のポイント: {random_memory['success_factors']}</small></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("別の成功体験を見る"):
            st.rerun()
    
    # バッジの表示
    badges_data = load_badges()
    earned_badges = [badge for badge in badges_data["badges"] if badge["earned"]]
    
    if earned_badges:
        st.markdown("### 獲得したバッジ")
        
        badges_html = ""
        for badge in earned_badges:
            badges_html += f"""<span class="badge-item" title="{badge['description']}">{badge['image']} {badge['name']}</span>"""
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            {badges_html}
        </div>
        """, unsafe_allow_html=True)

# マイクロタスク生成関数
def generate_micro_tasks(goals_df, tasks_df):
    micro_tasks = []
    
    # アクティブな目標を取得
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        return micro_tasks
    
    # 各目標から1つずつマイクロタスクを生成
    for _, goal in active_goals.iterrows():
        goal_name = goal['name']
        goal_id = goal['id']
        
        # 未完了のタスクを取得
        incomplete_tasks = tasks_df[(tasks_df['goal_id'] == goal_id) & (tasks_df['status'] != 'completed')] if not tasks_df.empty else pd.DataFrame()
        
        if not incomplete_tasks.empty:
            # 未完了タスクから1つのマイクロタスクを作成
            task = incomplete_tasks.iloc[0]
            micro_tasks.append({
                'goal_name': goal_name,
                'description': f"1分だけ {task['description']} に取り組む"
            })
        else:
            # 汎用的なマイクロタスクの提案
            suggestions = [
                f"{goal_name}について考える時間を1分だけ取る",
                f"{goal_name}に関連する情報を1つ調べる",
                f"{goal_name}の最初の一歩を考える",
                f"{goal_name}をノートに書き出す",
                f"{goal_name}について友人や家族に話す"
            ]
            micro_tasks.append({
                'goal_name': goal_name,
                'description': random.choice(suggestions)
            })
    
    # 最大3つのマイクロタスクをランダムに選択
    if len(micro_tasks) > 3:
        micro_tasks = random.sample(micro_tasks, 3)
    
    return micro_tasks

# SMART目標設定ページ
def show_smart_goal_setting():
    st.markdown('<h2 class="sub-header">📝 SMART目標設定</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    SMART目標設定法は、効果的な目標を立てるためのフレームワークです：
    - 🎯 **S**pecific（具体的）: 明確で具体的な目標
    - 📊 **M**easurable（測定可能）: 進捗を数値で測定できる
    - 👍 **A**chievable（達成可能）: 現実的に達成できる
    - 🔄 **R**elevant（関連性）: あなたの価値観や大きな目標に関連している
    - ⏱️ **T**ime-bound（期限付き）: 明確な期限がある
    """)
    
    # 新しい目標を設定
    st.markdown("### 新しい目標を設定")
    
    # 目標のカテゴリ
    goal_categories = [
        "健康・フィットネス", "学習・スキル", "キャリア・仕事",
        "人間関係", "趣味・娯楽", "精神・マインドフルネス",
        "お金・財務", "家庭・家族", "その他"
    ]
    
    with st.form("smart_goal_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            goal_name = st.text_input("目標名", placeholder="例：毎朝ジョギングする、プログラミングを学ぶなど")
            goal_description = st.text_area("目標の詳細", placeholder="この目標に取り組む理由や、達成したい具体的な内容")
        
        with col2:
            goal_category = st.selectbox("カテゴリ", goal_categories)
            goal_deadline = st.date_input("目標の期限", datetime.now() + timedelta(days=30))
        
        # SMART基準の入力
        st.markdown("### SMART基準")
        
        specific = st.text_input("Specific（具体的）", placeholder="具体的に何をするのか？例：週3回、30分間ジョギングする")
        measurable = st.text_input("Measurable（測定可能）", placeholder="どうやって進捗を測定するか？例：走った回数と距離を記録する")
        achievable = st.text_input("Achievable（達成可能）", placeholder="なぜこの目標は達成可能か？例：近所に走るのに適した公園がある")
        relevant = st.text_input("Relevant（関連性）", placeholder="なぜこの目標はあなたにとって重要か？例：健康的になり、体力をつけたい")
        time_bound = st.text_input("Time-bound（期限付き）", placeholder="いつまでに達成するか？例：3ヶ月後までに週3回のジョギングを習慣化する")
        
        # 小さな目標と最低基準
        st.markdown("### モチベーション維持のための工夫")
        
        mini_goal = st.text_input("小さな目標（達成しやすい）", placeholder="例：まずは週1回、10分間のジョギングから始める")
        minimum_criteria = st.text_input("ミニマム達成基準（最低限これだけ）", placeholder="例：天気が悪い日は室内で5分間のストレッチで代用する")
        
        submit = st.form_submit_button("目標を登録")
        
        if submit:
            if not goal_name or not specific or not measurable or not time_bound:
                st.error("目標名と、Specific、Measurable、Time-boundの項目は必須です。")
            else:
                # 新しい目標を追加
                goals_df = load_goals()
                smart_goals_df = load_smart_goals()
                
                # 目標のID生成
                goal_id = str(uuid.uuid4())
                
                # 基本的な目標情報
                new_goal = {
                    "id": goal_id,
                    "name": goal_name,
                    "description": goal_description,
                    "category": goal_category,
                    "deadline": goal_deadline.strftime("%Y-%m-%d"),
                    "progress": 0,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "status": "active"
                }
                
                # SMART詳細情報
                new_smart_goal = {
                    "id": str(uuid.uuid4()),
                    "goal_id": goal_id,
                    "specific": specific,
                    "measurable": measurable,
                    "achievable": achievable,
                    "relevant": relevant,
                    "time_bound": time_bound,
                    "mini_goal": mini_goal,
                    "minimum_criteria": minimum_criteria
                }
                
                # データフレームに追加
                if goals_df.empty:
                    goals_df = pd.DataFrame([new_goal])
                else:
                    goals_df = pd.concat([goals_df, pd.DataFrame([new_goal])], ignore_index=True)
                
                if smart_goals_df.empty:
                    smart_goals_df = pd.DataFrame([new_smart_goal])
                else:
                    smart_goals_df = pd.concat([smart_goals_df, pd.DataFrame([new_smart_goal])], ignore_index=True)
                
                # 保存
                save_goals(goals_df)
                save_smart_goals(smart_goals_df)
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 10
                save_points(points_data)
                
                # バッジ更新
                update_badges()
                
                st.success("新しい目標を登録しました！10ポイント獲得！")
                st.balloons()
    
    # 既存の目標を編集
    goals_df = load_goals()
    smart_goals_df = load_smart_goals()
    
    if not goals_df.empty:
        st.markdown("### 既存の目標を編集")
        
        # 編集する目標を選択
        goal_options = goals_df['name'].tolist()
        selected_goal = st.selectbox("編集する目標を選択", goal_options)
        
        # 選択された目標の情報を取得
        selected_goal_data = goals_df[goals_df['name'] == selected_goal].iloc[0]
        goal_id = selected_goal_data['id']
        
        # SMART詳細情報を取得
        smart_goal_data = smart_goals_df[smart_goals_df['goal_id'] == goal_id].iloc[0] if not smart_goals_df[smart_goals_df['goal_id'] == goal_id].empty else {}
        
        with st.form("edit_goal_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                updated_name = st.text_input("目標名", value=selected_goal_data['name'])
                updated_description = st.text_area("目標の詳細", value=selected_goal_data['description'])
            
            with col2:
                updated_category = st.selectbox("カテゴリ", goal_categories, index=goal_categories.index(selected_goal_data['category']) if selected_goal_data['category'] in goal_categories else 0)
                updated_deadline = st.date_input("目標の期限", datetime.strptime(selected_goal_data['deadline'], "%Y-%m-%d") if 'deadline' in selected_goal_data else datetime.now() + timedelta(days=30))
            
            # 進捗状況の更新
            updated_progress = st.slider("進捗状況", 0, 100, int(selected_goal_data['progress']))
            
            # 状態の更新
            status_options = ["active", "paused", "completed"]
            status_labels = ["進行中", "一時停止", "完了"]
            status_index = status_options.index(selected_goal_data['status']) if 'status' in selected_goal_data and selected_goal_data['status'] in status_options else 0
            updated_status = st.selectbox("状態", status_labels, index=status_index)
            status_map = {label: option for label, option in zip(status_labels, status_options)}
            
            # SMART詳細情報の更新
            st.markdown("### SMART基準の更新")
            
            updated_specific = st.text_input("Specific（具体的）", value=smart_goal_data.get('specific', ''))
            updated_measurable = st.text_input("Measurable（測定可能）", value=smart_goal_data.get('measurable', ''))
            updated_achievable = st.text_input("Achievable（達成可能）", value=smart_goal_data.get('achievable', ''))
            updated_relevant = st.text_input("Relevant（関連性）", value=smart_goal_data.get('relevant', ''))
            updated_time_bound = st.text_input("Time-bound（期限付き）", value=smart_goal_data.get('time_bound', ''))
            
            # 小さな目標と最低基準の更新
            st.markdown("### モチベーション維持のための工夫")
            
            updated_mini_goal = st.text_input("小さな目標（達成しやすい）", value=smart_goal_data.get('mini_goal', ''))
            updated_minimum_criteria = st.text_input("ミニマム達成基準（最低限これだけ）", value=smart_goal_data.get('minimum_criteria', ''))
            
            submit_update = st.form_submit_button("変更を保存")
            
            if submit_update:
                # 基本情報の更新
                goals_df.loc[goals_df['id'] == goal_id, 'name'] = updated_name
                goals_df.loc[goals_df['id'] == goal_id, 'description'] = updated_description
                goals_df.loc[goals_df['id'] == goal_id, 'category'] = updated_category
                goals_df.loc[goals_df['id'] == goal_id, 'deadline'] = updated_deadline.strftime("%Y-%m-%d")
                goals_df.loc[goals_df['id'] == goal_id, 'progress'] = updated_progress
                goals_df.loc[goals_df['id'] == goal_id, 'status'] = status_map[updated_status]
                
                # 目標が完了した場合、完了日を記録
                if status_map[updated_status] == "completed" and (goals_df.loc[goals_df['id'] == goal_id, 'status'].iloc[0] != "completed"):
                    goals_df.loc[goals_df['id'] == goal_id, 'completed_at'] = datetime.now().strftime("%Y-%m-%d")
                    
                    # ポイント獲得
                    points_data = load_points()
                    points_data["points"] += 50
                    save_points(points_data)
                    
                    # バッジ更新
                    update_badges()
                
                # SMART詳細情報の更新
                if not smart_goals_df[smart_goals_df['goal_id'] == goal_id].empty:
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'specific'] = updated_specific
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'measurable'] = updated_measurable
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'achievable'] = updated_achievable
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'relevant'] = updated_relevant
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'time_bound'] = updated_time_bound
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'mini_goal'] = updated_mini_goal
                    smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'minimum_criteria'] = updated_minimum_criteria
                
                # 保存
                save_goals(goals_df)
                save_smart_goals(smart_goals_df)
                
                st.success("目標を更新しました！")
                
                if status_map[updated_status] == "completed" and (goals_df.loc[goals_df['id'] == goal_id, 'status'].iloc[0] != "completed"):
                    st.success("目標達成おめでとうございます！50ポイント獲得！")
                    st.balloons()
    else:
        st.info("まだ目標が設定されていません。上のフォームから目標を設定しましょう。")

# タスク管理ページ
def show_task_management():
    st.markdown('<h2 class="sub-header">✅ タスク管理</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    tasks_df = load_tasks()
    
    if goals_df.empty:
        st.info("まだ目標が設定されていません。「SMART目標設定」から最初の目標を設定しましょう！")
        return
    
    # 新しいタスクの追加
    st.markdown("### 新しいタスクを追加")
    
    with st.form("new_task_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 目標の選択
            active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
            goal_options = active_goals['name'].tolist()
            selected_goal = st.selectbox("目標", goal_options)
            
            # 選択された目標のIDを取得
            goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
            
            task_description = st.text_input("タスクの内容", placeholder="目標達成のための具体的なステップ")
        
        with col2:
            task_deadline = st.date_input("期限", datetime.now() + timedelta(days=7))
            task_points = st.number_input("獲得ポイント", min_value=1, max_value=20, value=5, help="このタスク完了時に獲得できるポイント")
        
        submit = st.form_submit_button("タスクを追加")
        
        if submit:
            if not task_description:
                st.error("タスクの内容は必須です。")
            else:
                # 新しいタスクを追加
                new_task = {
                    "id": str(uuid.uuid4()),
                    "goal_id": goal_id,
                    "description": task_description,
                    "status": "pending",
                    "deadline": task_deadline.strftime("%Y-%m-%d"),
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "completed_at": None,
                    "points": task_points
                }
                
                if tasks_df.empty:
                    tasks_df = pd.DataFrame([new_task])
                else:
                    tasks_df = pd.concat([tasks_df, pd.DataFrame([new_task])], ignore_index=True)
                
                save_tasks(tasks_df)
                
                st.success("新しいタスクを追加しました！")
    
    # タスクリストの表示と管理
    # この機能は04_目標達成.pyファイルのタスク管理セクションに追加します
# show_task_management()関数内のタスクリスト表示部分を以下のコードに置き換えてください

# タスクリストの表示と管理
    if not goals_df.empty:
        st.markdown("### タスクリスト")
        
        # 表示する目標の選択
        goal_filter_options = ["すべての目標"] + goals_df['name'].tolist()
        selected_goal_filter = st.selectbox("表示する目標を選択", goal_filter_options)
        
        # 状態によるフィルタリング
        status_filter_options = ["すべて", "未完了", "完了"]
        selected_status_filter = st.selectbox("表示するステータス", status_filter_options)
        
        # タスクのフィルタリング
        filtered_tasks = tasks_df.copy() if not tasks_df.empty else pd.DataFrame()
        
        if not filtered_tasks.empty:
            # 目標でフィルタリング
            if selected_goal_filter != "すべての目標":
                goal_id = goals_df[goals_df['name'] == selected_goal_filter]['id'].iloc[0]
                filtered_tasks = filtered_tasks[filtered_tasks['goal_id'] == goal_id]
            
            # 状態でフィルタリング
            if selected_status_filter == "未完了":
                filtered_tasks = filtered_tasks[filtered_tasks['status'] != 'completed']
            elif selected_status_filter == "完了":
                filtered_tasks = filtered_tasks[filtered_tasks['status'] == 'completed']
            
            # タスクがある場合は表示
            if not filtered_tasks.empty:
                for _, task in filtered_tasks.iterrows():
                    goal_name = goals_df[goals_df['id'] == task['goal_id']]['name'].iloc[0] if task['goal_id'] in goals_df['id'].values else "不明な目標"
                    
                    col1, col2, col3 = st.columns([3, 1, 1])  # 3列に変更: 内容、ステータス変更、削除
                    
                    with col1:
                        # タスクの内容表示
                        status_text = "✅ 完了" if task['status'] == 'completed' else "⏳ 未完了"
                        deadline_text = task['deadline']
                        days_left = (datetime.strptime(task['deadline'], "%Y-%m-%d").date() - datetime.now().date()).days if 'deadline' in task else 0
                        deadline_warning = ""
                        
                        if task['status'] != 'completed':
                            if days_left < 0:
                                deadline_warning = f"<span style='color: #F44336;'>期限切れ ({abs(days_left)}日前)</span>"
                            elif days_left == 0:
                                deadline_warning = "<span style='color: #FFC107;'>今日が期限</span>"
                            elif days_left < 3:
                                deadline_warning = f"<span style='color: #FFC107;'>あと{days_left}日</span>"
                            else:
                                deadline_warning = f"あと{days_left}日"
                        
                        st.markdown(f"""
                        <div class="{'mini-task' if task['status'] != 'completed' else 'mini-task' + ' goal-complete'}">
                            <p>{status_text} | <b>{task['description']}</b></p>
                            <p>目標: {goal_name} | 期限: {deadline_text} ({deadline_warning})</p>
                            <p>ポイント: {task['points']}pt</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # タスクのステータス変更ボタン
                        if task['status'] != 'completed':
                            if st.button("完了にする", key=f"complete_{task['id']}"):
                                # タスクを完了に変更
                                tasks_df.loc[tasks_df['id'] == task['id'], 'status'] = 'completed'
                                tasks_df.loc[tasks_df['id'] == task['id'], 'completed_at'] = datetime.now().strftime("%Y-%m-%d")
                                
                                # ポイント獲得
                                points_data = load_points()
                                points_data["points"] += task['points']
                                save_points(points_data)
                                
                                # 目標の進捗を更新
                                update_goal_progress(task['goal_id'])
                                
                                # バッジ更新
                                update_badges()
                                
                                save_tasks(tasks_df)
                                
                                st.success(f"タスクを完了しました！{task['points']}ポイント獲得！")
                                st.rerun()
                        else:
                            if st.button("未完了に戻す", key=f"revert_{task['id']}"):
                                # タスクを未完了に戻す
                                tasks_df.loc[tasks_df['id'] == task['id'], 'status'] = 'pending'
                                tasks_df.loc[tasks_df['id'] == task['id'], 'completed_at'] = None
                                
                                # ポイントを戻す
                                points_data = load_points()
                                points_data["points"] = max(0, points_data["points"] - task['points'])
                                save_points(points_data)
                                
                                # 目標の進捗を更新
                                update_goal_progress(task['goal_id'])
                                
                                save_tasks(tasks_df)
                                
                                st.info(f"タスクを未完了に戻しました。{task['points']}ポイント返却。")
                                st.rerun()
                    
                    with col3:
                        # タスク削除ボタンを追加
                        if st.button("削除", key=f"delete_task_{task['id']}"):
                            # 確認ダイアログ（Streamlitでは直接は実装できないので簡易的に）
                            if 'delete_confirmation' not in st.session_state:
                                st.session_state.delete_confirmation = {}
                            
                            task_id = task['id']
                            
                            if task_id not in st.session_state.delete_confirmation:
                                st.session_state.delete_confirmation[task_id] = True
                                st.warning(f"タスク「{task['description']}」を削除しますか？この操作は元に戻せません。もう一度削除ボタンを押すと削除されます。")
                                st.rerun()
                            else:
                                # タスクを削除
                                tasks_df = tasks_df[tasks_df['id'] != task_id]
                                save_tasks(tasks_df)
                                
                                # 確認状態をリセット
                                st.session_state.delete_confirmation.pop(task_id, None)
                                
                                st.success("タスクを削除しました！")
                                st.rerun()
            else:
                st.info("条件に合うタスクがありません。別のフィルターを選択するか、新しいタスクを追加してください。")
        else:
            st.info("まだタスクがありません。上のフォームからタスクを追加しましょう。")
    
    # 未来の自分からのメッセージ作成
    st.markdown("### 未来の自分からのメッセージ")
    
    st.write("目標達成後に開ける、自分へのメッセージを書いておきましょう。モチベーション維持に役立ちます。")
    
    with st.form("future_message_form"):
        # 目標の選択
        active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns and not goals_df.empty else pd.DataFrame()
        
        if not active_goals.empty:
            goal_options = active_goals['name'].tolist()
            selected_goal = st.selectbox("メッセージを残す目標", goal_options, key="message_goal")
            
            # 選択された目標のIDを取得
            goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
            
            message_content = st.text_area("未来の自分へのメッセージ", 
                                        placeholder="例：「この目標を達成した自分へ。よく頑張りました！この成功を次の目標に活かしていきましょう。」")
            
            submit_message = st.form_submit_button("メッセージを保存")
            
            if submit_message:
                if not message_content:
                    st.error("メッセージの内容は必須です。")
                else:
                    # 未来のメッセージを追加
                    future_messages = load_future_messages()
                    
                    new_message = {
                        "id": str(uuid.uuid4()),
                        "goal_id": goal_id,
                        "goal_name": selected_goal,
                        "message": message_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d"),
                        "opened": False
                    }
                    
                    future_messages.append(new_message)
                    save_future_messages(future_messages)
                    
                    st.success("未来の自分へのメッセージを保存しました！")
        else:
            st.info("アクティブな目標がありません。「SMART目標設定」から目標を設定してください。")
    
    # 保存されているメッセージの表示
    future_messages = load_future_messages()
    
    if future_messages:
        # 完了した目標のメッセージ
        completed_goals_ids = goals_df[goals_df['status'] == 'completed']['id'].tolist() if 'status' in goals_df.columns else []
        completed_messages = [msg for msg in future_messages if msg['goal_id'] in completed_goals_ids and not msg['opened']]
        
        if completed_messages:
            st.markdown("### 開封可能なメッセージ")
            
            for message in completed_messages:
                st.markdown(f"""
                <div class="message-card">
                    <h4>🎉 {message['goal_name']}を達成しました！</h4>
                    <p>達成前の自分からのメッセージがあります。</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("メッセージを開封", key=f"open_{message['id']}"):
                    st.markdown(f"""
                    <div class="message-card" style="background-color: #E8F5E9;">
                        <h4>📩 メッセージの内容:</h4>
                        <p>"{message['message']}"</p>
                        <p><small>作成日: {message['created_at']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # メッセージを開封済みに変更
                    for i, msg in enumerate(future_messages):
                        if msg['id'] == message['id']:
                            future_messages[i]['opened'] = True
                    
                    save_future_messages(future_messages)
        
        # 他のメッセージ一覧
        with st.expander("保存済みメッセージ一覧", expanded=False):
            for message in future_messages:
                goal_name = message['goal_name']
                status = "✅ 達成済み" if message['goal_id'] in completed_goals_ids else "⏳ 未達成"
                opened = "（開封済み）" if message['opened'] else "（未開封）"
                
                st.markdown(f"""
                <div class="message-card" style="opacity: 0.7;">
                    <p>目標: {goal_name} | 状態: {status} {opened if message['goal_id'] in completed_goals_ids else ''}</p>
                    <p><small>作成日: {message['created_at']}</small></p>
                </div>
                """, unsafe_allow_html=True)

# 目標の進捗を更新する関数
def update_goal_progress(goal_id):
    goals_df = load_goals()
    tasks_df = load_tasks()
    
    if not goals_df.empty and goal_id in goals_df['id'].values:
        # 目標に関連するタスクを取得
        goal_tasks = tasks_df[tasks_df['goal_id'] == goal_id] if not tasks_df.empty else pd.DataFrame()
        
        if not goal_tasks.empty:
            # 全タスク数と完了タスク数を計算
            total_tasks = len(goal_tasks)
            completed_tasks = len(goal_tasks[goal_tasks['status'] == 'completed'])
            
            # 進捗率を計算（完了タスク数 ÷ 全タスク数 × 100）
            progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            
            # 目標の進捗を更新
            goals_df.loc[goals_df['id'] == goal_id, 'progress'] = progress
            
            # 進捗が100%になったら、目標を完了に変更
            if progress == 100 and goals_df.loc[goals_df['id'] == goal_id, 'status'].iloc[0] != 'completed':
                goals_df.loc[goals_df['id'] == goal_id, 'status'] = 'completed'
                goals_df.loc[goals_df['id'] == goal_id, 'completed_at'] = datetime.now().strftime("%Y-%m-%d")
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 50
                save_points(points_data)
            
            save_goals(goals_df)
            
            return True
    
    return False

# パート6: 報酬設定ページのメイン関数
def show_reward_settings():
    st.markdown('<h2 class="sub-header">🎁 報酬設定</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    
    if goals_df.empty:
        st.info("まだ目標が設定されていません。「SMART目標設定」から最初の目標を設定しましょう！")
        return
    
    # タブの設定
    tabs = st.tabs(["報酬設定", "未来メッセージ", "ポイント・バッジ", "モチベーション"])
    
    # 報酬設定タブ
    with tabs[0]:
        show_reward_tab(goals_df)
    
    # 未来メッセージタブ
    with tabs[1]:
        show_future_message_tab(goals_df)
    
    # ポイント・バッジタブ
    with tabs[2]:
        show_points_badges_tab()
    
    # モチベーションタブ
    with tabs[3]:
        show_motivation_tab(goals_df)

# 報酬設定タブの表示
def show_reward_tab(goals_df):
    st.markdown("### 目標達成報酬の設定")
    st.write("目標を達成したら自分へのご褒美を設定しましょう。モチベーション維持に役立ちます。")
    
    # アクティブな目標を選択
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        st.info("アクティブな目標がありません。新しい目標を設定するか、目標のステータスを変更してください。")
        return
    
    # 目標の選択
    goal_options = active_goals['name'].tolist()
    selected_goal = st.selectbox("目標を選択", goal_options, key="reward_goal_select")
    
    # 選択された目標のID取得
    goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
    
    # 報酬の追加フォーム
    with st.form("add_reward_form"):
        st.markdown("#### 新しい報酬を追加")
        reward_name = st.text_input("報酬名", placeholder="例：新しい服を買う、好きな映画を見るなど")
        reward_description = st.text_area("報酬の詳細（オプション）", placeholder="報酬に関する詳細情報")
        reward_condition = st.text_input("達成条件", placeholder="例：体重を3kg減らす、1ヶ月続けるなど")
        
        submit_button = st.form_submit_button("報酬を追加")
        
        if submit_button:
            if not reward_name or not reward_condition:
                st.error("報酬名と達成条件は必須です。")
            else:
                # 報酬を追加
                rewards = load_rewards()
                
                new_reward = {
                    "id": str(random.randint(1000, 9999)),
                    "goal_id": goal_id,
                    "goal_name": selected_goal,
                    "name": reward_name,
                    "description": reward_description,
                    "condition": reward_condition,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "is_redeemed": False,
                    "redeemed_at": None
                }
                
                rewards.append(new_reward)
                save_rewards(rewards)
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 5
                save_points(points_data)
                
                # バッジの更新確認
                check_reward_badge()
                
                st.success(f"報酬「{reward_name}」を追加しました！5ポイント獲得！")
                st.rerun()
    
    # 既存の報酬一覧
    rewards = load_rewards()
    goal_rewards = [reward for reward in rewards if reward["goal_id"] == goal_id]
    
    if goal_rewards:
        st.markdown("#### 設定済みの報酬")
        
        for i, reward in enumerate(goal_rewards):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if reward["is_redeemed"]:
                    st.markdown(f"""
                    <div class="reward-card" style="opacity: 0.7;">
                        <h4>🏆 {reward['name']} (獲得済み)</h4>
                        <p>{reward['description'] if reward['description'] else '説明なし'}</p>
                        <p><b>条件:</b> {reward['condition']}</p>
                        <p><small>獲得日: {reward['redeemed_at']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="reward-card">
                        <h4>🎁 {reward['name']} (未獲得)</h4>
                        <p>{reward['description'] if reward['description'] else '説明なし'}</p>
                        <p><b>条件:</b> {reward['condition']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if not reward["is_redeemed"]:
                    if st.button("獲得する", key=f"redeem_reward_{i}"):
                        # 報酬を獲得状態に変更
                        rewards = load_rewards()
                        for j, r in enumerate(rewards):
                            if r["id"] == reward["id"]:
                                rewards[j]["is_redeemed"] = True
                                rewards[j]["redeemed_at"] = datetime.now().strftime("%Y-%m-%d")
                        
                        save_rewards(rewards)
                        
                        # ポイント獲得
                        points_data = load_points()
                        points_data["points"] += 20
                        save_points(points_data)
                        
                        st.success(f"報酬「{reward['name']}」を獲得しました！20ポイント獲得！")
                        st.balloons()
                        st.rerun()
                
                if st.button("削除", key=f"delete_reward_{i}"):
                    # 報酬を削除
                    rewards = load_rewards()
                    rewards = [r for r in rewards if r["id"] != reward["id"]]
                    save_rewards(rewards)
                    
                    st.success(f"報酬「{reward['name']}」を削除しました。")
                    st.rerun()
    else:
        st.info("まだ報酬が設定されていません。上のフォームから報酬を追加してください。")

# 未来メッセージタブの表示
def show_future_message_tab(goals_df):
    st.markdown("### 未来の自分からのメッセージ")
    st.write("目標達成の途中や達成後に読める、励ましのメッセージを書いておきましょう。")
    
    # アクティブな目標を選択
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        st.info("アクティブな目標がありません。新しい目標を設定するか、目標のステータスを変更してください。")
        return
    
    # 目標の選択
    goal_options = active_goals['name'].tolist()
    selected_goal = st.selectbox("目標を選択", goal_options, key="message_goal_select")
    
    # 選択された目標のID取得
    goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
    
    # メッセージ追加フォーム
    with st.form("add_message_form"):
        st.markdown("#### 新しいメッセージを作成")
        
        message_content = st.text_area("未来の自分へのメッセージ", 
                                      placeholder="例：辛い時もあったけど、よく頑張ったね！次の目標も一緒に頑張ろう！")
        
        unlock_condition = st.selectbox("解放条件", 
                                      ["25%達成時", "50%達成時", "75%達成時", "100%達成時（完全達成）", "挫折しそうな時"])
        
        submit_button = st.form_submit_button("メッセージを保存")
        
        if submit_button:
            if not message_content:
                st.error("メッセージ内容は必須です。")
            else:
                # メッセージを追加
                messages = load_future_messages()
                
                new_message = {
                    "id": str(random.randint(1000, 9999)),
                    "goal_id": goal_id,
                    "goal_name": selected_goal,
                    "message": message_content,
                    "unlock_condition": unlock_condition,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "is_unlocked": False,
                    "unlocked_at": None
                }
                
                messages.append(new_message)
                save_future_messages(messages)
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 5
                save_points(points_data)
                
                st.success("未来の自分へのメッセージを保存しました！5ポイント獲得！")
                st.rerun()
    
    # 既存のメッセージ一覧
    messages = load_future_messages()
    goal_messages = [message for message in messages if message["goal_id"] == goal_id]
    
    if goal_messages:
        st.markdown("#### 保存したメッセージ")
        
        for i, message in enumerate(goal_messages):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if message["is_unlocked"]:
                    st.markdown(f"""
                    <div class="message-card" style="opacity: 0.7;">
                        <h4>📬 未来の自分からのメッセージ (開封済み)</h4>
                        <p><b>解放条件:</b> {message['unlock_condition']}</p>
                        <p><small>開封日: {message['unlocked_at']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="message-card">
                        <h4>📫 未来の自分からのメッセージ (未開封)</h4>
                        <p><b>解放条件:</b> {message['unlock_condition']}</p>
                        <p><small>作成日: {message['created_at']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                button_label = "再度読む" if message["is_unlocked"] else "開封する"
                
                if st.button(button_label, key=f"view_message_{i}"):
                    # 開封処理
                    if not message["is_unlocked"]:
                        # 進捗チェック
                        current_progress = goals_df.loc[goals_df['id'] == goal_id, 'progress'].iloc[0]
                        
                        # 解放条件チェック
                        can_unlock = False
                        
                        if message["unlock_condition"] == "25%達成時" and current_progress >= 25:
                            can_unlock = True
                        elif message["unlock_condition"] == "50%達成時" and current_progress >= 50:
                            can_unlock = True
                        elif message["unlock_condition"] == "75%達成時" and current_progress >= 75:
                            can_unlock = True
                        elif message["unlock_condition"] == "100%達成時（完全達成）" and current_progress >= 100:
                            can_unlock = True
                        elif message["unlock_condition"] == "挫折しそうな時":
                            can_unlock = True
                        
                        if can_unlock:
                            # メッセージを開封状態に変更
                            messages = load_future_messages()
                            for j, msg in enumerate(messages):
                                if msg["id"] == message["id"]:
                                    messages[j]["is_unlocked"] = True
                                    messages[j]["unlocked_at"] = datetime.now().strftime("%Y-%m-%d")
                            
                            save_future_messages(messages)
                            
                            # ポイント獲得
                            points_data = load_points()
                            points_data["points"] += 10
                            save_points(points_data)
                            
                            st.success("メッセージを開封しました！10ポイント獲得！")
                        else:
                            st.warning(f"まだ解放条件 ({message['unlock_condition']}) を満たしていません。")
                    
                    # メッセージ内容を表示
                    st.markdown(f"""
                    <div class="message-card" style="background-color: #E8F5E9;">
                        <h4>📩 メッセージの内容:</h4>
                        <p>"{message['message']}"</p>
                        <p><small>作成日: {message['created_at']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("削除", key=f"delete_message_{i}"):
                    # メッセージを削除
                    messages = load_future_messages()
                    messages = [msg for msg in messages if msg["id"] != message["id"]]
                    save_future_messages(messages)
                    
                    st.success("メッセージを削除しました。")
                    st.rerun()
    else:
        st.info("まだメッセージが保存されていません。上のフォームからメッセージを作成してください。")

# ポイントとバッジタブの表示
def show_points_badges_tab():
    col1, col2 = st.columns(2)
    
    with col1:
        show_points_section()
    
    with col2:
        show_badges_section()

# ポイント表示セクション
def show_points_section():
    st.markdown("### 達成ポイント")
    
    # ポイント情報を取得
    points_data = load_points()
    total_points = points_data["points"]
    
    # レベル計算
    level = max(1, int(total_points ** 0.5 / 5))
    next_level = level + 1
    next_level_points = (next_level * 5) ** 2
    
    # 進捗計算
    current_level_points = (level * 5) ** 2
    progress_percent = min(100, ((total_points - current_level_points) / (next_level_points - current_level_points)) * 100) if next_level_points > current_level_points else 0
    
    # ポイント表示
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #E8F5E9; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: #2E7D32; font-size: 3rem;">{total_points}</h1>
        <p>累計ポイント</p>
    </div>
    """, unsafe_allow_html=True)
    
    # レベル表示
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <p>レベル {level}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # プログレスバー
    st.progress(progress_percent / 100)
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
        <span>現在: {total_points}pt</span>
        <span>次のレベルまで: あと{next_level_points - total_points}pt</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ポイント獲得方法
    with st.expander("ポイント獲得方法", expanded=False):
        st.markdown("""
        - 目標設定: +10ポイント
        - 目標達成: +50ポイント
        - タスク完了: +タスクのポイント
        - 報酬設定: +5ポイント
        - 報酬獲得: +20ポイント
        - 未来メッセージ作成: +5ポイント
        - 未来メッセージ解除: +10ポイント
        - バッジ獲得: +30ポイント
        """)

# バッジ表示セクション
def show_badges_section():
    st.markdown("### 獲得バッジ")
    
    # バッジ情報を取得
    badges_data = load_badges()
    badges = badges_data["badges"]
    
    # バッジの表示
    badge_cols = st.columns(3)
    
    for i, badge in enumerate(badges):
        col_index = i % 3
        
        with badge_cols[col_index]:
            if badge["earned"]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #F3E5F5; border-radius: 10px; margin-bottom: 10px;">
                    <h1 style="font-size: 2rem;">{badge["image"]}</h1>
                    <p style="font-weight: bold; margin: 0;">{badge["name"]}</p>
                    <p style="font-size: 0.8rem;">{badge["description"]}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background-color: #F5F5F5; border-radius: 10px; margin-bottom: 10px; opacity: 0.5;">
                    <h1 style="font-size: 2rem;">{badge["image"]}</h1>
                    <p style="margin: 0;">{badge["name"]}</p>
                    <p style="font-size: 0.8rem;">{badge["description"]}</p>
                </div>
                """, unsafe_allow_html=True)

# モチベーションタブの表示
def show_motivation_tab(goals_df):
    st.markdown("### やる気を高めるツール")
    st.write("モチベーションが下がった時や、目標が難しく感じる時に活用しましょう")
    
    # やる気が出ない時のサポート
    if st.button("😔 今日やる気が出ない...", use_container_width=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-box">
                <h4>⏱️ たった5分だけ始めてみる</h4>
                <p>5分経ったら止めてもOK。多くの場合、始めるとそのまま続けられます。</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
                <h4>🧠 なぜやる気が出ないのか考える</h4>
                <p>疲れているのか、難しすぎるのか、目標が合っていないのか、原因を探ります。</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-box">
                <h4>✅ 最小限のタスクを決める</h4>
                <p>「今日はこれだけやれば合格」という最低ラインを決めましょう。</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
                <h4>💡 目標を調整する</h4>
                <p>今の状態に合わせて、一時的により小さな目標に調整することも大切です。</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 1分だけでもOKのボタン
    if st.button("⌛ 1分だけでもOK！超小さなタスク", use_container_width=True):
        # マイクロタスク生成
        micro_tasks = generate_micro_tasks(goals_df, None)
        
        if micro_tasks:
            st.markdown("""
            <div class="insight-box">
                <h4>大丈夫です！小さな一歩から始めましょう。</h4>
                <p>以下のどれか1つだけでも取り組んでみましょう：</p>
            </div>
            """, unsafe_allow_html=True)
            
            for task in micro_tasks:
                st.markdown(f"""
                <div class="mini-task">
                    <h4>💫 {task['description']}</h4>
                    <p>目標: {task['goal_name']}</p>
                    <p><small>たった1分でもOK！少しでも進めれば素晴らしい成果です。</small></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("アクティブな目標がありません。新しい目標を設定してください。")

# ミニマム達成基準ボタン
    if st.button("✅ ミニマム達成基準を設定", use_container_width=True):
        st.markdown("""
        <div class="insight-box">
            <h4>ミニマム達成基準の設定</h4>
            <p>「完璧にできなくても、これだけやれば今日は合格」という基準を設定しましょう。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # SMART目標データの取得
        smart_goals_df = load_smart_goals()
        
        # アクティブな目標を取得
        active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
        
        if not active_goals.empty:
            goal_options = active_goals['name'].tolist()
            selected_goal = st.selectbox("目標を選択", goal_options, key="minimum_goal_select")
            
            # 選択された目標のID取得
            goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
            
            # ミニマム基準を表示または設定
            minimum_criteria = ""
            
            if not smart_goals_df.empty and not smart_goals_df[smart_goals_df['goal_id'] == goal_id].empty:
                minimum_criteria = smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'minimum_criteria'].iloc[0]
            
            with st.form("minimum_criteria_form"):
                new_minimum_criteria = st.text_area("ミニマム達成基準", 
                                                 value=minimum_criteria if minimum_criteria else "",
                                                 placeholder="例：天気が悪い日は10分だけでも運動する、難しい問題は1問だけ解くなど")
                
                submit_button = st.form_submit_button("設定を保存")
                
                if submit_button:
                    if not new_minimum_criteria:
                        st.error("ミニマム達成基準を入力してください。")
                    else:
                        # SMART目標データを更新
                        if smart_goals_df.empty or smart_goals_df[smart_goals_df['goal_id'] == goal_id].empty:
                            st.warning("SMART目標データが見つかりません。「SMART目標設定」ページで設定してください。")
                        else:
                            smart_goals_df.loc[smart_goals_df['goal_id'] == goal_id, 'minimum_criteria'] = new_minimum_criteria
                            
                            save_smart_goals(smart_goals_df)
                            
                            st.success("ミニマム達成基準を設定しました！")
        else:
            st.info("アクティブな目標がありません。新しい目標を設定してください。")
    
    # 問題と対策ボタン
    if st.button("🧠 起こりうる問題と対策を考える", use_container_width=True):
        st.markdown("""
        <div class="insight-box">
            <h4>起こりうる問題と対策プラン</h4>
            <p>目標達成の障害となりそうな問題をリストアップし、「もし〇〇になったら、こうする」という対策プランを立てましょう。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # アクティブな目標を取得
        active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
        
        if not active_goals.empty:
            goal_options = active_goals['name'].tolist()
            selected_goal = st.selectbox("目標を選択", goal_options, key="problem_goal_select")
            
            # 選択された目標のID取得
            goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
            
            # 既存の問題と対策を取得
            problems_data = load_problems()
            goal_problems = next((item for item in problems_data if item.get("goal_id") == goal_id), None)
            
            problems = goal_problems.get("problems", []) if goal_problems else []
            plans = goal_problems.get("plans", []) if goal_problems else []
            
            with st.form("problems_plans_form"):
                st.markdown("#### 問題のリストアップ")
                
                obstacles = st.text_area("目標達成の障害となりそうな問題", 
                                       value="\n".join(problems) if problems else "",
                                       placeholder="各行に1つの問題を書いてください\n例：\n忙しくて時間がない\nモチベーションが続かない\n周囲のサポートがない",
                                       height=150)
                
                st.markdown("#### 「もしも」プラン")
                
                contingency_plans = st.text_area("「もし〇〇になったら、こうする」という対策プラン", 
                                               value="\n".join(plans) if plans else "",
                                               placeholder="各行に1つの対策を書いてください\n例：\nもし忙しくて時間がなければ、朝15分早く起きて取り組む\nもしモチベーションが下がったら、目標達成後の自分をイメージする\nもし周囲のサポートがなければ、オンラインコミュニティに参加する",
                                               height=150)
                
                submit_button = st.form_submit_button("保存する")
                
                if submit_button:
                    # 入力を処理
                    problems_list = [p.strip() for p in obstacles.split("\n") if p.strip()]
                    plans_list = [p.strip() for p in contingency_plans.split("\n") if p.strip()]
                    
                    if not problems_list:
                        st.error("少なくとも1つの問題を入力してください。")
                    elif not plans_list:
                        st.error("少なくとも1つの対策プランを入力してください。")
                    else:
                        # 問題と対策を保存
                        if goal_problems:
                            # 既存のデータを更新
                            for i, item in enumerate(problems_data):
                                if item.get("goal_id") == goal_id:
                                    problems_data[i]["problems"] = problems_list
                                    problems_data[i]["plans"] = plans_list
                                    problems_data[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
                        else:
                            # 新しいデータを追加
                            problems_data.append({
                                "goal_id": goal_id,
                                "goal_name": selected_goal,
                                "problems": problems_list,
                                "plans": plans_list,
                                "created_at": datetime.now().strftime("%Y-%m-%d")
                            })
                        
                        save_problems(problems_data)
                        
                        # ポイント獲得
                        points_data = load_points()
                        points_data["points"] += 5
                        save_points(points_data)
                        
                        # 問題解決者バッジをチェック
                        check_problem_solver_badge(problems_data)
                        
                        st.success("問題と対策を保存しました！5ポイント獲得！")
        else:
            st.info("アクティブな目標がありません。新しい目標を設定してください。")

# 1. 進捗振り返りページ（既存の関数に機能を追加）
def show_progress_review():
    st.markdown('<h2 class="sub-header">📈 進捗振り返り</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    tasks_df = load_tasks()
    smart_goals_df = load_smart_goals()
    
    if goals_df.empty:
        st.info("まだ目標が設定されていません。「SMART目標設定」から最初の目標を設定しましょう！")
        return
    
    # タブの設定
    tabs = st.tabs(["目標の達成度", "週間/月間振り返り", "AIアドバイス", "成功体験"])
    
    # 目標の達成度タブ
    with tabs[0]:
        show_goal_achievement_tab(goals_df, tasks_df)
    
    # 週間/月間振り返りタブ
    with tabs[1]:
        show_periodic_review_tab(goals_df, smart_goals_df, tasks_df)
    
    # AIアドバイスタブ
    with tabs[2]:
        show_ai_advice_tab(goals_df, smart_goals_df, tasks_df)
    
    # 成功体験タブ
    with tabs[3]:
        show_success_experience_tab()

# 目標の達成度タブ
def show_goal_achievement_tab(goals_df, tasks_df):
    st.markdown("### 目標の達成度")
    
    # 進行中の目標一覧
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if not active_goals.empty:
        # 目標の進捗状況グラフ
        if 'progress' in active_goals.columns:
            fig_progress = px.bar(
                active_goals.sort_values('progress', ascending=False),
                x='name',
                y='progress',
                title="目標の進捗状況",
                labels={'name': '目標', 'progress': '進捗 (%)'},
                color='progress',
                color_continuous_scale=["red", "yellow", "green"],
                range_color=[0, 100]
            )
            st.plotly_chart(fig_progress, use_container_width=True)
        
        # 各目標の詳細レポート
        for _, goal in active_goals.iterrows():
            with st.expander(f"{goal['name']} ({goal['progress']}%)"):
                # 目標の基本情報
                st.markdown(f"**カテゴリ:** {goal.get('category', '未分類')}")
                st.markdown(f"**説明:** {goal['description']}")
                
                # 締め切りまでの日数計算
                if 'deadline' in goal and goal['deadline']:
                    deadline_date = datetime.strptime(goal['deadline'], "%Y-%m-%d").date()
                    days_left = (deadline_date - datetime.now().date()).days
                    
                    if days_left < 0:
                        st.markdown(f"**締め切り:** <span style='color: #F44336;'>期限切れ ({abs(days_left)}日前)</span>", unsafe_allow_html=True)
                    elif days_left == 0:
                        st.markdown("**締め切り:** 今日が期限です", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**締め切り:** あと{days_left}日")
                
                # タスクの完了状況
                goal_tasks = tasks_df[tasks_df['goal_id'] == goal['id']] if not tasks_df.empty else pd.DataFrame()
                
                if not goal_tasks.empty:
                    completed_tasks = goal_tasks[goal_tasks['status'] == 'completed']
                    pending_tasks = goal_tasks[goal_tasks['status'] != 'completed']
                    
                    st.markdown(f"**タスク完了率:** {len(completed_tasks)}/{len(goal_tasks)} ({int(len(completed_tasks)/len(goal_tasks)*100)}%)")
                    
                    if not completed_tasks.empty:
                        st.markdown("**完了したタスク:**")
                        for _, task in completed_tasks.iterrows():
                            st.markdown(f"- ✅ {task['description']} ({task.get('completed_at', '不明')})")
                    
                    if not pending_tasks.empty:
                        st.markdown("**未完了のタスク:**")
                        for _, task in pending_tasks.iterrows():
                            deadline = task.get('deadline', '期限なし')
                            st.markdown(f"- ⏳ {task['description']} (期限: {deadline})")
                else:
                    st.info("この目標にはまだタスクが設定されていません。")
                
                # 進捗グラフ
                st.markdown("**進捗状況:**")
                st.progress(goal['progress'] / 100)
    else:
        st.info("現在、進行中の目標はありません。")
    
    # 完了した目標
    completed_goals = goals_df[goals_df['status'] == 'completed'] if 'status' in goals_df.columns else pd.DataFrame()
    
    if not completed_goals.empty:
        st.markdown("### 達成済みの目標")
        
        for _, goal in completed_goals.iterrows():
            st.markdown(f"""
            <div class="goal-card goal-complete">
                <h4>✅ {goal['name']}</h4>
                <p>{goal['description']}</p>
                <p>カテゴリ: {goal.get('category', '未分類')}</p>
                <p>完了日: {goal.get('completed_at', '不明')}</p>
            </div>
            """, unsafe_allow_html=True)

# 週間/月間振り返りタブ
def show_periodic_review_tab(goals_df, smart_goals_df, tasks_df):
    st.markdown("### 定期的な目標振り返り")
    
    # 振り返りの期間選択
    review_period = st.radio("振り返りの期間", ["週間振り返り", "月間振り返り"])
    
    # 目標の選択
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        st.info("現在、進行中の目標はありません。新しい目標を設定してください。")
        return
    
    goal_options = active_goals['name'].tolist()
    selected_goal = st.selectbox("振り返る目標を選択", goal_options)
    
    # 選択された目標のID取得
    goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
    goal_data = active_goals[active_goals['id'] == goal_id].iloc[0]
    
    # 振り返りの日付
    today = datetime.now().date()
    
    if review_period == "週間振り返り":
        st.markdown(f"### {selected_goal} の週間振り返り ({today.strftime('%Y/%m/%d')})")
        
        # 週間進捗状況の分析
        st.markdown("#### 今週の進捗状況")
        
        # 1週間前の日付
        week_ago = today - timedelta(days=7)
        
        # タスクの完了状況
        goal_tasks = tasks_df[tasks_df['goal_id'] == goal_id] if not tasks_df.empty else pd.DataFrame()
        
        if not goal_tasks.empty:
            # 今週完了したタスク
            week_completed_tasks = goal_tasks[(goal_tasks['status'] == 'completed') & 
                                           (pd.to_datetime(goal_tasks['completed_at']).dt.date >= week_ago)]
            
            st.markdown(f"**今週完了したタスク:** {len(week_completed_tasks)}件")
            
            for _, task in week_completed_tasks.iterrows():
                st.markdown(f"- ✅ {task['description']} ({task.get('completed_at', '不明')})")
        
        # 週間振り返りフォーム
        with st.form("weekly_review_form"):
            st.markdown("#### 週間振り返り質問")
            
            week_achievement = st.text_area("今週、この目標に関して達成したことは？", 
                                         placeholder="例：週2回のジョギングを達成した、プログラミングの基礎を学んだなど")
            
            week_challenges = st.text_area("今週、困難だったことや障害は？", 
                                        placeholder="例：時間管理が難しかった、モチベーションが下がった日があったなど")
            
            week_next_steps = st.text_area("来週、取り組むべきことは？", 
                                         placeholder="例：ジョギングの距離を伸ばす、次の章に進むなど")
            
            week_goal_adjustment = st.radio("目標の調整は必要ですか？", 
                                          ["調整は不要", "少し調整が必要", "大幅な調整が必要"])
            
            submit_button = st.form_submit_button("振り返りを保存")
            
            if submit_button:
                if not week_achievement and not week_challenges and not week_next_steps:
                    st.error("少なくとも1つの項目に記入してください。")
                else:
                    # 週間振り返りデータを保存
                    # 実際の実装では、週間振り返りのデータを保存するロジックを追加
                    
                    st.success("週間振り返りを保存しました！")
                    
                    # 目標調整の必要性に応じたアドバイス
                    if week_goal_adjustment == "少し調整が必要":
                        st.markdown("""
                        <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                            <h4>目標の微調整を検討しましょう</h4>
                            <p>目標達成のペースや方法を少し調整することで、より効果的に進められるかもしれません。SMART目標設定ページで小さな調整を行ってみてください。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif week_goal_adjustment == "大幅な調整が必要":
                        st.markdown("""
                        <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                            <h4>目標の見直しが必要です</h4>
                            <p>現在の目標が現実的でないか、状況が変わった可能性があります。SMART目標設定ページで目標を再検討し、より達成可能な形に調整しましょう。</p>
                        </div>
                        """, unsafe_allow_html=True)
    else:  # 月間振り返り
        st.markdown(f"### {selected_goal} の月間振り返り ({today.strftime('%Y/%m')})")
        
        # 月間進捗状況の分析
        st.markdown("#### 今月の進捗状況")
        
        # 1ヶ月前の日付
        month_ago = today - timedelta(days=30)
        
        # タスクの完了状況
        goal_tasks = tasks_df[tasks_df['goal_id'] == goal_id] if not tasks_df.empty else pd.DataFrame()
        
        if not goal_tasks.empty:
            # 今月完了したタスク
            month_completed_tasks = goal_tasks[(goal_tasks['status'] == 'completed') & 
                                            (pd.to_datetime(goal_tasks['completed_at']).dt.date >= month_ago)]
            
            st.markdown(f"**今月完了したタスク:** {len(month_completed_tasks)}件")
            
            if not month_completed_tasks.empty:
                # 完了タスクの日付ごとの集計
                if 'completed_at' in month_completed_tasks.columns:
                    month_completed_tasks['completed_date'] = pd.to_datetime(month_completed_tasks['completed_at']).dt.date
                    completed_by_date = month_completed_tasks.groupby('completed_date').size().reset_index()
                    completed_by_date.columns = ['date', 'count']
                    
                    # タスク完了の日別グラフ
                    fig_tasks = px.bar(
                        completed_by_date,
                        x='date',
                        y='count',
                        title="日別の完了タスク数",
                        labels={'date': '日付', 'count': 'タスク数'}
                    )
                    st.plotly_chart(fig_tasks, use_container_width=True)
        
        # 月間振り返りフォーム
        with st.form("monthly_review_form"):
            st.markdown("#### 月間振り返り質問")
            
            month_progress = st.slider("目標に対する進捗度は？", 0, 100, int(goal_data['progress']))
            
            month_achievements = st.text_area("今月の主な成果は？", 
                                           placeholder="例：5kg減量に成功した、プログラミング言語の基礎を習得したなど")
            
            month_challenges = st.text_area("今月の課題や障害は？", 
                                         placeholder="例：時間確保が難しかった、予想より進捗が遅かったなど")
            
            month_learnings = st.text_area("学んだことや気づきは？", 
                                        placeholder="例：朝の時間帯の方が集中できる、小さなステップに分けると達成しやすいなど")
            
            month_goal_revision = st.radio("目標の見直しは必要？", 
                                        ["目標は適切で調整不要", "少し調整が必要", "目標の再設定が必要"])
            
            next_month_focus = st.text_area("来月のフォーカスポイントは？", 
                                         placeholder="例：週3回の運動習慣を定着させる、応用編に進むなど")
            
            submit_button = st.form_submit_button("振り返りを保存")
            
            if submit_button:
                if not month_achievements and not month_challenges and not month_learnings and not next_month_focus:
                    st.error("少なくとも1つの項目に記入してください。")
                else:
                    # 月間振り返りデータを保存
                    # 実際の実装では、月間振り返りのデータを保存するロジックを追加
                    
                    # 進捗率の更新
                    if month_progress != int(goal_data['progress']):
                        goals_df.loc[goals_df['id'] == goal_id, 'progress'] = month_progress
                        save_goals(goals_df)
                    
                    st.success("月間振り返りを保存しました！")
                    
                    # 目標見直しに関するアドバイス
                    if month_goal_revision == "少し調整が必要":
                        st.markdown("""
                        <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                            <h4>目標の微調整を行いましょう</h4>
                            <p>これまでの進捗と学びを元に、目標の一部を調整すると良いでしょう。タイムラインの延長や小さな目標の追加を検討してください。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif month_goal_revision == "目標の再設定が必要":
                        st.markdown("""
                        <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                            <h4>目標の再設定を検討してください</h4>
                            <p>現在の目標が現実と合っていない可能性があります。SMART目標設定ページで目標を見直し、現在の状況に合わせた新しい目標を設定しましょう。</p>
                        </div>
                        """, unsafe_allow_html=True)

# AIアドバイスタブ
def show_ai_advice_tab(goals_df, smart_goals_df, tasks_df):
    st.markdown("### AIによる改善提案")
    
    # 目標の選択
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        st.info("現在、進行中の目標はありません。新しい目標を設定してください。")
        return
    
    goal_options = active_goals['name'].tolist()
    selected_goal = st.selectbox("目標を選択", goal_options, key="ai_advice_goal")
    
    # 選択された目標のID取得
    goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
    goal_data = active_goals[active_goals['id'] == goal_id].iloc[0]
    
    # SMART目標データの取得
    smart_goal_data = {}
    if not smart_goals_df.empty and goal_id in smart_goals_df['goal_id'].values:
        smart_goal_data = smart_goals_df[smart_goals_df['goal_id'] == goal_id].iloc[0].to_dict()
    
    # タスクデータの取得
    goal_tasks = tasks_df[tasks_df['goal_id'] == goal_id] if not tasks_df.empty else pd.DataFrame()
    
    if st.button("AIアドバイスを生成", key="generate_ai_advice"):
        # 進捗状況に基づいたアドバイス
        progress = goal_data['progress']
        days_left = 0
        
        if 'deadline' in goal_data and goal_data['deadline']:
            deadline_date = datetime.strptime(goal_data['deadline'], "%Y-%m-%d").date()
            days_left = (deadline_date - datetime.now().date()).days
        
        st.markdown("#### AIによる目標達成のアドバイス")
        
        # 進捗状況に応じたアドバイス
        if progress < 25:
            if days_left < 7:
                st.markdown("""
                <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                    <h4>目標の見直しが必要です</h4>
                    <p>進捗が25%未満で、期限まで1週間を切っています。より現実的な目標に調整することを検討してください。</p>
                    <ul>
                        <li>目標の範囲を縮小する</li>
                        <li>期限を延長する</li>
                        <li>達成基準を現実的なものに変更する</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                    <h4>小さなステップに分解しましょう</h4>
                    <p>進捗が初期段階のようです。より小さな達成可能なステップに分解することで、モチベーションを高められます。</p>
                    <ul>
                        <li>1日あたりの最小タスクを設定する</li>
                        <li>「1分だけでもOK」の超小さなタスクを活用する</li>
                        <li>最初の一歩を踏み出すことに集中する</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        elif progress < 50:
            if days_left < 0:
                st.markdown("""
                <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                    <h4>期限が過ぎています - 再計画が必要です</h4>
                    <p>期限が過ぎていますが、まだ半分の進捗です。目標を見直し、新しい期限を設定しましょう。</p>
                    <ul>
                        <li>これまでの進捗ペースを考慮して、現実的な新しい期限を設定する</li>
                        <li>目標を2つに分割することも検討する</li>
                        <li>これまでの障害を分析し、対策を立てる</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box" style="background-color: #E3F2FD; border-left: 5px solid #2196F3;">
                    <h4>モメンタムを作り出しましょう</h4>
                    <p>良いスタートを切りました。ここからモメンタムを作り出すことが重要です。</p>
                    <ul>
                        <li>毎日同じ時間に取り組む習慣を作る</li>
                        <li>進捗を視覚化して、達成感を高める</li>
                        <li>達成したタスクを振り返り、モチベーションを維持する</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        elif progress < 75:
            st.markdown("""
            <div class="insight-box" style="background-color: #E8F5E9; border-left: 5px solid #4CAF50;">
                <h4>順調に進んでいます！</h4>
                <p>進捗は半分以上で、良いペースです。このまま継続して、最後まで頑張りましょう。</p>
                <ul>
                    <li>中だるみを防ぐために、短期的な報酬を設定する</li>
                    <li>これまでの成果を振り返って、達成感を味わう</li>
                    <li>残りのタスクを優先順位付けして、効率的に進める</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box" style="background-color: #E8F5E9; border-left: 5px solid #4CAF50;">
                <h4>もう少しで達成です！</h4>
                <p>ゴールまであと一歩です。最後のスパートをかけましょう。</p>
                <ul>
                    <li>残りのタスクに集中して、完遂する</li>
                    <li>達成後の報酬を楽しみにする</li>
                    <li>次の目標について考え始める</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # タスク管理に関するアドバイス
        if not goal_tasks.empty:
            completed_tasks = goal_tasks[goal_tasks['status'] == 'completed']
            pending_tasks = goal_tasks[goal_tasks['status'] != 'completed']
            
            if len(pending_tasks) > 3:
                st.markdown("""
                <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                    <h4>タスクの優先順位付けをしましょう</h4>
                    <p>未完了のタスクが多いようです。優先順位をつけて、最も重要なタスクから取り組むと良いでしょう。</p>
                    <ul>
                        <li>タスクを「重要かつ緊急」「重要だが緊急でない」などに分類する</li>
                        <li>1日に取り組むタスク数を制限して、集中する</li>
                        <li>複雑なタスクはさらに小さく分解する</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            elif len(completed_tasks) == 0:
                st.markdown("""
                <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                    <h4>最初の一歩を踏み出しましょう</h4>
                    <p>まだタスクを完了していないようです。小さなタスクから始めて、モメンタムを作りましょう。</p>
                    <ul>
                        <li>最も簡単なタスクから始める</li>
                        <li>「1分だけでもOK」のアプローチを試す</li>
                        <li>完了したらすぐに記録して、達成感を得る</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # SMART目標の要素に基づくアドバイス
        if smart_goal_data:
            smart_advice = []
            
            if not smart_goal_data.get('specific', ''):
                smart_advice.append("目標をより具体的に定義すると、達成しやすくなります。何をどれだけ達成するのか、明確にしましょう。")
            
            if not smart_goal_data.get('measurable', ''):
                smart_advice.append("進捗を測定する方法を決めると、目標への道のりが見えやすくなります。数値化できる指標を設定しましょう。")
            
            if not smart_goal_data.get('achievable', ''):
                smart_advice.append("目標が達成可能かどうか再確認しましょう。無理のない、現実的な目標設定が成功の鍵です。")
            
            if not smart_goal_data.get('relevant', ''):
                smart_advice.append("この目標があなたにとって本当に重要かどうか考えてみましょう。あなたの価値観や長期的な目標に合致していますか？")
            
            if not smart_goal_data.get('time_bound', ''):
                smart_advice.append("明確な期限を設定すると、行動に移しやすくなります。いつまでに達成するのか、期限を決めましょう。")
            
            if smart_advice:
                st.markdown("#### SMART目標の改善ポイント")
                
                for advice in smart_advice:
                    st.markdown(f"- {advice}")
        
        # 目標達成のための具体的な提案
        st.markdown("#### 目標達成のための具体的な提案")
        
        suggestions = [
            "**朝のルーティン**: 朝の10分を目標に取り組む時間として確保すると、習慣化しやすくなります。",
            "**視覚化**: 進捗状況を視覚的に記録して、達成感を高めましょう。",
            "**アカウンタビリティ**: 友人や家族に目標を共有して、定期的に報告する仕組みを作りましょう。",
            "**環境最適化**: 目標達成を妨げる環境要因を取り除き、成功しやすい環境を整えましょう。",
            "**報酬システム**: 小さな目標達成ごとに自分へのご褒美を用意して、モチベーションを維持しましょう。",
            "**習慣の連鎖**: 既存の習慣に新しい行動を連鎖させると、続けやすくなります。",
            "**最小実行単位**: 「1分だけでもOK」という超小さな目標を設定して、始めるハードルを下げましょう。"
        ]
        
        # ランダムに3つの提案を表示
        random_suggestions = random.sample(suggestions, min(3, len(suggestions)))
        
        for suggestion in random_suggestions:
            st.markdown(f"- {suggestion}")
        
        if st.button("もっと提案を見る", key="more_suggestions"):
            remaining_suggestions = [s for s in suggestions if s not in random_suggestions]
            if remaining_suggestions:
                more_random = random.sample(remaining_suggestions, min(3, len(remaining_suggestions)))
                for suggestion in more_random:
                    st.markdown(f"- {suggestion}")
            else:
                st.info("すべての提案を表示しました。")

# 成功体験タブ
def show_success_experience_tab():
    st.markdown("### 成功体験の振り返り")
    
    # 成功体験の記録と参照
    tab1, tab2 = st.tabs(["成功体験を記録", "過去の成功を振り返る"])
    
    with tab1:
        st.markdown("#### 新しい成功体験を記録")
        st.write("あなたが達成した目標や、うまくいった経験を記録しましょう。将来、似たような状況で参考にできます。")
        
        with st.form("success_experience_form"):
            success_title = st.text_input("成功体験のタイトル", placeholder="例：初めてのマラソン完走、プロジェクト納期達成など")
            success_description = st.text_area("詳細な説明", placeholder="どんな目標を達成したのか、どのような状況だったのかなど")
            success_factors = st.text_area("成功の要因", placeholder="なぜ成功できたのか、どんな工夫や努力をしたのかなど")
            success_learnings = st.text_area("学んだこと", placeholder="この経験から得た教訓や気づきなど")
            
            submit_button = st.form_submit_button("記録する")
            
            if submit_button:
                if not success_title or not success_description:
                    st.error("タイトルと詳細説明は必須です。")
                else:
                    # 成功体験データを追加
                    success_memories = load_success_memories()
                    
                    new_memory = {
                        "id": str(uuid.uuid4()),
                        "title": success_title,
                        "description": success_description,
                        "success_factors": success_factors,
                        "learnings": success_learnings,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    success_memories.append(new_memory)
                    save_success_memories(success_memories)
                    
                    # ポイント獲得
                    points_data = load_points()
                    points_data["points"] += 15
                    save_points(points_data)
                    
                    st.success("成功体験を記録しました！15ポイント獲得！")
                    st.balloons()
    
    with tab2:
        st.markdown("#### 過去の成功体験")
        st.write("過去の成功体験を振り返ることで、現在の課題にも活かせるヒントが見つかるかもしれません。")
        
        # 成功体験データの取得
        success_memories = load_success_memories()
        
        if success_memories:
            for memory in success_memories:
                with st.expander(f"{memory['title']} ({memory.get('created_at', '日付不明')})"):
                    st.markdown(f"**詳細:** {memory['description']}")
                    st.markdown(f"**成功の要因:** {memory.get('success_factors', '記録なし')}")
                    st.markdown(f"**学んだこと:** {memory.get('learnings', '記録なし')}")
                    
                    if st.button("現在の目標に活かす", key=f"apply_{memory['id']}"):
                        st.markdown("""
                        <div class="insight-box">
                            <h4>過去の成功を現在の目標に活かすには</h4>
                            <p>過去の成功体験から学んだことを、現在の目標達成に応用してみましょう：</p>
                            <ol>
                                <li>同じ成功要因を現在の目標にも取り入れる</li>
                                <li>似たような障害や課題があれば、過去の解決策を参考にする</li>
                                <li>その時の自分の強みや状態を思い出し、今も活かせるか考える</li>
                            </ol>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("まだ成功体験が記録されていません。「成功体験を記録」タブから記録を追加してください。")
        
        # ランダムなモチベーション向上メッセージ
        st.markdown("#### 成功の思い出")
        
        motivation_messages = [
            "過去の成功は、あなたの能力の証です。今の課題も必ず克服できます！",
            "困難を乗り越えてきた経験は、あなたの大切な財産です。自信を持って前進しましょう。",
            "過去のあなたができたことは、今のあなたもできます。むしろ、今はもっと成長しているはずです。",
            "すべての成功体験は、小さな一歩の積み重ねから始まりました。今日も一歩を踏み出しましょう。",
            "過去の成功を思い出し、同じ満足感をまた味わいましょう。あなたならできます！"
        ]
        
        st.markdown(f"#### 💭 {random.choice(motivation_messages)}")

# バッジの更新確認
def update_badges():
    # バッジデータの取得
    badges_data = load_badges()
    badges = badges_data["badges"]
    
    # 目標設定バッジの確認
    goals_df = load_goals()
    if not goals_df.empty and not any(badge["id"] == "first_goal" and badge["earned"] for badge in badges):
        # 最初の目標設定バッジを獲得
        for i, badge in enumerate(badges):
            if badge["id"] == "first_goal":
                badges[i]["earned"] = True
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 30
                save_points(points_data)
                
                save_badges({"badges": badges})
                break
    
    # 3つの目標設定バッジの確認
    if len(goals_df) >= 3 and not any(badge["id"] == "three_goals" and badge["earned"] for badge in badges):
        # 3つの目標設定バッジを獲得
        for i, badge in enumerate(badges):
            if badge["id"] == "three_goals":
                badges[i]["earned"] = True
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 30
                save_points(points_data)
                
                save_badges({"badges": badges})
                break
    
    # 最初の目標達成バッジの確認
    if 'status' in goals_df.columns and (goals_df['status'] == 'completed').any() and not any(badge["id"] == "first_complete" and badge["earned"] for badge in badges):
        # 最初の目標達成バッジを獲得
        for i, badge in enumerate(badges):
            if badge["id"] == "first_complete":
                badges[i]["earned"] = True
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 30
                save_points(points_data)
                
                save_badges({"badges": badges})
                break
    
    # 継続のバッジチェック
    tasks_df = load_tasks()
    if not tasks_df.empty and 'completed_at' in tasks_df.columns:
        # 完了したタスクを日付でソート
        completed_tasks = tasks_df[tasks_df['status'] == 'completed'].copy()
        
        if not completed_tasks.empty:
            completed_tasks['completed_date'] = pd.to_datetime(completed_tasks['completed_at']).dt.date
            
            # 日付ごとのタスク完了数
            daily_completions = completed_tasks.groupby('completed_date').size()
            
            # 連続した日付を確認
            consecutive_days = 0
            current_date = None
            
            for date in sorted(daily_completions.index):
                if current_date is None:
                    consecutive_days = 1
                elif (date - current_date).days == 1:
                    consecutive_days += 1
                else:
                    consecutive_days = 1
                
                current_date = date
                
                if consecutive_days >= 7 and not any(badge["id"] == "consistent" and badge["earned"] for badge in badges):
                    # 継続の達人バッジを獲得
                    for i, badge in enumerate(badges):
                        if badge["id"] == "consistent":
                            badges[i]["earned"] = True
                            
                            # ポイント獲得
                            points_data = load_points()
                            points_data["points"] += 30
                            save_points(points_data)
                            
                            save_badges({"badges": badges})
                            break
                    
                    break
    
    save_badges({"badges": badges})

# 報酬バッジの確認
def check_reward_badge():
    # バッジデータの取得
    badges_data = load_badges()
    badges = badges_data["badges"]
    
    # 報酬設定バッジの確認
    rewards = load_rewards()
    
    if len(rewards) >= 3 and not any(badge["id"] == "reward_planner" and badge["earned"] for badge in badges):
        # 報酬プランナーバッジを獲得
        for i, badge in enumerate(badges):
            if badge["id"] == "reward_planner":
                badges[i]["earned"] = True
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 30
                save_points(points_data)
                
                save_badges({"badges": badges})
                return True
    
    return False

# 問題解決者バッジの確認
def check_problem_solver_badge(problems_data):
    # バッジデータの取得
    badges_data = load_badges()
    badges = badges_data["badges"]
    
    # 問題と対策のカウント
    problem_count = sum(len(item.get("problems", [])) for item in problems_data)
    
    if problem_count >= 3 and not any(badge["id"] == "problem_solver" and badge["earned"] for badge in badges):
        # 問題解決者バッジを獲得
        for i, badge in enumerate(badges):
            if badge["id"] == "problem_solver":
                badges[i]["earned"] = True
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 30
                save_points(points_data)
                
                save_badges({"badges": badges})
                return True
    
    return False

# マイクロタスク生成関数
# マイクロタスク生成関数
def generate_micro_tasks(goals_df, tasks_df=None):
    micro_tasks = []
    
    # アクティブな目標を取得
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        return micro_tasks
    
    # 各目標から1つずつマイクロタスクを生成
    for _, goal in active_goals.iterrows():
        goal_name = goal['name']
        goal_id = goal['id']
        
        # 未完了のタスクを取得（tasks_dfが提供されている場合）
        if tasks_df is not None and not tasks_df.empty:
            incomplete_tasks = tasks_df[(tasks_df['goal_id'] == goal_id) & (tasks_df['status'] != 'completed')]
            
            if not incomplete_tasks.empty:
                # 未完了タスクから1つのマイクロタスクを作成
                task = incomplete_tasks.iloc[0]
                micro_tasks.append({
                    'goal_name': goal_name,
                    'description': f"1分だけ {task['description']} に取り組む"
                })
                continue
        
        # 汎用的なマイクロタスクの提案
        suggestions = [
            f"{goal_name}について1分間考える",
            f"{goal_name}に関連する情報を1つ読む",
            f"{goal_name}の最初の一歩を紙に書き出す",
            f"{goal_name}に関係する物を整理する",
            f"{goal_name}に関する画像をイメージする",
            f"{goal_name}について友人や家族と簡単に話す",
            f"{goal_name}のための小さな準備をする",
            f"{goal_name}を進めるための障害を1つ特定する",
            f"{goal_name}に関する肯定的な言葉を唱える"
        ]
        
        micro_tasks.append({
            'goal_name': goal_name,
            'description': random.choice(suggestions)
        })
    
    # 最大5つのマイクロタスクを選択
    if len(micro_tasks) > 5:
        micro_tasks = random.sample(micro_tasks, 5)
    
    return micro_tasks



# 問題と対策のページ関数
def show_problems_and_solutions():
    st.markdown('<h2 class="sub-header">🔍 問題と対策</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    problems_data = load_problems()
    
    if goals_df.empty:
        st.info("まだ目標が設定されていません。「SMART目標設定」から最初の目標を設定しましょう！")
        return
    
    st.markdown("""
    目標達成の障害となる問題を事前に特定し、対策を立てておくことで、
    困難に直面したときでも前進し続けることができます。
    """)
    
    # 目標の選択
    active_goals = goals_df[goals_df['status'] == 'active'] if 'status' in goals_df.columns else goals_df
    
    if active_goals.empty:
        st.info("アクティブな目標がありません。新しい目標を設定するか、目標のステータスを変更してください。")
        return
    
    goal_options = active_goals['name'].tolist()
    selected_goal = st.selectbox("目標を選択", goal_options)
    
    # 選択された目標のID取得
    goal_id = active_goals[active_goals['name'] == selected_goal]['id'].iloc[0]
    
    # 既存の問題と対策を取得
    goal_problems = next((item for item in problems_data if item.get("goal_id") == goal_id), None)
    
    problems = goal_problems.get("problems", []) if goal_problems else []
    plans = goal_problems.get("plans", []) if goal_problems else []
    
    # 新しい問題と対策の追加
    with st.form("problems_solutions_form"):
        st.markdown("### 問題と対策を追加")
        
        st.markdown("""
        #### 問題のリストアップ
        目標達成の障害となりそうな問題や課題をリストアップしましょう。
        """)
        
        obstacles = st.text_area("目標達成の障害となりそうな問題", 
                               value="\n".join(problems) if problems else "",
                               placeholder="各行に1つの問題を書いてください\n例：\n忙しくて時間がない\nモチベーションが続かない\n周囲のサポートがない",
                               height=150)
        
        st.markdown("""
        #### 「もしも」プラン
        「もし〇〇になったら、こうする」という具体的な対策プランを考えましょう。
        """)
        
        contingency_plans = st.text_area("「もし〇〇になったら、こうする」という対策プラン", 
                                       value="\n".join(plans) if plans else "",
                                       placeholder="各行に1つの対策を書いてください\n例：\nもし忙しくて時間がなければ、朝15分早く起きて取り組む\nもしモチベーションが下がったら、目標達成後の自分をイメージする\nもし周囲のサポートがなければ、オンラインコミュニティに参加する",
                                       height=150)
        
        submit_button = st.form_submit_button("保存する")
        
        if submit_button:
            # 入力を処理
            problems_list = [p.strip() for p in obstacles.split("\n") if p.strip()]
            plans_list = [p.strip() for p in contingency_plans.split("\n") if p.strip()]
            
            if not problems_list:
                st.error("少なくとも1つの問題を入力してください。")
            elif not plans_list:
                st.error("少なくとも1つの対策プランを入力してください。")
            else:
                # 問題と対策を保存
                if goal_problems:
                    # 既存のデータを更新
                    for i, item in enumerate(problems_data):
                        if item.get("goal_id") == goal_id:
                            problems_data[i]["problems"] = problems_list
                            problems_data[i]["plans"] = plans_list
                            problems_data[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
                else:
                    # 新しいデータを追加
                    problems_data.append({
                        "goal_id": goal_id,
                        "goal_name": selected_goal,
                        "problems": problems_list,
                        "plans": plans_list,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    })
                
                save_problems(problems_data)
                
                # ポイント獲得
                points_data = load_points()
                points_data["points"] += 5
                save_points(points_data)
                
                # 問題解決者バッジをチェック
                check_problem_solver_badge(problems_data)
                
                st.success("問題と対策を保存しました！5ポイント獲得！")
    
    # 保存された問題と対策の表示
    if goal_problems:
        st.markdown("### 対策リスト")
        
        problems = goal_problems.get("problems", [])
        plans = goal_problems.get("plans", [])
        
        for i, (problem, plan) in enumerate(zip(problems, plans) if len(problems) == len(plans) else zip(problems, plans + [''] * (len(problems) - len(plans)))):
            st.markdown(f"""
            <div class="problem-item">
                <h4>問題: {problem}</h4>
                <p><strong>対策:</strong> {plan if i < len(plans) else '対策が設定されていません'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # もし問題と対策の数が合わない場合の処理
        if len(problems) < len(plans):
            for plan in plans[len(problems):]:
                st.markdown(f"""
                <div class="problem-item">
                    <h4>問題: 未設定</h4>
                    <p><strong>対策:</strong> {plan}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("まだ問題と対策が設定されていません。上のフォームから追加してください。")
    
    # 一般的な問題解決のヒント
    with st.expander("問題解決のヒント", expanded=False):
        st.markdown("""
        ### 効果的な問題解決のヒント
        
        1. **具体的に定義する**: 問題を具体的に定義すると、解決策も見つけやすくなります。
        2. **根本原因を探る**: 表面的な問題だけでなく、根本的な原因を特定しましょう。
        3. **複数の解決策を考える**: 1つの解決策にこだわらず、複数の選択肢を検討しましょう。
        4. **最悪のシナリオを想定する**: 最悪の事態を想定し、そのための対策も考えておきましょう。
        5. **早めに対処する**: 問題が大きくなる前に、早めに対処するのが効果的です。
        6. **小さなステップに分ける**: 大きな問題は、小さな解決可能な問題に分割しましょう。
        7. **失敗から学ぶ**: 失敗は学びの機会です。次の解決策に活かしましょう。
        """)

# 成功体験の記録ページ関数
def show_success_experiences():
    st.markdown('<h2 class="sub-header">🌟 成功体験の記録</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    過去の成功体験を記録し、振り返ることで、自信を高め、
    将来の目標達成に役立てることができます。
    """)
    
    # 成功体験の記録と参照
    tab1, tab2 = st.tabs(["新しい成功体験を記録", "過去の成功体験を振り返る"])
    
    with tab1:
        st.markdown("### 新しい成功体験を記録")
        st.write("あなたが達成した目標や、うまくいった経験を記録しましょう。将来、似たような状況で参考にできます。")
        
        with st.form("success_experience_form"):
            success_title = st.text_input("成功体験のタイトル", placeholder="例：初めてのマラソン完走、プロジェクト納期達成など")
            success_description = st.text_area("詳細な説明", placeholder="どんな目標を達成したのか、どのような状況だったのかなど")
            success_factors = st.text_area("成功の要因", placeholder="なぜ成功できたのか、どんな工夫や努力をしたのかなど")
            success_learnings = st.text_area("学んだこと", placeholder="この経験から得た教訓や気づきなど")
            
            submit_button = st.form_submit_button("記録する")
            
            if submit_button:
                if not success_title or not success_description:
                    st.error("タイトルと詳細説明は必須です。")
                else:
                    # 成功体験データを追加
                    success_memories = load_success_memories()
                    
                    new_memory = {
                        "id": str(uuid.uuid4()),
                        "title": success_title,
                        "description": success_description,
                        "success_factors": success_factors,
                        "learnings": success_learnings,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    success_memories.append(new_memory)
                    save_success_memories(success_memories)
                    
                    # ポイント獲得
                    points_data = load_points()
                    points_data["points"] += 15
                    save_points(points_data)
                    
                    st.success("成功体験を記録しました！15ポイント獲得！")
                    st.balloons()
    
    with tab2:
        st.markdown("### 過去の成功体験")
        st.write("過去の成功体験を振り返ることで、現在の課題にも活かせるヒントが見つかるかもしれません。")
        
        # 成功体験データの取得
        success_memories = load_success_memories()
        
        if success_memories:
            for memory in success_memories:
                with st.expander(f"{memory['title']} ({memory.get('created_at', '日付不明')})"):
                    st.markdown(f"**詳細:** {memory['description']}")
                    st.markdown(f"**成功の要因:** {memory.get('success_factors', '記録なし')}")
                    st.markdown(f"**学んだこと:** {memory.get('learnings', '記録なし')}")
                    
                    if st.button("現在の目標に活かす", key=f"apply_{memory['id']}"):
                        st.markdown("""
                        <div class="insight-box">
                            <h4>過去の成功を現在の目標に活かすには</h4>
                            <p>過去の成功体験から学んだことを、現在の目標達成に応用してみましょう：</p>
                            <ol>
                                <li>同じ成功要因を現在の目標にも取り入れる</li>
                                <li>似たような障害や課題があれば、過去の解決策を参考にする</li>
                                <li>その時の自分の強みや状態を思い出し、今も活かせるか考える</li>
                            </ol>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("まだ成功体験が記録されていません。「新しい成功体験を記録」タブから記録を追加してください。")
        
        # 成功の言葉
        success_quotes = [
            "「成功とは、失敗から失敗へと情熱を失わずに進むことである」- ウィンストン・チャーチル",
            "「成功の秘訣は、決して諦めないことだ」- アルバート・アインシュタイン",
            "「小さな成功の積み重ねが、大きな自信につながる」- 不明",
            "「成功とは、小さな努力を毎日積み重ねることである」- ロバート・コリアー",
            "「成功するまで成功しなかったことはない」- 不明"
        ]
        
        st.markdown(f"### 📝 {random.choice(success_quotes)}")            


# ページ内ナビゲーションに進捗振り返りオプションを追加
# メインの選択メニューに関数を対応させる
if page == "目標ダッシュボード":
    show_goal_dashboard()
elif page == "SMART目標設定":
    show_smart_goal_setting()
elif page == "タスク管理":
    show_task_management()
elif page == "報酬設定":
    show_reward_settings()
elif page == "問題と対策":
    show_problems_and_solutions()
elif page == "成功体験の記録":
    show_success_experiences()
elif page == "進捗振り返り":
    show_progress_review()

if __name__ == "__main__":
    # バッジの更新確認
    update_badges()    