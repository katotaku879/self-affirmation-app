import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import random

# ページの設定
st.set_page_config(
    page_title="成長の可視化 - 自己肯定アプリ",
    page_icon="🌱",
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
    .achievement {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .milestone {
        background-color: #DCEDC8;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #8BC34A;
    }
    .emotion-positive {
        color: #4CAF50;
        font-weight: bold;
    }
    .emotion-neutral {
        color: #FFC107;
        font-weight: bold;
    }
    .emotion-negative {
        color: #F44336;
        font-weight: bold;
    }
    .progress-container {
        padding: 1.5rem;
        background-color: #F1F8E9;
        border-radius: 10px;
        margin-top: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .comparison-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    .card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 0.5rem;
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# データファイルのパス
DATA_FILE = "growth_data.json"
ACHIEVEMENTS_FILE = "achievements.json"
MILESTONES_FILE = "milestones.json"
EMOTIONS_FILE = "emotions.json"

# データファイルの初期化
def initialize_data_files():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(ACHIEVEMENTS_FILE):
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(MILESTONES_FILE):
        default_milestones = [
            {"name": "継続の達人", "description": "同じカテゴリーで10回達成", "required_count": 10, "achieved": False},
            {"name": "成長の兆し", "description": "初めて成長率10%達成", "required_growth": 10, "achieved": False},
            {"name": "着実な進歩", "description": "合計50回の記録達成", "required_total": 50, "achieved": False},
            {"name": "習慣化マスター", "description": "30日連続で記録", "required_streak": 30, "achieved": False},
            {"name": "バランスの達人", "description": "3つ以上のカテゴリーで記録", "required_categories": 3, "achieved": False},
        ]
        with open(MILESTONES_FILE, "w") as f:
            json.dump(default_milestones, f)
    
    if not os.path.exists(EMOTIONS_FILE):
        default_emotions = {
            "positive": ["嬉しい", "満足", "誇らしい", "わくわく", "達成感", "感謝", "希望", "自信"],
            "neutral": ["普通", "平静", "集中", "思慮深い", "穏やか", "安定"],
            "negative": ["不安", "心配", "疲れ", "緊張", "不満", "困惑"]
        }
        with open(EMOTIONS_FILE, "w") as f:
            json.dump(default_emotions, f)

# 初期化を実行
initialize_data_files()

# データを読み込む関数
def load_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data) if data else pd.DataFrame(columns=["date", "category", "achievement", "value", "comment", "emotion"])

def load_achievements():
    with open(ACHIEVEMENTS_FILE, "r") as f:
        return json.load(f)

def load_milestones():
    with open(MILESTONES_FILE, "r") as f:
        return json.load(f)

def load_emotions():
    with open(EMOTIONS_FILE, "r") as f:
        return json.load(f)

# データを保存する関数
def save_data(df):
    with open(DATA_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_achievements(achievements):
    with open(ACHIEVEMENTS_FILE, "w") as f:
        json.dump(achievements, f)

def save_milestones(milestones):
    with open(MILESTONES_FILE, "w") as f:
        json.dump(milestones, f)

# ページ内ナビゲーション
st.markdown('<h1 class="main-header">🌱 成長の可視化</h1>', unsafe_allow_html=True)

# ページ内のナビゲーション
page = st.sidebar.radio(
    "成長の可視化メニュー",
    ["ダッシュボード", "成長記録の追加", "成長の振り返り", "達成リスト", "マイルストーン"]
)

# ダッシュボードページ
def show_dashboard():
    st.markdown('<h2 class="sub-header">📊 成長ダッシュボード</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    df = load_data()
    
    if df.empty:
        st.info("まだ記録がありません。「成長記録の追加」から最初の記録を追加しましょう！")
        return
    
    # 最新のデータと統計情報
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 最新の成長記録")
        latest = df.iloc[-1]
        st.markdown(f"""
        <div class="achievement">
            <h4>{latest['achievement']}</h4>
            <p>カテゴリー: {latest['category']}</p>
            <p>達成値: {latest['value']}</p>
            <p>達成日: {latest['date']}</p>
            <p>コメント: {latest['comment']}</p>
            <p>感情: <span class="emotion-{get_emotion_type(latest['emotion'])}">{latest['emotion']}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 成長の統計")
        total_achievements = len(df)
        categories = df['category'].nunique()
        
        # カテゴリー別の達成数を計算
        category_counts = df['category'].value_counts()
        most_frequent_category = category_counts.idxmax()
        most_frequent_count = category_counts.max()
        
        # 連続記録の計算
        df_sorted = df.sort_values('date')
        dates = pd.to_datetime(df_sorted['date'])
        streaks = calc_streaks(dates)
        current_streak = streaks[-1] if streaks else 0
        max_streak = max(streaks) if streaks else 0
        
        st.markdown(f"""
        <div class="progress-container">
            <p>総記録数: <b>{total_achievements}</b></p>
            <p>記録カテゴリー数: <b>{categories}</b></p>
            <p>最も頻度の高いカテゴリー: <b>{most_frequent_category}</b> ({most_frequent_count}回)</p>
            <p>現在の連続記録: <b>{current_streak}日</b></p>
            <p>最長連続記録: <b>{max_streak}日</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    # 成長グラフ
    st.markdown("### 成長の推移")
    
    # カテゴリー選択
    categories = df['category'].unique()
    selected_category = st.selectbox("カテゴリーを選択", categories)
    
    # 選択したカテゴリーのデータをフィルタリング
    filtered_df = df[df['category'] == selected_category].copy()
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    filtered_df = filtered_df.sort_values('date')
    
    if not filtered_df.empty:
        # 値の推移グラフ
        fig = px.line(
            filtered_df, 
            x='date', 
            y='value', 
            title=f"{selected_category}の成長推移",
            markers=True
        )
        fig.update_layout(
            xaxis_title="日付",
            yaxis_title="達成値",
            hovermode="closest"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 感情分析
        emotion_df = filtered_df.copy()
        emotions = load_emotions()
        emotion_df['emotion_type'] = emotion_df['emotion'].apply(lambda x: 
            'positive' if x in emotions['positive'] else 
            'negative' if x in emotions['negative'] else 'neutral'
        )
        
        emotion_counts = emotion_df['emotion_type'].value_counts().reset_index()
        emotion_counts.columns = ['感情タイプ', '回数']
        
        # 感情分布ドーナツチャート
        fig_emotion = px.pie(
            emotion_counts, 
            values='回数', 
            names='感情タイプ',
            title="達成時の感情分布",
            hole=0.4,
            color='感情タイプ',
            color_discrete_map={
                'positive': '#4CAF50',
                'neutral': '#FFC107',
                'negative': '#F44336'
            }
        )
        st.plotly_chart(fig_emotion, use_container_width=True)
    
    # 1週間前vs今の比較
    st.markdown('<h3 class="sub-header">📈 1週間前 vs 今の比較</h3>', unsafe_allow_html=True)
    
    if len(df) > 1:
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        recent_df = df.copy()
        recent_df['date'] = pd.to_datetime(recent_df['date']).dt.date
        
        recent_records = recent_df[recent_df['date'] >= week_ago]
        
        if not recent_records.empty:
            week_achievements = len(recent_records)
            week_categories = recent_records['category'].nunique()
            
            # 週間の成長率計算
            growth_rates = []
            for category in recent_records['category'].unique():
                cat_data = recent_records[recent_records['category'] == category].sort_values('date')
                if len(cat_data) >= 2:
                    first_value = cat_data.iloc[0]['value']
                    last_value = cat_data.iloc[-1]['value']
                    if first_value > 0:  # ゼロ除算を避ける
                        growth_rate = (last_value - first_value) / first_value * 100
                        growth_rates.append((category, growth_rate))
            
            st.markdown(f"""
            <div class="comparison-container">
                <div class="card">
                    <h4>1週間の成果</h4>
                    <p>記録数: <b>{week_achievements}</b></p>
                    <p>活動カテゴリー: <b>{week_categories}</b></p>
                </div>
                <div class="card">
                    <h4>成長率</h4>
            """, unsafe_allow_html=True)
            
            if growth_rates:
                for category, rate in growth_rates:
                    arrow = "↑" if rate > 0 else "↓" if rate < 0 else "→"
                    color = "green" if rate > 0 else "red" if rate < 0 else "gray"
                    st.markdown(f"<p>{category}: <span style='color:{color}'>{arrow} {rate:.1f}%</span></p>", unsafe_allow_html=True)
            else:
                st.markdown("<p>まだ十分なデータがありません</p>", unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("過去1週間の記録がありません。")
    else:
        st.info("比較するための十分なデータがありません。")
    
    # マイルストーン達成状況
    st.markdown('<h3 class="sub-header">🏆 マイルストーン達成状況</h3>', unsafe_allow_html=True)
    
    milestones = load_milestones()
    achieved_milestones = [m for m in milestones if m['achieved']]
    
    if achieved_milestones:
        for milestone in achieved_milestones[:3]:  # 最新の3つだけ表示
            st.markdown(f"""
            <div class="milestone">
                <h4>{milestone['name']}</h4>
                <p>{milestone['description']}</p>
                <p>達成日: {milestone.get('achieved_date', '記録なし')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("まだマイルストーンを達成していません。継続して記録を増やしていきましょう！")

# 成長記録の追加ページ
def show_add_achievement():
    st.markdown('<h2 class="sub-header">✏️ 成長記録の追加</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    df = load_data()
    emotions = load_emotions()
    
    # フォーム
    with st.form("achievement_form"):
        # 既存のカテゴリーがあれば表示、なければ新規入力
        existing_categories = df['category'].unique() if not df.empty else []
        category_option = st.radio(
            "カテゴリーの選択",
            ["既存のカテゴリーから選択", "新しいカテゴリーを作成"],
            index=0 if len(existing_categories) > 0 else 1
        )
        
        if category_option == "既存のカテゴリーから選択" and len(existing_categories) > 0:
            category = st.selectbox("カテゴリー", existing_categories)
        else:
            category = st.text_input("新しいカテゴリー名")
        
        achievement = st.text_input("達成したこと")
        value = st.number_input("達成値（数値）", min_value=0, value=1)
        date = st.date_input("達成日", datetime.now())
        comment = st.text_area("コメント（できるようになったこと、感じたことなど）")
        
        # 感情の選択
        all_emotions = emotions['positive'] + emotions['neutral'] + emotions['negative']
        emotion = st.selectbox("達成時の感情", all_emotions)
        
        submit = st.form_submit_button("記録を追加")
        
        if submit:
            if not category or not achievement:
                st.error("カテゴリーと達成したことは必須項目です。")
            else:
                # 新しい記録を追加
                new_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "category": category,
                    "achievement": achievement,
                    "value": value,
                    "comment": comment,
                    "emotion": emotion
                }
                
                if df.empty:
                    df = pd.DataFrame([new_record])
                else:
                    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                
                save_data(df)
                
                # 達成記録の追加
                achievements = load_achievements()
                achievement_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "achievement": achievement,
                    "category": category
                }
                achievements.append(achievement_record)
                save_achievements(achievements)
                
                # マイルストーンの確認と更新
                check_and_update_milestones(df)
                
                st.success("記録を追加しました！")
                st.balloons()

# 成長の振り返りページ
def show_reflection():
    st.markdown('<h2 class="sub-header">🔄 成長の振り返り</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    df = load_data()
    
    if df.empty:
        st.info("まだ記録がありません。「成長記録の追加」から最初の記録を追加しましょう！")
        return
    
    # 期間選択
    period = st.selectbox(
        "振り返り期間",
        ["1週間", "1ヶ月", "3ヶ月", "6ヶ月", "1年", "全期間"]
    )
    
    # 期間に基づいてデータをフィルタリング
    filtered_df = filter_by_period(df, period)
    
    if filtered_df.empty:
        st.info(f"選択した期間（{period}）のデータがありません。")
        return
    
    # 成長レポートの生成
    st.markdown('<h3 class="sub-header">📋 成長レポート</h3>', unsafe_allow_html=True)
    
    # 基本統計
    total_achievements = len(filtered_df)
    categories = filtered_df['category'].nunique()
    category_counts = filtered_df['category'].value_counts()
    
    st.markdown(f"""
    <div class="progress-container">
        <h4>{period}の振り返り</h4>
        <p>総記録数: <b>{total_achievements}</b></p>
        <p>活動カテゴリー数: <b>{categories}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # カテゴリー別の活動数グラフ
    fig_category = px.bar(
        category_counts.reset_index(),
        x='category',  # 'index' から 'category' に変更
        y='count',     # 'category' から 'count' に変更
        title="カテゴリー別の記録数",
        labels={'category': 'カテゴリー', 'count': '記録数'}
    )
    st.plotly_chart(fig_category, use_container_width=True)
    
    # 成長率の計算
    growth_data = []
    for category in filtered_df['category'].unique():
        cat_data = filtered_df[filtered_df['category'] == category].sort_values('date')
        if len(cat_data) >= 2:
            first_record = cat_data.iloc[0]
            last_record = cat_data.iloc[-1]
            first_value = first_record['value']
            last_value = last_record['value']
            if first_value > 0:  # ゼロ除算を避ける
                growth_rate = (last_value - first_value) / first_value * 100
                growth_data.append({
                    'category': category,
                    'first_date': first_record['date'],
                    'last_date': last_record['date'],
                    'first_value': first_value,
                    'last_value': last_value,
                    'growth_rate': growth_rate
                })
    
    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        
        # 成長率グラフ
        fig_growth = px.bar(
            growth_df,
            x='category',
            y='growth_rate',
            title="カテゴリー別の成長率",
            labels={'category': 'カテゴリー', 'growth_rate': '成長率 (%)'},
            color='growth_rate',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[-10, max(50, growth_df['growth_rate'].max())]
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # 最も成長したカテゴリー
        if not growth_df.empty:
            max_growth_idx = growth_df['growth_rate'].idxmax()
            max_growth = growth_df.iloc[max_growth_idx]
            
            st.markdown(f"""
            <div class="progress-container">
                <h4>最も成長したカテゴリー: {max_growth['category']}</h4>
                <p>期間: {max_growth['first_date']} から {max_growth['last_date']}</p>
                <p>初期値: {max_growth['first_value']} → 現在値: {max_growth['last_value']}</p>
                <p>成長率: <span style='color:green'>{max_growth['growth_rate']:.1f}%</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("成長率を計算するための十分なデータがありません。")

# 達成リストページ
def show_achievements():
    st.markdown('<h2 class="sub-header">🏅 達成リスト</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    achievements = load_achievements()
    
    if not achievements:
        st.info("まだ達成記録がありません。「成長記録の追加」から最初の記録を追加しましょう！")
        return
    
    # 達成リストをタイムライン形式で表示
    st.markdown("### 達成タイムライン")
    
    # 新しい順に並べ替え
    achievements_sorted = sorted(achievements, key=lambda x: x['date'], reverse=True)
    
    for achievement in achievements_sorted:
        st.markdown(f"""
        <div class="achievement">
            <h4>{achievement['achievement']}</h4>
            <p>カテゴリー: {achievement['category']}</p>
            <p>達成日: {achievement['date']}</p>
        </div>
        """, unsafe_allow_html=True)

# マイルストーンページ
def show_milestones():
    st.markdown('<h2 class="sub-header">🏆 マイルストーン</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    milestones = load_milestones()
    
    if not milestones:
        st.error("マイルストーンデータが読み込めません。")
        return
    
    # 達成済みと未達成のマイルストーンを分ける
    achieved = [m for m in milestones if m.get('achieved', False)]
    not_achieved = [m for m in milestones if not m.get('achieved', False)]
    
    # 達成済みマイルストーン
    st.markdown("### 達成済みマイルストーン")
    
    if achieved:
        for milestone in achieved:
            st.markdown(f"""
            <div class="milestone">
                <h4>{milestone['name']}</h4>
                <p>{milestone['description']}</p>
                <p>達成日: {milestone.get('achieved_date', '記録なし')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("まだマイルストーンを達成していません。継続して記録を増やしていきましょう！")
    
    # 未達成マイルストーン
    st.markdown("### 挑戦中のマイルストーン")
    
    if not_achieved:
        for milestone in not_achieved:
            # 進捗状況の計算
            progress = calculate_milestone_progress(milestone)
            
            st.markdown(f"""
            <div class="milestone" style="opacity: 0.7;">
                <h4>{milestone['name']}</h4>
                <p>{milestone['description']}</p>
                <p>進捗: {progress['current']}/{progress['required']} ({progress['percentage']}%)</p>
                <div style="background-color: #ddd; border-radius: 5px; height: 10px; width: 100%;">
                    <div style="background-color: #4CAF50; border-radius: 5px; height: 10px; width: {min(100, progress['percentage'])}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("すべてのマイルストーンを達成しました！おめでとうございます！")

# ユーティリティ関数
def filter_by_period(df, period):
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    today = pd.Timestamp(datetime.now().date())
    
    if period == "1週間":
        start_date = today - pd.Timedelta(days=7)
    elif period == "1ヶ月":
        start_date = today - pd.Timedelta(days=30)
    elif period == "3ヶ月":
        start_date = today - pd.Timedelta(days=90)
    elif period == "6ヶ月":
        start_date = today - pd.Timedelta(days=180)
    elif period == "1年":
        start_date = today - pd.Timedelta(days=365)
    else:  # 全期間
        return df_copy
    
    return df_copy[df_copy['date'] >= start_date]

def calc_streaks(dates):
    """連続記録の日数を計算する"""
    if len(dates) < 1:
        return []
    
    # 日付をソート
    sorted_dates = sorted(dates)
    
    # 1日ごとのカウント用のインデックスを作成
    date_range = pd.date_range(start=sorted_dates[0], end=sorted_dates[-1])
    date_index = pd.DataFrame(index=date_range)
    
    # 記録がある日付に1を設定
    date_index['recorded'] = 0
    for date in sorted_dates:
        date_index.loc[date, 'recorded'] = 1
    
    # 連続日数の計算
    streaks = []
    current_streak = 0
    
    for recorded in date_index['recorded']:
        if recorded == 1:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 0
    
    # 最後の連続記録を追加
    if current_streak > 0:
        streaks.append(current_streak)
    
    return streaks

def get_emotion_type(emotion):
    """感情のタイプ（positive, neutral, negative）を取得"""
    emotions = load_emotions()
    if emotion in emotions['positive']:
        return 'positive'
    elif emotion in emotions['negative']:
        return 'negative'
    else:
        return 'neutral'

def check_and_update_milestones(df):
    """マイルストーンの達成状況を確認・更新する"""
    milestones = load_milestones()
    updated = False
    
    for i, milestone in enumerate(milestones):
        if not milestone.get('achieved', False):  # まだ達成していないマイルストーンのみチェック
            achieved = False
            
            # マイルストーンのタイプによってチェック方法を変える
            if 'required_count' in milestone:
                # 同じカテゴリーでの繰り返し回数チェック
                category_counts = df['category'].value_counts()
                if (category_counts >= milestone['required_count']).any():
                    achieved = True
            
            elif 'required_growth' in milestone:
                # 成長率のチェック
                for category in df['category'].unique():
                    cat_data = df[df['category'] == category].sort_values('date')
                    if len(cat_data) >= 2:
                        first_value = cat_data.iloc[0]['value']
                        last_value = cat_data.iloc[-1]['value']
                        if first_value > 0:  # ゼロ除算を避ける
                            growth_rate = (last_value - first_value) / first_value * 100
                            if growth_rate >= milestone['required_growth']:
                                achieved = True
                                break
            
            elif 'required_total' in milestone:
                # 総記録数のチェック
                if len(df) >= milestone['required_total']:
                    achieved = True

            elif 'required_streak' in milestone:
                # 連続記録のチェック
                dates = pd.to_datetime(df.sort_values('date')['date'])
                streaks = calc_streaks(dates)
                if streaks and max(streaks) >= milestone['required_streak']:
                    achieved = True
            
            elif 'required_categories' in milestone:
                # カテゴリー数のチェック
                if df['category'].nunique() >= milestone['required_categories']:
                    achieved = True
            
            # 達成した場合、マイルストーンを更新
            if achieved:
                milestones[i]['achieved'] = True
                milestones[i]['achieved_date'] = datetime.now().strftime("%Y-%m-%d")
                updated = True
    
    if updated:
        save_milestones(milestones)

def calculate_milestone_progress(milestone):
    """マイルストーンの進捗状況を計算する"""
    df = load_data()
    
    if 'required_count' in milestone:
        # 同じカテゴリーでの繰り返し回数チェック
        category_counts = df['category'].value_counts()
        max_count = category_counts.max() if not category_counts.empty else 0
        return {
            'current': max_count,
            'required': milestone['required_count'],
            'percentage': min(100, int(max_count / milestone['required_count'] * 100))
        }
    
    elif 'required_growth' in milestone:
        # 成長率のチェック
        max_growth = 0
        for category in df['category'].unique():
            cat_data = df[df['category'] == category].sort_values('date')
            if len(cat_data) >= 2:
                first_value = cat_data.iloc[0]['value']
                last_value = cat_data.iloc[-1]['value']
                if first_value > 0:  # ゼロ除算を避ける
                    growth_rate = (last_value - first_value) / first_value * 100
                    max_growth = max(max_growth, growth_rate)
        
        return {
            'current': round(max_growth, 1),
            'required': milestone['required_growth'],
            'percentage': min(100, int(max_growth / milestone['required_growth'] * 100))
        }
    
    elif 'required_total' in milestone:
        # 総記録数のチェック
        total = len(df)
        return {
            'current': total,
            'required': milestone['required_total'],
            'percentage': min(100, int(total / milestone['required_total'] * 100))
        }
    
    elif 'required_streak' in milestone:
        # 連続記録のチェック
        dates = pd.to_datetime(df.sort_values('date')['date'])
        streaks = calc_streaks(dates)
        max_streak = max(streaks) if streaks else 0
        
        return {
            'current': max_streak,
            'required': milestone['required_streak'],
            'percentage': min(100, int(max_streak / milestone['required_streak'] * 100))
        }
    
    elif 'required_categories' in milestone:
        # カテゴリー数のチェック
        categories = df['category'].nunique()
        return {
            'current': categories,
            'required': milestone['required_categories'],
            'percentage': min(100, int(categories / milestone['required_categories'] * 100))
        }
    
    return {'current': 0, 'required': 1, 'percentage': 0}

def generate_monthly_report():
    """月間レポートを自動生成する"""
    df = load_data()
    if df.empty:
        return "まだデータがありません。"
    
    # 今月のデータ
    df['date'] = pd.to_datetime(df['date'])
    today = datetime.now()
    first_day = today.replace(day=1)
    last_month = first_day - timedelta(days=1)
    first_day_last_month = last_month.replace(day=1)
    
    # 先月のデータを抽出
    last_month_data = df[(df['date'] >= first_day_last_month) & (df['date'] < first_day)]
    
    if last_month_data.empty:
        return "先月のデータがありません。"
    
    # 基本統計
    total_achievements = len(last_month_data)
    categories = last_month_data['category'].nunique()
    category_counts = last_month_data['category'].value_counts()
    most_frequent_category = category_counts.idxmax() if not category_counts.empty else "なし"
    
    # 成長率の計算
    growth_data = []
    for category in last_month_data['category'].unique():
        cat_data = last_month_data[last_month_data['category'] == category].sort_values('date')
        if len(cat_data) >= 2:
            first_value = cat_data.iloc[0]['value']
            last_value = cat_data.iloc[-1]['value']
            if first_value > 0:  # ゼロ除算を避ける
                growth_rate = (last_value - first_value) / first_value * 100
                growth_data.append((category, growth_rate))
    
    # レポート生成
    report = f"## {last_month.year}年{last_month.month}月の振り返りレポート\n\n"
    report += f"### 基本統計\n"
    report += f"- 総記録数: {total_achievements}件\n"
    report += f"- 活動カテゴリー数: {categories}個\n"
    report += f"- 最も活動したカテゴリー: {most_frequent_category}\n\n"
    
    if growth_data:
        report += f"### 成長率\n"
        for category, rate in sorted(growth_data, key=lambda x: x[1], reverse=True):
            report += f"- {category}: {rate:.1f}%\n"
        
        max_growth = max(growth_data, key=lambda x: x[1]) if growth_data else None
        if max_growth:
            report += f"\n**今月最も成長したのは {max_growth[0]} でした！ (成長率: {max_growth[1]:.1f}%)**\n\n"
    
    # 感情分析
    emotions = load_emotions()
    last_month_data['emotion_type'] = last_month_data['emotion'].apply(lambda x: 
        'positive' if x in emotions['positive'] else 
        'negative' if x in emotions['negative'] else 'neutral'
    )
    
    emotion_counts = last_month_data['emotion_type'].value_counts()
    total_emotions = emotion_counts.sum()
    
    if total_emotions > 0:
        report += f"### 感情分析\n"
        positive_ratio = emotion_counts.get('positive', 0) / total_emotions * 100
        report += f"- ポジティブな感情の割合: {positive_ratio:.1f}%\n"
        report += f"- ニュートラルな感情の割合: {emotion_counts.get('neutral', 0) / total_emotions * 100:.1f}%\n"
        report += f"- ネガティブな感情の割合: {emotion_counts.get('negative', 0) / total_emotions * 100:.1f}%\n\n"
        
        if positive_ratio >= 70:
            report += "**素晴らしい！ポジティブな感情が多かった月でした！**\n\n"
        elif positive_ratio >= 50:
            report += "**良い傾向です。ポジティブな感情がやや多めでした。**\n\n"
        else:
            report += "**次の月はもう少しポジティブな体験を増やしていきましょう。**\n\n"
    
    # 今月の目標提案
    report += f"### 来月の目標提案\n"
    
    # カテゴリーごとの提案
    for category in last_month_data['category'].unique():
        report += f"- **{category}**: "
        cat_data = last_month_data[last_month_data['category'] == category].sort_values('date')
        if len(cat_data) >= 2:
            last_value = cat_data.iloc[-1]['value']
            # 簡単な目標提案（前月の最終値から5-10%アップ）
            target = last_value * (1 + random.uniform(0.05, 0.1))
            report += f"目標値 {target:.1f} を目指しましょう！\n"
        else:
            report += f"継続して記録していきましょう！\n"
    
    report += "\n**新しい月も頑張りましょう！**"
    
    return report

# 選択したページを表示
if page == "ダッシュボード":
    show_dashboard()
elif page == "成長記録の追加":
    show_add_achievement()
elif page == "成長の振り返り":
    show_reflection()
elif page == "達成リスト":
    show_achievements()
elif page == "マイルストーン":
    show_milestones()