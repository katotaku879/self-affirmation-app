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
    page_title="ポジティブな習慣の定着 - 自己肯定アプリ",
    page_icon="✨",
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
    .habit-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
    }
    .habit-active {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .habit-skipped {
        background-color: #FFF9C4;
        border-left: 5px solid #FFC107;
    }
    .habit-missed {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .small-win {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
    }
    .medal-bronze {
        background-color: #D7CCC8;
        color: #5D4037;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .medal-silver {
        background-color: #E0E0E0;
        color: #424242;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .medal-gold {
        background-color: #FFF9C4;
        color: #F57F17;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .medal-platinum {
        background-color: #E1F5FE;
        color: #0288D1;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.3rem;
    }
    .medal-diamond {
        background-color: #E8EAF6;
        color: #3F51B5;
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
    .future-message {
        background-color: #E0F7FA;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #00BCD4;
        font-style: italic;
    }
    .positive-stat {
        color: #4CAF50;
        font-weight: bold;
    }
    .warning-stat {
        color: #FFC107;
        font-weight: bold;
    }
    .negative-stat {
        color: #F44336;
        font-weight: bold;
    }
    .habit-check {
        font-size: 1.2rem;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        background-color: #FAFAFA;
    }
    .success-badge {
        background-color: #DCEDC8;
        color: #33691E;
        padding: 0.3rem 0.7rem;
        border-radius: 15px;
        font-weight: bold;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# データファイルのパス
HABITS_FILE = "habits.json"
HABIT_RECORDS_FILE = "habit_records.json"
SMALL_WINS_FILE = "small_wins.json"
REWARDS_FILE = "rewards.json"
FUTURE_MESSAGES_FILE = "future_messages.json"
MEDALS_FILE = "medals.json"

# データファイルの初期化
def initialize_habit_files():
    if not os.path.exists(HABITS_FILE):
        with open(HABITS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(HABIT_RECORDS_FILE):
        with open(HABIT_RECORDS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(SMALL_WINS_FILE):
        with open(SMALL_WINS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(REWARDS_FILE):
        default_rewards = {
            "user_rewards": [
                {"id": str(uuid.uuid4()), "name": "映画鑑賞", "description": "好きな映画を見る", "used": False},
                {"id": str(uuid.uuid4()), "name": "お気に入りのカフェでゆっくり", "description": "カフェでのんびり過ごす時間", "used": False},
                {"id": str(uuid.uuid4()), "name": "小さな買い物", "description": "自分へのプレゼント", "used": False}
            ]
        }
        with open(REWARDS_FILE, "w") as f:
            json.dump(default_rewards, f)
    
    if not os.path.exists(FUTURE_MESSAGES_FILE):
        with open(FUTURE_MESSAGES_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(MEDALS_FILE):
        default_medals = {
            "medals": [
                {"days": 3, "name": "ブロンズメダル", "class": "medal-bronze", "description": "3日連続達成"},
                {"days": 7, "name": "シルバーメダル", "class": "medal-silver", "description": "7日連続達成"},
                {"days": 14, "name": "ゴールドメダル", "class": "medal-gold", "description": "14日連続達成"},
                {"days": 30, "name": "プラチナメダル", "class": "medal-platinum", "description": "30日連続達成"},
                {"days": 60, "name": "ダイヤモンドメダル", "class": "medal-diamond", "description": "60日連続達成"}
            ]
        }
        with open(MEDALS_FILE, "w") as f:
            json.dump(default_medals, f)

# 初期化を実行
initialize_habit_files()

# データを読み込む関数
def load_habits():
    with open(HABITS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "name", "description", "frequency", "time_of_day", "start_date", "future_vision", "skip_allowed", "reward_milestone", "last_reviewed", "is_active"])

def load_habit_records():
    with open(HABIT_RECORDS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["habit_id", "date", "status", "notes"])

def load_small_wins():
    with open(SMALL_WINS_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "habit_id", "date", "description", "feeling"])

def load_rewards():
    with open(REWARDS_FILE, "r") as f:
        return json.load(f)

def load_future_messages():
    with open(FUTURE_MESSAGES_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "habit_id", "creation_date", "target_date", "message"])

def load_medals():
    with open(MEDALS_FILE, "r") as f:
        return json.load(f)

# データを保存する関数
def save_habits(df):
    with open(HABITS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_habit_records(df):
    with open(HABIT_RECORDS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_small_wins(df):
    with open(SMALL_WINS_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_rewards(rewards_data):
    with open(REWARDS_FILE, "w") as f:
        json.dump(rewards_data, f)

def save_future_messages(df):
    with open(FUTURE_MESSAGES_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

# ページタイトル
st.markdown('<h1 class="main-header">✨ ポジティブな習慣の定着</h1>', unsafe_allow_html=True)

# ページ内ナビゲーション
page = st.sidebar.radio(
    "習慣の定着メニュー",
    ["習慣ダッシュボード", "習慣の追加・編集", "今日の習慣チェック", 
     "小さな成功の記録", "達成メダル", "ご褒美設定", "習慣の振り返り"]
)

# 習慣ダッシュボードページ
def show_habit_dashboard():
    st.markdown('<h2 class="sub-header">📊 習慣ダッシュボード</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    records_df = load_habit_records()
    small_wins_df = load_small_wins()
    
    if habits_df.empty:
        st.info("まだ習慣が登録されていません。「習慣の追加・編集」から最初の習慣を登録しましょう！")
        return
    
    # 今日の日付
    today = date.today().strftime("%Y-%m-%d")
    
    # アクティブな習慣のみ表示
    active_habits = habits_df[habits_df['is_active'] == True]
    
    if active_habits.empty:
        st.warning("アクティブな習慣がありません。「習慣の追加・編集」からアクティブな習慣を設定しましょう。")
    else:
        # 今日の習慣ステータス
        st.markdown("### 今日の習慣")
        
        # 今日の記録を抽出
        today_records = records_df[records_df['date'] == today]
        
        for _, habit in active_habits.iterrows():
            habit_id = habit['id']
            habit_name = habit['name']
            
            # この習慣の今日の記録があるか確認
            today_status = "未チェック"
            today_notes = ""
            card_class = "habit-card"
            
            if not today_records.empty:
                habit_today = today_records[today_records['habit_id'] == habit_id]
                if not habit_today.empty:
                    today_status = habit_today.iloc[0]['status']
                    today_notes = habit_today.iloc[0]['notes'] if 'notes' in habit_today.iloc[0] else ""
                    
                    if today_status == "達成":
                        card_class = "habit-card habit-active"
                    elif today_status == "スキップ":
                        card_class = "habit-card habit-skipped"
                    elif today_status == "未達成":
                        card_class = "habit-card habit-missed"
            
            # 連続達成日数の計算
            streak = calculate_streak(habit_id, records_df, today)
            
            # 達成率の計算
            completion_rate = calculate_completion_rate(habit_id, records_df)
            
            # メダル情報の取得
            medal_info = get_medal_info(streak)
            medal_display = ""
            if medal_info:
                medal_display = f"""<span class="{medal_info['class']}">{medal_info['name']}</span>"""
            
            st.markdown(f"""
            <div class="{card_class}">
                <h3>{habit_name}</h3>
                <p><strong>ステータス:</strong> {today_status}</p>
                <p><strong>連続達成日数:</strong> {streak}日 {medal_display}</p>
                <p><strong>総合達成率:</strong> {completion_rate:.1f}%</p>
                <p><strong>メモ:</strong> {today_notes}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 習慣の達成状況グラフ
        st.markdown("### 習慣の達成状況")
        
        # 各習慣の達成率を計算
        habit_stats = []
        for _, habit in active_habits.iterrows():
            habit_id = habit['id']
            habit_name = habit['name']
            completion_rate = calculate_completion_rate(habit_id, records_df)
            streak = calculate_streak(habit_id, records_df, today)
            
            habit_stats.append({
                "habit_name": habit_name,
                "completion_rate": completion_rate,
                "streak": streak
            })
        
        habit_stats_df = pd.DataFrame(habit_stats)
        
        if not habit_stats_df.empty:
            # 達成率のグラフ
            fig_rates = px.bar(
                habit_stats_df,
                x="habit_name",
                y="completion_rate",
                title="習慣ごとの達成率",
                labels={"habit_name": "習慣", "completion_rate": "達成率 (%)"},
                color="completion_rate",
                color_continuous_scale=["red", "yellow", "green"],
                range_color=[0, 100]
            )
            st.plotly_chart(fig_rates, use_container_width=True)
            
            # 連続日数のグラフ
            fig_streaks = px.bar(
                habit_stats_df,
                x="habit_name",
                y="streak",
                title="習慣ごとの連続達成日数",
                labels={"habit_name": "習慣", "streak": "連続日数"},
                color="streak",
                color_continuous_scale=["blue", "purple"],
            )
            st.plotly_chart(fig_streaks, use_container_width=True)
        
        # 最近の小さな成功
        st.markdown("### 最近の小さな成功")
        
        recent_wins = small_wins_df.sort_values('date', ascending=False).head(3)
        
        if not recent_wins.empty:
            for _, win in recent_wins.iterrows():
                habit_name = "全般"
                if not pd.isna(win.get('habit_id')) and win['habit_id'] in habits_df['id'].values:
                    habit_row = habits_df[habits_df['id'] == win['habit_id']]
                    if not habit_row.empty:
                        habit_name = habit_row.iloc[0]['name']
                
                st.markdown(f"""
                <div class="small-win">
                    <h4>{win['date']} - {habit_name}</h4>
                    <p>{win['description']}</p>
                    <p><em>感情: {win.get('feeling', '')}</em></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("まだ小さな成功の記録がありません。「小さな成功の記録」から記録を追加しましょう！")
        
        # 未来からのメッセージ表示
        future_messages_df = load_future_messages()
        if not future_messages_df.empty:
            today_date = datetime.now().date()
            eligible_messages = []
            
            for _, message in future_messages_df.iterrows():
                creation_date = datetime.strptime(message['creation_date'], "%Y-%m-%d").date()
                target_date = datetime.strptime(message['target_date'], "%Y-%m-%d").date()
                
                # メッセージを表示する条件: ターゲット日に達した、かつ作成から1ヶ月以上経過
                if today_date >= target_date and (today_date - creation_date).days >= 30:
                    habit_name = "全般"
                    if not pd.isna(message.get('habit_id')) and message['habit_id'] in habits_df['id'].values:
                        habit_row = habits_df[habits_df['id'] == message['habit_id']]
                        if not habit_row.empty:
                            habit_name = habit_row.iloc[0]['name']
                    
                    eligible_messages.append({
                        "habit_name": habit_name,
                        "message": message['message'],
                        "creation_date": creation_date
                    })
            
            if eligible_messages:
                st.markdown("### 過去の自分からのメッセージ")
                
                for msg in eligible_messages[:1]:  # 最新の1つだけ表示
                    st.markdown(f"""
                    <div class="future-message">
                        <h4>{msg['creation_date']} の自分からのメッセージ - {msg['habit_name']}</h4>
                        <p>"{msg['message']}"</p>
                    </div>
                    """, unsafe_allow_html=True)

# 習慣の追加・編集ページ
def show_habit_management():
    st.markdown('<h2 class="sub-header">✏️ 習慣の追加・編集</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    
    # 新規追加または編集の選択
    action = st.radio(
        "アクション",
        ["新しい習慣を追加", "既存の習慣を編集"],
        index=0 if habits_df.empty else None
    )
    
    if action == "新しい習慣を追加":
        with st.form("new_habit_form"):
            st.markdown("### 新しい習慣の追加")
            
            habit_name = st.text_input("習慣の名前（例：朝の散歩、瞑想など）")
            habit_description = st.text_area("習慣の詳細")
            
            frequency_options = ["毎日", "平日のみ", "週末のみ", "週に数回", "月に数回"]
            frequency = st.selectbox("頻度", frequency_options)
            
            time_options = ["朝", "昼", "夕方", "夜", "就寝前", "いつでも"]
            time_of_day = st.selectbox("時間帯", time_options)
            
            start_date = st.date_input("開始日", datetime.now())
            
            future_vision = st.text_area("この習慣を続けたらどうなりたいか？（未来の姿）")
            
            skip_allowed = st.checkbox("週に1回のスキップを許可する", value=True)
            
            reward_options = ["3日連続達成", "7日連続達成", "14日連続達成", "30日連続達成", "なし"]
            reward_milestone = st.selectbox("ご褒美の条件", reward_options)
            
            submit = st.form_submit_button("習慣を追加")
            
            if submit:
                if not habit_name:
                    st.error("習慣の名前は必須です。")
                else:
                    # 新しい習慣を追加
                    new_habit = {
                        "id": str(uuid.uuid4()),
                        "name": habit_name,
                        "description": habit_description,
                        "frequency": frequency,
                        "time_of_day": time_of_day,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "future_vision": future_vision,
                        "skip_allowed": skip_allowed,
                        "reward_milestone": reward_milestone,
                        "last_reviewed": datetime.now().strftime("%Y-%m-%d"),
                        "is_active": True
                    }
                    
                    if habits_df.empty:
                        habits_df = pd.DataFrame([new_habit])
                    else:
                        habits_df = pd.concat([habits_df, pd.DataFrame([new_habit])], ignore_index=True)
                    
                    save_habits(habits_df)
                    
                    # 未来からのメッセージを作成
                    future_date = start_date + timedelta(days=30)  # 30日後
                    
                    future_message = {
                        "id": str(uuid.uuid4()),
                        "habit_id": new_habit["id"],
                        "creation_date": start_date.strftime("%Y-%m-%d"),
                        "target_date": future_date.strftime("%Y-%m-%d"),
                        "message": f"30日前にあなたは「{habit_name}」という習慣を始めて、「{future_vision}」という未来を描いていました。継続は力なりです。今の自分を誇りに思ってください！"
                    }
                    
                    future_messages_df = load_future_messages()
                    if future_messages_df.empty:
                        future_messages_df = pd.DataFrame([future_message])
                    else:
                        future_messages_df = pd.concat([future_messages_df, pd.DataFrame([future_message])], ignore_index=True)
                    
                    save_future_messages(future_messages_df)
                    
                    st.success("新しい習慣を追加しました！")
                    st.balloons()
    
    # ポジティブな習慣メニューの習慣の追加・編集部分を修正し、削除機能を追加するコード
# 02_ポジティブな習慣.py の show_habit_management() 関数内の既存の習慣を編集するセクションを以下のコードに置き換えてください

    elif action == "既存の習慣を編集" and not habits_df.empty:
        # 編集する習慣の選択
        habit_names = habits_df['name'].tolist()
        selected_habit_name = st.selectbox("編集する習慣を選択", habit_names)
        
        selected_habit = habits_df[habits_df['name'] == selected_habit_name].iloc[0]
        
        # タブを使って「編集」と「削除」を分ける
        edit_tab, delete_tab = st.tabs(["習慣を編集", "習慣を削除"])
        
        with edit_tab:
            with st.form("edit_habit_form"):
                st.markdown(f"### 「{selected_habit_name}」の編集")
                
                habit_name = st.text_input("習慣の名前", value=selected_habit['name'])
                habit_description = st.text_area("習慣の詳細", value=selected_habit['description'])
                
                frequency_options = ["毎日", "平日のみ", "週末のみ", "週に数回", "月に数回"]
                frequency = st.selectbox("頻度", frequency_options, index=frequency_options.index(selected_habit['frequency']) if selected_habit['frequency'] in frequency_options else 0)
                
                time_options = ["朝", "昼", "夕方", "夜", "就寝前", "いつでも"]
                time_of_day = st.selectbox("時間帯", time_options, index=time_options.index(selected_habit['time_of_day']) if selected_habit['time_of_day'] in time_options else 0)
                
                start_date = st.date_input("開始日", datetime.strptime(selected_habit['start_date'], "%Y-%m-%d"))
                
                future_vision = st.text_area("この習慣を続けたらどうなりたいか？（未来の姿）", value=selected_habit['future_vision'])
                
                skip_allowed = st.checkbox("週に1回のスキップを許可する", value=selected_habit['skip_allowed'])
                
                reward_options = ["3日連続達成", "7日連続達成", "14日連続達成", "30日連続達成", "なし"]
                reward_milestone = st.selectbox("ご褒美の条件", reward_options, index=reward_options.index(selected_habit['reward_milestone']) if selected_habit['reward_milestone'] in reward_options else 0)
                
                is_active = st.checkbox("アクティブな習慣", value=selected_habit['is_active'])
                
                submit = st.form_submit_button("習慣を更新")
                
                if submit:
                    if not habit_name:
                        st.error("習慣の名前は必須です。")
                    else:
                        # 習慣を更新
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'name'] = habit_name
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'description'] = habit_description
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'frequency'] = frequency
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'time_of_day'] = time_of_day
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'start_date'] = start_date.strftime("%Y-%m-%d")
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'future_vision'] = future_vision
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'skip_allowed'] = skip_allowed
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'reward_milestone'] = reward_milestone
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'last_reviewed'] = datetime.now().strftime("%Y-%m-%d")
                        habits_df.loc[habits_df['id'] == selected_habit['id'], 'is_active'] = is_active
                        
                        save_habits(habits_df)
                        
                        st.success("習慣を更新しました！")
        
        with delete_tab:
            st.markdown(f"### 「{selected_habit_name}」の削除")
            
            st.warning(f"""
            **注意**: 習慣を削除すると、この習慣に関連するすべての記録も削除されます。
            この操作は取り消せません。
            """)
            
            # 削除の確認
            confirmation = st.text_input(
                "削除を確認するには、習慣の名前を入力してください",
                key="delete_confirmation"
            )
            
            if st.button("この習慣を完全に削除", key="delete_habit_button"):
                if confirmation == selected_habit_name:
                    # 習慣の削除
                    habits_df = habits_df[habits_df['id'] != selected_habit['id']]
                    save_habits(habits_df)
                    
                    # 関連する記録も削除（オプション）
                    try:
                        habit_records_df = load_habit_records()
                        if not habit_records_df.empty:
                            habit_records_df = habit_records_df[habit_records_df['habit_id'] != selected_habit['id']]
                            save_habit_records(habit_records_df)
                    except:
                        st.error("習慣記録の削除中にエラーが発生しました。習慣自体は削除されています。")
                    
                    st.success(f"習慣「{selected_habit_name}」を削除しました！")
                    st.info("「習慣の追加・編集」ページを再読み込みして更新してください。")
                    
                    # 直接rerunするとエラーになることがあるため、ユーザーに再読み込みを促す
                else:
                    st.error("習慣名が一致しません。正確な習慣名を入力してください。")

# 今日の習慣チェックページ
def show_habit_daily_check():
    st.markdown('<h2 class="sub-header">✅ 今日の習慣チェック</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    records_df = load_habit_records()
    
    if habits_df.empty:
        st.info("まだ習慣が登録されていません。「習慣の追加・編集」から最初の習慣を登録しましょう！")
        return
    
    # 今日の日付
    today = date.today().strftime("%Y-%m-%d")
    
    # アクティブな習慣のみ表示
    active_habits = habits_df[habits_df['is_active'] == True]
    
    if active_habits.empty:
        st.warning("アクティブな習慣がありません。「習慣の追加・編集」からアクティブな習慣を設定しましょう。")
    else:
        # 今日の記録を抽出
        today_records = records_df[records_df['date'] == today]
        
        st.markdown("### 今日の習慣チェック")
        
        # 表示する習慣をフィルタリング
        habits_to_display = []
        for _, habit in active_habits.iterrows():
            habit_id = habit['id']
            
            # この習慣の今日の記録があるか確認
            already_achieved = False
            if not today_records.empty:
                habit_today = today_records[today_records['habit_id'] == habit_id]
                if not habit_today.empty and habit_today.iloc[0]['status'] == "達成":
                    already_achieved = True
                    
            # 達成していない習慣のみリストに追加
            if not already_achieved:
                habits_to_display.append(habit)
        
        if not habits_to_display:
            st.success("🎉 今日の習慣はすべて達成しました！素晴らしい！")
            return
            
        # 未達成の習慣のみ表示して処理
        for habit in habits_to_display:
            habit_id = habit['id']
            habit_name = habit['name']
            
            # この習慣の今日の記録があるか確認
            status = "未チェック"
            notes = ""
            
            if not today_records.empty:
                habit_today = today_records[today_records['habit_id'] == habit_id]
                if not habit_today.empty:
                    status = habit_today.iloc[0]['status']
                    notes = habit_today.iloc[0]['notes'] if 'notes' in habit_today.iloc[0] else ""
            
            # 習慣のステータスを更新するフォーム
            with st.form(f"check_habit_{habit_id}"):
                st.markdown(f"#### {habit_name}")
                st.markdown(f"**頻度**: {habit['frequency']} | **時間帯**: {habit['time_of_day']}")
                
                # スキップが許可されているかどうかを確認
                status_options = ["達成", "未達成", "スキップ"] if habit['skip_allowed'] else ["達成", "未達成"]
                selected_status = st.radio("ステータス", status_options, index=status_options.index(status) if status in status_options else 0)

                 # スキップを選択した場合、スキップの理由を表示
                if selected_status == "スキップ":
                    st.markdown("""
                    <div style="background-color: #FFF9C4; padding: 10px; border-radius: 5px;">
                        <p>💡 <strong>スキップOKです！</strong> 完璧を目指さず、調整しながら継続していきましょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                habit_notes = st.text_area("メモ（オプション）", value=notes)
                
                submit = st.form_submit_button("保存")
                
                if submit:
                    # 既存の記録を更新または新しい記録を追加
                    new_record = {
                        "habit_id": habit_id,
                        "date": today,
                        "status": selected_status,
                        "notes": habit_notes
                    }
                    
                    # 既存の記録があるか確認
                    existing_record = False
                    if not today_records.empty:
                        habit_today = today_records[today_records['habit_id'] == habit_id]
                        if not habit_today.empty:
                            existing_record = True
                            records_df.loc[(records_df['date'] == today) & (records_df['habit_id'] == habit_id), 'status'] = selected_status
                            records_df.loc[(records_df['date'] == today) & (records_df['habit_id'] == habit_id), 'notes'] = habit_notes
                    
                    if not existing_record:
                        if records_df.empty:
                            records_df = pd.DataFrame([new_record])
                        else:
                            records_df = pd.concat([records_df, pd.DataFrame([new_record])], ignore_index=True)
                    
                    save_habit_records(records_df)
                    
                    # 達成した場合、達成メッセージを表示
                    if selected_status == "達成":
                        st.success(f"「{habit_name}」を達成しました！素晴らしい！")
                        
                        # 連続達成日数を確認
                        streak = calculate_streak(habit_id, records_df, today)
                        
                        # メダル獲得の確認
                        medal_info = get_medal_info(streak)
                        if medal_info:
                            st.markdown(f"""
                            <div class="{medal_info['class']}" style="padding: 15px; text-align: center; margin: 10px 0;">
                                <h3>🏆 おめでとうございます！</h3>
                                <p>{medal_info['name']}を獲得しました！</p>
                                <p>{medal_info['description']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # ご褒美の条件を確認
                        reward_milestone = habit['reward_milestone']
                        if reward_milestone != "なし":
                            days_required = int(reward_milestone.split("日")[0])
                            if streak >= days_required and streak % days_required == 0:  # ちょうど達成した場合
                                st.balloons()
                                st.markdown(f"""
                                <div style="background-color: #F3E5F5; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                    <h3>🎁 ご褒美タイム！</h3>
                                    <p>{reward_milestone}を達成しました！ご褒美を選んで自分を労いましょう。</p>
                                    <p>「ご褒美設定」ページで設定したご褒美から選べます。</p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    elif selected_status == "スキップ":
                        st.info("習慣をスキップしました。休息も大切です！")
                        
                        # 達成率を計算して表示
                        completion_rate = calculate_completion_rate(habit_id, records_df)
                        if completion_rate >= 80:
                            st.markdown(f"""
                            <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px;">
                                <p>👍 <strong>素晴らしい！スキップしても達成率は{completion_rate:.1f}%です。</strong> 柔軟に続けていくことが大切です。</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # 小さな成功の記録を促す
                    if selected_status == "達成":
                        st.markdown("""
                        <div style="background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin-top: 20px;">
                            <p>💡 <strong>ヒント：</strong> 「小さな成功の記録」ページで、今日の達成感や気づきを記録しておきましょう！</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
        
        # 習慣の見直し提案
        st.markdown("### 習慣の最適化提案")
        
        # 今日が月初めか確認
        is_month_start = datetime.now().day == 1
        
        if is_month_start:
            st.markdown("""
            <div style="background-color: #E0F7FA; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4>🔄 月初めの習慣見直しのタイミングです</h4>
                <p>今月も頑張っていきましょう！習慣を見直して、より続けやすい形に調整することも大切です。</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 達成率の低い習慣を特定
        low_completion_habits = []
        for _, habit in active_habits.iterrows():
            habit_id = habit['id']
            completion_rate = calculate_completion_rate(habit_id, records_df)
            
            if completion_rate < 60:  # 達成率が60%未満の習慣
                low_completion_habits.append({
                    "id": habit_id,
                    "name": habit['name'],
                    "completion_rate": completion_rate
                })
        
        if low_completion_habits:
            st.markdown("#### 最適化の提案があります")
            
            for habit in low_completion_habits:
                st.markdown(f"""
                <div style="background-color: #FFEBEE; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4>「{habit['name']}」の達成率: {habit['completion_rate']:.1f}%</h4>
                    <p>この習慣は続けにくいかもしれません。以下の調整を検討してみましょう：</p>
                    <ul>
                        <li>目標を小さくする（例：30分の運動→10分に減らす）</li>
                        <li>頻度を減らす（例：毎日→週3回に変更）</li>
                        <li>実行する時間帯を変える</li>
                        <li>習慣をもっと楽しい/簡単なものに変更する</li>
                    </ul>
                    <p>「習慣の追加・編集」ページで調整できます。</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4>👍 素晴らしい継続状況です！</h4>
                <p>すべての習慣が良い達成率で進んでいます。このまま続けていきましょう！</p>
            </div>
            """, unsafe_allow_html=True)

# 小さな成功の記録ページ
def show_small_wins():
    st.markdown('<h2 class="sub-header">✨ 小さな成功の記録</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    small_wins_df = load_small_wins()
    
    # 新しい小さな成功の追加
    st.markdown("### 今日の小さな成功")
    
    with st.form("small_win_form"):
        # 習慣の選択（または全般）
        habit_options = ["全般（特定の習慣に関連しない）"] + habits_df['name'].tolist() if not habits_df.empty else ["全般（特定の習慣に関連しない）"]
        selected_habit = st.selectbox("関連する習慣", habit_options)
        
        win_description = st.text_area("今日の小さな成功は？", placeholder="例：朝5分早く起きて深呼吸ができた、新しいレシピに挑戦した、など")
        
        feeling_options = ["嬉しい", "満足", "誇らしい", "わくわく", "達成感", "感謝", "希望", "自信", "普通"]
        feeling = st.selectbox("その時の感情", feeling_options)
        
        win_date = st.date_input("日付", datetime.now())
        
        submit = st.form_submit_button("記録する")
        
        if submit:
            if not win_description:
                st.error("成功の内容を入力してください。")
            else:
                # 習慣IDの取得
                habit_id = None
                if selected_habit != "全般（特定の習慣に関連しない）" and not habits_df.empty:
                    habit_row = habits_df[habits_df['name'] == selected_habit]
                    if not habit_row.empty:
                        habit_id = habit_row.iloc[0]['id']
                
                # 新しい小さな成功を追加
                new_win = {
                    "id": str(uuid.uuid4()),
                    "habit_id": habit_id,
                    "date": win_date.strftime("%Y-%m-%d"),
                    "description": win_description,
                    "feeling": feeling
                }
                
                if small_wins_df.empty:
                    small_wins_df = pd.DataFrame([new_win])
                else:
                    small_wins_df = pd.concat([small_wins_df, pd.DataFrame([new_win])], ignore_index=True)
                
                save_small_wins(small_wins_df)
                
                st.success("小さな成功を記録しました！")
                st.balloons()
    
    # 過去の小さな成功一覧
    st.markdown("### 小さな成功の履歴")
    
    if not small_wins_df.empty:
        # 日付でソート
        sorted_wins = small_wins_df.sort_values('date', ascending=False)
        
        for _, win in sorted_wins.iterrows():
            habit_name = "全般"
            if not pd.isna(win.get('habit_id')) and win['habit_id'] in habits_df['id'].values:
                habit_row = habits_df[habits_df['id'] == win['habit_id']]
                if not habit_row.empty:
                    habit_name = habit_row.iloc[0]['name']
            
            st.markdown(f"""
            <div class="small-win">
                <h4>{win['date']} - {habit_name}</h4>
                <p>{win['description']}</p>
                <p><em>感情: {win.get('feeling', '')}</em></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("まだ小さな成功の記録がありません。上のフォームから最初の記録を追加しましょう！")

# 達成メダルページ
def show_medals():
    st.markdown('<h2 class="sub-header">🏅 達成メダル</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    records_df = load_habit_records()
    medals = load_medals()['medals']
    
    if habits_df.empty:
        st.info("まだ習慣が登録されていません。「習慣の追加・編集」から最初の習慣を登録しましょう！")
        return
    
    # 今日の日付
    today = date.today().strftime("%Y-%m-%d")
    
    # メダル一覧を表示
    st.markdown("### メダルの種類")
    
    medal_cols = st.columns(len(medals))
    for i, medal in enumerate(medals):
        with medal_cols[i]:
            st.markdown(f"""
            <div class="{medal['class']}" style="text-align: center; padding: 10px;">
                <h4>{medal['name']}</h4>
                <p>{medal['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 各習慣のメダル獲得状況
    st.markdown("### 習慣ごとのメダル獲得状況")
    
    for _, habit in habits_df.iterrows():
        habit_id = habit['id']
        habit_name = habit['name']
        
        # 連続達成日数の計算
        streak = calculate_streak(habit_id, records_df, today)
        
        # 獲得メダルの確認
        acquired_medals = []
        for medal in medals:
            if streak >= medal['days']:
                acquired_medals.append(medal)
        
        # メダル表示
        st.markdown(f"#### {habit_name} (連続達成: {streak}日)")
        
        if acquired_medals:
            medal_display = ""
            for medal in acquired_medals:
                medal_display += f"""<span class="{medal['class']}">{medal['name']}</span> """
            
            st.markdown(f"""
            <div style="margin: 10px 0;">
                {medal_display}
            </div>
            """, unsafe_allow_html=True)
            
            # 次のメダルまでの残り日数
            next_medal = None
            for medal in medals:
                if streak < medal['days']:
                    next_medal = medal
                    break
            
            if next_medal:
                days_left = next_medal['days'] - streak
                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <p>次の{next_medal['name']}まであと<strong>{days_left}日</strong>です！頑張りましょう！</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <p>🎊 <strong>すべてのメダルを獲得しました！</strong> 素晴らしい継続力です！</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #FFEBEE; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <p>まだメダルを獲得していません。継続して習慣を続けていきましょう！</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 最初のメダルまでの残り日数
            first_medal = medals[0]
            days_left = first_medal['days'] - streak
            st.markdown(f"""
            <div style="background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <p>最初の{first_medal['name']}まであと<strong>{days_left}日</strong>です！頑張りましょう！</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)

# ご褒美設定ページ
def show_rewards():
    st.markdown('<h2 class="sub-header">🎁 ご褒美設定</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    rewards_data = load_rewards()
    
    # ご褒美一覧
    st.markdown("### 現在のご褒美リスト")
    
    user_rewards = rewards_data.get('user_rewards', [])
    
    if user_rewards:
        for reward in user_rewards:
            used_badge = '<span class="success-badge">使用済</span>' if reward.get('used', False) else ''
            
            st.markdown(f"""
            <div class="reward-card">
                <h4>{reward['name']} {used_badge}</h4>
                <p>{reward['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("まだご褒美が登録されていません。以下のフォームから追加しましょう。")
    
    # 新しいご褒美の追加
    st.markdown("### 新しいご褒美を追加")
    
    with st.form("new_reward_form"):
        reward_name = st.text_input("ご褒美の名前", placeholder="映画鑑賞、お気に入りのカフェでお茶、など")
        reward_description = st.text_area("詳細", placeholder="どんなご褒美なのか、具体的に書いておくと良いでしょう")
        
        submit = st.form_submit_button("ご褒美を追加")
        
        if submit:
            if not reward_name:
                st.error("ご褒美の名前を入力してください。")
            else:
                # 新しいご褒美を追加
                new_reward = {
                    "id": str(uuid.uuid4()),
                    "name": reward_name,
                    "description": reward_description,
                    "used": False
                }
                
                user_rewards.append(new_reward)
                rewards_data['user_rewards'] = user_rewards
                
                save_rewards(rewards_data)
                
                st.success("新しいご褒美を追加しました！")
    
    # ご褒美の使用/リセット
    if user_rewards:
        st.markdown("### ご褒美の使用/リセット")
        
        reward_options = [f"{r['name']}" for r in user_rewards]
        selected_reward = st.selectbox("ご褒美を選択", reward_options)
        
        selected_index = None
        for i, r in enumerate(user_rewards):
            if r['name'] == selected_reward:
                selected_index = i
                break
        
        if selected_index is not None:
            reward = user_rewards[selected_index]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if not reward.get('used', False):
                    if st.button("ご褒美を使用"):
                        user_rewards[selected_index]['used'] = True
                        rewards_data['user_rewards'] = user_rewards
                        save_rewards(rewards_data)
                        st.success(f"「{reward['name']}」を使用しました！楽しんでくださいね。")
            
            with col2:
                if reward.get('used', False):
                    if st.button("リセット"):
                        user_rewards[selected_index]['used'] = False
                        rewards_data['user_rewards'] = user_rewards
                        save_rewards(rewards_data)
                        st.success(f"「{reward['name']}」をリセットしました。また達成したときに使えます。")

# 習慣の振り返りページ
def show_habit_review():
    st.markdown('<h2 class="sub-header">🔄 習慣の振り返り</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    habits_df = load_habits()
    records_df = load_habit_records()
    
    if habits_df.empty:
        st.info("まだ習慣が登録されていません。「習慣の追加・編集」から最初の習慣を登録しましょう！")
        return
    
    # 期間選択
    period = st.selectbox(
        "振り返り期間",
        ["1週間", "1ヶ月", "3ヶ月", "すべて"]
    )
    
    # 期間に基づいて日付範囲を計算
    end_date = datetime.now().date()
    
    if period == "1週間":
        start_date = end_date - timedelta(days=7)
    elif period == "1ヶ月":
        start_date = end_date - timedelta(days=30)
    elif period == "3ヶ月":
        start_date = end_date - timedelta(days=90)
    else:  # すべて
        start_date = datetime.strptime(habits_df['start_date'].min(), "%Y-%m-%d").date() if not habits_df.empty else end_date
    
    # 日付範囲のフォーマット
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # 期間内のレコードをフィルタリング
    records_df['date'] = pd.to_datetime(records_df['date']).dt.date
    filtered_records = records_df[(records_df['date'] >= start_date) & (records_df['date'] <= end_date)]
    
    st.markdown(f"### {start_date_str} から {end_date_str} までの振り返り")
    
    if filtered_records.empty:
        st.warning("選択した期間のデータがありません。")
    else:
        # 習慣ごとの達成統計
        st.markdown("#### 習慣ごとの達成状況")
        
        habit_stats = []
        
        for _, habit in habits_df.iterrows():
            habit_id = habit['id']
            habit_name = habit['name']
            
            # この習慣の記録を抽出
            habit_records = filtered_records[filtered_records['habit_id'] == habit_id]
            
            if not habit_records.empty:
                total_days = len(habit_records)
                achieved_days = len(habit_records[habit_records['status'] == "達成"])
                skipped_days = len(habit_records[habit_records['status'] == "スキップ"])
                missed_days = len(habit_records[habit_records['status'] == "未達成"])
                
                achievement_rate = achieved_days / total_days * 100 if total_days > 0 else 0
                
                habit_stats.append({
                    "habit_name": habit_name,
                    "total_days": total_days,
                    "achieved_days": achieved_days,
                    "skipped_days": skipped_days,
                    "missed_days": missed_days,
                    "achievement_rate": achievement_rate
                })
        
        if habit_stats:
            habit_stats_df = pd.DataFrame(habit_stats)
            
            # 達成率グラフ
            fig_achievement = px.bar(
                habit_stats_df.sort_values('achievement_rate', ascending=False),
                x="habit_name",
                y="achievement_rate",
                title="習慣ごとの達成率",
                labels={"habit_name": "習慣", "achievement_rate": "達成率 (%)"},
                color="achievement_rate",
                color_continuous_scale=["red", "yellow", "green"],
                range_color=[0, 100]
            )
            st.plotly_chart(fig_achievement, use_container_width=True)
            
            # 各習慣の詳細データ
            for stat in habit_stats:
                status_class = "positive-stat" if stat['achievement_rate'] >= 80 else "warning-stat" if stat['achievement_rate'] >= 50 else "negative-stat"
                
                st.markdown(f"""
                <div class="habit-card">
                    <h4>{stat['habit_name']}</h4>
                    <p>総日数: {stat['total_days']}日</p>
                    <p>達成: {stat['achieved_days']}日 | スキップ: {stat['skipped_days']}日 | 未達成: {stat['missed_days']}日</p>
                    <p>達成率: <span class="{status_class}">{stat['achievement_rate']:.1f}%</span></p>
                </div>
                """, unsafe_allow_html=True)
        
        # 全体の達成トレンド
        st.markdown("#### 全体の達成トレンド")
        
        # 日付ごとに達成状況を集計
        date_status = filtered_records.groupby(['date', 'status']).size().unstack(fill_value=0)
        
        if not date_status.empty:
            # 必要な列が存在することを確認
            for status in ["達成", "スキップ", "未達成"]:
                if status not in date_status.columns:
                    date_status[status] = 0
            
            # 達成率の計算
            date_status['total'] = date_status.sum(axis=1)
            date_status['達成率'] = date_status['達成'] / date_status['total'] * 100
            
            # トレンドグラフ
            fig_trend = px.line(
                date_status.reset_index(),
                x="date",
                y="達成率",
                title="日ごとの達成率の推移",
                labels={"date": "日付", "達成率": "達成率 (%)"}
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # 習慣の最適化提案
        st.markdown("#### 習慣の最適化提案")
        
        # 達成率の低い習慣を特定
        low_achievement_habits = []
        for stat in habit_stats:
            if stat['achievement_rate'] < 60:
                low_achievement_habits.append(stat['habit_name'])
        
        if low_achievement_habits:
            st.markdown("""
            <div style="background-color: #FFEBEE; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4>💡 一部の習慣が続けにくいかもしれません</h4>
                <p>以下の習慣は達成率が低いため、調整を検討してみましょう：</p>
            """, unsafe_allow_html=True)
            
            for habit_name in low_achievement_habits:
                st.markdown(f"- **{habit_name}**")
            
            st.markdown("""
                <p>習慣を続けるためのヒント：</p>
                <ul>
                    <li>目標を小さくする（ハードルを下げる）</li>
                    <li>頻度を調整する（毎日→週3回など）</li>
                    <li>時間帯を変える（朝が苦手なら夕方に）</li>
                    <li>楽しく続けられる工夫を追加する</li>
                </ul>
                <p>「習慣の追加・編集」ページで調整できます。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4>🎉 素晴らしい達成状況です！</h4>
                <p>すべての習慣がうまく実行されています。このまま継続していきましょう！</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 未来の自分からのメッセージ記録
        st.markdown("#### 未来の自分へのメッセージ")
        
        with st.form("future_message_form"):
            st.markdown("継続している未来の自分へメッセージを残しましょう。このメッセージは1ヶ月後に表示されます。")
            
            # 習慣の選択
            habit_options = ["全般（特定の習慣に関連しない）"] + habits_df['name'].tolist()
            selected_habit = st.selectbox("関連する習慣", habit_options)
            
            message_text = st.text_area("1ヶ月後の自分へのメッセージ", placeholder="例：この習慣を始めた理由を忘れないで！良い変化が感じられているはず...")
            
            submit = st.form_submit_button("メッセージを保存")
            
            if submit:
                if not message_text:
                    st.error("メッセージを入力してください。")
                else:
                    # 習慣IDの取得
                    habit_id = None
                    if selected_habit != "全般（特定の習慣に関連しない）":
                        habit_row = habits_df[habits_df['name'] == selected_habit]
                        if not habit_row.empty:
                            habit_id = habit_row.iloc[0]['id'] 

                    today_date = datetime.now().date()
                    target_date = today_date + timedelta(days=30)  # 1ヶ月後 

                    # 新しいメッセージを追加
                    future_messages_df = load_future_messages()
                    
                    new_message = {
                        "id": str(uuid.uuid4()),
                        "habit_id": habit_id,
                        "creation_date": today_date.strftime("%Y-%m-%d"),
                        "target_date": target_date.strftime("%Y-%m-%d"),
                        "message": message_text
                    }
                    
                    if future_messages_df.empty:
                        future_messages_df = pd.DataFrame([new_message])
                    else:
                        future_messages_df = pd.concat([future_messages_df, pd.DataFrame([new_message])], ignore_index=True)
                    
                    save_future_messages(future_messages_df)
                    
                    st.success(f"メッセージが保存されました！{target_date.strftime('%Y-%m-%d')}に表示されます。")

# ユーティリティ関数
def calculate_streak(habit_id, records_df, end_date):
    """習慣の連続達成日数を計算する"""
    if records_df.empty:
        return 0
    
    # この習慣のレコードを抽出してソート
    habit_records = records_df[records_df['habit_id'] == habit_id].copy()
    if habit_records.empty:
        return 0
    
    habit_records['date'] = pd.to_datetime(habit_records['date'])
    habit_records = habit_records.sort_values('date', ascending=False)
    
    # 連続達成日数の計算
    streak = 0
    current_date = pd.to_datetime(end_date)
    
    for _, record in habit_records.iterrows():
        # 日付の差が1日より大きい場合、連続記録が途切れている
        if record['date'].date() != current_date.date() - timedelta(days=streak):
            break
        
        # 達成またはスキップの場合は連続とみなす
        if record['status'] in ["達成", "スキップ"]:
            streak += 1
        else:
            break
    
    return streak

def calculate_completion_rate(habit_id, records_df):
    """習慣の達成率を計算する"""
    if records_df.empty:
        return 0
    
    # この習慣のレコードを抽出
    habit_records = records_df[records_df['habit_id'] == habit_id]
    if habit_records.empty:
        return 0
    
    total_records = len(habit_records)
    achieved_records = len(habit_records[habit_records['status'] == "達成"])
    
    return achieved_records / total_records * 100 if total_records > 0 else 0

def get_medal_info(streak):
    """連続日数に基づいたメダル情報を取得する"""
    medals = load_medals()['medals']
    
    # 連続日数に合うメダルを探す
    eligible_medals = [m for m in medals if streak >= m['days']]
    
    if eligible_medals:
        # 最も高いレベルのメダルを返す
        return max(eligible_medals, key=lambda x: x['days'])
    
    return None

# 選択したページを表示
if page == "習慣ダッシュボード":
    show_habit_dashboard()
elif page == "習慣の追加・編集":
    show_habit_management()
elif page == "今日の習慣チェック":
    show_habit_daily_check()
elif page == "小さな成功の記録":
    show_small_wins()
elif page == "達成メダル":
    show_medals()
elif page == "ご褒美設定":
    show_rewards()
elif page == "習慣の振り返り":
    show_habit_review()       