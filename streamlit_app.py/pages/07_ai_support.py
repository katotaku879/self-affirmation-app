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
import re
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ページの設定
st.set_page_config(
    page_title="AIサポート - 自己肯定アプリ",
    page_icon="🤖",
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
    .ai-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
    }
    .insight-card {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #2196F3;
    }
    .warning-card {
        background-color: #FFF8E1;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #FFC107;
    }
    .strategy-card {
        background-color: #F3E5F5;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #9C27B0;
    }
    .motivation-card {
        background-color: #E0F7FA;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #00BCD4;
    }
    .report-card {
        background-color: #EFEBE9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #795548;
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
    .comparison-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    .comparison-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 0.5rem;
        flex: 1;
    }
    .chat-container {
        margin-bottom: 20px;
        border-radius: 10px;
        background-color: #F5F5F5;
        padding: 15px;
    }
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        position: relative;
        display: inline-block;
    }
    .bot-bubble {
        background-color: #E3F2FD;
        margin-right: auto;
        border-bottom-left-radius: 5px;
        border-top-right-radius: 18px;
        border-bottom-right-radius: 18px;
        border-top-left-radius: 18px;
    }
    .user-bubble {
        background-color: #E8F5E9;
        margin-left: auto;
        border-bottom-right-radius: 5px; 
        border-top-left-radius: 18px;
        border-bottom-left-radius: 18px;
        border-top-right-radius: 18px;
        float: right;
        clear: both;
    }
    .chat-name {
        font-size: 0.8rem;
        margin-bottom: 2px;
        font-weight: bold;
    }
    .pattern-badge {
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 3px;
    }
    .goal-badge {
        background-color: #E8F5E9;
        color: #388E3C;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 3px;
    }
    .emotion-badge {
        background-color: #FFF8E1;
        color: #F57F17;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 3px;
    }
    .action-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .insight-list {
        list-style-type: none;
        padding-left: 0;
    }
    .insight-list li {
        margin-bottom: 10px;
        padding-left: 25px;
        position: relative;
    }
    .insight-list li:before {
        content: "💡";
        position: absolute;
        left: 0;
        top: 0;
    }
    .challenge-list {
        list-style-type: none;
        padding-left: 0;
    }
    .challenge-list li {
        margin-bottom: 10px;
        padding-left: 25px;
        position: relative;
    }
    .challenge-list li:before {
        content: "🚀";
        position: absolute;
        left: 0;
        top: 0;
    }
    .strategy-list {
        list-style-type: none;
        padding-left: 0;
    }
    .strategy-list li {
        margin-bottom: 10px;
        padding-left: 25px;
        position: relative;
    }
    .strategy-list li:before {
        content: "⭐";
        position: absolute;
        left: 0;
        top: 0;
    }
</style>
""", unsafe_allow_html=True)

# 既存のデータファイルパス
EMOTION_LOGS_FILE = "emotion_logs.json"
GROWTH_DATA_FILE = "growth_data.json"
GOALS_FILE = "goals.json"
TASK_FILE = "tasks.json"
HABIT_RECORDS_FILE = "habit_records.json"
SMALL_WINS_FILE = "small_wins.json"
ACTIVITY_LOG_FILE = "activity_log.json"
SELF_ESTEEM_LOG_FILE = "self_esteem_log.json"

# AIサポート用のデータファイルパス
AI_DAILY_LOGS_FILE = "ai_daily_logs.json"
AI_WEEKLY_REPORTS_FILE = "ai_weekly_reports.json"
AI_INSIGHTS_FILE = "ai_insights.json"
AI_USER_PROFILE_FILE = "ai_user_profile.json"
AI_CHAT_HISTORY_FILE = "ai_chat_history.json"

# データファイルの初期化
def initialize_ai_support_files():
    if not os.path.exists(AI_DAILY_LOGS_FILE):
        with open(AI_DAILY_LOGS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(AI_WEEKLY_REPORTS_FILE):
        with open(AI_WEEKLY_REPORTS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(AI_INSIGHTS_FILE):
        with open(AI_INSIGHTS_FILE, "w") as f:
            json.dump({"goal_insights": [], "emotion_insights": [], "habit_insights": [], "productivity_insights": []}, f)
    
    if not os.path.exists(AI_USER_PROFILE_FILE):
        default_profile = {
            "goal_pattern": "unknown",  # "short_term" or "long_term"
            "motivation_triggers": [],
            "demotivation_triggers": [],
            "productive_time": "unknown",  # "morning", "afternoon", "evening"
            "learning_style": "unknown",  # "visual", "practical", "theoretical"
            "personality_traits": {
                "conscientiousness": 50,
                "resilience": 50,
                "openness": 50,
                "social_orientation": 50,
                "planning_preference": 50  # high = planner, low = improviser
            },
            "strength_areas": [],
            "improvement_areas": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        with open(AI_USER_PROFILE_FILE, "w") as f:
            json.dump(default_profile, f)
    
    if not os.path.exists(AI_CHAT_HISTORY_FILE):
        with open(AI_CHAT_HISTORY_FILE, "w") as f:
            json.dump([], f)

# 初期化を実行
initialize_ai_support_files()

# セッション状態の初期化
if 'customize_strategy' not in st.session_state:
    st.session_state.customize_strategy = False

# データ読み込み関数
def load_emotion_logs():
    try:
        with open(EMOTION_LOGS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_growth_data():
    try:
        with open(GROWTH_DATA_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_goals():
    try:
        with open(GOALS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_habit_records():
    try:
        with open(HABIT_RECORDS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_small_wins():
    try:
        with open(SMALL_WINS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_activity_log():
    try:
        with open(ACTIVITY_LOG_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_self_esteem_log():
    try:
        with open(SELF_ESTEEM_LOG_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_ai_daily_logs():
    try:
        with open(AI_DAILY_LOGS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_ai_weekly_reports():
    try:
        with open(AI_WEEKLY_REPORTS_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_ai_insights():
    try:
        with open(AI_INSIGHTS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"goal_insights": [], "emotion_insights": [], "habit_insights": [], "productivity_insights": []}

def load_user_profile():
    try:
        with open(AI_USER_PROFILE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # デフォルトプロファイルを返す
        return {
            "goal_pattern": "unknown",
            "motivation_triggers": [],
            "demotivation_triggers": [],
            "productive_time": "unknown",
            "learning_style": "unknown",
            "personality_traits": {
                "conscientiousness": 50,
                "resilience": 50,
                "openness": 50,
                "social_orientation": 50,
                "planning_preference": 50
            },
            "strength_areas": [],
            "improvement_areas": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }

def load_chat_history():
    try:
        with open(AI_CHAT_HISTORY_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

# データ保存関数
def save_ai_daily_logs(df):
    with open(AI_DAILY_LOGS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_ai_weekly_reports(df):
    with open(AI_WEEKLY_REPORTS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_ai_insights(insights_data):
    with open(AI_INSIGHTS_FILE, "w") as f:
        json.dump(insights_data, f)

def save_user_profile(profile_data):
    with open(AI_USER_PROFILE_FILE, "w") as f:
        json.dump(profile_data, f)

def save_chat_history(df):
    with open(AI_CHAT_HISTORY_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

# マルチページアプリのタイトル
st.markdown('<h1 class="main-header">🤖 AIサポート</h1>', unsafe_allow_html=True)

# ページナビゲーション
page = st.sidebar.radio(
    "AIサポートメニュー",
    ["AIチャットサポート", "今日のチェックイン", "パーソナル分析", "週間レポート", "成長戦略提案"],
)

# AIチャットサポートページ
def show_ai_chat_support():
    st.markdown('<h2 class="sub-header">💬 AIチャットサポート</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    あなたの成長をサポートするAIアシスタントです。
    モチベーション、目標達成、習慣形成など、様々な質問や相談に対応します。
    また、あなたのこれまでの活動データを分析した上で、パーソナライズされたアドバイスも提供します。
    """)
    
    # チャット履歴の読み込み
    chat_history = load_chat_history()
    
    # チャット履歴の表示
    if not chat_history.empty and 'message' in chat_history.columns and 'sender' in chat_history.columns:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for _, chat in chat_history.iterrows():
            if chat['sender'] == 'user':
                st.markdown(f"""
                <div class="chat-bubble user-bubble">
                    <div class="chat-name">あなた</div>
                    {chat['message']}
                </div>
                <div style="clear: both;"></div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble bot-bubble">
                    <div class="chat-name">AIサポート</div>
                    {chat['message']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 新しいメッセージ入力
    with st.form("chat_form"):
        user_message = st.text_area("メッセージを入力してください", height=100)
        submit_button = st.form_submit_button("送信")
        
        if submit_button and user_message:
            # ユーザーメッセージをチャット履歴に追加
            new_user_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "user",
                "message": user_message
            }
            
            if chat_history.empty:
                chat_history = pd.DataFrame([new_user_message])
            else:
                chat_history = pd.concat([chat_history, pd.DataFrame([new_user_message])], ignore_index=True)
            
            # AIの応答を生成
            ai_response = generate_ai_response(user_message)
            
            # AI応答をチャット履歴に追加
            new_ai_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "ai",
                "message": ai_response
            }
            
            chat_history = pd.concat([chat_history, pd.DataFrame([new_ai_message])], ignore_index=True)
            
            # チャット履歴を保存
            save_chat_history(chat_history)
            
            # 画面を更新して新しいメッセージを表示
            st.rerun()
    
    # クイックアクション
    st.markdown("### クイックアクション")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("モチベーションが下がっています"):
            # 新しいユーザーメッセージをチャット履歴に追加
            new_user_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "user",
                "message": "モチベーションが下がっています。どうすれば良いですか？"
            }
            
            if chat_history.empty:
                chat_history = pd.DataFrame([new_user_message])
            else:
                chat_history = pd.concat([chat_history, pd.DataFrame([new_user_message])], ignore_index=True)
            
            # AIの応答を生成
            ai_response = generate_motivation_boost()
            
            # AI応答をチャット履歴に追加
            new_ai_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "ai",
                "message": ai_response
            }
            
            chat_history = pd.concat([chat_history, pd.DataFrame([new_ai_message])], ignore_index=True)
            
            # チャット履歴を保存
            save_chat_history(chat_history)
            
            # 画面を更新して新しいメッセージを表示
            st.experimental_rerun()
    
    with col2:
        if st.button("目標達成のアドバイスが欲しい"):
            # 新しいユーザーメッセージをチャット履歴に追加
            new_user_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "user",
                "message": "目標達成のアドバイスが欲しいです。"
            }
            
            if chat_history.empty:
                chat_history = pd.DataFrame([new_user_message])
            else:
                chat_history = pd.concat([chat_history, pd.DataFrame([new_user_message])], ignore_index=True)
            
            # AIの応答を生成
            ai_response = generate_goal_advice()
            
            # AI応答をチャット履歴に追加
            new_ai_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "ai",
                "message": ai_response
            }
            
            chat_history = pd.concat([chat_history, pd.DataFrame([new_ai_message])], ignore_index=True)
            
            # チャット履歴を保存
            save_chat_history(chat_history)
            
            # 画面を更新して新しいメッセージを表示
            st.experimental_rerun()
    
    with col3:
        if st.button("私の強みは何ですか？"):
            # 新しいユーザーメッセージをチャット履歴に追加
            new_user_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "user",
                "message": "私の強みは何ですか？"
            }
            
            if chat_history.empty:
                chat_history = pd.DataFrame([new_user_message])
            else:
                chat_history = pd.concat([chat_history, pd.DataFrame([new_user_message])], ignore_index=True)
            
            # AIの応答を生成
            ai_response = generate_strength_analysis()
            
            # AI応答をチャット履歴に追加
            new_ai_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sender": "ai",
                "message": ai_response
            }
            
            chat_history = pd.concat([chat_history, pd.DataFrame([new_ai_message])], ignore_index=True)
            
            # チャット履歴を保存
            save_chat_history(chat_history)
            
            # 画面を更新して新しいメッセージを表示
            st.experimental_rerun()
    
    # 履歴のクリア
    if not chat_history.empty:
        if st.button("チャット履歴をクリア"):
            # 空のデータフレームで履歴を上書き
            save_chat_history(pd.DataFrame())
            st.success("チャット履歴をクリアしました。")
            st.experimental_rerun()

# 今日のチェックインページ
def show_daily_checkin():
    st.markdown('<h2 class="sub-header">📝 今日のチェックイン</h2>', unsafe_allow_html=True)
    
    # 日付の設定
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    st.markdown(f"""
    <div class="ai-card">
        <h3>今日は{today.strftime('%Y年%m月%d日')}です</h3>
        <p>今日の調子や目標の進捗、気づきなどを記録しましょう。
        AIがあなたの状態に合わせてアドバイスを提供します。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 既存のデータを読み込む
    daily_logs = load_ai_daily_logs()
    
    # 今日のログがあるか確認
    today_log = daily_logs[daily_logs['date'] == today_str] if not daily_logs.empty and 'date' in daily_logs.columns else pd.DataFrame()
    
    # 今日のログが既にある場合は表示、なければ新規作成
    if not today_log.empty:
        st.markdown("### 今日の記録")
        
        mood = today_log.iloc[0]['mood']
        progress = today_log.iloc[0]['progress']
        insights = today_log.iloc[0]['insights']
        challenges = today_log.iloc[0]['challenges']
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>今日の調子: {mood}/10</h4>
            <p>目標の進捗状況: {progress}/10</p>
            <h4>気づき・学び:</h4>
            <p>{insights}</p>
            <h4>課題・困難:</h4>
            <p>{challenges}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AIフィードバック表示
        if 'ai_feedback' in today_log.iloc[0]:
            ai_feedback = today_log.iloc[0]['ai_feedback']
            
            st.markdown(f"""
            <div class="ai-card">
                <h4>AIフィードバック</h4>
                <p>{ai_feedback}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 記録を更新するオプション
        if st.button("記録を更新する"):
            # 既存の記録を削除
            daily_logs = daily_logs[daily_logs['date'] != today_str]
            save_ai_daily_logs(daily_logs)
            st.experimental_rerun()
    else:
        # 新しい記録を作成
        st.markdown("### 今日の状態を記録")
        
        with st.form("daily_checkin_form"):
            mood = st.slider("今日の調子はどうですか？", 1, 10, 5)
            progress = st.slider("目標の進捗状況は？", 1, 10, 5)
            insights = st.text_area("今日の気づきや学びは？", placeholder="例：早起きすると集中力が高いことに気づいた、新しい方法を試してみた など")
            challenges = st.text_area("課題や困難なことは？", placeholder="例：時間管理が難しかった、モチベーションを維持するのが大変 など")
            
            submit_button = st.form_submit_button("記録する")
            
            if submit_button:
                # AIフィードバックを生成
                ai_feedback = generate_daily_feedback(mood, progress, insights, challenges)
                
                # 新しい記録を追加
                new_log = {
                    "date": today_str,
                    "mood": mood,
                    "progress": progress,
                    "insights": insights,
                    "challenges": challenges,
                    "ai_feedback": ai_feedback
                }
                
                if daily_logs.empty:
                    daily_logs = pd.DataFrame([new_log])
                else:
                    daily_logs = pd.concat([daily_logs, pd.DataFrame([new_log])], ignore_index=True)
                
                save_ai_daily_logs(daily_logs)
                
                # ユーザープロファイルの更新
                update_user_profile_from_daily_log(mood, progress, insights, challenges)
                
                st.success("今日の記録を保存しました！")
                st.experimental_rerun()
    
    # 最近の記録を表示
    if not daily_logs.empty and len(daily_logs) > 1:
        st.markdown("### 最近の記録")

     # 今日以外の最新5件を取得
        recent_logs = daily_logs[daily_logs['date'] != today_str].sort_values('date', ascending=False).head(5)
        
        if not recent_logs.empty:
            for _, log in recent_logs.iterrows():
                log_date = datetime.strptime(log['date'], "%Y-%m-%d").strftime("%Y年%m月%d日")
                
                with st.expander(f"{log_date}の記録"):
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>調子: {log['mood']}/10 | 進捗: {log['progress']}/10</h4>
                        <h5>気づき・学び:</h5>
                        <p>{log['insights']}</p>
                        <h5>課題・困難:</h5>
                        <p>{log['challenges']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'ai_feedback' in log:
                        st.markdown(f"""
                        <div class="ai-card">
                            <h4>AIフィードバック</h4>
                            <p>{log['ai_feedback']}</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # 調子と進捗状況の推移グラフ
    if not daily_logs.empty and len(daily_logs) >= 3:
        st.markdown("### 調子と進捗状況の推移")
        
        # 日付順にソート
        daily_logs['date'] = pd.to_datetime(daily_logs['date'])
        sorted_logs = daily_logs.sort_values('date')
        
        # 最大30日分のデータを表示
        recent_data = sorted_logs.tail(30)
        
        # グラフ用のデータ準備
        fig = go.Figure()
        
        # 調子の推移
        fig.add_trace(go.Scatter(
            x=recent_data['date'],
            y=recent_data['mood'],
            mode='lines+markers',
            name='調子',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ))
        
        # 進捗状況の推移
        fig.add_trace(go.Scatter(
            x=recent_data['date'],
            y=recent_data['progress'],
            mode='lines+markers',
            name='進捗状況',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ))
        
        # グラフのレイアウト設定
        fig.update_layout(
            title='調子と進捗状況の推移',
            xaxis_title='日付',
            yaxis_title='スコア (1-10)',
            yaxis=dict(range=[0, 11]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 相関分析
        correlation = recent_data['mood'].corr(recent_data['progress'])
        
        if abs(correlation) > 0.7:
            st.markdown(f"""
            <div class="insight-card">
                <h4>調子と進捗の関係</h4>
                <p>あなたの調子と目標の進捗には<strong>強い相関関係</strong>があります (相関係数: {correlation:.2f})。</p>
                <p>{'調子が良いと目標の進捗も良くなる傾向があります。調子を維持することが目標達成につながるでしょう。' if correlation > 0 else '目標の進捗が良いと調子も良くなる傾向があります。小さな成功体験を積み重ねることで、全体的な調子も向上するでしょう。'}</p>
            </div>
            """, unsafe_allow_html=True)
        elif abs(correlation) > 0.3:
            st.markdown(f"""
            <div class="insight-card">
                <h4>調子と進捗の関係</h4>
                <p>あなたの調子と目標の進捗には<strong>ある程度の相関関係</strong>があります (相関係数: {correlation:.2f})。</p>
                <p>{'調子と目標の進捗は互いに影響し合っている可能性があります。' if correlation > 0 else '調子と目標の進捗には負の相関があります。これは興味深いパターンで、さらなる分析が必要かもしれません。'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-card">
                <h4>調子と進捗の関係</h4>
                <p>あなたの調子と目標の進捗には<strong>強い相関関係はありません</strong> (相関係数: {correlation:.2f})。</p>
                <p>これは、あなたが調子に関わらず目標に取り組む能力があることを示しているかもしれません。この独立性は強みになる可能性があります。</p>
            </div>
            """, unsafe_allow_html=True)

# パーソナル分析ページ
def show_personal_analysis():
    st.markdown('<h2 class="sub-header">🔍 パーソナル分析</h2>', unsafe_allow_html=True)
    
    # ユーザープロファイル読み込み
    user_profile = load_user_profile()
    
    st.markdown("""
    AIがあなたの活動データを分析し、あなたの特性や傾向を把握しています。
    この分析結果は、より効果的な目標達成や自己成長のために活用できます。
    """)
    
    # プロファイル概要
    st.markdown("### あなたのプロファイル")
    
    # 目標パターン
    goal_pattern = user_profile.get("goal_pattern", "unknown")
    goal_pattern_description = ""
    
    if goal_pattern == "short_term":
        goal_pattern_description = "短期目標を積み重ねるタイプです。小さな成功体験を重視し、段階的に大きな目標に近づくアプローチが効果的です。"
    elif goal_pattern == "long_term":
        goal_pattern_description = "長期的な視点で目標に取り組むタイプです。大きなビジョンを持ち、それに向かって計画的に進むアプローチが効果的です。"
    else:
        goal_pattern_description = "まだ十分なデータがないため、目標パターンが特定できていません。もう少し活動データが増えると、分析が可能になります。"
    
    # 生産性の高い時間帯
    productive_time = user_profile.get("productive_time", "unknown")
    productive_time_description = ""
    
    if productive_time == "morning":
        productive_time_description = "朝の時間帯に最も生産性が高い傾向があります。重要なタスクや集中力を要する作業は午前中に行うと効果的です。"
    elif productive_time == "afternoon":
        productive_time_description = "午後の時間帯に最も生産性が高い傾向があります。重要なタスクや集中力を要する作業は午後に行うと効果的です。"
    elif productive_time == "evening":
        productive_time_description = "夕方から夜の時間帯に最も生産性が高い傾向があります。重要なタスクや集中力を要する作業は夕方以降に行うと効果的です。"
    else:
        productive_time_description = "まだ十分なデータがないため、最も生産性の高い時間帯が特定できていません。もう少し活動データが増えると、分析が可能になります。"
    
    # 学習スタイル
    learning_style = user_profile.get("learning_style", "unknown")
    learning_style_description = ""
    
    if learning_style == "visual":
        learning_style_description = "視覚的な情報から最も効果的に学ぶタイプです。図表、イメージ、色分けなどの視覚的な要素を活用すると学習効果が高まります。"
    elif learning_style == "practical":
        learning_style_description = "実践を通じて最も効果的に学ぶタイプです。実際に手を動かし、経験を通じて学ぶアプローチが効果的です。"
    elif learning_style == "theoretical":
        learning_style_description = "概念や理論から最も効果的に学ぶタイプです。体系的な理解や論理的な説明を通じて学ぶアプローチが効果的です。"
    else:
        learning_style_description = "まだ十分なデータがないため、学習スタイルが特定できていません。もう少し活動データが増えると、分析が可能になります。"
    
    # プロファイル概要表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="ai-card">
            <h4>目標達成パターン</h4>
            <p><strong>{goal_pattern if goal_pattern != "unknown" else "分析中..."}</strong></p>
            <p>{goal_pattern_description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="ai-card">
            <h4>学習スタイル</h4>
            <p><strong>{learning_style if learning_style != "unknown" else "分析中..."}</strong></p>
            <p>{learning_style_description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="ai-card">
            <h4>生産性の高い時間帯</h4>
            <p><strong>{productive_time if productive_time != "unknown" else "分析中..."}</strong></p>
            <p>{productive_time_description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # モチベーショントリガー
        motivation_triggers = user_profile.get("motivation_triggers", [])
        demotivation_triggers = user_profile.get("demotivation_triggers", [])
        
        triggers_html = ""
        if motivation_triggers:
            triggers_html += "<h5>モチベーションが上がる要因:</h5><ul>"
            for trigger in motivation_triggers[:3]:  # 最大3つまで表示
                triggers_html += f"<li>{trigger}</li>"
            triggers_html += "</ul>"
        
        if demotivation_triggers:
            triggers_html += "<h5>モチベーションが下がる要因:</h5><ul>"
            for trigger in demotivation_triggers[:3]:  # 最大3つまで表示
                triggers_html += f"<li>{trigger}</li>"
            triggers_html += "</ul>"
        
        if not motivation_triggers and not demotivation_triggers:
            triggers_html = "<p>まだ十分なデータがないため、モチベーショントリガーが特定できていません。</p>"
        
        st.markdown(f"""
        <div class="ai-card">
            <h4>モチベーショントリガー</h4>
            {triggers_html}
        </div>
        """, unsafe_allow_html=True)
    
    # パーソナリティ特性
    st.markdown("### パーソナリティ特性")
    
    personality_traits = user_profile.get("personality_traits", {})
    
    if personality_traits:
        # レーダーチャートのデータ準備
        categories = [
            '計画性<br>(Conscientiousness)', 
            '回復力<br>(Resilience)', 
            '好奇心<br>(Openness)', 
            '社交性<br>(Social Orientation)', 
            '計画指向<br>(Planning Preference)'
        ]
        
        values = [
            personality_traits.get("conscientiousness", 50),
            personality_traits.get("resilience", 50),
            personality_traits.get("openness", 50),
            personality_traits.get("social_orientation", 50),
            personality_traits.get("planning_preference", 50)
        ]
        
        # 値を閉じたポリゴンにするために最初の値を最後にも追加
        values.append(values[0])
        categories.append(categories[0])
        
        # レーダーチャート作成
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='あなたの特性',
            line_color='#4CAF50',
            fillcolor='rgba(76, 175, 80, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 特性の解釈
        col1, col2 = st.columns(2)
        
        with col1:
            # 計画性
            conscientiousness = personality_traits.get("conscientiousness", 50)
            if conscientiousness > 70:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>計画性: {conscientiousness}/100</h4>
                    <p>あなたは非常に計画的で、目標に向かって着実に進む能力が高いです。締め切りを守り、タスクを計画通りに実行することが得意です。</p>
                </div>
                """, unsafe_allow_html=True)
            elif conscientiousness > 40:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>計画性: {conscientiousness}/100</h4>
                    <p>あなたはバランスの取れた計画性を持っています。計画を立てつつも、状況に応じて柔軟に対応できる能力があります。</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>計画性: {conscientiousness}/100</h4>
                    <p>あなたは柔軟性があり、即興的なアプローチを好む傾向があります。計画よりも直感や創造性を重視する場面が多いかもしれません。</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 好奇心
            openness = personality_traits.get("openness", 50)
            if openness > 70:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>好奇心: {openness}/100</h4>
                    <p>あなたは非常に好奇心が強く、新しいアイデアや経験に対してオープンです。様々な視点から物事を考え、創造的なソリューションを見つけることが得意です。</p>
                </div>
                """, unsafe_allow_html=True)
            elif openness > 40:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>好奇心: {openness}/100</h4>
                    <p>あなたはバランスの取れた好奇心を持っています。新しいアイデアに対してオープンでありながらも、現実的な視点も大切にしています。</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>好奇心: {openness}/100</h4>
                    <p>あなたは実用的で現実的なアプローチを好む傾向があります。具体的で実証済みの方法を重視し、安定性を大切にしています。</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # 回復力
            resilience = personality_traits.get("resilience", 50)
            if resilience > 70:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>回復力: {resilience}/100</h4>
                    <p>あなたは高い回復力を持ち、逆境や困難から素早く立ち直る能力があります。ストレスへの耐性も高く、困難な状況でも前向きな姿勢を維持できます。</p>
                </div>
                """, unsafe_allow_html=True)
            elif resilience > 40:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>回復力: {resilience}/100</h4>
                    <p>あなたはバランスの取れた回復力を持っています。困難に直面した際には時間がかかることもありますが、適切なサポートがあれば回復できる能力があります。</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>回復力: {resilience}/100</h4>
                    <p>あなたは感受性が強く、逆境や困難の影響を受けやすい傾向があります。自己ケアや効果的なストレス管理の方法を学ぶことで、回復力を高めることができるでしょう。</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 社交性
            social_orientation = personality_traits.get("social_orientation", 50)
            if social_orientation > 70:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>社交性: {social_orientation}/100</h4>
                    <p>あなたは社交的で、他者との交流からエネルギーを得る傾向があります。チームでの活動やコラボレーションを通じて最も効果的に成長できるでしょう。</p>
                </div>
                """, unsafe_allow_html=True)
            elif social_orientation > 40:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>社交性: {social_orientation}/100</h4>
                    <p>あなたはバランスの取れた社交性を持っています。他者との交流も独りの時間も大切にし、状況に応じて適切に切り替えることができます。</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>社交性: {social_orientation}/100</h4>
                    <p>あなたは内向的な傾向があり、独りで考えたり活動したりする時間から多くのエネルギーを得ます。深い集中力を要する個人作業を通じて最も効果的に成長できるでしょう。</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("まだ十分なデータがないため、パーソナリティ特性の分析ができていません。もう少し活動データが増えると、分析が可能になります。")
    
    # 強みと改善点
    st.markdown("### 強みと改善点")
    
    strength_areas = user_profile.get("strength_areas", [])
    improvement_areas = user_profile.get("improvement_areas", [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 強み")
        
        if strength_areas:
            for strength in strength_areas:
                st.markdown(f"""
                <div class="strength-item">
                    <h4>{strength}</h4>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("まだ十分なデータがないため、強みが特定できていません。")
    
    with col2:
        st.markdown("#### 改善点")
        
        if improvement_areas:
            for improvement in improvement_areas:
                st.markdown(f"""
                <div class="weakness-item">
                    <h4>{improvement}</h4>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("まだ十分なデータがないため、改善点が特定できていません。")

# 週間レポートページ
def show_weekly_report():
    st.markdown('<h2 class="sub-header">📊 週間レポート</h2>', unsafe_allow_html=True)
    
    # 週間レポートの読み込み
    weekly_reports = load_ai_weekly_reports()
    
    # 今週の日付範囲を計算
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    week_range = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
    
    st.markdown(f"""
    <div class="ai-card">
        <h3>週間レポート（{start_of_week.strftime('%Y年%m月%d日')} - {end_of_week.strftime('%Y年%m月%d日')}）</h3>
        <p>一週間の活動データを分析し、達成状況や傾向、気づきなどをレポートします。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 今週のレポートがあるか確認
    this_week_report = weekly_reports[weekly_reports['week_range'] == week_range] if not weekly_reports.empty and 'week_range' in weekly_reports.columns else pd.DataFrame()
    
    # レポートがある場合は表示、なければ生成
    if not this_week_report.empty:
        # 既存のレポートを表示
        report_data = this_week_report.iloc[0]
        
        # 達成状況
        st.markdown("### 今週の達成状況")
        
        if 'achievements' in report_data:
            achievements = report_data['achievements']
            if achievements:
                st.markdown('<ul class="insight-list">', unsafe_allow_html=True)
                for achievement in achievements:
                    st.markdown(f"<li>{achievement}</li>", unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.info("達成したことはまだ記録されていません。")
        
        # 気づきや学び
        st.markdown("### 今週の気づきや学び")
        
        if 'insights' in report_data:
            insights = report_data['insights']
            if insights:
                st.markdown('<ul class="insight-list">', unsafe_allow_html=True)
                for insight in insights:
                    st.markdown(f"<li>{insight}</li>", unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.info("気づきや学びはまだ記録されていません。")
        
        # 課題や困難
        st.markdown("### 今週の課題や困難")
        
        if 'challenges' in report_data:
            challenges = report_data['challenges']
            if challenges:
                st.markdown('<ul class="challenge-list">', unsafe_allow_html=True)
                for challenge in challenges:
                    st.markdown(f"<li>{challenge}</li>", unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.info("課題や困難はまだ記録されていません。")
        
        # 来週の戦略
        st.markdown("### 来週の戦略提案")
        
        if 'strategies' in report_data:
            strategies = report_data['strategies']
            if strategies:
                st.markdown('<ul class="strategy-list">', unsafe_allow_html=True)
                for strategy in strategies:
                    st.markdown(f"<li>{strategy}</li>", unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.info("戦略提案はまだ記録されていません。")
        
        # 週間の調子と進捗のグラフ
        if 'daily_data' in report_data:
            daily_data = report_data['daily_data']
            if daily_data:
                st.markdown("### 一週間の調子と進捗")
                
                # グラフ用のデータ準備
                dates = []
                moods = []
                progress = []
                
                for day_data in daily_data:
                    if 'date' in day_data and 'mood' in day_data and 'progress' in day_data:
                        dates.append(day_data['date'])
                        moods.append(day_data['mood'])
                        progress.append(day_data['progress'])
                
                if dates:
                    # グラフの作成
                    fig = go.Figure()
                    
                    # 調子の推移
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=moods,
                        mode='lines+markers',
                        name='調子',
                        line=dict(color='#4CAF50', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # 進捗状況の推移
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=progress,
                        mode='lines+markers',
                        name='進捗状況',
                        line=dict(color='#2196F3', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # グラフのレイアウト設定
                    fig.update_layout(
                        title='一週間の調子と進捗状況',
                        xaxis_title='日付',
                        yaxis_title='スコア (1-10)',
                        yaxis=dict(range=[0, 11]),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # レポートの更新ボタン
        if st.button("レポートを更新する"):
            # レポートを再生成
            new_report = generate_weekly_report(start_of_week, end_of_week)
            
            # 既存のレポートを置き換え
            weekly_reports.loc[weekly_reports['week_range'] == week_range] = new_report
            
            save_ai_weekly_reports(weekly_reports)
            
            st.success("週間レポートを更新しました！")
            st.experimental_rerun()
    else:
        # 新しいレポートを生成
        if st.button("今週のレポートを生成"):
            # レポートを生成
            new_report = generate_weekly_report(start_of_week, end_of_week)
            
            # レポートを保存
            if weekly_reports.empty:
                weekly_reports = pd.DataFrame([new_report])
            else:
                weekly_reports = pd.concat([weekly_reports, pd.DataFrame([new_report])], ignore_index=True)
            
            save_ai_weekly_reports(weekly_reports)
            
            st.success("週間レポートを生成しました！")
            st.experimental_rerun()
        else:
            st.info("「今週のレポートを生成」ボタンをクリックして、今週のレポートを作成しましょう。")
    
    # 過去のレポート
    if not weekly_reports.empty and len(weekly_reports) > 1:
        st.markdown("### 過去のレポート")
        
        # 今週以外の過去のレポートを取得
        past_reports = weekly_reports[weekly_reports['week_range'] != week_range].sort_values('week_range', ascending=False)
        
        if not past_reports.empty:
            for _, report in past_reports.iterrows():    
            # 週の範囲を整形
                week_range = report['week_range']
                start_date, end_date = week_range.split('_')
                start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y年%m月%d日")
                
                with st.expander(f"{start_date} - {end_date}のレポート"):
                    # 達成状況
                    if 'achievements' in report and report['achievements']:
                        st.markdown("#### 達成したこと")
                        
                        st.markdown('<ul class="insight-list">', unsafe_allow_html=True)
                        for achievement in report['achievements']:
                            st.markdown(f"<li>{achievement}</li>", unsafe_allow_html=True)
                        st.markdown('</ul>', unsafe_allow_html=True)
                    
                    # 気づきや学び
                    if 'insights' in report and report['insights']:
                        st.markdown("#### 気づきや学び")
                        
                        st.markdown('<ul class="insight-list">', unsafe_allow_html=True)
                        for insight in report['insights']:
                            st.markdown(f"<li>{insight}</li>", unsafe_allow_html=True)
                        st.markdown('</ul>', unsafe_allow_html=True)
                    
                    # 課題や困難
                    if 'challenges' in report and report['challenges']:
                        st.markdown("#### 課題や困難")
                        
                        st.markdown('<ul class="challenge-list">', unsafe_allow_html=True)
                        for challenge in report['challenges']:
                            st.markdown(f"<li>{challenge}</li>", unsafe_allow_html=True)
                        st.markdown('</ul>', unsafe_allow_html=True)
        else:
            st.info("過去のレポートはまだありません。")

# 成長戦略提案ページ
def show_growth_strategy():
    st.markdown('<h2 class="sub-header">🚀 成長戦略提案</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    あなたのデータを分析し、より効果的に成長するための戦略を提案します。
    これらの提案は、あなたの行動パターン、目標達成状況、感情の変化などに基づいています。
    """)
    
    # ユーザープロファイル読み込み
    user_profile = load_user_profile()
    
    # パーソナライズされた戦略提案
    st.markdown("### あなたに最適な成長戦略")
    
    # 目標達成パターンに基づく戦略
    goal_pattern = user_profile.get("goal_pattern", "unknown")
    
    if goal_pattern == "short_term":
        st.markdown(f"""
        <div class="strategy-card">
            <h4>短期目標を積み重ねる方が成果を出しやすいタイプです！</h4>
            <p>あなたのデータを分析したところ、大きな目標を小さなステップに分解して取り組む方が成功率が高いことがわかりました。</p>
            <ul class="strategy-list">
                <li>大きな目標を週単位や日単位の小さなタスクに分割する</li>
                <li>日々の小さな成功体験を記録し、成果を可視化する</li>
                <li>「今日だけ」という意識で、一日ごとに小さな前進を積み重ねる</li>
                <li>一度に複数の大きな目標に取り組むよりも、一つの目標に集中する</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    elif goal_pattern == "long_term":
        st.markdown(f"""
        <div class="strategy-card">
            <h4>長期的な視点で計画を立てる方が成果を出しやすいタイプです！</h4>
            <p>あなたのデータを分析したところ、大きなビジョンを持ち、計画的に進める方が成功率が高いことがわかりました。</p>
            <ul class="strategy-list">
                <li>明確な長期ビジョンを設定し、そこから逆算して中期・短期目標を立てる</li>
                <li>定期的な振り返りと計画の調整を行い、方向性を維持する</li>
                <li>進捗を測定するための指標を設定し、定期的にチェックする</li>
                <li>小さな挫折に一喜一憂せず、大きな流れを重視する</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="strategy-card">
            <h4>あなた専用の成長戦略を分析中...</h4>
            <p>まだ十分なデータがないため、あなたに最適な目標達成パターンを特定できていません。より多くの活動データが集まると、パーソナライズされた戦略を提案できるようになります。</p>
            <p>一般的な成長戦略としては、以下のアプローチが効果的です：</p>
            <ul class="strategy-list">
                <li>SMART目標（具体的、測定可能、達成可能、関連性のある、期限付きの目標）を設定する</li>
                <li>進捗を定期的に記録し、振り返る習慣をつける</li>
                <li>小さな成功体験を積み重ね、自己肯定感を高める</li>
                <li>挑戦と休息のバランスを取り、持続可能なペースで進める</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 生産性の高い時間帯に基づく戦略
    productive_time = user_profile.get("productive_time", "unknown")
    
    if productive_time != "unknown":
        time_desc = {
            "morning": "朝の時間帯",
            "afternoon": "午後の時間帯",
            "evening": "夕方から夜の時間帯"
        }
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>{time_desc[productive_time]}は集中しやすい時間帯です！</h4>
            <p>あなたのデータを分析したところ、{time_desc[productive_time]}に最も生産性が高いことがわかりました。</p>
            <ul class="strategy-list">
                <li>重要なタスクや集中力を要する作業は{time_desc[productive_time]}に計画する</li>
                <li>{time_desc[productive_time]}の時間を確保し、優先的に目標達成に取り組む</li>
                <li>この時間帯は通知やメールをオフにし、集中環境を整える</li>
                <li>他の時間帯は、より創造的な活動や準備作業に充てる</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # AIインサイトの読み込み
    ai_insights = load_ai_insights()
    
    # 行動パターンに基づく提案
    st.markdown("### 行動パターンに基づく提案")
    
    if ai_insights.get("habit_insights"):
        # 最新の習慣インサイトを取得
        latest_habit_insight = ai_insights["habit_insights"][-1]
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>{latest_habit_insight['title']}</h4>
            <p>{latest_habit_insight['description']}</p>
            <ul class="strategy-list">
        """, unsafe_allow_html=True)
        
        for suggestion in latest_habit_insight.get('suggestions', []):
            st.markdown(f"<li>{suggestion}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        # デフォルトの習慣インサイト
        st.markdown(f"""
        <div class="insight-card">
            <h4>習慣の形成パターンを分析中...</h4>
            <p>まだ十分なデータがないため、あなたの習慣形成パターンを特定できていません。より多くの活動データが集まると、パーソナライズされた提案ができるようになります。</p>
            <p>一般的な習慣形成の戦略としては、以下のアプローチが効果的です：</p>
            <ul class="strategy-list">
                <li>新しい習慣は既存の習慣と紐づけると定着しやすい（例：コーヒーを入れた後に5分間の瞑想）</li>
                <li>最初は非常に小さな行動から始め、徐々に拡大する</li>
                <li>環境を整え、習慣の実行をできるだけ簡単にする</li>
                <li>習慣の実行を記録し、連続記録（ストリーク）を作る</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # モチベーション管理に基づく提案
    st.markdown("### モチベーション管理に基づく提案")
    
    # モチベーショントリガーの分析
    motivation_triggers = user_profile.get("motivation_triggers", [])
    demotivation_triggers = user_profile.get("demotivation_triggers", [])
    
    if motivation_triggers or demotivation_triggers:
        st.markdown(f"""
        <div class="motivation-card">
            <h4>あなたのモチベーション管理戦略</h4>
            <p>あなたのデータを分析し、モチベーションに影響を与える要因を特定しました。これらを意識することで、モチベーションをより効果的に管理できます。</p>
        """, unsafe_allow_html=True)
        
        if motivation_triggers:
            st.markdown("<h5>モチベーションを高める方法：</h5><ul class='strategy-list'>", unsafe_allow_html=True)
            for trigger in motivation_triggers[:5]:  # 最大5つまで表示
                st.markdown(f"<li>{trigger}</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
        
        if demotivation_triggers:
            st.markdown("<h5>モチベーション低下を防ぐ方法：</h5><ul class='strategy-list'>", unsafe_allow_html=True)
            for trigger in demotivation_triggers[:5]:  # 最大5つまで表示
                st.markdown(f"<li>「{trigger}」という状況を認識し、対策を立てる</li>", unsafe_allow_html=True)
            st.markdown("</ul>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # デフォルトのモチベーション提案
        st.markdown(f"""
        <div class="motivation-card">
            <h4>モチベーション管理戦略を分析中...</h4>
            <p>まだ十分なデータがないため、あなたのモチベーショントリガーを特定できていません。より多くの活動データが集まると、パーソナライズされた提案ができるようになります。</p>
            <p>一般的なモチベーション維持の戦略としては、以下のアプローチが効果的です：</p>
            <ul class="strategy-list">
                <li>「なぜ」この目標が重要なのかを明確にし、定期的に思い出す</li>
                <li>大きな目標を小さな達成可能なステップに分解する</li>
                <li>進捗を視覚化し、成果を実感できるようにする</li>
                <li>モチベーションが下がった時のための対処法を事前に計画しておく</li>
                <li>自分へのご褒美システムを作り、小さな成功を祝う</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 学習傾向に基づく提案
    st.markdown("### 学習効率を高める提案")
    
    learning_style = user_profile.get("learning_style", "unknown")
    
    if learning_style != "unknown":
        style_desc = {
            "visual": "視覚的な情報から最も効果的に学ぶ",
            "practical": "実践を通じて最も効果的に学ぶ",
            "theoretical": "概念や理論から最も効果的に学ぶ"
        }
        
        style_strategies = {
            "visual": [
                "情報を図表やチャート、マインドマップなどに視覚化する",
                "カラーコーディングを使って情報を整理する",
                "ビデオやイメージを活用した学習リソースを選ぶ",
                "学んだことを図やダイアグラムとして描き出す"
            ],
            "practical": [
                "理論を学んだらすぐに実践する機会を作る",
                "実際のプロジェクトを通じて学習する",
                "ロールプレイや実験、体験型のワークショップを活用する",
                "学んだことを実生活に応用する方法を常に考える"
            ],
            "theoretical": [
                "概念や原理を深く理解することに時間をかける",
                "体系的に整理された教材や書籍を選ぶ",
                "学んだことを論理的な構造にまとめる",
                "背景にある理論や研究を探求する"
            ]
        }
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>あなたは{style_desc[learning_style]}タイプです！</h4>
            <p>あなたのデータを分析したところ、{style_desc[learning_style]}タイプであることがわかりました。このタイプに合わせた学習方法を取り入れることで、より効率的に知識やスキルを習得できます。</p>
            <ul class="strategy-list">
        """, unsafe_allow_html=True)
        
        for strategy in style_strategies[learning_style]:
            st.markdown(f"<li>{strategy}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        # デフォルトの学習スタイル提案
        st.markdown(f"""
        <div class="insight-card">
            <h4>学習スタイルを分析中...</h4>
            <p>まだ十分なデータがないため、あなたの学習スタイルを特定できていません。より多くの活動データが集まると、パーソナライズされた提案ができるようになります。</p>
            <p>効果的な学習のためには、複数のアプローチを組み合わせると良いでしょう：</p>
            <ul class="strategy-list">
                <li>視覚的要素（図表、チャート、ビデオ）を活用する</li>
                <li>実践的な応用（演習、プロジェクト、実験）を取り入れる</li>
                <li>概念的理解（理論、背景、体系的知識）を深める</li>
                <li>異なる学習方法を試し、最も効果的なものを見つける</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 次のステップ提案
    st.markdown("### 次のステップ提案")
    
    # AIインサイトから次のステップを提案
    if ai_insights.get("goal_insights"):
        # 最新の目標インサイトを取得
        latest_goal_insight = ai_insights["goal_insights"][-1]
        
        st.markdown(f"""
        <div class="strategy-card">
            <h4>{latest_goal_insight['title']}</h4>
            <p>{latest_goal_insight['description']}</p>
            <h5>推奨アクション：</h5>
            <ul class="strategy-list">
        """, unsafe_allow_html=True)
        
        for action in latest_goal_insight.get('actions', []):
            st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        # デフォルトの次のステップ提案
        next_steps = [
            "「今日のチェックイン」機能を使って、毎日の状態と進捗を記録してみましょう",
            "「SMART目標設定」で具体的な目標を設定し、小さなタスクに分解してみましょう",
            "「習慣ダッシュボード」で継続的な習慣を形成し、記録してみましょう",
            "「感情ログ」で日々の感情を記録し、パターンを把握してみましょう",
            "「AIチャットサポート」で具体的な悩みや質問を相談してみましょう"
        ]
        
        st.markdown(f"""
        <div class="strategy-card">
            <h4>次に試してみると良いこと</h4>
            <p>アプリの機能をより活用し、自己成長を加速させるための提案です：</p>
            <ul class="strategy-list">
        """, unsafe_allow_html=True)
        
        for step in next_steps:
            st.markdown(f"<li>{step}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 戦略カスタマイズ
    st.markdown("### 戦略のカスタマイズ")
    
    st.markdown("""
    提案された戦略をあなた自身の状況に合わせてカスタマイズしましょう。
    以下のボタンをクリックすると、より詳細な質問に答えることで、さらにパーソナライズされた提案を受け取ることができます。
    """)
    
    if st.button("戦略をカスタマイズする"):
        st.session_state.customize_strategy = True
    
    if st.session_state.get('customize_strategy', False):
        with st.form("strategy_customize_form"):
            st.markdown("#### 現在の状況を教えてください")
            
            current_focus = st.selectbox(
                "現在最も注力している分野は？",
                ["仕事・キャリア", "学習・スキル", "健康・運動", "人間関係", "趣味・創作", "精神的充足", "その他"]
            )
            
            time_available = st.slider("1日にどれくらいの時間を目標達成に使えますか？（分）", 5, 180, 30, step=5)
            
            motivation_level = st.slider("現在のモチベーションレベルは？", 1, 10, 5)
            
            biggest_obstacle = st.text_area("現在の最大の障害は何ですか？")
            
            submit_button = st.form_submit_button("カスタマイズした戦略を生成")
            
            if submit_button:
                # カスタマイズされた戦略を生成
                custom_strategy = generate_custom_strategy(
                    current_focus,
                    time_available,
                    motivation_level,
                    biggest_obstacle
                )
                
                st.markdown(f"""
                <div class="strategy-card">
                    <h4>あなた専用のカスタマイズ戦略</h4>
                    {custom_strategy}
                </div>
                """, unsafe_allow_html=True)
                
                # セッション状態をリセット
                st.session_state.customize_strategy = False

# AIレスポンス生成関数群
def generate_ai_response(user_message):
    """ユーザーのメッセージに対するAIの応答を生成する"""
    # メッセージから意図を推測
    intent = detect_intent(user_message)
    
    # 意図に基づいて適切な応答を生成
    if intent == "motivation":
        return generate_motivation_boost()
    elif intent == "goal_advice":
        return generate_goal_advice()
    elif intent == "habit_formation":
        return generate_habit_advice()
    elif intent == "strength_analysis":
        return generate_strength_analysis()
    elif intent == "time_management":
        return generate_time_management_advice()
    elif intent == "self_doubt":
        return generate_self_doubt_response()
    else:
        # 一般的な応答
        responses = [
            "ご質問ありがとうございます。もう少し具体的に教えていただけると、より適切なアドバイスができます。",
            "なるほど、理解しました。その点については、あなたの過去のデータからいくつかの洞察を得ることができます。",
            "その質問について考えてみました。あなたの活動パターンに基づくと、以下のようなアプローチが効果的かもしれません。",
            "興味深い質問ですね。あなたの強みを活かすという観点から考えると、次のような方法が考えられます。"
        ]
        return random.choice(responses) + " さらに何か具体的なことについて聞きたいことはありますか？モチベーション管理、目標設定、習慣形成などについてアドバイスできます。"

def detect_intent(message):
    """メッセージから意図を推測する"""
    message = message.lower()
    
    # モチベーション関連
    if any(word in message for word in ["モチベーション", "やる気", "意欲", "やる気が出ない", "続かない"]):
        return "motivation"
    
    # 目標設定・達成関連
    elif any(word in message for word in ["目標", "達成", "計画", "戦略", "成功"]):
        return "goal_advice"
    
    # 習慣形成関連
    elif any(word in message for word in ["習慣", "継続", "毎日", "ルーティン"]):
        return "habit_formation"
    
    # 強み分析関連
    elif any(word in message for word in ["強み", "長所", "得意", "スキル", "能力"]):
        return "strength_analysis"
    
    # 時間管理関連
    elif any(word in message for word in ["時間", "管理", "効率", "生産性", "忙しい"]):
        return "time_management"
    
    # 自己疑念関連
    elif any(word in message for word in ["自信", "不安", "心配", "怖い", "失敗"]):
        return "self_doubt"
    
    # 意図が特定できない場合
    else:
        return "unknown"

def generate_motivation_boost():
    """モチベーション向上のアドバイスを生成する"""
    # ユーザープロファイルから最適なアドバイスを生成
    user_profile = load_user_profile()
    
    # モチベーショントリガーがあれば活用
    motivation_triggers = user_profile.get("motivation_triggers", [])
    
    if motivation_triggers:
        trigger = random.choice(motivation_triggers)
        advice = f"""
        <p>モチベーションが下がっているようですね。あなたのデータを分析したところ、「<strong>{trigger}</strong>」がモチベーションを高める効果があるようです。</p>
        <p>今日は以下のことを試してみてはいかがでしょうか：</p>
        <ul>
            <li>{trigger}に関連したアクションを取る</li>
            <li>小さな目標を設定し、達成感を味わう</li>
            <li>過去の成功体験を振り返る</li>
        </ul>
        <p>また、モチベーションは一時的に下がることがあっても自然なことです。無理せず、小さな一歩から再開していきましょう。</p>
        """
    else:
        # 一般的なモチベーションアドバイス
        advice = """
        <p>モチベーションが下がっているようですね。これは誰にでも起こる自然なことです。</p>
        <p>以下のアプローチが効果的かもしれません：</p>
        <ul>
            <li>「5分だけ」と決めて、小さく始めてみる</li>
            <li>目標を思い出し、「なぜ」これを達成したいのかを再確認する</li>
            <li>過去の成功体験を振り返り、自分の能力を思い出す</li>
            <li>環境を変えてみる（場所を変える、音楽をかける、などの小さな変化）</li>
            <li>誰かに話すか、サポートを求める</li>
        </ul>
        <p>モチベーションの波は自然なものです。大切なのは、感情に関わらず一貫した行動を続けることです。</p>
        """
    
    return advice   

def generate_goal_advice():
    """目標達成のアドバイスを生成する"""
    # ユーザープロファイルから最適なアドバイスを生成
    user_profile = load_user_profile()
    
    # 目標パターンに基づくアドバイス
    goal_pattern = user_profile.get("goal_pattern", "unknown")
    
    if goal_pattern == "short_term":
        advice = """
        <p>あなたのデータを分析したところ、短期目標を積み重ねる方法が最も効果的であることがわかりました。</p>
        <p>目標達成に向けて、以下の方法を試してみてください：</p>
        <ul>
            <li>大きな目標を週単位や日単位の小さなタスクに分割する</li>
            <li>毎日の小さな成功体験を記録し、進捗を可視化する</li>
            <li>完璧を目指すよりも、継続することを優先する</li>
            <li>一日ごとに「今日だけ」という意識で取り組む</li>
            <li>小さな達成を積極的に祝い、自己肯定感を高める</li>
        </ul>
        <p>小さな一歩の積み重ねが、大きな変化を生み出します！</p>
        """
    elif goal_pattern == "long_term":
        advice = """
        <p>あなたのデータを分析したところ、長期的な視点で計画を立てるアプローチが最も効果的であることがわかりました。</p>
        <p>目標達成に向けて、以下の方法を試してみてください：</p>
        <ul>
            <li>明確なビジョンを設定し、そこから逆算して中期・短期目標を立てる</li>
            <li>定期的（週次・月次）に進捗を振り返り、必要に応じて計画を調整する</li>
            <li>進捗を測定するための具体的な指標を設定する</li>
            <li>一時的な挫折に一喜一憂せず、大きな流れを重視する</li>
            <li>目標達成までのロードマップを視覚化し、常に参照できるようにする</li>
        </ul>
        <p>明確なビジョンと計画が、確実な目標達成につながります！</p>
        """
    else:
        # 一般的な目標達成アドバイス
        advice = """
        <p>効果的な目標達成のためには、SMART基準（具体的、測定可能、達成可能、関連性、期限付き）で目標を設定することが重要です。</p>
        <p>目標達成に向けて、以下の方法を試してみてください：</p>
        <ul>
            <li>目標を具体的かつ測定可能な形で定義し、期限を設定する</li>
            <li>大きな目標を小さなステップに分解し、それぞれに期限を設ける</li>
            <li>進捗を定期的に記録し、可視化する</li>
            <li>目標達成の「なぜ」を明確にし、モチベーションを維持する</li>
            <li>障害となりそうなことを事前に特定し、対策を立てる</li>
            <li>定期的に振り返りと調整を行い、柔軟に対応する</li>
        </ul>
        <p>継続的な取り組みと定期的な振り返りが、目標達成への近道です！</p>
        """
    
    return advice

def generate_habit_advice():
    """習慣形成のアドバイスを生成する"""
    # ユーザープロファイルから最適なアドバイスを生成
    user_profile = load_user_profile()
    
    # 学習スタイルに基づくアドバイス
    learning_style = user_profile.get("learning_style", "unknown")
    
    if learning_style == "visual":
        advice = """
        <p>あなたは視覚的な情報から効果的に学ぶタイプです。習慣形成にも視覚的な要素を取り入れると効果的でしょう。</p>
        <p>習慣形成のために、以下の方法を試してみてください：</p>
        <ul>
            <li>習慣トラッカーを使用し、進捗を視覚的に確認する</li>
            <li>カレンダーやチャートを使って連続達成日数を記録する</li>
            <li>習慣を思い出させるための視覚的なリマインダーを設置する</li>
            <li>達成したい習慣の理想像を視覚化し、イメージする時間を持つ</li>
            <li>習慣形成の過程や結果を写真や動画で記録する</li>
        </ul>
        <p>視覚的なフィードバックが、あなたの習慣形成を促進します！</p>
        """
    elif learning_style == "practical":
        advice = """
        <p>あなたは実践を通じて効果的に学ぶタイプです。習慣形成にも実践的なアプローチが効果的でしょう。</p>
        <p>習慣形成のために、以下の方法を試してみてください：</p>
        <ul>
            <li>習慣を小さな実践的なステップに分解する</li>
            <li>新しい習慣を既存のルーティンに組み込む「習慣の連鎖」を活用する</li>
            <li>環境を最適化し、習慣実行のハードルを下げる</li>
            <li>様々なアプローチを試し、自分に最も効果的な方法を見つける</li>
            <li>実際の行動変化に焦点を当て、結果を測定する</li>
        </ul>
        <p>実践と試行錯誤が、あなたの習慣形成を促進します！</p>
        """
    elif learning_style == "theoretical":
        advice = """
        <p>あなたは概念や理論から効果的に学ぶタイプです。習慣形成にも理論的な理解が効果的でしょう。</p>
        <p>習慣形成のために、以下の方法を試してみてください：</p>
        <ul>
            <li>習慣形成のメカニズム（きっかけ→行動→報酬のループなど）を理解する</li>
            <li>習慣形成に関する書籍や研究から知識を得る</li>
            <li>習慣形成の過程を詳細に記録し、パターンを分析する</li>
            <li>「なぜ」その習慣が重要なのかを深く理解し、内的動機を強化する</li>
            <li>目標と習慣の関連性を明確にし、体系的なアプローチを取る</li>
        </ul>
        <p>深い理解と体系的なアプローチが、あなたの習慣形成を促進します！</p>
        """
    else:
        # 一般的な習慣形成アドバイス
        advice = """
        <p>効果的な習慣形成には、行動科学の原則を活用することが重要です。</p>
        <p>習慣形成のために、以下の方法を試してみてください：</p>
        <ul>
            <li>新しい習慣を非常に小さく始める（例：「2分ルール」を適用する）</li>
            <li>新しい習慣を既存の習慣に「連鎖」させる（例：「コーヒーを飲んだ後に5分間瞑想する」）</li>
            <li>環境を整え、習慣の実行をできるだけ簡単にする</li>
            <li>即時的な報酬を設定し、ポジティブな感情と結びつける</li>
            <li>「習慣の追跡」を行い、連続記録（ストリーク）を作る</li>
            <li>「もし○○なら、△△する」という実行意図を設定する</li>
        </ul>
        <p>一貫性と小さな成功の積み重ねが、新しい習慣の定着につながります！</p>
        """
    
    return advice

def generate_strength_analysis():
    """強み分析のレスポンスを生成する"""
    # ユーザープロファイルから強みを抽出
    user_profile = load_user_profile()
    strength_areas = user_profile.get("strength_areas", [])
    
    if strength_areas:
        # 強みに基づくレスポンス
        strengths_html = ""
        for strength in strength_areas[:3]:  # 最大3つの強みを表示
            strengths_html += f"<li><strong>{strength}</strong></li>"
        
        advice = f"""
        <p>あなたのデータを分析した結果、以下のような強みが見られます：</p>
        <ul>
            {strengths_html}
        </ul>
        <p>これらの強みを意識的に活用することで、目標達成や自己成長がより効果的になります。例えば：</p>
        <ul>
            <li>強みを活かせる状況や機会を積極的に選ぶ</li>
            <li>課題に直面した際に、これらの強みをどう活用できるか考える</li>
            <li>強みをさらに伸ばすための学習や練習に取り組む</li>
            <li>強みを活かして他者をサポートしたり、価値を提供する</li>
        </ul>
        <p>あなたの強みは、自信を持って活用できる大きな資産です！</p>
        """
    else:
        # 強みデータがない場合の一般的なレスポンス
        advice = """
        <p>まだ十分なデータがないため、具体的な強みを特定できていません。しかし、強みを発見するためのいくつかの方法があります：</p>
        <ul>
            <li>過去の成功体験や達成を振り返り、そこで発揮された能力を特定する</li>
            <li>エネルギーを感じる活動や、時間を忘れて没頭できる活動に注目する</li>
            <li>周囲の人からのフィードバックに耳を傾け、評価されている点を集める</li>
            <li>様々な活動に取り組み、自然と高いパフォーマンスを発揮できる分野を見つける</li>
            <li>「成長の記録」や「小さな成功の記録」機能を使って、データを蓄積する</li>
        </ul>
        <p>強みを理解し活用することで、自己肯定感が高まり、目標達成も効率的になります！</p>
        """
    
    return advice

def generate_time_management_advice():
    """時間管理のアドバイスを生成する"""
    # ユーザープロファイルから最適なアドバイスを生成
    user_profile = load_user_profile()
    
    # 生産性の高い時間帯に基づくアドバイス
    productive_time = user_profile.get("productive_time", "unknown")
    
    if productive_time != "unknown":
        time_desc = {
            "morning": "朝の時間帯",
            "afternoon": "午後の時間帯",
            "evening": "夕方から夜の時間帯"
        }
        
        advice = f"""
        <p>あなたのデータを分析したところ、<strong>{time_desc[productive_time]}</strong>に最も生産性が高いことがわかりました。</p>
        <p>時間管理を最適化するために、以下の方法を試してみてください：</p>
        <ul>
            <li>最も重要なタスクや集中力を要する作業は{time_desc[productive_time]}に計画する</li>
            <li>{time_desc[productive_time]}の時間を最大限確保できるようにスケジュールを調整する</li>
            <li>この時間帯は通知やメールをオフにし、深い集中（ディープワーク）のために環境を整える</li>
            <li>他の時間帯は、ルーティンワークや準備作業、打ち合わせなどに充てる</li>
            <li>定期的に時間の使い方を記録し、最適化の余地を見つける</li>
        </ul>
        <p>あなたの生産性リズムに合わせた時間管理が、効率と成果を高めます！</p>
        """
    else:
        # 一般的な時間管理アドバイス
        advice = """
        <p>効果的な時間管理は、目標達成と自己成長の重要な要素です。</p>
        <p>時間管理を改善するために、以下の方法を試してみてください：</p>
        <ul>
            <li>「重要かつ緊急」のマトリックスを使って、タスクの優先順位を決める</li>
            <li>一日の始めに、その日の「最重要タスク」を3つ特定する</li>
            <li>ポモドーロテクニック（25分集中＋5分休憩）を活用する</li>
            <li>「タイムブロッキング」で、重要なタスクに事前に時間を確保する</li>
            <li>定期的に「時間監査」を行い、時間の使い方を分析する</li>
            <li>「バッチ処理」で同種のタスクをまとめて効率化する</li>
            <li>「2分ルール」を適用し、すぐにできる小さなタスクはその場で片付ける</li>
        </ul>
        <p>また、自分の生産性が高い時間帯を観察し、その時間に最も重要なタスクを行うと効果的です。</p>
        """
    
    return advice

def generate_self_doubt_response():
    """自己疑念に対するレスポンスを生成する"""
    # 日々のログからポジティブな記録を抽出
    small_wins = load_small_wins()
    success_evidence = []
    
    if not small_wins.empty and 'description' in small_wins.columns:
        # 最新のポジティブな記録を取得
        recent_wins = small_wins.sort_values('date', ascending=False).head(3)
        if not recent_wins.empty:
            for _, win in recent_wins.iterrows():
                success_evidence.append(win['description'])
    
    if success_evidence:
        # 成功体験に基づくレスポンス
        evidence_html = ""
        for evidence in success_evidence:
            evidence_html += f"<li>{evidence}</li>"
        
        advice = f"""
        <p>自信が揺らいでいるようですね。自己疑念は誰にでも訪れるものですが、それを乗り越えるためのリソースは既にあなたの中にあります。</p>
        <p>あなたの最近の成功体験を思い出してみましょう：</p>
        <ul>
            {evidence_html}
        </ul>
        <p>これらの体験は、あなたの能力と可能性の証拠です。困難な状況で、これらの成功体験を思い出すことが助けになります。</p>
        <p>また、以下のアプローチも効果的です：</p>
        <ul>
            <li>「完璧」を目指すのではなく、「進歩」に焦点を当てる</li>
            <li>失敗を「学びの機会」として捉え直す</li>
            <li>自分に対して、親しい友人に話すような優しい言葉をかける</li>
            <li>小さな一歩から始め、達成感を積み重ねる</li>
        </ul>
        <p>自己疑念は一時的なものです。あなたの成長の証拠に目を向けることで、自信を取り戻せます。</p>
        """
    else:
        # 一般的な自己疑念対応
        advice = """
        <p>自信が揺らいでいるようですね。自己疑念は誰にでも訪れるものですが、それを乗り越えるための方法がいくつかあります。</p>
        <p>自己疑念に対処するために、以下のアプローチを試してみてください：</p>
        <ul>
            <li>過去の成功体験や克服した困難を思い出し、自分の能力を再確認する</li>
            <li>内なる批判的な声に気づき、それを客観的に検証する</li>
            <li>「もし友人がこの状況にいたら、何とアドバイスするか」と考え、自分自身にも同じ言葉をかける</li>
            <li>完璧主義を手放し、「十分に良い」状態を受け入れる</li>
            <li>小さな一歩から始め、達成感を積み重ねる</li>
            <li>自分の強みや価値を思い出し、それらに焦点を当てる</li>
            <li>必要に応じて、信頼できる人にサポートを求める</li>
        </ul>
        <p>自己疑念は成長過程の自然な一部です。それを克服するたびに、より強くなっていきます。</p>
        """
    
    return advice

def generate_daily_feedback(mood, progress, insights, challenges):
    """日々のチェックインに対するAIフィードバックを生成する"""
    # 気分と進捗に基づくフィードバック
    feedback = ""
    
    # 気分に応じたフィードバック
    if mood >= 8:
        feedback += f"今日は調子が良いようですね！この良い状態を観察し、何が今日の良い気分に貢献しているのか注目してみましょう。"
    elif mood >= 5:
        feedback += f"安定した状態をキープしていますね。"
    else:
        feedback += f"今日は少し調子が優れないようですね。無理せず、自分を労わる時間を取りましょう。"
    
    # 進捗に応じたフィードバック
    if progress >= 8:
        feedback += f" 目標への進捗も素晴らしいです！この勢いを維持していきましょう。"
    elif progress >= 5:
        feedback += f" 目標に向けて着実に進んでいます。一歩ずつ、確実に前進していきましょう。"
    else:
        feedback += f" 目標の進捗には課題があるようです。小さなステップに分解して、取り組みやすくすることも一つの方法です。"
    
    # 気づきと課題に基づく具体的なアドバイス
    if insights:
        # 気づきからキーワードを抽出
        keywords = insights.lower().split()
        
        if any(word in keywords for word in ["早起き", "朝", "早い", "早朝"]):
            feedback += f" 早起きの効果に気づかれたようですね。朝の時間を効果的に活用することで、一日全体の生産性が向上することが多いです。"
        
        if any(word in keywords for word in ["集中", "フォーカス", "没頭"]):
            feedback += f" 集中力に関する気づきがありましたね。深い集中状態（フロー状態）を作り出すには、通知をオフにし、一つのタスクに25分間集中するポモドーロテクニックも効果的です。"
    
    if challenges:
        # 課題からキーワードを抽出
        keywords = challenges.lower().split()
        
        if any(word in keywords for word in ["時間", "忙しい", "余裕"]):
            feedback += f" 時間管理に課題を感じているようですね。「急ぎではないが重要なこと」に時間を確保するために、一日の始めに最重要タスクを決めて取り組む方法が効果的です。"
        
        if any(word in keywords for word in ["モチベーション", "やる気", "意欲"]):
            feedback += f" モチベーション維持に課題があるようです。大きな目標を小さなステップに分解し、各ステップの達成を祝うことで、モチベーションを維持しやすくなります。"
    
    # 一般的なアドバイスを追加
    general_advice = [
        "今日の経験を記録することで、パターンを発見し、自己理解を深めることができます。",
        "小さな成功体験も見逃さず、意識的に認識することが自己肯定感を高めます。",
        "困難に直面した時こそ、自分がなぜその目標を追求しているのか、根本的な「なぜ」を思い出すことが大切です。",
        "継続は力なり。完璧でなくても、コンスタントに小さな一歩を積み重ねていきましょう。",
        "自分に優しく接すること。自己批判は進歩の妨げになることがあります。"
    ]
    
    feedback += f" {random.choice(general_advice)}"
    
    return feedback

def generate_weekly_report(start_of_week, end_of_week):
    """週間レポートを生成する"""
    # 日付範囲の文字列
    week_range = f"{start_of_week.strftime('%Y-%m-%d')}_{end_of_week.strftime('%Y-%m-%d')}"
    
    # 一週間のデータを集計
    daily_logs = load_ai_daily_logs()
    
    # 日付を変換
    if not daily_logs.empty and 'date' in daily_logs.columns:
        daily_logs['date'] = pd.to_datetime(daily_logs['date']).dt.date
    
    # 指定した週のデータをフィルタリング
    week_logs = daily_logs[(daily_logs['date'] >= start_of_week) & (daily_logs['date'] <= end_of_week)] if not daily_logs.empty else pd.DataFrame()
    
    # 日々のデータを収集
    daily_data = []
    if not week_logs.empty:
        for _, log in week_logs.iterrows():
            daily_data.append({
                'date': log['date'].strftime('%Y-%m-%d'),
                'mood': log['mood'],
                'progress': log['progress'],
                'insights': log['insights'],
                'challenges': log['challenges']
            })
    
    # 達成したことのリスト
    achievements = []
    
    # 週間の小さな成功体験を抽出
    small_wins = load_small_wins()
    if not small_wins.empty and 'date' in small_wins.columns:
        small_wins['date'] = pd.to_datetime(small_wins['date']).dt.date
        week_wins = small_wins[(small_wins['date'] >= start_of_week) & (small_wins['date'] <= end_of_week)]
        
        if not week_wins.empty and 'description' in week_wins.columns:
            for _, win in week_wins.iterrows():
                achievements.append(win['description'])
    
    # 週間の気づきや学びのリスト
    insights = []
    
    # 日々のログから気づきを抽出
    if not week_logs.empty and 'insights' in week_logs.columns:
        for _, log in week_logs.iterrows():
            if log['insights']:
                insights.append(log['insights'])
    
    # 週間の課題や困難のリスト
    challenges = []
    
    # 日々のログから課題を抽出
    if not week_logs.empty and 'challenges' in week_logs.columns:
        for _, log in week_logs.iterrows():
            if log['challenges']:
                challenges.append(log['challenges'])
    
    # 来週の戦略提案
    strategies = []
    
    # 課題に基づく戦略を生成
    if challenges:
        for challenge in challenges[:3]:  # 上位3つの課題に対する戦略
            if "時間" in challenge.lower():
                strategies.append("時間管理を改善するために「タイムブロッキング」を試してみる。一日の始めに、重要なタスクのための時間を予め確保しておく。")
            elif "モチベーション" in challenge.lower() or "やる気" in challenge.lower():
                strategies.append("モチベーション低下に対しては「5分ルール」を試してみる。まずは5分だけ始める約束をし、多くの場合はそのまま続けられるようになる。")
            elif "集中" in challenge.lower():
                strategies.append("集中力向上のためにポモドーロテクニック（25分集中＋5分休憩）を活用し、集中と休息のリズムを作る。")
            else:
                strategies.append(f"「{challenge[:20]}...」という課題に対しては、問題を小さく分解し、一つずつ対処する戦略を取る。")
    
    # デフォルトの戦略提案
    if len(strategies) < 3:
        default_strategies = [
            "週の始めに「最重要目標」を3つ特定し、それらに焦点を当てる",
            "毎日、短時間でも目標に向けた行動を取る「習慣の連鎖」を意識する",
            "週末に振り返りの時間を設け、進捗を確認し、次週の計画を立てる",
            "「完璧」を目指すのではなく、「継続」を重視する姿勢を持つ",
            "自分の生産性が高い時間帯を特定し、その時間に最重要タスクに取り組む"
        ]
        for strategy in default_strategies:
            if len(strategies) < 3:
                strategies.append(strategy)
    
    # レポートデータを構築
    report = {
        "week_range": week_range,
        "achievements": achievements[:5],  # 最大5つの達成
        "insights": insights[:5],  # 最大5つの気づき
        "challenges": challenges[:5],  # 最大5つの課題
        "strategies": strategies[:5],  # 最大5つの戦略
        "daily_data": daily_data,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return report 

def generate_custom_strategy(focus_area, time_available, motivation_level, obstacle):
    """ユーザーの現在の状況に合わせてカスタマイズされた戦略を生成する"""
    
    # ユーザープロファイル読み込み
    user_profile = load_user_profile()
    
    # 時間に応じた戦略
    time_strategy = ""
    if time_available <= 15:
        time_strategy = f"""
        <p>1日{time_available}分という限られた時間でも効果的に取り組める方法：</p>
        <ul class="strategy-list">
            <li>「小さな習慣」アプローチを活用し、わずか2分でも実行できるミニマルバージョンを設定する</li>
            <li>「タイマー集中法」で、短時間でも集中して取り組む</li>
            <li>日常の隙間時間（通勤中、待ち時間など）を活用する</li>
        </ul>
        """
    elif time_available <= 45:
        time_strategy = f"""
        <p>1日{time_available}分の時間を最大限に活用する方法：</p>
        <ul class="strategy-list">
            <li>ポモドーロテクニック（25分集中＋5分休憩）を活用する</li>
            <li>事前に明確な「今日の最小目標」を設定し、限られた時間で最大の効果を得る</li>
            <li>集中を妨げる要素（通知、雑音など）を事前に排除する環境を整える</li>
        </ul>
        """
    else:
        time_strategy = f"""
        <p>1日{time_available}分という貴重な時間を効果的に構造化する方法：</p>
        <ul class="strategy-list">
            <li>時間を「集中ブロック」と「振り返りブロック」に分割する</li>
            <li>複数のセッションに分けて、エネルギーレベルが高い時間帯に配置する</li>
            <li>長時間集中のために「ディープワークプロトコル」を確立する</li>
        </ul>
        """
    
    # モチベーションレベルに応じた戦略
    motivation_strategy = ""
    if motivation_level <= 3:
        motivation_strategy = f"""
        <p>現在のモチベーションが低い状態でも前進するための方法：</p>
        <ul class="strategy-list">
            <li>「5分だけ」ルールを適用し、まずは短時間だけ始めてみる</li>
            <li>感情ではなく「システム」に従って行動する習慣を作る</li>
            <li>成功イメージを視覚化し、目標達成後の感覚を思い出す</li>
            <li>自分へのご褒美を設定し、小さな達成にも報酬を与える</li>
        </ul>
        """
    elif motivation_level <= 7:
        motivation_strategy = f"""
        <p>現在の安定したモチベーションを維持・強化する方法：</p>
        <ul class="strategy-list">
            <li>定期的に「なぜ」この目標が重要なのかを振り返る時間を設ける</li>
            <li>進捗を視覚化し、成果を実感できるようにする</li>
            <li>学習やフィードバックのループを作り、常に改善していく感覚を持つ</li>
        </ul>
        """
    else:
        motivation_strategy = f"""
        <p>現在の高いモチベーションを最大限に活かす方法：</p>
        <ul class="strategy-list">
            <li>「バッチ処理」で関連タスクをまとめて効率的に進める</li>
            <li>難易度の高いタスクや先延ばしにしていた課題に取り組む</li>
            <li>長期的な基盤作りや、将来のモチベーション低下時に役立つシステムを構築する</li>
        </ul>
        """
    
    # フォーカスエリアに応じた戦略
    focus_strategy = ""
    focus_strategies = {
        "仕事・キャリア": """
        <p>仕事・キャリア分野で最大の成果を出すための方法：</p>
        <ul class="strategy-list">
            <li>「重要だが緊急ではない」領域のタスクに計画的に時間を割り当てる</li>
            <li>スキルマトリックスを作成し、最も成長が必要な領域を特定する</li>
            <li>成果を数値化・可視化し、定期的に振り返る習慣をつける</li>
        </ul>
        """,
        "学習・スキル": """
        <p>学習・スキル習得を効率化する方法：</p>
        <ul class="strategy-list">
            <li>「分散学習」を活用し、短時間でも継続的に取り組む</li>
            <li>「アウトプット駆動型学習」で、学んだことをすぐに実践・教えることで定着させる</li>
            <li>目標スキルの「最小実用レベル」を定義し、そこに向かって集中的に取り組む</li>
        </ul>
        """,
        "健康・運動": """
        <p>健康・運動習慣を確実に定着させる方法：</p>
        <ul class="strategy-list">
            <li>「習慣の連鎖」を活用し、既存のルーティンに新しい健康習慣を紐づける</li>
            <li>環境を最適化し、運動・健康的な選択をデフォルトにする</li>
            <li>即時的なフィードバックループを作り、小さな成功を実感できるようにする</li>
        </ul>
        """,
        "人間関係": """
        <p>人間関係を育み、深める効果的な方法：</p>
        <ul class="strategy-list">
            <li>「質問の技術」を磨き、相手に対する真の興味と理解を示す</li>
            <li>「感謝の習慣」を取り入れ、定期的に感謝の気持ちを表現する</li>
            <li>共有体験を計画的に作り、思い出と絆を深める機会を増やす</li>
        </ul>
        """,
        "趣味・創作": """
        <p>趣味・創作活動を充実させる方法：</p>
        <ul class="strategy-list">
            <li>「創造的なルーティン」を確立し、インスピレーションに頼らず定期的に創作する</li>
            <li>「共有コミットメント」を活用し、同じ興味を持つコミュニティに参加する</li>
            <li>「進化する目標」を設定し、常に新しい挑戦と成長の機会を作る</li>
        </ul>
        """,
        "精神的充足": """
        <p>精神的充足と内面の平和を育む方法：</p>
        <ul class="strategy-list">
            <li>「マインドフルネス実践」を日常に取り入れ、現在の瞬間に意識を向ける</li>
            <li>「価値観の明確化」を行い、本当に大切にしたいことに時間とエネルギーを使う</li>
            <li>「感謝日記」で、日々の小さな喜びや感謝を意識的に記録する</li>
        </ul>
        """,
        "その他": """
        <p>目標達成のための汎用的な効果的アプローチ：</p>
        <ul class="strategy-list">
            <li>「小さな一歩」戦略で、大きな目標を達成可能な小さなステップに分解する</li>
            <li>「アカウンタビリティ」を活用し、誰かに進捗を報告する仕組みを作る</li>
            <li>「振り返りと最適化」を定期的に行い、アプローチを継続的に改善する</li>
        </ul>
        """
    }
    
    focus_strategy = focus_strategies.get(focus_area, focus_strategies["その他"])
    
    # 障害に対する戦略
    obstacle_strategy = ""
    if obstacle:
        obstacle_keywords = obstacle.lower()
        
        if any(word in obstacle_keywords for word in ["時間", "忙しい", "余裕"]):
            obstacle_strategy = """
            <p>時間不足の障害に対処する方法：</p>
            <ul class="strategy-list">
                <li>「時間監査」を行い、実際の時間の使い方を把握する</li>
                <li>「バッファタイム」を意識的に設け、予想外の事態に対応できるようにする</li>
                <li>「委任と削減」で、重要度の低いタスクを減らす</li>
            </ul>
            """
        elif any(word in obstacle_keywords for word in ["モチベーション", "やる気", "意欲", "続かない"]):
            obstacle_strategy = """
            <p>モチベーション維持の課題に対処する方法：</p>
            <ul class="strategy-list">
                <li>「目標の細分化」で、大きな目標を小さな達成可能な目標に分割する</li>
                <li>「進捗の可視化」で、成果を実感できるようにする</li>
                <li>「環境設計」で、目標行動のトリガーを増やし、障害を減らす</li>
            </ul>
            """
        elif any(word in obstacle_keywords for word in ["集中", "気が散る", "誘惑", "注意散漫"]):
            obstacle_strategy = """
            <p>集中力の課題に対処する方法：</p>
            <ul class="strategy-list">
                <li>「デジタルミニマリズム」を実践し、通知やSNSの誘惑を減らす</li>
                <li>「集中環境の確立」で、作業専用の物理的・心理的空間を作る</li>
                <li>「集中力回復ルーティン」で、定期的に脳を休息させる</li>
            </ul>
            """
        elif any(word in obstacle_keywords for word in ["不安", "心配", "怖い", "恐れ"]):
            obstacle_strategy = """
            <p>不安や恐れの感情に対処する方法：</p>
            <ul class="strategy-list">
                <li>「思考記録」で、不安な考えを書き出し、客観的に検証する</li>
                <li>「最悪のシナリオ計画」で、起こりうる最悪の事態と対処法を考える</li>
                <li>「小さな勇気の習慣」で、徐々に不安に立ち向かう経験を積む</li>
            </ul>
            """
        else:
            obstacle_strategy = f"""
            <p>「{obstacle[:50]}...」という障害に対処する方法：</p>
            <ul class="strategy-list">
                <li>「問題分解」で、障害を小さな取り組み可能な部分に分ける</li>
                <li>「代替アプローチ」を複数考え、様々な角度から問題に取り組む</li>
                <li>「専門知識の獲得」で、この特定の障害に関する情報や戦略を学ぶ</li>
            </ul>
            """
    
    # ユーザープロファイルに基づく個別化した戦略
    profile_strategy = ""
    
    goal_pattern = user_profile.get("goal_pattern", "unknown")
    if goal_pattern == "short_term":
        profile_strategy = """
        <p>あなたの短期目標志向に合わせた最適アプローチ：</p>
        <ul class="strategy-list">
            <li>週単位や日単位の小さな目標を設定し、頻繁に達成感を得る</li>
            <li>「今日だけ」という意識で、一日ごとに小さな前進を積み重ねる</li>
            <li>目に見える進捗トラッカーを活用し、成果を可視化する</li>
        </ul>
        """
    elif goal_pattern == "long_term":
        profile_strategy = """
        <p>あなたの長期志向に合わせた最適アプローチ：</p>
        <ul class="strategy-list">
            <li>大きなビジョンを明確にし、それに向かう「なぜ」を深く理解する</li>
            <li>長期目標から逆算した中期・短期の道筋を作る</li>
            <li>定期的な振り返りと調整のサイクルを確立する</li>
        </ul>
        """
    
    # 最終的なカスタマイズ戦略を構築
    custom_strategy = f"""
    <h4>あなた専用の{focus_area}戦略</h4>
    
    {time_strategy}
    
    {motivation_strategy}
    
    {focus_strategy}
    
    {obstacle_strategy}
    
    {profile_strategy if profile_strategy else ""}
    
    <p>これらの戦略を組み合わせ、あなたの状況に最適化してください。すべてを一度に実行する必要はありません。最も実行しやすいと感じるものから始めて、徐々に他の戦略も取り入れていくことをおすすめします。</p>
    """
    
    return custom_strategy

def update_user_profile_from_daily_log(mood, progress, insights, challenges):
    """日々のチェックインデータからユーザープロファイルを更新する"""
    user_profile = load_user_profile()
    
    # 直近のデータを分析
    daily_logs = load_ai_daily_logs()
    
    # 十分なデータがある場合（少なくとも7日分）
    if not daily_logs.empty and len(daily_logs) >= 7:
        # 目標達成パターンの分析
        # 短期目標の達成率と長期目標の達成率を比較
        goals_df = load_goals()
        
        if not goals_df.empty and 'goal_type' in goals_df.columns and 'status' in goals_df.columns:
            short_term_goals = goals_df[goals_df['goal_type'] == 'short_term']
            long_term_goals = goals_df[goals_df['goal_type'] == 'long_term']
            
            if not short_term_goals.empty and not long_term_goals.empty:
                short_term_completion_rate = len(short_term_goals[short_term_goals['status'] == 'completed']) / len(short_term_goals) if len(short_term_goals) > 0 else 0
                long_term_progress_rate = sum(long_term_goals['progress'].astype(float)) / (len(long_term_goals) * 100) if len(long_term_goals) > 0 else 0
                
                if short_term_completion_rate > long_term_progress_rate * 1.5:
                    user_profile['goal_pattern'] = 'short_term'
                elif long_term_progress_rate > short_term_completion_rate:
                    user_profile['goal_pattern'] = 'long_term'
        
        # 生産性の高い時間帯の分析
        activity_log = load_activity_log()
        
        if not activity_log.empty and 'timestamp' in activity_log.columns and 'productivity_rating' in activity_log.columns:
            activity_log['hour'] = pd.to_datetime(activity_log['timestamp']).dt.hour
            
            # 時間帯ごとの平均生産性
            morning_productivity = activity_log[(activity_log['hour'] >= 5) & (activity_log['hour'] < 12)]['productivity_rating'].mean()
            afternoon_productivity = activity_log[(activity_log['hour'] >= 12) & (activity_log['hour'] < 17)]['productivity_rating'].mean()
            evening_productivity = activity_log[(activity_log['hour'] >= 17) & (activity_log['hour'] < 23)]['productivity_rating'].mean()
            
            # 最も生産性の高い時間帯を特定
            max_productivity = max(morning_productivity, afternoon_productivity, evening_productivity)
            
            if not np.isnan(max_productivity):
                if max_productivity == morning_productivity:
                    user_profile['productive_time'] = 'morning'
                elif max_productivity == afternoon_productivity:
                    user_profile['productive_time'] = 'afternoon'
                elif max_productivity == evening_productivity:
                    user_profile['productive_time'] = 'evening'
        
        # 学習スタイルの分析
        growth_data = load_growth_data()
        
        if not growth_data.empty and 'learning_method' in growth_data.columns and 'effectiveness' in growth_data.columns:
            visual_effectiveness = growth_data[growth_data['learning_method'].str.contains('visual', case=False, na=False)]['effectiveness'].mean()
            practical_effectiveness = growth_data[growth_data['learning_method'].str.contains('practical|hands-on|experience', case=False, na=False)]['effectiveness'].mean()
            theoretical_effectiveness = growth_data[growth_data['learning_method'].str.contains('theoretical|reading|concept', case=False, na=False)]['effectiveness'].mean()
            
            # 最も効果的な学習スタイルを特定
            styles = {
                visual_effectiveness: 'visual',
                practical_effectiveness: 'practical',
                theoretical_effectiveness: 'theoretical'
            }
            
            max_effectiveness = max(visual_effectiveness, practical_effectiveness, theoretical_effectiveness)
            
            if not np.isnan(max_effectiveness):
                user_profile['learning_style'] = styles[max_effectiveness]
    
    # 今日のチェックインからモチベーショントリガーを更新
    if insights:
        # 気分が良い日の気づきからモチベーショントリガーを抽出
        if mood >= 7:
            # キーワード抽出（簡易版）
            keywords = re.findall(r'\b\w+\b', insights.lower())
            common_words = ['私', 'わたし', 'です', 'ます', 'した', 'ので', 'から', 'ながら', 'ている', 'いる', 'ある']
            keywords = [word for word in keywords if word not in common_words and len(word) > 1]
            
            # 頻出キーワードをモチベーショントリガーとして追加
            for keyword in keywords:
                if keyword not in user_profile['motivation_triggers']:
                    user_profile['motivation_triggers'].append(keyword)
                    # リストの長さを制限
                    if len(user_profile['motivation_triggers']) > 10:
                        user_profile['motivation_triggers'].pop(0)
    
    if challenges:
        # 気分が悪い日の課題からモチベーション低下要因を抽出
        if mood <= 4:
            # キーワード抽出（簡易版）
            keywords = re.findall(r'\b\w+\b', challenges.lower())
            common_words = ['私', 'わたし', 'です', 'ます', 'した', 'ので', 'から', 'ながら', 'ている', 'いる', 'ある']
            keywords = [word for word in keywords if word not in common_words and len(word) > 1]
            
            # 頻出キーワードをモチベーション低下要因として追加
            for keyword in keywords:
                if keyword not in user_profile['demotivation_triggers']:
                    user_profile['demotivation_triggers'].append(keyword)
                    # リストの長さを制限
                    if len(user_profile['demotivation_triggers']) > 10:
                        user_profile['demotivation_triggers'].pop(0)
    
    # 強みと改善点の更新
    habit_records = load_habit_records()
    tasks = load_tasks()
    
    if not habit_records.empty and 'habit_name' in habit_records.columns and 'completed' in habit_records.columns:
        # 習慣の完了率を計算
        habit_success = {}
        for habit in habit_records['habit_name'].unique():
            habit_data = habit_records[habit_records['habit_name'] == habit]
            completion_rate = habit_data['completed'].sum() / len(habit_data) if len(habit_data) > 0 else 0
            habit_success[habit] = completion_rate
        
        # 完了率の高い習慣を強みとして追加
        strengths = []
        for habit, rate in sorted(habit_success.items(), key=lambda x: x[1], reverse=True):
            if rate >= 0.7 and len(strengths) < 3:  # 70%以上の完了率を持つ習慣
                strengths.append(f"{habit}の継続力")
        
        # 既存の強みと組み合わせる
        existing_strengths = user_profile.get('strength_areas', [])
        user_profile['strength_areas'] = list(set(existing_strengths + strengths))[:5]  # 最大5つまで
        
        # 完了率の低い習慣を改善点として追加
        improvements = []
        for habit, rate in sorted(habit_success.items(), key=lambda x: x[1]):
            if rate <= 0.3 and len(improvements) < 3:  # 30%以下の完了率を持つ習慣
                improvements.append(f"{habit}の継続性")
        
        # 既存の改善点と組み合わせる
        existing_improvements = user_profile.get('improvement_areas', [])
        user_profile['improvement_areas'] = list(set(existing_improvements + improvements))[:5]  # 最大5つまで
    
    # パーソナリティ特性の更新
    emotion_logs = load_emotion_logs()
    
    if not emotion_logs.empty and 'emotion' in emotion_logs.columns:
        # 感情ログから回復力を推定
        negative_emotions = emotion_logs[emotion_logs['emotion'].isin(['悲しい', '不安', '怒り', 'フラストレーション', '落ち込み'])]
        
        if not negative_emotions.empty:
            # 感情の回復速度の分析
            negative_emotions['date'] = pd.to_datetime(negative_emotions['date'])
            negative_emotions = negative_emotions.sort_values('date')
            
            recovery_times = []
            for i in range(len(negative_emotions) - 1):
                current = negative_emotions.iloc[i]
                next_log = emotion_logs[emotion_logs['date'] > current['date']].sort_values('date').iloc[0] if not emotion_logs[emotion_logs['date'] > current['date']].empty else None
                
                if next_log is not None and next_log['emotion'] in ['幸せ', '満足', '穏やか', '前向き', '希望']:
                    recovery_time = (pd.to_datetime(next_log['date']) - pd.to_datetime(current['date'])).total_seconds() / 3600  # 時間単位
                    if recovery_time < 48:  # 2日以内の回復のみカウント
                        recovery_times.append(recovery_time)
            
            if recovery_times:
                avg_recovery_time = sum(recovery_times) / len(recovery_times)
                # 回復時間から回復力スコアを計算（短いほど高スコア）
                resilience_score = max(0, min(100, 100 - (avg_recovery_time / 48) * 100))
                user_profile['personality_traits']['resilience'] = int(resilience_score)
    
    # 最終更新日を記録
    user_profile['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    # 更新したプロファイルを保存
    save_user_profile(user_profile)

# 選択されたページに基づいて適切な関数を呼び出す
if page == "AIチャットサポート":
    show_ai_chat_support()
elif page == "今日のチェックイン":
    show_daily_checkin()
elif page == "パーソナル分析":
    show_personal_analysis()
elif page == "週間レポート":
    show_weekly_report()
elif page == "成長戦略提案":
    show_growth_strategy() 