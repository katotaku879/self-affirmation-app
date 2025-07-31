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
import calendar
from PIL import Image
import io
import base64

# ページの設定
st.set_page_config(
    page_title="モチベーション管理 - 自己肯定アプリ",
    page_icon="💪",
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
    .quote-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
        text-align: center;
    }
    .streak-card {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #2196F3;
    }
    .message-card {
        background-color: #E0F7FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #00BCD4;
    }
    .achievement-card {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #9C27B0;
    }
    .calendar-day {
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin: 2px;
        border-radius: 20px;
        display: inline-block;
    }
    .calendar-day-active {
        background-color: #4CAF50;
        color: white;
    }
    .calendar-day-inactive {
        background-color: #F5F5F5;
        color: #9E9E9E;
    }
    .calendar-day-today {
        border: 2px solid #2196F3;
        line-height: 36px;
    }
    .insight-box {
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
    }
    .badge-container {
        text-align: center;
        padding: 10px;
        margin: 10px 0;
    }
    .badge-item {
        background-color: #F3E5F5;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .mini-challenge {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #FFC107;
    }
    .stat-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .calendar-wrapper {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .calendar-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        grid-gap: 5px;
    }
    .weekday-label {
        text-align: center;
        font-weight: bold;
        padding: 5px 0;
        font-size: 0.9rem;
    }
    .calendar-cell {
        aspect-ratio: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        margin: 0 auto;
        font-size: 0.9rem;
    }
    .calendar-cell-active {
        background-color: #4CAF50;
        color: white;
    }
    .calendar-cell-today {
        border: 2px solid #2196F3;
    }
    .calendar-cell-empty {
        background-color: #F5F5F5;
        color: #9E9E9E;
    }
</style>
""", unsafe_allow_html=True)

# データファイルのパス
ACTIVITY_LOG_FILE = "activity_log.json"
CHALLENGE_FILE = "challenges.json"
TITLE_FILE = "titles.json"
MESSAGES_FILE = "motivation_messages.json"
ACHIEVEMENTS_FILE = "motivation_achievements.json"
DAILY_QUOTE_FILE = "daily_quotes.json"

# データファイルの初期化
def initialize_motivation_files():
    if not os.path.exists(ACTIVITY_LOG_FILE):
        with open(ACTIVITY_LOG_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(CHALLENGE_FILE):
        default_challenges = [
            {
                "id": str(uuid.uuid4()),
                "name": "7日継続チャレンジ",
                "description": "7日間連続でアプリを開く",
                "target_days": 7,
                "start_date": None,
                "current_streak": 0,
                "completed": False,
                "reward_points": 50
            },
            {
                "id": str(uuid.uuid4()),
                "name": "30日継続チャレンジ",
                "description": "30日間連続でアプリを開く",
                "target_days": 30,
                "start_date": None,
                "current_streak": 0,
                "completed": False,
                "reward_points": 200
            }
        ]
        with open(CHALLENGE_FILE, "w") as f:
            json.dump(default_challenges, f)
    
    if not os.path.exists(TITLE_FILE):
        default_titles = [
            {"id": "beginner", "name": "初心者", "description": "はじめてアプリを使用", "requirement": 1, "image": "🌱", "earned": False},
            {"id": "regular", "name": "定期訪問者", "description": "10日間アプリを使用", "requirement": 10, "image": "🌿", "earned": False},
            {"id": "devoted", "name": "熱心な実践者", "description": "30日間アプリを使用", "requirement": 30, "image": "🌳", "earned": False},
            {"id": "master", "name": "継続マスター", "description": "50日間アプリを使用", "requirement": 50, "image": "🌟", "earned": False},
            {"id": "guru", "name": "自己肯定の達人", "description": "100日間アプリを使用", "requirement": 100, "image": "👑", "earned": False}
        ]
        with open(TITLE_FILE, "w") as f:
            json.dump({"titles": default_titles}, f)
    
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(ACHIEVEMENTS_FILE):
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(DAILY_QUOTE_FILE):
        default_quotes = [
            {"quote": "今日のあなたは、昨日のあなたが憧れた姿です。", "author": "不明"},
            {"quote": "継続は力なり。毎日の小さな一歩が、大きな変化を生み出します。", "author": "不明"},
            {"quote": "ゴールを見失ったとき、プロセスを信じましょう。", "author": "不明"},
            {"quote": "完璧を目指すよりも、前進し続けることが大切です。", "author": "不明"},
            {"quote": "自分を信じれば、何でもできる。ただ、努力は必要です。", "author": "不明"},
            {"quote": "一日一日が成長の機会です。", "author": "不明"},
            {"quote": "今日一日、あなたがどんな選択をするかで未来が変わります。", "author": "不明"},
            {"quote": "自分を批判するよりも、自分を励ましましょう。", "author": "不明"},
            {"quote": "小さな進歩も、進歩です。自分の成長を祝いましょう。", "author": "不明"},
            {"quote": "一度の失敗は成功への一歩です。諦めないでください。", "author": "不明"}
        ]
        with open(DAILY_QUOTE_FILE, "w") as f:
            json.dump(default_quotes, f)

# 初期化を実行
initialize_motivation_files()

# データ読み込み関数
def load_activity_log():
    with open(ACTIVITY_LOG_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["date", "activity_type", "notes", "points"])

def load_challenges():
    with open(CHALLENGE_FILE, "r") as f:
        return json.load(f)

def load_titles():
    with open(TITLE_FILE, "r") as f:
        return json.load(f)

def load_messages():
    with open(MESSAGES_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "content", "created_date", "target_date", "opened"])

def load_achievements():
    with open(ACHIEVEMENTS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "name", "description", "date", "points"])

def load_daily_quotes():
    with open(DAILY_QUOTE_FILE, "r") as f:
        return json.load(f)

# データ保存関数
def save_activity_log(df):
    with open(ACTIVITY_LOG_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_challenges(challenges):
    with open(CHALLENGE_FILE, "w") as f:
        json.dump(challenges, f)

def save_titles(titles_data):
    with open(TITLE_FILE, "w") as f:
        json.dump(titles_data, f)

def save_messages(df):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_achievements(df):
    with open(ACHIEVEMENTS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

# ポイント関数（04_goal_achievementと共有）
def get_points():
    try:
        with open("points.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルが存在しない、または読み込めない場合は新規作成
        points_data = {"points": 0}
        with open("points.json", "w") as f:
            json.dump(points_data, f)
        return points_data

def save_points(points_data):
    with open("points.json", "w") as f:
        json.dump(points_data, f)

def add_points(amount, reason="活動"):
    points_data = get_points()
    points_data["points"] += amount
    save_points(points_data)
    
    # アクティビティログに記録
    activity_log = load_activity_log()
    new_activity = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "activity_type": "ポイント獲得",
        "notes": reason,
        "points": amount
    }
    
    if activity_log.empty:
        activity_log = pd.DataFrame([new_activity])
    else:
        activity_log = pd.concat([activity_log, pd.DataFrame([new_activity])], ignore_index=True)
    
    save_activity_log(activity_log)
    
    return points_data["points"]

# 今日のアクティビティを記録
def record_daily_activity():
    today = date.today().strftime("%Y-%m-%d")
    activity_log = load_activity_log()
    
    # 今日の記録があるか確認
    today_login = activity_log[(activity_log['date'] == today) & (activity_log['activity_type'] == "ログイン")]
    
    if today_login.empty:
        # 今日初めてのログイン
        new_activity = {
            "date": today,
            "activity_type": "ログイン",
            "notes": "アプリを開いた",
            "points": 5
        }
        
        if activity_log.empty:
            activity_log = pd.DataFrame([new_activity])
        else:
            activity_log = pd.concat([activity_log, pd.DataFrame([new_activity])], ignore_index=True)
        
        save_activity_log(activity_log)
        
        # ポイント追加
        add_points(5, "毎日のログイン")
        
        # チャレンジ更新
        update_challenges()
        
        # 称号更新
        update_titles()
        
        return True
    
    return False

# チャレンジの更新
def update_challenges():
    today = date.today()
    challenges = load_challenges()
    activity_log = load_activity_log()
    
    # アクティビティログから日付のリスト作成（昇順）
    if not activity_log.empty and 'date' in activity_log.columns:
        activity_dates = pd.to_datetime(activity_log['date']).dt.date.unique()
        activity_dates = sorted(activity_dates)
    else:
        activity_dates = []
    
    for i, challenge in enumerate(challenges):
        # チャレンジがまだ開始されていない場合、今日から開始
        if challenge["start_date"] is None and not challenge["completed"]:
            challenges[i]["start_date"] = today.strftime("%Y-%m-%d")
            challenges[i]["current_streak"] = 1
        elif not challenge["completed"]:
            # 開始日から今日までの連続日数を計算
            start_date = datetime.strptime(challenge["start_date"], "%Y-%m-%d").date()
            
            # 連続日数を計算
            streak = 0
            expected_date = start_date
            
            for activity_date in activity_dates:
                if activity_date == expected_date:
                    streak += 1
                    expected_date = activity_date + timedelta(days=1)
                elif activity_date > expected_date:
                    # 連続が途切れた
                    break
            
            # 今日のログインがあれば+1
            if today in activity_dates:
                if expected_date == today:
                    streak += 1
            
            challenges[i]["current_streak"] = streak
            
            # チャレンジ達成確認
            if streak >= challenge["target_days"]:
                challenges[i]["completed"] = True
                
                # ポイント獲得
                add_points(challenge["reward_points"], f"チャレンジ達成: {challenge['name']}")
                
                # 実績に追加
                add_achievement(challenge["name"], challenge["description"], challenge["reward_points"])
    
    save_challenges(challenges)

# 称号の更新
def update_titles():
    activity_log = load_activity_log()
    titles_data = load_titles()
    titles = titles_data["titles"]
    
    # アクティビティログからユニークな日付をカウント
    if not activity_log.empty and 'date' in activity_log.columns:
        unique_days = activity_log['date'].nunique()
    else:
        unique_days = 0
    
    for i, title in enumerate(titles):
        if not title["earned"] and unique_days >= title["requirement"]:
            # 称号獲得
            titles[i]["earned"] = True
            
            # ポイント獲得
            add_points(title["requirement"] * 2, f"称号獲得: {title['name']}")
            
            # 実績に追加
            add_achievement(f"称号「{title['name']}」を獲得", title["description"], title["requirement"] * 2)
    
    titles_data["titles"] = titles
    save_titles(titles_data)

# 実績の追加
def add_achievement(name, description, points):
    achievements = load_achievements()
    
    new_achievement = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "date": date.today().strftime("%Y-%m-%d"),
        "points": points
    }
    
    if achievements.empty:
        achievements = pd.DataFrame([new_achievement])
    else:
        achievements = pd.concat([achievements, pd.DataFrame([new_achievement])], ignore_index=True)
    
    save_achievements(achievements)

# マルチページアプリのタイトル
st.markdown('<h1 class="main-header">💪 モチベーション管理</h1>', unsafe_allow_html=True)

# 毎日のログイン記録
first_login_today = record_daily_activity()

# サイドバーにポイント表示
points_data = get_points()
st.sidebar.markdown(f"### 📊 現在のポイント: {points_data['points']}ポイント")

# ページナビゲーション
page = st.sidebar.radio(
    "モチベーション管理メニュー",
    ["モチベーションダッシュボード", "努力カレンダー", "継続チャレンジ", "未来へのメッセージ", "実績と称号"],
)

# 毎日のポジティブな一言（初回ログイン時のみ表示）
if first_login_today:
    quotes = load_daily_quotes()
    daily_quote = random.choice(quotes)
    
    st.markdown(f"""
    <div class="quote-card">
        <h2>今日のポジティブな一言</h2>
        <p style="font-size: 1.5rem;">"{daily_quote['quote']}"</p>
        <p>- {daily_quote['author']}</p>
    </div>
    """, unsafe_allow_html=True)

# モチベーションダッシュボードページ
def show_motivation_dashboard():
    st.markdown('<h2 class="sub-header">📊 モチベーションダッシュボード</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    activity_log = load_activity_log()
    challenges = load_challenges()
    titles_data = load_titles()
    messages = load_messages()
    achievements = load_achievements()
    
    # 過去30日間の活動グラフ
    st.markdown("### 過去30日間の活動状況")
    
    if not activity_log.empty and 'date' in activity_log.columns:
        # 日付を変換
        activity_log['date'] = pd.to_datetime(activity_log['date']).dt.date
        
        # 過去30日間の日付範囲を作成
        today = date.today()
        date_range = [today - timedelta(days=x) for x in range(29, -1, -1)]
        
        # 各日のアクティビティ数をカウント
        activity_counts = []
        
        for single_date in date_range:
            day_activity = activity_log[activity_log['date'] == single_date]
            activity_counts.append(len(day_activity))
        
        # グラフデータの作成
        graph_data = pd.DataFrame({
            'date': date_range,
            'activity_count': activity_counts
        })
        
        # グラフの描画
        fig = px.bar(
            graph_data,
            x='date',
            y='activity_count',
            title="日別のアクティビティ数",
            labels={'date': '日付', 'activity_count': 'アクティビティ数'},
            color='activity_count',
            color_continuous_scale=["lightblue", "blue"]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 累計ポイントの折れ線グラフを表示
        if 'points' in activity_log.columns:
            # 日付ごとの累計ポイントを計算
            activity_log = activity_log.sort_values('date')
            activity_log['cumulative_points'] = activity_log['points'].cumsum()
            
            # 最新のデータを30日分取得
            recent_activity = activity_log.drop_duplicates('date', keep='last').tail(30)
            
            if not recent_activity.empty:
                fig_points = px.line(
                    recent_activity,
                    x='date',
                    y='cumulative_points',
                    title="累計ポイントの推移",
                    labels={'date': '日付', 'cumulative_points': '累計ポイント'},
                    markers=True
                )
                st.plotly_chart(fig_points, use_container_width=True)
    
    # 統計情報
    st.markdown("### 統計情報")
    
    col1, col2, col3 = st.columns(3)
    
    # 継続日数
    current_streak = calculate_current_streak(activity_log)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <p>現在の継続日数</p>
            <p class="stat-value">{}</p>
            <p>日</p>
        </div>
        """.format(current_streak), unsafe_allow_html=True)
    
    # 最長継続日数
    max_streak = calculate_max_streak(activity_log)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <p>最長継続記録</p>
            <p class="stat-value">{}</p>
            <p>日</p>
        </div>
        """.format(max_streak), unsafe_allow_html=True)
    
    # 総活動ポイント
    total_points = points_data["points"]
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <p>総獲得ポイント</p>
            <p class="stat-value">{}</p>
            <p>ポイント</p>
        </div>
        """.format(total_points), unsafe_allow_html=True)
    
    # AIフィードバック
    st.markdown("### 先週の振り返り")
    
    # 先週のデータを抽出
    if not activity_log.empty and 'date' in activity_log.columns:
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        last_week_activity = activity_log[(activity_log['date'] >= week_ago) & (activity_log['date'] < today)]
        
        if not last_week_activity.empty:
            # アクティビティの分析
            activity_types = last_week_activity['activity_type'].value_counts()
            total_points_week = last_week_activity['points'].sum()
            active_days = last_week_activity['date'].nunique()
            
            # フィードバックを生成
            feedback = generate_weekly_feedback(activity_types, total_points_week, active_days)
            
            st.markdown(f"""
            <div class="insight-box">
                <h4>先週の振り返り</h4>
                {feedback}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("先週のデータがまだありません。引き続きアプリを使って記録を増やしましょう！")
    
    # 過去の成功を振り返る
    if not achievements.empty:
        st.markdown("### 過去の成功体験")
        
        # ランダムに過去の実績を選択
        if len(achievements) > 0:
            random_achievement = achievements.sample(1).iloc[0]
            
            st.markdown(f"""
            <div class="achievement-card">
                <h4>🏆 {random_achievement['name']}</h4>
                <p>{random_achievement['description']}</p>
                <p>達成日: {random_achievement['date']}</p>
                <p>獲得ポイント: {random_achievement['points']}pt</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="insight-box">
                <h4>AIからのメッセージ</h4>
                <p>あなたは過去にこの素晴らしい成果を達成しました！この成功体験を思い出し、現在の目標に向けても同じように頑張りましょう。</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 未来の自分へのメッセージをランダム表示
    if not messages.empty and 'opened' in messages.columns:
        opened_messages = messages[messages['opened'] == True]
        
        if not opened_messages.empty:
            random_message = opened_messages.sample(1).iloc[0]
            
            st.markdown("### 過去の自分からのメッセージ")
            
            st.markdown(f"""
            <div class="message-card">
                <h4>📩 {random_message['created_date']}の自分からのメッセージ</h4>
                <p>"{random_message['content']}"</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 最低限の行動提案
    st.markdown("### 今日の最低限の行動")
    
    minimum_actions = [
        "今日は5分だけでも、目標に向けた小さな一歩を踏み出しましょう。",
        "たった1つのタスクだけでも完了させれば、今日は成功です。",
        "完璧を目指さず、少しでも進められれば良しとしましょう。",
        "今日の体調や状況に合わせて、無理のない範囲で取り組みましょう。",
        "今までの努力を無駄にしないために、習慣を維持する小さな行動を選びましょう。"
    ]
    
    st.markdown(f"""
    <div class="insight-box">
        <h4>今日のアドバイス</h4>
        <p>{random.choice(minimum_actions)}</p>
        <p>小さな一歩の積み重ねが、大きな変化を生み出します。</p>
    </div>
    """, unsafe_allow_html=True)

# 努力カレンダーページ
def show_effort_calendar():
    st.markdown('<h2 class="sub-header">📅 努力カレンダー</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    activity_log = load_activity_log()
    
    # アクティブな日付のリスト作成
    active_dates = []
    if not activity_log.empty and 'date' in activity_log.columns:
        activity_log['date'] = pd.to_datetime(activity_log['date'])
        active_dates = activity_log['date'].dt.strftime('%Y-%m-%d').unique()
    
    # 月を選択とカレンダー表示を同じ行に
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 月を選択
        today = date.today()
        months = []
        for i in range(6):
            month_date = today.replace(day=1) - timedelta(days=30*i)
            months.append((month_date.year, month_date.month))
        
        month_options = [f"{year}年{month}月" for year, month in months]
        selected_month_str = st.selectbox("表示する月", month_options)
        
        selected_year = int(selected_month_str.split('年')[0])
        selected_month = int(selected_month_str.split('年')[1].split('月')[0])
    
    # カレンダー部分をHTMLで直接構築
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # HTMLカレンダーの構築
    calendar_html = f"""
    <div class="calendar-wrapper">
        <div class="calendar-title">{selected_year}年{selected_month}月</div>
        <div class="calendar-grid">
            <div class="weekday-label">月</div>
            <div class="weekday-label">火</div>
            <div class="weekday-label">水</div>
            <div class="weekday-label">木</div>
            <div class="weekday-label">金</div>
            <div class="weekday-label">土</div>
            <div class="weekday-label">日</div>
    """
    
    for week in cal:
        for day in week:
            if day == 0:
                # 月に含まれない日
                calendar_html += '<div class="calendar-cell"></div>'
            else:
                date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                is_today = (date(selected_year, selected_month, day) == date.today())
                is_active = date_str in active_dates
                
                cell_class = "calendar-cell"
                if is_active:
                    cell_class += " calendar-cell-active"
                else:
                    cell_class += " calendar-cell-empty"
                
                if is_today:
                    cell_class += " calendar-cell-today"
                
                calendar_html += f'<div class="{cell_class}">{day}</div>'
    
    calendar_html += """
        </div>
    </div>
    """
    
    with col2:
        st.markdown(calendar_html, unsafe_allow_html=True)
    
    # 月間活動統計
    st.markdown("### 月間活動統計")
    
    # 表示を3列に分けて横に並べる
    stat_cols = st.columns(3)
    
    # 選択した月のデータを抽出
    if not activity_log.empty:
        month_activity = activity_log[(activity_log['date'].dt.year == selected_year) & 
                                     (activity_log['date'].dt.month == selected_month)]
        
        if not month_activity.empty:
            # 活動日数
            active_days_count = month_activity['date'].dt.date.nunique()
            
            # 月の日数
            _, days_in_month = calendar.monthrange(selected_year, selected_month)
            
            # 活動率
            activity_rate = (active_days_count / days_in_month) * 100
            
            with stat_cols[0]:
                st.markdown(f"""
                <div class="stat-card">
                    <p>活動日数</p>
                    <p class="stat-value">{active_days_count}</p>
                    <p>/ {days_in_month}日</p>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[1]:
                st.markdown(f"""
                <div class="stat-card">
                    <p>活動率</p>
                    <p class="stat-value">{activity_rate:.1f}%</p>
                    <p>の日にアクティブ</p>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[2]:
                if 'points' in month_activity.columns:
                    total_points = month_activity['points'].sum()
                    st.markdown(f"""
                    <div class="stat-card">
                        <p>獲得ポイント</p>
                        <p class="stat-value">{total_points}</p>
                        <p>ポイント</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # カレンダーの活動グラフ
            activity_by_date = month_activity.groupby(month_activity['date'].dt.date).size().reset_index()
            activity_by_date.columns = ['date', 'count']
            
            fig = px.bar(
                activity_by_date,
                x='date',
                y='count',
                title=f"{selected_year}年{selected_month}月の活動分布",
                labels={'date': '日付', 'count': 'アクティビティ数'}
            )
            fig.update_layout(height=300)  # グラフの高さを小さくする
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"{selected_year}年{selected_month}月のデータがありません。")
    
    # 今後の目標設定
    st.markdown("### 来月の活動目標")
    
    with st.form("monthly_goal_form"):
        target_days = st.slider("来月の活動目標日数", 1, 31, 20)
        strategy = st.text_area("目標達成のための戦略", placeholder="例：毎朝アプリを開く習慣をつける、リマインダーを設定する、など")
        
        submit_button = st.form_submit_button("目標を設定")
        
        if submit_button:
            st.success(f"来月の活動目標を{target_days}日に設定しました！")
            st.balloons()
            
            # ここで目標データを保存する処理を追加（実装例では省略）
            # 実際の実装では、目標データを保存するロジックを追加

# 継続チャレンジページ
def show_challenge_tracker():
    st.markdown('<h2 class="sub-header">🏆 継続チャレンジ</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    challenges = load_challenges()
    activity_log = load_activity_log()
    
    # 現在のチャレンジ
    st.markdown("### 進行中のチャレンジ")
    
    active_challenges = [c for c in challenges if not c["completed"] and c["start_date"] is not None]
    
    if active_challenges:
        for challenge in active_challenges:
            progress_percent = min(100, (challenge["current_streak"] / challenge["target_days"]) * 100)
            
            st.markdown(f"""
            <div class="streak-card">
                <h3>{challenge["name"]}</h3>
                <p>{challenge["description"]}</p>
                <p>目標日数: {challenge["target_days"]}日</p>
                <p>現在の連続日数: {challenge["current_streak"]}日</p>
                <p>達成報酬: {challenge["reward_points"]}ポイント</p>
                <div style="margin-top: 10px; margin-bottom: 10px;">
                    <div style="background-color: #E0E0E0; border-radius: 5px; height: 10px; width: 100%;">
                        <div style="background-color: #4CAF50; border-radius: 5px; height: 10px; width: {progress_percent}%;"></div>
                    </div>
                </div>
                <p>進捗: {progress_percent:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("現在進行中のチャレンジはありません。新しいチャレンジを開始しましょう！")
    
    # 完了したチャレンジ
    completed_challenges = [c for c in challenges if c["completed"]]
    
    if completed_challenges:
        st.markdown("### 達成済みのチャレンジ")
        
        for challenge in completed_challenges:
            st.markdown(f"""
            <div class="streak-card" style="background-color: #DCEDC8;">
                <h3>✅ {challenge["name"]}</h3>
                <p>{challenge["description"]}</p>
                <p>目標日数: {challenge["target_days"]}日</p>
                <p>獲得ポイント: {challenge["reward_points"]}ポイント</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 新しいチャレンジの作成
    st.markdown("### 新しいチャレンジを作成")
    
    with st.form("new_challenge_form"):
        challenge_name = st.text_input("チャレンジ名", placeholder="例：朝活30日チャレンジ")
        challenge_description = st.text_area("詳細", placeholder="例：30日間連続で朝6時に起きる")
        target_days = st.slider("目標日数", 1, 100, 30)
        reward_points = st.number_input("達成報酬ポイント", min_value=10, max_value=500, value=target_days * 5)
        
        submit_button = st.form_submit_button("チャレンジを作成")
        
        if submit_button:
            if not challenge_name:
                st.error("チャレンジ名を入力してください。")
            else:
                # チャレンジを追加
                new_challenge = {
                    "id": str(uuid.uuid4()),
                    "name": challenge_name,
                    "description": challenge_description,
                    "target_days": target_days,
                    "start_date": date.today().strftime("%Y-%m-%d"),
                    "current_streak": 1,  # 今日からスタート
                    "completed": False,
                    "reward_points": reward_points
                }
                
                challenges.append(new_challenge)
                save_challenges(challenges)
                
                st.success("新しいチャレンジを作成しました！")
                st.balloons()
                st.rerun()
    
    # チャレンジのヒント
    st.markdown("### チャレンジを成功させるヒント")
    
    st.markdown("""
    1. **無理のない目標を設定する**: 達成可能なチャレンジから始めましょう。
    2. **毎日同じ時間に**: 特定の時間をルーティンにすると習慣化しやすくなります。
    3. **記録をつける**: このアプリで進捗を記録し、達成感を感じましょう。
    4. **目に見える場所に目標を置く**: リマインダーや付箋などで目標を視覚化しましょう。
    5. **途切れても再開する**: 1日失敗しても諦めず、すぐに再開しましょう。
    """)

# 未来へのメッセージページ
def show_future_messages():
    st.markdown('<h2 class="sub-header">💌 未来へのメッセージ</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    messages = load_messages()
    
    st.markdown("""
    未来の自分へのメッセージを残しましょう。これは、ある期間が経過した後に
    開封できるタイムカプセルのような機能です。モチベーションを維持するのに役立ちます。
    """)
    
    # 新しいメッセージの作成
    st.markdown("### 新しいメッセージを作成")
    
    with st.form("future_message_form"):
        message_content = st.text_area("メッセージの内容", placeholder="未来の自分へのメッセージを書いてください...")
        target_date_option = st.selectbox("いつ開封できるようにしますか？", 
                               ["1週間後", "1ヶ月後", "3ヶ月後", "6ヶ月後", "1年後"])
        
        # 開封日の計算
        today = date.today()
        if target_date_option == "1週間後":
            target_date = today + timedelta(days=7)
        elif target_date_option == "1ヶ月後":
            target_date = today + timedelta(days=30)
        elif target_date_option == "3ヶ月後":
            target_date = today + timedelta(days=90)
        elif target_date_option == "6ヶ月後":
            target_date = today + timedelta(days=180)
        else:  # 1年後
            target_date = today + timedelta(days=365)
        
        st.markdown(f"開封予定日: {target_date.strftime('%Y年%m月%d日')}")
        
        submit_button = st.form_submit_button("メッセージを保存")
        
        if submit_button:
            if not message_content:
                st.error("メッセージを入力してください。")
            else:
                # メッセージを保存
                new_message = {
                    "id": str(uuid.uuid4()),
                    "content": message_content,
                    "created_date": today.strftime("%Y-%m-%d"),
                    "target_date": target_date.strftime("%Y-%m-%d"),
                    "opened": False
                }
                
                if messages.empty:
                    messages = pd.DataFrame([new_message])
                else:
                    messages = pd.concat([messages, pd.DataFrame([new_message])], ignore_index=True)
                
                save_messages(messages)
                
                # ポイント獲得
                add_points(10, "未来へのメッセージ作成")
                
                st.success("メッセージを保存しました！指定した日になると開封できます。")
                st.balloons()
    
    # 開封可能なメッセージ
    st.markdown("### 開封可能なメッセージ")
    
    if not messages.empty and 'target_date' in messages.columns and 'opened' in messages.columns:
        # 日付を変換
        messages['target_date'] = pd.to_datetime(messages['target_date']).dt.date
        today = date.today()
        
        # 開封可能なメッセージを抽出
        openable_messages = messages[(messages['target_date'] <= today) & (messages['opened'] == False)]
        
        if not openable_messages.empty:
            for _, message in openable_messages.iterrows():
                st.markdown(f"""
                <div class="message-card">
                    <h4>📬 {message['created_date']}に書いたメッセージ</h4>
                    <p>開封予定日: {message['target_date']}</p>
                    <p>今日開封できます！</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("開封する", key=f"open_{message['id']}"):
                    st.markdown(f"""
                    <div class="message-card" style="background-color: #E8F5E9;">
                        <h4>📩 メッセージの内容:</h4>
                        <p>"{message['content']}"</p>
                        <p><small>作成日: {message['created_date']}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # メッセージを開封済みに更新
                    messages.loc[messages['id'] == message['id'], 'opened'] = True
                    save_messages(messages)
                    
                    # ポイント獲得
                    add_points(20, "未来からのメッセージを開封")
                    
                    st.success("メッセージを開封しました！20ポイント獲得！")
        else:
            st.info("現在、開封可能なメッセージはありません。")
    
    # 待機中のメッセージ
    st.markdown("### 待機中のメッセージ")
    
    if not messages.empty and 'target_date' in messages.columns and 'opened' in messages.columns:
        today = date.today()
        
        # 待機中のメッセージを抽出
        waiting_messages = messages[(messages['target_date'] > today) & (messages['opened'] == False)]
        
        if not waiting_messages.empty:
            for _, message in waiting_messages.iterrows():
                # 残り日数を計算
                days_left = (message['target_date'] - today).days
                
                st.markdown(f"""
                <div class="message-card" style="opacity: 0.7;">
                    <h4>📫 {message['created_date']}に書いたメッセージ</h4>
                    <p>開封予定日: {message['target_date']}</p>
                    <p>開封まであと{days_left}日</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("待機中のメッセージはありません。")
    
    # 開封済みのメッセージ
    with st.expander("開封済みのメッセージ", expanded=False):
        if not messages.empty and 'opened' in messages.columns:
            opened_messages = messages[messages['opened'] == True]
            
            if not opened_messages.empty:
                for _, message in opened_messages.iterrows():
                    st.markdown(f"""
                    <div class="message-card" style="opacity: 0.7;">
                        <h4>📭 {message['created_date']}に書いたメッセージ (開封済み)</h4>
                        <p>"{message['content']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("開封済みのメッセージはありません。")

# 実績と称号ページ
def show_achievements_titles():
    st.markdown('<h2 class="sub-header">🏆 実績と称号</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    achievements = load_achievements()
    titles_data = load_titles()
    
    # 獲得した称号の表示
    st.markdown("### 獲得した称号")
    
    earned_titles = [t for t in titles_data["titles"] if t["earned"]]
    
    if earned_titles:
        st.markdown('<div class="badge-container">', unsafe_allow_html=True)
        
        for title in earned_titles:
            st.markdown(f"""
            <span class="badge-item" title="{title['description']}">
                {title['image']} {title['name']}
            </span>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 現在の最高称号
        highest_title = max(earned_titles, key=lambda x: x["requirement"])
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>現在の称号: {highest_title['image']} {highest_title['name']}</h4>
            <p>{highest_title['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("まだ称号を獲得していません。アプリを継続的に使うことで称号を獲得できます。")
    
    # 獲得可能な称号
    not_earned_titles = [t for t in titles_data["titles"] if not t["earned"]]
    
    if not_earned_titles:
        st.markdown("### 獲得可能な称号")
        
        # 次に獲得できる称号
        next_title = min(not_earned_titles, key=lambda x: x["requirement"])
        
        st.markdown(f"""
        <div class="insight-box" style="background-color: #F5F5F5; border-left: 5px solid #9E9E9E;">
            <h4>次の称号: {next_title['image']} {next_title['name']}</h4>
            <p>{next_title['description']}</p>
            <p>アプリを{next_title['requirement']}日使用すると獲得できます。</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 他の称号一覧
        other_titles = [t for t in not_earned_titles if t != next_title]
        
        if other_titles:
            st.markdown("#### その他の獲得可能な称号")
            
            for title in other_titles:
                st.markdown(f"""
                <div style="background-color: #F5F5F5; padding: 10px; border-radius: 10px; margin: 5px 0; opacity: 0.7;">
                    <p>{title['image']} <strong>{title['name']}</strong> - {title['description']}</p>
                    <p>必要日数: {title['requirement']}日</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 実績リスト
    st.markdown("### 獲得した実績")
    
    if not achievements.empty:
        # 実績を日付順にソート
        achievements = achievements.sort_values('date', ascending=False)
        
        for _, achievement in achievements.iterrows():
            st.markdown(f"""
            <div class="achievement-card">
                <h4>🏆 {achievement['name']}</h4>
                <p>{achievement['description']}</p>
                <p>達成日: {achievement['date']}</p>
                <p>獲得ポイント: {achievement['points']}pt</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("まだ実績を獲得していません。様々なチャレンジや活動を行って実績を獲得しましょう。")
    
    # 実績グラフ
    if not achievements.empty and 'date' in achievements.columns and 'points' in achievements.columns:
        # 日付を変換
        achievements['date'] = pd.to_datetime(achievements['date'])
        
        # 月別の実績数と獲得ポイントを集計
        achievements['year_month'] = achievements['date'].dt.strftime('%Y-%m')
        monthly_stats = achievements.groupby('year_month').agg({
            'id': 'count',
            'points': 'sum'
        }).reset_index()
        monthly_stats.columns = ['year_month', 'count', 'points']
        
        # グラフ表示
        fig = px.bar(
            monthly_stats,
            x='year_month',
            y=['count', 'points'],
            title="月別の実績獲得状況",
            labels={'year_month': '年月', 'value': '数', 'variable': '種類'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

# ユーティリティ関数
def calculate_current_streak(activity_log):
    """現在の連続ログイン日数を計算"""
    if activity_log.empty or 'date' not in activity_log.columns:
        return 0
    
    # 日付をソート
    activity_log['date'] = pd.to_datetime(activity_log['date']).dt.date
    login_dates = activity_log[activity_log['activity_type'] == "ログイン"]['date'].unique()
    login_dates = sorted(login_dates, reverse=True)
    
    if not login_dates:
        return 0
    
    # 今日または昨日のログインがあるか確認
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if today not in login_dates and yesterday not in login_dates:
        return 0
    
    # 連続日数を計算
    streak = 1
    prev_date = login_dates[0]
    
    for i in range(1, len(login_dates)):
        current_date = login_dates[i]
        days_diff = (prev_date - current_date).days
        
        if days_diff == 1:
            streak += 1
            prev_date = current_date
        else:
            break
    
    return streak

def calculate_max_streak(activity_log):
    """最長の連続ログイン日数を計算"""
    if activity_log.empty or 'date' not in activity_log.columns:
        return 0
    
    # 日付をソート
    activity_log['date'] = pd.to_datetime(activity_log['date']).dt.date
    login_dates = activity_log[activity_log['activity_type'] == "ログイン"]['date'].unique()
    login_dates = sorted(login_dates)
    
    if not login_dates:
        return 0
    
    # 最長連続日数を計算
    max_streak = 1
    current_streak = 1
    prev_date = login_dates[0]
    
    for i in range(1, len(login_dates)):
        current_date = login_dates[i]
        days_diff = (current_date - prev_date).days
        
        if days_diff == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
        
        prev_date = current_date
    
    return max_streak

def generate_weekly_feedback(activity_types, total_points, active_days):
    """週間アクティビティに基づいたフィードバックを生成"""
    feedback = f"<p>先週は<strong>{active_days}日間</strong>アプリを使用し、<strong>{total_points}ポイント</strong>を獲得しました。</p>"
    
    if active_days >= 5:
        feedback += "<p>毎日の習慣化がとても素晴らしいです！継続は力なり、素晴らしい成果が期待できます。</p>"
    elif active_days >= 3:
        feedback += "<p>コンスタントにアプリを使えています。理想は毎日の使用ですが、現在のペースでも良い進歩です。</p>"
    else:
        feedback += "<p>アプリの使用頻度が少なめです。できれば毎日少しの時間でも使うと、より効果的です。</p>"
    
    # 最もよく行った活動
    if len(activity_types) > 0:
        top_activity = activity_types.index[0]
        feedback += f"<p>最も頻繁に行った活動は「<strong>{top_activity}</strong>」でした。</p>"
    
    # 次の週の提案
    suggestions = [
        "毎日同じ時間にアプリを開く習慣をつけると継続しやすくなります。",
        "小さな目標から始めて、徐々にレベルアップしていきましょう。",
        "達成感を味わうために、完了したタスクや活動を記録し続けましょう。",
        "週に一度、自分の進捗を振り返る時間を作りましょう。",
        "モチベーションが下がったら、過去の成功体験を思い出しましょう。"
    ]
    
    feedback += f"<p>次週のアドバイス: {random.choice(suggestions)}</p>"
    
    return feedback

# ページ選択に応じた内容を表示
if page == "モチベーションダッシュボード":
    show_motivation_dashboard()
elif page == "努力カレンダー":
    show_effort_calendar()
elif page == "継続チャレンジ":
    show_challenge_tracker()
elif page == "未来へのメッセージ":
    show_future_messages()
elif page == "実績と称号":
    show_achievements_titles()