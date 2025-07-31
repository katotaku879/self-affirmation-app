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
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# NLTKのダウンロード（初回実行時のみ必要）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# ページの設定
st.set_page_config(
    page_title="自己分析 - 自己肯定アプリ",
    page_icon="🔍",
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
    .insight-card {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #4CAF50;
    }
    .trend-card {
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
    .negative-card {
        background-color: #FFEBEE;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #F44336;
    }
    .strength-item {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .weakness-item {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #FFC107;
    }
    .pattern-item {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
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
    .tag-cloud {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        background-color: #F5F5F5;
        margin: 10px 0;
    }
    .tag-item {
        display: inline-block;
        margin: 5px;
        padding: 3px 10px;
        border-radius: 15px;
        background-color: #E3F2FD;
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
    .thought-pattern {
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .thought-negative {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .thought-positive {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .thought-neutral {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
    }
    .suggestion {
        background-color: #E8F5E9;
        padding: 10px;
        border-radius: 10px;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 既存のデータファイルパス
EMOTION_LOGS_FILE = "emotion_logs.json"
GROWTH_DATA_FILE = "growth_data.json"
GOALS_FILE = "goals.json"
HABIT_RECORDS_FILE = "habit_records.json"
SMALL_WINS_FILE = "small_wins.json"
ACTIVITY_LOG_FILE = "activity_log.json"

# 新しいデータファイルパス
ANALYSIS_REPORT_FILE = "analysis_report.json"
THOUGHT_PATTERNS_FILE = "analysis_thought_patterns.json"
STRENGTH_WEAKNESS_FILE = "strength_weakness.json"
SELF_ESTEEM_LOG_FILE = "self_esteem_log.json"

# データファイルの初期化
def initialize_analysis_files():
    if not os.path.exists(ANALYSIS_REPORT_FILE):
        with open(ANALYSIS_REPORT_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(THOUGHT_PATTERNS_FILE):
        default_patterns = {
            "patterns": [
                {"id": "perfectionism", "name": "完璧主義", "count": 0, "keywords": ["しなければならない", "べき", "完璧", "失敗できない"], "examples": [], "type": "negative"},
                {"id": "negative_filter", "name": "ネガティブフィルター", "count": 0, "keywords": ["どうせ", "無理", "失敗", "できない"], "examples": [], "type": "negative"},
                {"id": "overgeneralization", "name": "過度の一般化", "count": 0, "keywords": ["いつも", "必ず", "絶対に", "全部"], "examples": [], "type": "negative"},
                {"id": "mindreading", "name": "心の読み過ぎ", "count": 0, "keywords": ["思われている", "思っているだろう", "嫌われている", "批判されている"], "examples": [], "type": "negative"},
                {"id": "positive_attitude", "name": "ポジティブ思考", "count": 0, "keywords": ["できる", "成長", "学び", "感謝"], "examples": [], "type": "positive"},
                {"id": "growth_mindset", "name": "成長思考", "count": 0, "keywords": ["挑戦", "学習", "進歩", "努力"], "examples": [], "type": "positive"}
            ]
        }
        with open(THOUGHT_PATTERNS_FILE, "w") as f:
            json.dump(default_patterns, f)
    
    if not os.path.exists(STRENGTH_WEAKNESS_FILE):
        default_strengths = {
            "strengths": [
                {"id": "persistence", "name": "粘り強さ", "score": 0, "evidence": []},
                {"id": "creativity", "name": "創造性", "score": 0, "evidence": []},
                {"id": "empathy", "name": "共感力", "score": 0, "evidence": []},
                {"id": "planning", "name": "計画力", "score": 0, "evidence": []}
            ],
            "weaknesses": [
                {"id": "procrastination", "name": "先延ばし", "score": 0, "evidence": []},
                {"id": "self_criticism", "name": "自己批判", "score": 0, "evidence": []},
                {"id": "inconsistency", "name": "不一貫性", "score": 0, "evidence": []}
            ]
        }
        with open(STRENGTH_WEAKNESS_FILE, "w") as f:
            json.dump(default_strengths, f)
    
    if not os.path.exists(SELF_ESTEEM_LOG_FILE):
        with open(SELF_ESTEEM_LOG_FILE, "w") as f:
            json.dump([], f)

# 初期化を実行
initialize_analysis_files()

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

def load_analysis_reports():
    try:
        with open(ANALYSIS_REPORT_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

def load_thought_patterns():
    try:
        with open(THOUGHT_PATTERNS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"patterns": []}

def load_strength_weakness():
    try:
        with open(STRENGTH_WEAKNESS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"strengths": [], "weaknesses": []}

def load_self_esteem_log():
    try:
        with open(SELF_ESTEEM_LOG_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data) if data else pd.DataFrame()
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

# データ保存関数
def save_analysis_reports(df):
    with open(ANALYSIS_REPORT_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

def save_thought_patterns(patterns_data):
    with open(THOUGHT_PATTERNS_FILE, "w") as f:
        json.dump(patterns_data, f)

def save_strength_weakness(strength_data):
    with open(STRENGTH_WEAKNESS_FILE, "w") as f:
        json.dump(strength_data, f)

def save_self_esteem_log(df):
    with open(SELF_ESTEEM_LOG_FILE, "w") as f:
        json.dump(df.to_dict("records"), f)

# マルチページアプリのタイトル
st.markdown('<h1 class="main-header">🔍 自己分析</h1>', unsafe_allow_html=True)

# ページナビゲーション
page = st.sidebar.radio(
    "自己分析メニュー",
    ["行動・感情分析", "強み・弱み分析", "目標傾向分析", "自己肯定感トラッカー"],
)

# 行動・感情分析ページ
def show_behavior_emotion_analysis():
    st.markdown('<h2 class="sub-header">📊 行動・感情分析</h2>', unsafe_allow_html=True)
    
    # 各種データの読み込み
    emotion_logs = load_emotion_logs()
    growth_data = load_growth_data()
    habit_records = load_habit_records()
    small_wins = load_small_wins()
    activity_log = load_activity_log()
    
    # データがない場合の処理
    if (emotion_logs.empty and growth_data.empty and 
        habit_records.empty and small_wins.empty and activity_log.empty):
        st.warning("分析に必要なデータがまだ十分にありません。他の機能を使って活動データを増やしましょう！")
        return
    
    # 感情ログの分析
    st.markdown("### 感情傾向の分析")
    
    if not emotion_logs.empty and 'emotion' in emotion_logs.columns:
        # 感情の種類をカウント
        emotions_count = emotion_logs['emotion'].value_counts()
        
        # 最も多い感情
        if not emotions_count.empty:
            top_emotion = emotions_count.index[0]
            top_count = emotions_count.iloc[0]
            
            st.markdown(f"""
            <div class="insight-card">
                <h4>最も多く記録された感情</h4>
                <p>あなたが最もよく記録している感情は「<strong>{top_emotion}</strong>」で、{top_count}回記録されています。</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 感情の円グラフ
            fig_emotion = px.pie(
                emotions_count.reset_index(),
                values=emotions_count.values,
                names=emotions_count.index,
                title="感情の分布",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_emotion, use_container_width=True)
        
        # 感情の種類を正・中立・負に分類
        if 'emotion_type' in emotion_logs.columns:
            # 既存の感情タイプ列を使用
            emotion_types = emotion_logs['emotion_type'].value_counts()
        else:
            # 感情タイプを定義
            positive_emotions = ["喜び", "楽しさ", "満足", "安心", "希望", "感謝", "興味", "誇り"]
            negative_emotions = ["悲しみ", "不安", "怒り", "恐れ", "疲労", "退屈", "混乱", "罪悪感"]
            
            # 感情タイプを追加
            emotion_logs['emotion_type'] = emotion_logs['emotion'].apply(
                lambda x: "positive" if x in positive_emotions else 
                ("negative" if x in negative_emotions else "neutral")
            )
            
            emotion_types = emotion_logs['emotion_type'].value_counts()
        
        if not emotion_types.empty:
            # 感情タイプの円グラフ
            fig_types = px.pie(
                emotion_types.reset_index(),
                values=emotion_types.values,
                names=emotion_types.index,
                title="感情タイプの分布",
                color_discrete_map={
                    "positive": "#4CAF50",
                    "neutral": "#FFC107",
                    "negative": "#F44336"
                }
            )
            st.plotly_chart(fig_types, use_container_width=True)
            
            # 感情タイプの割合計算
            positive_ratio = emotion_types.get("positive", 0) / emotion_types.sum() * 100 if not emotion_types.empty else 0
            negative_ratio = emotion_types.get("negative", 0) / emotion_types.sum() * 100 if not emotion_types.empty else 0
            
            # 感情バランスの解釈
            emotional_balance = ""
            if positive_ratio > 60:
                emotional_balance = f"""
                <div class="insight-card">
                    <h4>感情バランスの分析</h4>
                    <p>あなたの記録にはポジティブな感情が<strong>{positive_ratio:.1f}%</strong>を占めています。これは心理的な健康状態が良好であることを示唆しています。</p>
                    <p>ポジティブな感情の割合が高いことは、レジリエンス（回復力）があり、ストレスへの対処力が高いことの表れかもしれません。</p>
                </div>
                """
            elif positive_ratio > 40:
                emotional_balance = f"""
                <div class="insight-card">
                    <h4>感情バランスの分析</h4>
                    <p>あなたの記録ではポジティブな感情が<strong>{positive_ratio:.1f}%</strong>、ネガティブな感情が<strong>{negative_ratio:.1f}%</strong>とバランスが取れています。</p>
                    <p>バランスの取れた感情の記録は、現実的な認識と健全な感情処理能力の表れかもしれません。</p>
                </div>
                """
            else:
                emotional_balance = f"""
                <div class="warning-card">
                    <h4>感情バランスの分析</h4>
                    <p>あなたの記録ではネガティブな感情が<strong>{negative_ratio:.1f}%</strong>を占めています。これは何か対処すべきストレスや課題がある可能性を示唆しています。</p>
                    <p>意識的にポジティブな体験を増やし、必要であれば専門家のサポートを検討することも有益かもしれません。</p>
                </div>
                """
            
            st.markdown(emotional_balance, unsafe_allow_html=True)
        
        # 時系列での感情変化
        if 'date' in emotion_logs.columns:
            # 日付を変換
            emotion_logs['date'] = pd.to_datetime(emotion_logs['date'])
            
            # 時系列でグループ化
            emotion_by_date = emotion_logs.groupby(['date', 'emotion_type']).size().reset_index()
            emotion_by_date.columns = ['date', 'emotion_type', 'count']
            
            # 時系列グラフ
            fig_timeline = px.line(
                emotion_by_date,
                x='date',
                y='count',
                color='emotion_type',
                title="時間経過による感情の変化",
                labels={'date': '日付', 'count': '回数', 'emotion_type': '感情タイプ'},
                color_discrete_map={
                    "positive": "#4CAF50",
                    "neutral": "#FFC107",
                    "negative": "#F44336"
                }
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("感情ログのデータがまだ十分にありません。「感情ログ」機能を使って記録を増やしましょう！")
    
    # 行動と成長の関連分析
    st.markdown("### 行動と成長の関連分析")
    
    # 習慣と気分の関連
    if not habit_records.empty and not emotion_logs.empty:
        # 日付ごとのデータ準備
        if 'date' in habit_records.columns and 'date' in emotion_logs.columns:
            # 日付を揃える
            habit_records['date'] = pd.to_datetime(habit_records['date']).dt.date
            emotion_logs['date'] = pd.to_datetime(emotion_logs['date']).dt.date
            
            # 両方のデータがある日を抽出
            common_dates = set(habit_records['date']) & set(emotion_logs['date'])
            
            if common_dates:
                # 習慣達成日と感情の関連を分析
                habit_completion = habit_records[habit_records['status'] == 'completed']
                habit_completion_dates = set(habit_completion['date'])
                
                # 習慣達成日と未達成日の感情を比較
                completed_emotion_logs = emotion_logs[emotion_logs['date'].isin(habit_completion_dates)]
                not_completed_emotion_logs = emotion_logs[~emotion_logs['date'].isin(habit_completion_dates)]
                
                # 感情タイプの比較
                if 'emotion_type' in completed_emotion_logs.columns and 'emotion_type' in not_completed_emotion_logs.columns:
                    completed_emotion_types = completed_emotion_logs['emotion_type'].value_counts(normalize=True) * 100
                    not_completed_emotion_types = not_completed_emotion_logs['emotion_type'].value_counts(normalize=True) * 100
                    
                    # ポジティブ感情の割合比較
                    completed_positive = completed_emotion_types.get("positive", 0)
                    not_completed_positive = not_completed_emotion_types.get("positive", 0)
                    
                    positive_diff = completed_positive - not_completed_positive
                    
                    if abs(positive_diff) > 10:
                        habit_emotion_insight = f"""
                        <div class="trend-card">
                            <h4>習慣達成と気分の関連</h4>
                            <p>習慣を達成した日は、達成しなかった日に比べて、ポジティブな感情の割合が<strong>{abs(positive_diff):.1f}%{'高い' if positive_diff > 0 else '低い'}</strong>傾向があります。</p>
                            <p>{'習慣の達成があなたの気分を向上させている可能性があります。継続していきましょう！' if positive_diff > 0 else '習慣の達成とネガティブな感情に関連がある可能性があります。習慣の内容や達成方法を見直してみましょう。'}</p>
                        </div>
                        """
                        st.markdown(habit_emotion_insight, unsafe_allow_html=True)
    
    # 活動と成長の関連分析
    activity_data_exists = (not growth_data.empty and not activity_log.empty)
    
    if activity_data_exists:
        # 日付データの準備
        if 'date' in growth_data.columns and 'date' in activity_log.columns:
            # 日付を揃える
            growth_data['date'] = pd.to_datetime(growth_data['date']).dt.date
            activity_log['date'] = pd.to_datetime(activity_log['date']).dt.date
            
            # 活動タイプと成長カテゴリの分析
            if 'category' in growth_data.columns and 'activity_type' in activity_log.columns:
                # 成長カテゴリ別の活動タイプ
                growth_categories = growth_data['category'].unique()
                activity_types = activity_log['activity_type'].unique()
                
                category_activity_data = []
                
                for category in growth_categories:
                    category_dates = set(growth_data[growth_data['category'] == category]['date'])
                    
                    for activity in activity_types:
                        activity_dates = set(activity_log[activity_log['activity_type'] == activity]['date'])
                        
                        # 共通の日付
                        common_days = len(category_dates & activity_dates)
                        
                        if common_days > 0:
                            category_activity_data.append({
                                'category': category,
                                'activity': activity,
                                'common_days': common_days
                            })
                
                if category_activity_data:
                    category_activity_df = pd.DataFrame(category_activity_data)
                    
                    # トップの組み合わせを抽出
                    top_combination = category_activity_df.sort_values('common_days', ascending=False).iloc[0]
                    
                    st.markdown(f"""
                    <div class="trend-card">
                        <h4>活動と成長の関連</h4>
                        <p>あなたは「<strong>{top_combination['activity']}</strong>」という活動を行った日に、「<strong>{top_combination['category']}</strong>」カテゴリーでの成長を記録する傾向があります。</p>
                        <p>この組み合わせは{top_combination['common_days']}日間で見られました。この関連性を活かして、意識的に成長を促進できるかもしれません。</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 関連をヒートマップで表示
                    pivot_df = category_activity_df.pivot(index='category', columns='activity', values='common_days').fillna(0)
                    
                    fig_heatmap = px.imshow(
                        pivot_df,
                        labels=dict(x="活動タイプ", y="成長カテゴリ", color="共通日数"),
                        title="活動タイプと成長カテゴリの関連性",
                        color_continuous_scale="Viridis"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 成長を感じた出来事のランキング
    st.markdown("### 成長を感じた出来事ランキング")
    
    if not small_wins.empty:
        # 小さな成功体験を分析
        if 'description' in small_wins.columns and 'date' in small_wins.columns:
            # 日付を揃える
            small_wins['date'] = pd.to_datetime(small_wins['date'])
            
            # 直近1ヶ月のデータを抽出
            one_month_ago = datetime.now() - timedelta(days=30)
            recent_wins = small_wins[small_wins['date'] >= one_month_ago]
            
            if not recent_wins.empty:
                # 感情分析（もし感情データがあれば）
                if 'feeling' in recent_wins.columns:
                    feeling_counts = recent_wins['feeling'].value_counts()
                    top_feelings = feeling_counts.head(3)
                    
                    st.markdown("#### この1ヶ月で最も感じた達成感情")
                    
                    feeling_cols = st.columns(min(3, len(top_feelings)))
                    
                    for i, (feeling, count) in enumerate(top_feelings.items()):
                        with feeling_cols[i % 3]:
                            st.markdown(f"""
                            <div class="stat-card">
                                <p>{feeling}</p>
                                <p class="stat-value">{count}</p>
                                <p>回</p>
                            </div>
                            """, unsafe_allow_html=True)

            # 成長を感じた出来事のテキスト分析
                win_texts = recent_wins['description'].tolist()
                
                # 簡易的な単語頻度分析
                all_text = " ".join(win_texts)
                
                # 形態素解析（簡易的な方法）
                try:
                    words = word_tokenize(all_text)
                    stop_words = set(stopwords.words('english'))
                    
                    # ストップワードの除去
                    words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
                    
                    # 単語の頻度をカウント
                    word_freq = Counter(words)
                    
                    # 上位の単語を表示
                    top_words = word_freq.most_common(10)
                    
                    if top_words:
                        st.markdown("#### 成長の記録によく出てくるキーワード")
                        
                        st.markdown('<div class="tag-cloud">', unsafe_allow_html=True)
                        
                        for word, count in top_words:
                            # フォントサイズを頻度に応じて変更
                            font_size = 14 + min(count * 2, 24)
                            
                            st.markdown(f"""
                            <span class="tag-item" style="font-size: {font_size}px">{word} ({count})</span>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # キーワード分析の解釈
                        st.markdown(f"""
                        <div class="insight-card">
                            <h4>キーワード分析</h4>
                            <p>あなたの成長記録からは、「<strong>{top_words[0][0]}</strong>」というキーワードが最も多く登場しています。これはあなたの成長や成功において重要な要素であることを示唆しています。</p>
                            <p>記録を続けることで、あなたの成長パターンやキーワードの変化を追跡できます。</p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"テキスト分析中にエラーが発生しました: {e}")
                
                # 成長を感じた出来事のランキング
                st.markdown("#### この1ヶ月で最も成長を感じた出来事")
                
                # 日付順にソートして表示
                sorted_wins = recent_wins.sort_values('date', ascending=False)
                
                for i, (_, win) in enumerate(sorted_wins.head(3).iterrows()):
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>#{i+1}: {win['date'].strftime('%Y/%m/%d')}</h4>
                        <p>{win['description']}</p>
                        <p><em>感情: {win.get('feeling', '記録なし')}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("最近の成長記録がありません。「小さな成功の記録」機能を使って記録を増やしましょう！")
    else:
        st.info("成長記録のデータがまだありません。「小さな成功の記録」機能を使って記録を増やしましょう！")
    
    # AIによる行動傾向の分析と提案
    st.markdown("### AIによる行動傾向の分析")
    
    # 活動ログと感情ログのデータがある場合
    data_available = not activity_log.empty and not emotion_logs.empty
    
    if data_available:
        # モチベーションが高かった日の分析
        if 'date' in activity_log.columns and 'date' in emotion_logs.columns and 'emotion_type' in emotion_logs.columns:
            # 日付を揃える
            activity_log['date'] = pd.to_datetime(activity_log['date']).dt.date
            emotion_logs['date'] = pd.to_datetime(emotion_logs['date']).dt.date
            
            # ポジティブ感情が記録された日
            positive_days = set(emotion_logs[emotion_logs['emotion_type'] == 'positive']['date'])
            
            # ポジティブな日の活動タイプをカウント
            positive_day_activities = activity_log[activity_log['date'].isin(positive_days)]
            
            if not positive_day_activities.empty and 'activity_type' in positive_day_activities.columns:
                activity_counts = positive_day_activities['activity_type'].value_counts()
                
                if not activity_counts.empty:
                    top_activity = activity_counts.index[0]
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>モチベーション向上の活動傾向</h4>
                        <p>あなたがポジティブな感情を記録した日には、「<strong>{top_activity}</strong>」という活動を行う傾向があります。</p>
                        <p>モチベーションを高めたいときは、この活動を意識的に取り入れることを検討してみましょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 活動頻度のグラフ
                    fig_activities = px.bar(
                        activity_counts.reset_index(),
                        x='index',
                        y=activity_counts.values,
                        title="ポジティブな日に行った活動",
                        labels={'index': '活動タイプ', 'y': '回数'}
                    )
                    st.plotly_chart(fig_activities, use_container_width=True)
        
        # 成長しやすい行動パターンの分析
        if not growth_data.empty and 'date' in growth_data.columns:
            # 日付の整形
            growth_data['date'] = pd.to_datetime(growth_data['date']).dt.date
            
            # 成長記録がある日の活動を分析
            growth_days = set(growth_data['date'])
            growth_day_activities = activity_log[activity_log['date'].isin(growth_days)]
            
            if not growth_day_activities.empty and 'activity_type' in growth_day_activities.columns:
                growth_activity_counts = growth_day_activities['activity_type'].value_counts()
                
                if not growth_activity_counts.empty:
                    top_growth_activity = growth_activity_counts.index[0]
                    
                    st.markdown(f"""
                    <div class="trend-card">
                        <h4>成長につながる行動パターン</h4>
                        <p>あなたが成長を記録した日には、「<strong>{top_growth_activity}</strong>」という活動を行う傾向があります。</p>
                        <p>この行動は、あなたの成長を促進している可能性があります。意識的に取り入れることで、さらなる成長が期待できるでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("行動と感情の関連分析には、さらに多くのデータが必要です。「感情ログ」や「活動ログ」を記録していきましょう！")                

# 強み・弱み分析ページ
def show_strength_weakness_analysis():
    st.markdown('<h2 class="sub-header">💪 強み・弱み分析</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    growth_data = load_growth_data()
    emotion_logs = load_emotion_logs()
    goals = load_goals()
    habit_records = load_habit_records()
    small_wins = load_small_wins()
    strength_weakness = load_strength_weakness()
    
    # データがない場合の処理
    if (growth_data.empty and emotion_logs.empty and 
        goals.empty and habit_records.empty and small_wins.empty):
        st.warning("分析に必要なデータがまだ十分にありません。他の機能を使って活動データを増やしましょう！")
        return
    
    # 強み・弱みの概要
    st.markdown("### あなたの強み・弱みの概要")
    
    # 現在の強み・弱みを表示
    if strength_weakness["strengths"] and strength_weakness["weaknesses"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 強み")
            
            for strength in strength_weakness["strengths"]:
                # スコアに基づいて表示を調整
                if strength["score"] > 7:
                    st.markdown(f"""
                    <div class="strength-item">
                        <h4>{strength["name"]} <span style="float:right;">⭐⭐⭐</span></h4>
                        <p>スコア: {strength["score"]}/10</p>
                        <p>これはあなたの大きな強みです。積極的に活用していきましょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif strength["score"] > 4:
                    st.markdown(f"""
                    <div class="strength-item">
                        <h4>{strength["name"]} <span style="float:right;">⭐⭐</span></h4>
                        <p>スコア: {strength["score"]}/10</p>
                        <p>これはあなたの強みの一つです。より意識的に活用できるでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="strength-item">
                        <h4>{strength["name"]} <span style="float:right;">⭐</span></h4>
                        <p>スコア: {strength["score"]}/10</p>
                        <p>まだ十分に発揮されていない強みかもしれません。</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 改善点")
            
            for weakness in strength_weakness["weaknesses"]:
                # スコアに基づいて表示を調整
                if weakness["score"] > 7:
                    st.markdown(f"""
                    <div class="weakness-item">
                        <h4>{weakness["name"]} <span style="float:right;">⚠️⚠️⚠️</span></h4>
                        <p>スコア: {weakness["score"]}/10</p>
                        <p>これは重点的に改善すると効果が高い領域です。</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif weakness["score"] > 4:
                    st.markdown(f"""
                    <div class="weakness-item">
                        <h4>{weakness["name"]} <span style="float:right;">⚠️⚠️</span></h4>
                        <p>スコア: {weakness["score"]}/10</p>
                        <p>このパターンが時々見られます。意識することで改善できるでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="weakness-item">
                        <h4>{weakness["name"]} <span style="float:right;">⚠️</span></h4>
                        <p>スコア: {weakness["score"]}/10</p>
                        <p>ほとんど問題になっていませんが、注意しておくと良いでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # 強み・弱みの分析と評価
    st.markdown("### 強み・弱みの詳細分析")
    
    # 強み分析タブ
    tab1, tab2 = st.tabs(["強み分析", "改善点分析"])
    
    with tab1:
        # 強みの自己評価
        st.markdown("#### 強みの自己評価")
        
        # 現在の強みのリスト
        strengths = strength_weakness["strengths"]
        
        # 選択する強み
        strength_options = [s["name"] for s in strengths] + ["新しい強みを追加"]
        selected_strength = st.selectbox("評価する強み", strength_options)
        
        if selected_strength == "新しい強みを追加":
            # 新しい強みの追加
            with st.form("new_strength_form"):
                new_strength_name = st.text_input("新しい強みの名前")
                new_strength_score = st.slider("自己評価スコア (1-10)", 1, 10, 5)
                new_strength_evidence = st.text_area("具体的なエピソードや証拠")
                
                submit_button = st.form_submit_button("強みを追加")
                
                if submit_button:
                    if not new_strength_name:
                        st.error("強みの名前を入力してください。")
                    else:
                        # 新しい強みを追加
                        new_strength = {
                            "id": str(uuid.uuid4()),
                            "name": new_strength_name,
                            "score": new_strength_score,
                            "evidence": [new_strength_evidence] if new_strength_evidence else []
                        }
                        
                        strength_weakness["strengths"].append(new_strength)
                        save_strength_weakness(strength_weakness)
                        
                        st.success(f"新しい強み「{new_strength_name}」を追加しました！")
                        st.experimental_rerun()
        else:
            # 既存の強みの更新
            selected_strength_data = next((s for s in strengths if s["name"] == selected_strength), None)
            
            if selected_strength_data:
                with st.form("update_strength_form"):
                    updated_score = st.slider("自己評価スコア (1-10)", 1, 10, selected_strength_data["score"])
                    
                    # 既存の証拠を表示
                    if selected_strength_data["evidence"]:
                        st.markdown("##### 既存のエピソード・証拠")
                        for i, evidence in enumerate(selected_strength_data["evidence"]):
                            st.text_area(f"エピソード {i+1}", evidence, disabled=True)
                    
                    new_evidence = st.text_area("新たなエピソードや証拠を追加")
                    
                    submit_button = st.form_submit_button("強みを更新")
                    
                    if submit_button:
                        # 強みを更新
                        for i, s in enumerate(strength_weakness["strengths"]):
                            if s["id"] == selected_strength_data["id"]:
                                strength_weakness["strengths"][i]["score"] = updated_score
                                if new_evidence:
                                    strength_weakness["strengths"][i]["evidence"].append(new_evidence)
                                break
                        
                        save_strength_weakness(strength_weakness)
                        
                        st.success(f"強み「{selected_strength}」を更新しました！")
                        st.experimental_rerun()
        
        # 強みの活かし方提案
        st.markdown("#### 強みの活かし方")
        
        # 高評価の強みを特定
        top_strengths = [s for s in strengths if s["score"] >= 7]
        
        if top_strengths:
            for strength in top_strengths:
                # 強みごとの活かし方提案
                if strength["name"] == "粘り強さ":
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{strength["name"]}の活かし方</h4>
                        <ul>
                            <li>長期的な目標を設定し、小さなステップに分けて取り組む</li>
                            <li>難易度の高いプロジェクトや技術的な習得にチャレンジする</li>
                            <li>困難に直面している人のメンターやサポート役になる</li>
                            <li>複雑な問題解決を要する状況で自分の強みを活かす</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif strength["name"] == "創造性":
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{strength["name"]}の活かし方</h4>
                        <ul>
                            <li>新しいアイデアやプロジェクトを積極的に提案する</li>
                            <li>問題解決に対して複数の視点からアプローチを考える</li>
                            <li>ブレインストーミングやアイデア出しの場で力を発揮する</li>
                            <li>芸術的な表現活動やクリエイティブな趣味に取り組む</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif strength["name"] == "共感力":
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{strength["name"]}の活かし方</h4>
                        <ul>
                            <li>チームの調和やコミュニケーションを促進する役割を担う</li>
                            <li>対人関係を重視する職種やプロジェクトに参加する</li>
                            <li>メンタリングや相談役として他者をサポートする</li>
                            <li>多様な視点や感情を理解できる強みを活かした意思決定をする</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif strength["name"] == "計画力":
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{strength["name"]}の活かし方</h4>
                        <ul>
                            <li>プロジェクト管理やチームコーディネート役を担当する</li>
                            <li>複雑なタスクを整理し、効率的な実行計画を立てる</li>
                            <li>目標達成のためのシステムや仕組みづくりを行う</li>
                            <li>予測困難な状況に対しても代替プランを用意する</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>{strength["name"]}の活かし方</h4>
                        <p>この強みを最大限に活かすには：</p>
                        <ul>
                            <li>この強みを必要とする状況や環境を積極的に選ぶ</li>
                            <li>日常生活の中でこの強みを発揮する機会を意識的に作る</li>
                            <li>この強みをさらに磨くための学習や練習に取り組む</li>
                            <li>この強みを活かして他者をサポートしたり、価値を提供する</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("まだ高評価の強みが登録されていません。自己評価を行って強みを発見しましょう！")
    
    with tab2:
        # 弱みの自己評価
        st.markdown("#### 改善点の自己評価")
        
        # 現在の弱みのリスト
        weaknesses = strength_weakness["weaknesses"]
        
        # 選択する弱み
        weakness_options = [w["name"] for w in weaknesses] + ["新しい改善点を追加"]
        selected_weakness = st.selectbox("評価する改善点", weakness_options)
        
        if selected_weakness == "新しい改善点を追加":
            # 新しい弱みの追加
            with st.form("new_weakness_form"):
                new_weakness_name = st.text_input("新しい改善点の名前")
                new_weakness_score = st.slider("自己評価スコア (1-10)", 1, 10, 5, help="高いほど改善の余地が大きい")
                new_weakness_evidence = st.text_area("具体的なエピソードや課題")
                
                submit_button = st.form_submit_button("改善点を追加")
                
                if submit_button:
                    if not new_weakness_name:
                        st.error("改善点の名前を入力してください。")
                    else:
                        # 新しい弱みを追加
                        new_weakness = {
                            "id": str(uuid.uuid4()),
                            "name": new_weakness_name,
                            "score": new_weakness_score,
                            "evidence": [new_weakness_evidence] if new_weakness_evidence else []
                        }
                        
                        strength_weakness["weaknesses"].append(new_weakness)
                        save_strength_weakness(strength_weakness)
                        
                        st.success(f"新しい改善点「{new_weakness_name}」を追加しました！")
                        st.experimental_rerun()
        else:
            # 既存の弱みの更新
            selected_weakness_data = next((w for w in weaknesses if w["name"] == selected_weakness), None)
            
            if selected_weakness_data:
                with st.form("update_weakness_form"):
                    updated_score = st.slider("自己評価スコア (1-10)", 1, 10, selected_weakness_data["score"], help="高いほど改善の余地が大きい")
                    
                    # 既存の証拠を表示
                    if selected_weakness_data["evidence"]:
                        st.markdown("##### 既存のエピソード・課題")
                        for i, evidence in enumerate(selected_weakness_data["evidence"]):
                            st.text_area(f"エピソード {i+1}", evidence, disabled=True)
                    
                    new_evidence = st.text_area("新たなエピソードや課題を追加")
                    
                    submit_button = st.form_submit_button("改善点を更新")
                    
                    if submit_button:
                        # 弱みを更新
                        for i, w in enumerate(strength_weakness["weaknesses"]):
                            if w["id"] == selected_weakness_data["id"]:
                                strength_weakness["weaknesses"][i]["score"] = updated_score
                                if new_evidence:
                                    strength_weakness["weaknesses"][i]["evidence"].append(new_evidence)
                                break
                        
                        save_strength_weakness(strength_weakness)
                        
                        st.success(f"改善点「{selected_weakness}」を更新しました！")
                        st.experimental_rerun()
        
        # 弱みの改善方法提案
        st.markdown("#### 改善点の対策")
        
        # 高評価の弱みを特定
        top_weaknesses = [w for w in weaknesses if w["score"] >= 6]
        
        if top_weaknesses:
            for weakness in top_weaknesses:
                # 弱みごとの改善提案
                if weakness["name"] == "先延ばし":
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>{weakness["name"]}の改善策</h4>
                        <ul>
                            <li>「2分ルール」：2分以内でできるタスクは、すぐに片付ける習慣をつける</li>
                            <li>タスクを小さなステップに分解し、最初の一歩だけ始めるよう自分と約束する</li>
                            <li>ポモドーロテクニック：25分集中→5分休憩のサイクルで作業を進める</li>
                            <li>締め切りを他者と共有するなど、外部からの動機付けを作る</li>
                            <li>「最低限これだけ」の基準を設定して、完璧主義を緩和する</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif weakness["name"] == "自己批判":
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>{weakness["name"]}の改善策</h4>
                        <ul>
                            <li>自己批判的な思考に気づいたら、それを第三者の視点で見直す練習をする</li>
                            <li>「友人ならどう声をかけるか」を考え、自分自身にも同じ言葉をかける</li>
                            <li>小さな成功や進歩を記録し、定期的に振り返る習慣をつける</li>
                            <li>完璧ではなくても「十分に良い」状態を受け入れる練習をする</li>
                            <li>自己肯定感を高めるポジティブアファメーションを実践する</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                elif weakness["name"] == "不一貫性":
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>{weakness["name"]}の改善策</h4>
                        <ul>
                            <li>習慣トラッカーを使用して、継続性を視覚化する</li>
                            <li>「最低限の基準」を設定し、毎日それだけは必ず実行する</li>
                            <li>環境の力を活用：必要なものを目につく場所に置いておく</li>
                            <li>既存の習慣に新しい行動を「繋げる」（習慣の連鎖）</li>
                            <li>一貫性を持って行動できた時は自分を褒め、報酬を与える</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>{weakness["name"]}の改善策</h4>
                        <p>この改善点に取り組むためのアドバイス：</p>
                        <ul>
                            <li>この課題が最も顕著に現れる状況や引き金を特定する</li>
                            <li>課題を小さなステップに分けて、段階的に取り組む</li>
                            <li>改善のための具体的な行動計画を立て、定期的に進捗を確認する</li>
                            <li>関連するスキルを伸ばすための学習や訓練を行う</li>
                            <li>改善の進捗を記録し、小さな成功も祝う習慣をつける</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("高スコアの改善点が登録されていません。自己評価を行って改善点を特定しましょう！")                

# 目標傾向分析ページ
def show_goal_trend_analysis():
    st.markdown('<h2 class="sub-header">🎯 目標傾向分析</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    goals_df = load_goals()
    smart_goals_df = load_smart_goals() if 'load_smart_goals' in globals() else pd.DataFrame()
    
    # データがない場合の処理
    if goals_df.empty:
        st.warning("分析に必要な目標データがまだありません。「SMART目標設定」機能を使って目標を設定しましょう！")
        return
    
    # 目標の概要統計
    st.markdown("### 目標達成の傾向分析")
    
    # 目標のステータスがある場合
    if 'status' in goals_df.columns:
        # 目標数のカウント
        total_goals = len(goals_df)
        completed_goals = len(goals_df[goals_df['status'] == 'completed'])
        active_goals = len(goals_df[goals_df['status'] == 'active'])
        paused_goals = len(goals_df[goals_df['status'] == 'paused']) if 'paused' in goals_df['status'].unique() else 0
        
        # 完了率
        completion_rate = completed_goals / total_goals * 100 if total_goals > 0 else 0
        
        # 統計表示用のカラムを作成
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <p>総目標数</p>
                <p class="stat-value">{total_goals}</p>
                <p>個</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <p>達成した目標</p>
                <p class="stat-value">{completed_goals}</p>
                <p>個</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <p>進行中の目標</p>
                <p class="stat-value">{active_goals}</p>
                <p>個</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <p>目標達成率</p>
                <p class="stat-value">{completion_rate:.1f}%</p>
                <p></p>
            </div>
            """, unsafe_allow_html=True)
        
        # 目標カテゴリ別の達成率
        if 'category' in goals_df.columns:
            st.markdown("#### カテゴリ別の目標達成率")
            
            # カテゴリごとの目標数と達成数をカウント
            category_stats = []
            
            for category in goals_df['category'].unique():
                category_goals = goals_df[goals_df['category'] == category]
                category_completed = len(category_goals[category_goals['status'] == 'completed'])
                category_total = len(category_goals)
                category_rate = category_completed / category_total * 100 if category_total > 0 else 0
                
                category_stats.append({
                    'category': category,
                    'completed': category_completed,
                    'total': category_total,
                    'completion_rate': category_rate
                })
            
            if category_stats:
                category_df = pd.DataFrame(category_stats)
                
                # カテゴリ別達成率の棒グラフ
                fig_category = px.bar(
                    category_df.sort_values('completion_rate', ascending=False),
                    x='category',
                    y='completion_rate',
                    title="カテゴリ別の目標達成率",
                    labels={'category': 'カテゴリ', 'completion_rate': '達成率 (%)'},
                    color='completion_rate',
                    color_continuous_scale=["red", "yellow", "green"],
                    range_color=[0, 100],
                    text_auto='.1f'
                )
                fig_category.update_traces(texttemplate='%{text}%', textposition='outside')
                st.plotly_chart(fig_category, use_container_width=True)
                
                # 最も成功率の高いカテゴリを特定
                most_successful_category = category_df.sort_values('completion_rate', ascending=False).iloc[0]
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>最も成功率の高い目標カテゴリ</h4>
                    <p>あなたは「<strong>{most_successful_category['category']}</strong>」カテゴリの目標で最も高い達成率（{most_successful_category['completion_rate']:.1f}%）を示しています。</p>
                    <p>このカテゴリでは{most_successful_category['total']}個中{most_successful_category['completed']}個の目標を達成しました。</p>
                    <p>このカテゴリに特に関心や強みがあるか、または目標の設定方法が特に効果的である可能性があります。</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 達成率が低いカテゴリに対するアドバイス
                if len(category_df) > 1:
                    least_successful_category = category_df.sort_values('completion_rate').iloc[0]
                    
                    if least_successful_category['completion_rate'] < 50:
                        st.markdown(f"""
                        <div class="warning-card">
                            <h4>達成率が低いカテゴリへのアドバイス</h4>
                            <p>「<strong>{least_successful_category['category']}</strong>」カテゴリでは達成率が{least_successful_category['completion_rate']:.1f}%とやや低くなっています。</p>
                            <p>このカテゴリの目標設定方法を見直すことで、成功率を高められる可能性があります：</p>
                            <ul>
                                <li>より小さなステップに分割する</li>
                                <li>より具体的で測定可能な目標にする</li>
                                <li>達成基準を現実的に調整する</li>
                                <li>このカテゴリの目標に特化したサポートや環境を整える</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
        
        # 短期vs長期目標の分析
        if 'deadline' in goals_df.columns and 'created_at' in goals_df.columns:
            st.markdown("#### 短期目標 vs 長期目標の傾向")
            
            # 目標期間の計算
            goals_df['created_at'] = pd.to_datetime(goals_df['created_at'])
            goals_df['deadline'] = pd.to_datetime(goals_df['deadline'])
            goals_df['duration_days'] = (goals_df['deadline'] - goals_df['created_at']).dt.days
            
            # 短期・中期・長期の定義
            goals_df['duration_type'] = pd.cut(
                goals_df['duration_days'],
                bins=[-1, 7, 30, float('inf')],
                labels=['短期（1週間以内）', '中期（1ヶ月以内）', '長期（1ヶ月超）']
            )
            
            # 期間ごとの達成率
            duration_stats = []
            
            for duration_type in goals_df['duration_type'].unique():
                duration_goals = goals_df[goals_df['duration_type'] == duration_type]
                duration_completed = len(duration_goals[duration_goals['status'] == 'completed'])
                duration_total = len(duration_goals)
                duration_rate = duration_completed / duration_total * 100 if duration_total > 0 else 0
                
                duration_stats.append({
                    'duration_type': duration_type,
                    'completed': duration_completed,
                    'total': duration_total,
                    'completion_rate': duration_rate
                })
            
            if duration_stats:
                duration_df = pd.DataFrame(duration_stats)
                
                # 期間タイプ別達成率の棒グラフ
                fig_duration = px.bar(
                    duration_df,
                    x='duration_type',
                    y='completion_rate',
                    title="目標期間別の達成率",
                    labels={'duration_type': '目標期間', 'completion_rate': '達成率 (%)'},
                    color='completion_rate',
                    color_continuous_scale=["red", "yellow", "green"],
                    range_color=[0, 100],
                    text_auto='.1f'
                )
                fig_duration.update_traces(texttemplate='%{text}%', textposition='outside')
                st.plotly_chart(fig_duration, use_container_width=True)
                
                # 最も成功率の高い期間タイプを特定
                most_successful_duration = duration_df.sort_values('completion_rate', ascending=False).iloc[0]
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>最も達成率の高い目標期間</h4>
                    <p>あなたは「<strong>{most_successful_duration['duration_type']}</strong>」の目標で最も高い達成率（{most_successful_duration['completion_rate']:.1f}%）を示しています。</p>
                    <p>この期間タイプの目標は、あなたの生活リズムや計画スタイルに合っている可能性があります。</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 具体的 vs 抽象的目標の分析
        if not smart_goals_df.empty and 'goal_id' in smart_goals_df.columns:
            st.markdown("#### SMART目標の要素分析")
            
            # SMARTの各要素がどの程度しっかり設定されているかを分析
            smart_elements = ['specific', 'measurable', 'achievable', 'relevant', 'time_bound']
            
            # 各要素の充実度をチェック（簡易的に文字数で判断）
            smart_quality = []
            
            for element in smart_elements:
                if element in smart_goals_df.columns:
                    # 文字数が20文字以上あれば「詳細」、それ以外は「簡易」と判断
                    detailed = (smart_goals_df[element].str.len() >= 20).sum()
                    simple = (smart_goals_df[element].str.len() < 20).sum() - (smart_goals_df[element] == "").sum()
                    empty = (smart_goals_df[element] == "").sum()
                    
                    element_names = {
                        'specific': '具体性',
                        'measurable': '測定可能性',
                        'achievable': '達成可能性',
                        'relevant': '関連性',
                        'time_bound': '期限'
                    }
                    
                    smart_quality.append({
                        'element': element_names.get(element, element),
                        'detailed': detailed,
                        'simple': simple,
                        'empty': empty
                    })
            
            if smart_quality:
                smart_df = pd.DataFrame(smart_quality)
                
                # 積み上げ棒グラフ
                fig_smart = px.bar(
                    smart_df,
                    x='element',
                    y=['detailed', 'simple', 'empty'],
                    title="SMART目標の要素設定状況",
                    labels={'element': '要素', 'value': '目標数', 'variable': '設定状況'},
                    color_discrete_map={
                        'detailed': '#4CAF50',
                        'simple': '#FFC107',
                        'empty': '#F44336'
                    },
                    barmode='stack'
                )
                fig_smart.update_layout(legend_title_text='設定状況', 
                                      legend=dict(
                                          orientation="h",
                                          yanchor="bottom",
                                          y=1.02,
                                          xanchor="right",
                                          x=1
                                      ))
                st.plotly_chart(fig_smart, use_container_width=True)
                
                # 弱点となる要素を特定
                weakness_element = smart_df.sort_values('empty', ascending=False).iloc[0]
                
                if weakness_element['empty'] > 0:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>SMART目標の改善ポイント</h4>
                        <p>「<strong>{weakness_element['element']}</strong>」の要素が最も多く欠けています。この要素を強化することで、目標達成率が向上する可能性があります。</p>
                        <p>例：</p>
                        <ul>
                    """, unsafe_allow_html=True)
                    
                    if weakness_element['element'] == '具体性':
                        st.markdown("""
                            <li>「運動する」→「週3回、30分以上のジョギングをする」</li>
                            <li>「読書をする」→「毎日就寝前に20ページ読む」</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif weakness_element['element'] == '測定可能性':
                        st.markdown("""
                            <li>「健康になる」→「体重を3kg減らす」「1km走るタイムを30秒縮める」</li>
                            <li>「語学力を上げる」→「TOEIC800点を達成する」「日常会話で1000語を使えるようになる」</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif weakness_element['element'] == '達成可能性':
                        st.markdown("""
                            <li>目標が現実的かどうかを確認する</li>
                            <li>必要なリソース（時間、スキル、サポート）を確保できるか検討する</li>
                            <li>過去の経験や同様の目標達成者の例を参考にする</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif weakness_element['element'] == '関連性':
                        st.markdown("""
                            <li>「なぜこの目標が重要なのか」を明確にする</li>
                            <li>長期的な目標や価値観との関連性を考える</li>
                            <li>目標達成後のメリットを具体的に想像する</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif weakness_element['element'] == '期限':
                        st.markdown("""
                            <li>「いつかやる」→「7月31日までに完了する」</li>
                            <li>長期目標は中間マイルストーンを設定する</li>
                            <li>期限を他者と共有し、アカウンタビリティを高める</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # 失敗した目標の改善提案
        if 'status' in goals_df.columns:
            failed_goals = goals_df[(goals_df['status'] != 'completed') & (goals_df['status'] != 'active')]
            
            if not failed_goals.empty:
                st.markdown("### 目標達成のための改善提案")
                
                # 改善提案の表示
                st.markdown("""
                失敗や停滞した目標から学び、次の目標設定をより効果的にするためのアドバイスです。
                """)
                
                # よくある失敗パターンの分析（ここでは単純化のため、固定のアドバイスを表示）
                st.markdown(f"""
                <div class="warning-card">
                    <h4>目標設定の改善ポイント</h4>
                    <p>分析結果から、次のような改善点が見つかりました：</p>
                    <ul>
                        <li><strong>適切なサイズの目標設定</strong>：大きすぎる目標は小さなステップに分割しましょう</li>
                        <li><strong>明確な成功基準の設定</strong>：「いつ、どのように達成したと判断するか」を事前に決めておきましょう</li>
                        <li><strong>進捗の可視化</strong>：目に見える形で進捗を追跡することでモチベーションを維持しやすくなります</li>
                        <li><strong>行動計画の具体化</strong>：「何を、いつ、どのように」という点を明確にしましょう</li>
                        <li><strong>障害の予測と対策</strong>：起こりうる問題を事前に想定し、対応策を考えておきましょう</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        # 今後の目標設定アドバイス
        st.markdown("### 今後の目標設定アドバイス")
        
        # 過去データに基づく個別化されたアドバイス
        if completed_goals > 0:
            # 成功した目標から特徴を抽出
            successful_goals = goals_df[goals_df['status'] == 'completed']
            
            # カテゴリ、期間などの特徴を分析
            success_features = []
            
            # カテゴリ分析
            if 'category' in successful_goals.columns and len(successful_goals['category'].unique()) > 0:
                top_category = successful_goals['category'].value_counts().index[0]
                success_features.append(f"「{top_category}」カテゴリの目標")
            
            # 期間分析
            if 'duration_type' in successful_goals.columns and len(successful_goals['duration_type'].unique()) > 0:
                top_duration = successful_goals['duration_type'].value_counts().index[0]
                success_features.append(f"{top_duration}の目標")
            
            # 特徴に基づくアドバイス生成
            if success_features:
                features_text = "、".join(success_features)
                
                st.markdown(f"""
                <div class="insight-card">
                    <h4>あなたに合った目標設定</h4>
                    <p>過去のデータから、あなたは<strong>{features_text}</strong>で成功しやすい傾向があります。</p>
                    <p>今後の目標設定では、これらの特徴を活かした目標を設定すると、成功率が高まる可能性があります。</p>
                    <p>同時に、新しい種類の目標にもチャレンジしつつ、成功しやすいパターンを徐々に見つけていきましょう。</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 一般的なベストプラクティス
        st.markdown("""
        #### 目標設定のベストプラクティス
        
        1. **SMART原則を活用する**：具体的、測定可能、達成可能、関連性があり、期限付きの目標を設定する
        2. **目標を書き出す**：目標を書き出すことで、達成率が大幅に向上します
        3. **可視化する**：目標や進捗を視覚的に確認できる場所に置く
        4. **小さなマイルストーンを設定する**：大きな目標を小さな成功体験の積み重ねに変える
        5. **アカウンタビリティを作る**：目標を他者と共有し、定期的に報告する仕組みを作る
        6. **習慣と紐づける**：既存の習慣に新しい行動を連鎖させる
        7. **内発的動機付けを強化する**：なぜその目標が自分にとって重要なのかを明確にする
        8. **失敗から学ぶ**：うまくいかなかった目標を分析し、次回に活かす
        """)
    else:
        st.info("目標のステータス情報がありません。「SMART目標設定」機能で目標を設定し、進捗を追跡しましょう。")

# 自己肯定感トラッカーページ
def show_self_esteem_tracker():
    st.markdown('<h2 class="sub-header">🌱 自己肯定感トラッカー</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    self_esteem_log = load_self_esteem_log()
    
    st.markdown("""
    自己肯定感は日々変動するものです。定期的に記録することで、
    あなたの自己肯定感に影響を与える要因を理解し、より高い自己肯定感を維持するための
    ヒントを得ることができます。
    """)
    
    # 新しい自己肯定感の記録
    st.markdown("### 今日の自己肯定感を記録")
    
    with st.form("self_esteem_form"):
        today = date.today()
        
        # 自己肯定感スコア
        self_esteem_score = st.slider("今日の自己肯定感はどの程度ですか？", 1, 10, 5)
        
        # 影響要因
        factors = st.multiselect(
            "自己肯定感に影響を与えた要因は？",
            ["仕事・学業の成果", "人間関係", "自己成長", "健康状態", "社会的評価", "金銭状況", "趣味・余暇", "その他"]
        )
        
        # 詳細な説明
        details = st.text_area("詳細（どんな出来事が影響しましたか？）", placeholder="例：プロジェクトでの成功、友人からの褒め言葉、新しいスキルの習得など")
        
        # 上昇したか下降したか
        direction = st.radio("昨日と比べて自己肯定感は？", ["上昇した", "変わらない", "下降した"])
        
        submit_button = st.form_submit_button("記録する")
        
        if submit_button:
            # 新しい記録を追加
            new_record = {
                "date": today.strftime("%Y-%m-%d"),
                "score": self_esteem_score,
                "factors": factors,
                "details": details,
                "direction": direction
            }
            
            if self_esteem_log.empty:
                self_esteem_log = pd.DataFrame([new_record])
            else:
                # 同じ日の記録がある場合は更新
                same_day = self_esteem_log[self_esteem_log['date'] == today.strftime("%Y-%m-%d")]
                if not same_day.empty:
                    self_esteem_log = self_esteem_log[self_esteem_log['date'] != today.strftime("%Y-%m-%d")]
                
                self_esteem_log = pd.concat([self_esteem_log, pd.DataFrame([new_record])], ignore_index=True)
            
            save_self_esteem_log(self_esteem_log)
            
            st.success("自己肯定感を記録しました！")
            
            # フィードバックの表示
            if self_esteem_score >= 8:
                st.markdown("""
                <div class="insight-card">
                    <h4>素晴らしい自己肯定感です！</h4>
                    <p>今日の高い自己肯定感を維持するために、何があなたをポジティブにしているのかをメモしておきましょう。
                    将来、自己肯定感が下がったときに、この記録が役立ちます。</p>
                </div>
                """, unsafe_allow_html=True)
            elif self_esteem_score >= 5:
                st.markdown("""
                <div class="insight-card">
                    <h4>安定した自己肯定感です</h4>
                    <p>バランスの取れた自己認識を持っています。より高めるためには、あなたの強みを活かす機会を
                    意識的に作ってみましょう。</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-card">
                    <h4>今日は少し自己肯定感が低いようです</h4>
                    <p>自己肯定感は日によって変動するものです。無理に高めようとせず、自分に優しく接してください。
                    できれば小さな成功体験を作ることで、徐々に回復していきます。</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 自己肯定感の変動グラフ
    if not self_esteem_log.empty and 'date' in self_esteem_log.columns and 'score' in self_esteem_log.columns:
        st.markdown("### 自己肯定感の変動グラフ")
        
        # データを日付順に整理
        self_esteem_log['date'] = pd.to_datetime(self_esteem_log['date'])
        sorted_log = self_esteem_log.sort_values('date')
        
        # 期間選択
        period = st.selectbox("表示期間", ["直近7日間", "直近1ヶ月", "直近3ヶ月", "全期間"])
        
        # 期間に応じたデータのフィルタリング
        today = datetime.now().date()
        
        if period == "直近7日間":
            start_date = today - timedelta(days=6)
            filtered_log = sorted_log[sorted_log['date'] >= pd.Timestamp(start_date)]
        elif period == "直近1ヶ月":
            start_date = today - timedelta(days=29)
            filtered_log = sorted_log[sorted_log['date'] >= pd.Timestamp(start_date)]
        elif period == "直近3ヶ月":
            start_date = today - timedelta(days=89)
            filtered_log = sorted_log[sorted_log['date'] >= pd.Timestamp(start_date)]
        else:  # 全期間
            filtered_log = sorted_log
        
        if not filtered_log.empty:
            # 変動グラフ
            fig_trend = px.line(
                filtered_log,
                x='date',
                y='score',
                title=f"自己肯定感の変動 ({period})",
                labels={'date': '日付', 'score': '自己肯定感スコア'},
                markers=True
            )
            fig_trend.update_layout(yaxis_range=[0, 11])
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 期間中の統計情報
            avg_score = filtered_log['score'].mean()
            max_score = filtered_log['score'].max()
            min_score = filtered_log['score'].min()
            
            # 統計情報を表示
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <p>平均スコア</p>
                    <p class="stat-value">{avg_score:.1f}</p>
                    <p>/10</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <p>最高スコア</p>
                    <p class="stat-value">{max_score}</p>
                    <p>/10</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <p>最低スコア</p>
                    <p class="stat-value">{min_score}</p>
                    <p>/10</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"選択した期間（{period}）のデータがありません。")
    
    # 影響要因の分析
    if not self_esteem_log.empty and 'factors' in self_esteem_log.columns and 'score' in self_esteem_log.columns:
        st.markdown("### 自己肯定感に影響する要因分析")
        
    # 要因ごとの平均スコアを計算
        factor_scores = []
        all_factors = []
        
        # すべての要因を抽出
        for factors_list in self_esteem_log['factors']:
            if isinstance(factors_list, list):
                all_factors.extend(factors_list)
        
        # ユニークな要因を取得
        unique_factors = list(set(all_factors))
        
        if unique_factors:
            # 各要因ごとの平均スコアを計算
            for factor in unique_factors:
                factor_records = self_esteem_log[[factor in factors if isinstance(factors, list) else False for factors in self_esteem_log['factors']]]
                if not factor_records.empty:
                    avg_factor_score = factor_records['score'].mean()
                    count = len(factor_records)
                    factor_scores.append({
                        'factor': factor,
                        'avg_score': avg_factor_score,
                        'count': count
                    })
            
            if factor_scores:
                # データフレームに変換
                factor_df = pd.DataFrame(factor_scores)
                
                # 平均スコアの棒グラフ
                fig_factors = px.bar(
                    factor_df.sort_values('avg_score', ascending=False),
                    x='factor',
                    y='avg_score',
                    title="要因別の平均自己肯定感スコア",
                    labels={'factor': '要因', 'avg_score': '平均スコア'},
                    color='avg_score',
                    color_continuous_scale=["red", "yellow", "green"],
                    range_color=[1, 10],
                    text_auto='.1f'
                )
                fig_factors.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_factors, use_container_width=True)
                
                # 最も影響力のある要因を特定
                if len(factor_df) > 1:
                    positive_factor = factor_df.sort_values('avg_score', ascending=False).iloc[0]
                    negative_factor = factor_df.sort_values('avg_score').iloc[0]
                    
                    st.markdown(f"""
                    <div class="insight-card">
                        <h4>自己肯定感への影響要因</h4>
                        <p>分析の結果、あなたの自己肯定感に<strong>最も良い影響</strong>を与えているのは「<strong>{positive_factor['factor']}</strong>」で、
                        このカテゴリでは平均{positive_factor['avg_score']:.1f}点のスコアとなっています。</p>
                        <p>一方、<strong>自己肯定感が低くなりがち</strong>なのは「<strong>{negative_factor['factor']}</strong>」に関することで、
                        平均{negative_factor['avg_score']:.1f}点のスコアになっています。</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ポジティブな要因を増やすアドバイス
                    st.markdown(f"""
                    <div class="trend-card">
                        <h4>自己肯定感を高めるためのアドバイス</h4>
                        <p><strong>{positive_factor['factor']}</strong>に関連する活動や経験を意識的に増やすことで、
                        自己肯定感の向上が期待できます。例えば：</p>
                    """, unsafe_allow_html=True)
                    
                    # 要因別のアドバイス
                    if positive_factor['factor'] == "仕事・学業の成果":
                        st.markdown("""
                        <ul>
                            <li>小さな達成可能な目標を設定し、達成感を積み重ねる</li>
                            <li>自分の成果を具体的に記録する習慣をつける</li>
                            <li>得意な分野で能力を発揮できる機会を積極的に作る</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif positive_factor['factor'] == "人間関係":
                        st.markdown("""
                        <ul>
                            <li>ポジティブな影響を与えてくれる人との時間を優先的に確保する</li>
                            <li>感謝の気持ちを伝える機会を増やす</li>
                            <li>相互にサポートし合える関係づくりを意識する</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif positive_factor['factor'] == "自己成長":
                        st.markdown("""
                        <ul>
                            <li>新しいスキルの習得や知識の獲得に取り組む</li>
                            <li>成長の過程を記録し、定期的に振り返る</li>
                            <li>わずかな進歩も認め、自分を褒める習慣をつける</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif positive_factor['factor'] == "健康状態":
                        st.markdown("""
                        <ul>
                            <li>適度な運動を定期的に行う</li>
                            <li>栄養バランスの良い食事と十分な睡眠を確保する</li>
                            <li>リラクゼーションやマインドフルネスの実践を取り入れる</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    elif positive_factor['factor'] == "趣味・余暇":
                        st.markdown("""
                        <ul>
                            <li>楽しみや充実感を得られる活動に定期的に時間を確保する</li>
                            <li>新しい趣味や活動に挑戦してみる</li>
                            <li>没頭できる活動を見つけ、フロー状態を経験する</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <ul>
                            <li>この要因に関連するポジティブな体験を増やす方法を考える</li>
                            <li>小さな成功体験を意識的に作り出す</li>
                            <li>この要因に関する良い出来事を記録する習慣をつける</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 自己肯定感が低下したときの対処法
                    st.markdown(f"""
                    <div class="warning-card">
                        <h4>自己肯定感が低下したときの対処法</h4>
                        <p>特に「<strong>{negative_factor['factor']}</strong>」に関連する出来事で自己肯定感が下がりやすい傾向があります。
                        そんなときは：</p>
                        <ul>
                            <li><strong>一時的なものと認識する</strong>：自己肯定感は変動するものです。一時的な落ち込みは自然なことです</li>
                            <li><strong>内的対話を見直す</strong>：否定的な自己対話に気づき、より思いやりのある言葉に置き換えてみましょう</li>
                            <li><strong>小さな成功体験を作る</strong>：簡単に達成できる小さなタスクに取り組み、達成感を得ましょう</li>
                            <li><strong>過去の成功を思い出す</strong>：自己肯定感が高かった時の記録を見返して、それを思い出しましょう</li>
                            <li><strong>サポートを求める</strong>：信頼できる人に話を聞いてもらうことも有効です</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("十分な要因データがまだありません。自己肯定感記録時に影響要因を選択することで、分析が可能になります。")
    
    # 自己肯定感を高める習慣
    st.markdown("### 自己肯定感を高める習慣")
    
    st.markdown("""
    以下の習慣を日常に取り入れることで、自己肯定感を高めることができます：
    
    1. **小さな成功を認める**：日々の小さな成功や進歩を意識的に記録する
    2. **自己対話を見直す**：否定的な内的対話を認識し、建設的な言葉に置き換える
    3. **感謝の習慣**：日々の感謝できることを記録する
    4. **強みを活かす**：自分の強みを意識的に活用する機会を作る
    5. **比較をやめる**：他者との比較ではなく、過去の自分との比較に焦点を当てる
    6. **身体的な健康を大切にする**：運動、睡眠、栄養に注意を払う
    7. **肯定的なフィードバックを記録する**：受け取った良いフィードバックを保存しておく
    8. **自己コンパッション**：失敗や挫折に対しても自分に優しく接する
    9. **自分の価値観に沿った生活**：自分の価値観を明確にし、それに沿った選択をする
    10. **サポートネットワークを築く**：ポジティブな影響を与えてくれる人との関係を育む
    """)
    
    # 自己肯定感の振り返り
    if not self_esteem_log.empty and len(self_esteem_log) >= 5:
        st.markdown("### 自己肯定感の振り返り")
        
        # 最も自己肯定感が高かった日の記録
        highest_record = self_esteem_log.loc[self_esteem_log['score'].idxmax()]
        
        st.markdown(f"""
        <div class="insight-card">
            <h4>最も自己肯定感が高かった日</h4>
            <p><strong>日付:</strong> {pd.to_datetime(highest_record['date']).strftime('%Y年%m月%d日')}</p>
            <p><strong>スコア:</strong> {highest_record['score']}/10</p>
            <p><strong>要因:</strong> {', '.join(highest_record['factors']) if isinstance(highest_record['factors'], list) else '記録なし'}</p>
            <p><strong>詳細:</strong> {highest_record['details']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 自己肯定感向上のためのヒント
        st.markdown("""
        <div class="trend-card">
            <h4>振り返りのヒント</h4>
            <p>自己肯定感が高かった日の記録を振り返ることで、何があなたにポジティブな影響を与えているのかを
            より深く理解できます。これらの要素を意識的に生活に取り入れることを検討してみましょう。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("十分なデータが記録されると、より詳細な分析と振り返りができるようになります。定期的に記録を続けましょう。")

# ページ選択に応じた内容を表示
if page == "行動・感情分析":
    show_behavior_emotion_analysis()
elif page == "強み・弱み分析":
    show_strength_weakness_analysis()
elif page == "目標傾向分析":
    show_goal_trend_analysis()
elif page == "自己肯定感トラッカー":
    show_self_esteem_tracker()   