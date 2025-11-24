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
from wordcloud import WordCloud

# ページの設定
st.set_page_config(
    page_title="自己認識の向上 - 自己肯定アプリ",
    page_icon="🧠",
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
    .emotion-card {
        background-color: #E3F2FD;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #2196F3;
    }
    .emotion-positive {
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .emotion-neutral {
        background-color: #FFF9C4;
        border-left: 5px solid #FFC107;
    }
    .emotion-negative {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
    }
    .strength-card {
        background-color: #F3E5F5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #9C27B0;
    }
    .value-card {
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
    .future-vision {
        background-color: #E8EAF6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #3F51B5;
    }
    .progress-stat {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .slider-label {
        font-weight: bold;
        margin-bottom: 0.5rem;
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
</style>
""", unsafe_allow_html=True)

# データファイルのパス
EMOTION_LOGS_FILE = "emotion_logs.json"
STRENGTHS_FILE = "strengths.json"
VALUES_FILE = "values.json"
FUTURE_VISION_FILE = "future_vision.json"
THOUGHT_PATTERNS_FILE = "thought_patterns.json"
VALUES_HISTORY_FILE = "values_history.json"

def load_values_history():
    """価値観履歴データを読み込む"""
    with open(VALUES_HISTORY_FILE, "r") as f:
        data = json.load(f)
    return data

def save_values_history(history_data):
    """価値観履歴データを保存する"""
    with open(VALUES_HISTORY_FILE, "w") as f:
        json.dump(history_data, f)

def save_values_snapshot(values_data):
    """現在の価値観のスナップショットを履歴に追加"""
    # 履歴を読み込む
    history = load_values_history()
    
    # 現在の日付を取得
    today = datetime.now().strftime("%Y-%m-%d")
    
    # スナップショットを作成
    snapshot = {
        "date": today,
        "values": []
    }
    
    # 価値観の重要度データをスナップショットに追加
    for value in values_data["values"]:
        snapshot["values"].append({
            "name": value["name"],
            "importance": value["importance"]
        })
    
    # 同じ日付のスナップショットがあれば置換、なければ追加
    for i, item in enumerate(history):
        if item["date"] == today:
            history[i] = snapshot
            save_values_history(history)
            return
    
    # 新しいスナップショットを追加
    history.append(snapshot)
    save_values_history(history)

# データファイルの初期化
def initialize_awareness_files():
    if not os.path.exists(EMOTION_LOGS_FILE):
        with open(EMOTION_LOGS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(STRENGTHS_FILE):
        with open(STRENGTHS_FILE, "w") as f:
            json.dump({
                "strengths": [],
                "skills": []
            }, f)
    
    if not os.path.exists(VALUES_FILE):
        default_values = {
            "values": [
                {"name": "仕事", "importance": 50, "description": "仕事での成果や成長"},
                {"name": "人間関係", "importance": 50, "description": "家族や友人との関係"},
                {"name": "成長", "importance": 50, "description": "自己成長や学び"},
                {"name": "趣味", "importance": 50, "description": "好きなことや楽しみ"},
                {"name": "健康", "importance": 50, "description": "心身の健康"},
                {"name": "社会貢献", "importance": 50, "description": "社会や他者への貢献"},
                {"name": "安定", "importance": 50, "description": "安定した生活や将来性"}
            ]
        }
        with open(VALUES_FILE, "w") as f:
            json.dump(default_values, f)
    
    if not os.path.exists(FUTURE_VISION_FILE):
        with open(FUTURE_VISION_FILE, "w") as f:
            json.dump({
                "vision": "",
                "creation_date": datetime.now().strftime("%Y-%m-%d"),
                "goals": [],
                "self_understanding_score": 50
            }, f)
    
    if not os.path.exists(THOUGHT_PATTERNS_FILE):
        with open(THOUGHT_PATTERNS_FILE, "w") as f:
            json.dump({
                "patterns": [
                    {"name": "過度の一般化", "count": 0, "examples": []},
                    {"name": "白黒思考", "count": 0, "examples": []},
                    {"name": "心のフィルター", "count": 0, "examples": []},
                    {"name": "マイナス思考", "count": 0, "examples": []},
                    {"name": "結論の飛躍", "count": 0, "examples": []},
                    {"name": "感情的決めつけ", "count": 0, "examples": []}
                ]
            }, f)

    if not os.path.exists(VALUES_HISTORY_FILE):
        with open(VALUES_HISTORY_FILE, "w") as f:
            json.dump([], f)
        
        # 初期データも保存しておく
        values_data = load_values()
        save_values_snapshot(values_data)        

# データ読み込み関数
@st.cache_data(ttl=60)  # この行を追加
def load_emotion_logs():
    try:
        with open(EMOTION_LOGS_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "date", "emotion", "intensity", "activity", "thoughts", "category"])
        return df
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame(columns=["id", "date", "emotion", "intensity", "activity", "thoughts", "category"])

def load_strengths():
    with open(STRENGTHS_FILE, "r") as f:
        return json.load(f)

def load_values():
    with open(VALUES_FILE, "r") as f:
        return json.load(f)

def load_future_vision():
    with open(FUTURE_VISION_FILE, "r") as f:
        return json.load(f)

def load_thought_patterns():
    with open(THOUGHT_PATTERNS_FILE, "r") as f:
        return json.load(f)

# データ保存関数
def save_emotion_logs(df):
    try:
        data = df.to_dict("records")
        with open(EMOTION_LOGS_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        load_emotion_logs.clear()  # キャッシュクリア
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

def save_strengths(strengths_data):
    with open(STRENGTHS_FILE, "w") as f:
        json.dump(strengths_data, f)

def save_values(values_data):
    with open(VALUES_FILE, "w") as f:
        json.dump(values_data, f)

def save_future_vision(vision_data):
    with open(FUTURE_VISION_FILE, "w") as f:
        json.dump(vision_data, f)

def save_thought_patterns(patterns_data):
    with open(THOUGHT_PATTERNS_FILE, "w") as f:
        json.dump(patterns_data, f)

# 初期化実行
initialize_awareness_files()

# ページナビゲーション
st.markdown('<h1 class="main-header">🧠 自己認識の向上</h1>', unsafe_allow_html=True)

# サイドバーナビゲーション
page = st.sidebar.radio(
    "自己認識メニュー",
    ["感情ログ", "思考パターン分析", "得意なことリスト", "価値観診断", "未来ビジョン", "自己認識の進歩"]
)

# ユーティリティ関数
def get_emotion_type(emotion):
    """感情のタイプ（positive, neutral, negative）を取得"""
    positive_emotions = ["喜び", "楽しさ", "満足", "安心", "希望", "感謝", "興味", "誇り"]
    negative_emotions = ["悲しみ", "不安", "怒り", "恐れ", "疲労", "退屈", "混乱", "罪悪感"]
    
    if emotion in positive_emotions:
        return "positive"
    elif emotion in negative_emotions:
        return "negative"
    else:
        return "neutral"
    
# 感情ログページ
def show_emotion_log():
    st.markdown('<h2 class="sub-header">😊 感情ログ</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    emotion_logs_df = load_emotion_logs()
    
    # 新しい感情ログの記録
    st.markdown("### 今日の感情を記録")
    
    with st.form("emotion_log_form"):
        # 日付選択
        log_date = st.date_input("日付", datetime.now())
        
        # 感情選択
        emotion_options = [
            "喜び", "楽しさ", "満足", "安心", "希望", "感謝", "興味", "誇り",  # ポジティブ
            "平静", "集中", "リラックス", "普通",  # ニュートラル
            "悲しみ", "不安", "怒り", "恐れ", "疲労", "退屈", "混乱", "罪悪感"  # ネガティブ
        ]
        emotion = st.selectbox("感情", emotion_options)
        
        # 感情の強さ
        intensity = st.slider("感情の強さ", 1, 10, 5)
        
        # 活動カテゴリ
        activity_categories = [
            "仕事・勉強", "家族・友人との時間", "趣味・娯楽", "運動・健康", 
            "休息・リラックス", "創作活動", "社会活動", "その他"
        ]
        category = st.selectbox("活動カテゴリー", activity_categories)
        
        # 具体的な活動
        activity = st.text_input("何をしていましたか？", placeholder="例：友人とカフェでおしゃべり、プロジェクトの作業など")
        
        # 思考内容
        thoughts = st.text_area("どんなことを考えていましたか？", placeholder="例：明日の予定、過去の出来事、気づいたことなど")
        
        submit = st.form_submit_button("記録する")
        
        if submit:
            if not emotion or not activity:
                st.error("感情と活動は必須項目です。")
            else:
                # 新しい感情ログを追加
                new_log = {
                    "id": str(uuid.uuid4()),
                    "date": log_date.strftime("%Y-%m-%d"),
                    "emotion": emotion,
                    "intensity": intensity,
                    "activity": activity,
                    "thoughts": thoughts,
                    "category": category
                }
                
                if emotion_logs_df.empty:
                    emotion_logs_df = pd.DataFrame([new_log])
                else:
                    emotion_logs_df = pd.concat([emotion_logs_df, pd.DataFrame([new_log])], ignore_index=True)
                
                save_emotion_logs(emotion_logs_df)
                
                st.success("感情ログを記録しました！")
                
                # 感情タイプを判定
                emotion_type = get_emotion_type(emotion)
                if emotion_type == "positive":
                    st.markdown("""
                    <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px;">
                        <p>👍 <strong>ポジティブな感情を記録しました！</strong> このような活動を増やしていくと良いでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # 感情ログの分析
    if not emotion_logs_df.empty:
        st.markdown("### 感情ログの分析")
        
        # 感情タイプの列を追加
        emotion_logs_df['emotion_type'] = emotion_logs_df['emotion'].apply(get_emotion_type)
        
        # 感情タイプの分布
        emotion_type_counts = emotion_logs_df['emotion_type'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 感情タイプの円グラフ
            fig_emotion_types = px.pie(
                emotion_type_counts.reset_index(),
                values=emotion_type_counts.values,
                names=emotion_type_counts.index,
                title="感情タイプの分布",
                color=emotion_type_counts.index,
                color_discrete_map={
                    "positive": "#4CAF50",
                    "neutral": "#FFC107",
                    "negative": "#F44336"
                }
            )
            fig_emotion_types.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig_emotion_types, use_container_width=True)
        
        with col2:
            # 活動カテゴリごとの感情タイプ
            category_emotion = pd.crosstab(emotion_logs_df['category'], emotion_logs_df['emotion_type'])
            
            # 各カテゴリのポジティブ率を計算
            if 'positive' in category_emotion.columns:
                category_emotion['total'] = category_emotion.sum(axis=1)
                category_emotion['positive_rate'] = (category_emotion['positive'] / category_emotion['total'] * 100).round(1)
                
                # ポジティブ率のグラフ
                fig_positive_rate = px.bar(
                    category_emotion.sort_values('positive_rate', ascending=False).reset_index(),
                    x='category',
                    y='positive_rate',
                    title="活動カテゴリごとのポジティブ感情率",
                    labels={'category': 'カテゴリ', 'positive_rate': 'ポジティブ感情の割合 (%)'},
                    color='positive_rate',
                    color_continuous_scale=["red", "yellow", "green"],
                    range_color=[0, 100]
                )
                st.plotly_chart(fig_positive_rate, use_container_width=True)
        
        # 気分が良くなる活動の発見
        st.markdown("### 気分が良くなる活動の発見")
        
        # 感情の強さが7以上のポジティブな記録を抽出
        if 'positive' in emotion_logs_df['emotion_type'].values:
            positive_logs = emotion_logs_df[(emotion_logs_df['emotion_type'] == 'positive') & (emotion_logs_df['intensity'] >= 7)]
            
            if not positive_logs.empty:
                # 活動の頻度をカウント
                positive_activities = positive_logs['activity'].value_counts().head(5)
                
                st.markdown("""
                <div class="insight-box">
                    <h4>あなたの気分を良くする活動トップ5</h4>
                    <p>以下の活動をした日は、特に良い気分になっていることが多いようです：</p>
                </div>
                """, unsafe_allow_html=True)
                
                for activity, count in positive_activities.items():
                    st.markdown(f"- **{activity}** ({count}回記録)")
                
                # カテゴリ別の分析
                positive_categories = positive_logs['category'].value_counts()
                if not positive_categories.empty:
                    top_category = positive_categories.index[0]
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>最もポジティブな感情を生むカテゴリ</h4>
                        <p>「{top_category}」に関する活動が、あなたの気分を最も良くしています。この分野の活動を増やすことを検討してみてください。</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("まだ強いポジティブ感情の記録がありません。感情の強さが7以上のポジティブな体験を記録してみましょう。")
        
        # ネガティブな感情と結びつく活動の特定
        if 'negative' in emotion_logs_df['emotion_type'].values:
            negative_logs = emotion_logs_df[(emotion_logs_df['emotion_type'] == 'negative') & (emotion_logs_df['intensity'] >= 7)]
            
            if not negative_logs.empty:
                # 活動の頻度をカウント
                negative_activities = negative_logs['activity'].value_counts().head(3)
                
                st.markdown("""
                <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                    <h4>気分を下げる可能性のある活動</h4>
                    <p>以下の活動をした日は、ネガティブな感情を感じることが多いようです：</p>
                </div>
                """, unsafe_allow_html=True)
                
                for activity, count in negative_activities.items():
                    st.markdown(f"- **{activity}** ({count}回記録)")
                
                st.markdown("""
                <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <p>💡 <strong>ヒント：</strong> これらの活動を減らすか、取り組み方を変えると、全体的な気分が安定するかもしれません。</p>
                </div>
                """, unsafe_allow_html=True)
                # 感情ログの既存の関数に追加するコード
# show_emotion_log() 関数内の「気分を下げる可能性のある活動の特定」セクションを拡張

# この部分を既存の気分を下げる活動の分析セクションの後に追加
    if 'negative' in emotion_logs_df['emotion_type'].values:
        negative_logs = emotion_logs_df[(emotion_logs_df['emotion_type'] == 'negative') & (emotion_logs_df['intensity'] >= 5)]
        
        if not negative_logs.empty:
            st.markdown("### 🔍 ネガティブ感情の詳細分析")
            
            # タブで詳細分析を整理
            neg_tabs = st.tabs(["活動分析", "感情パターン", "時間帯分析", "思考パターン", "対策提案"])
            
            with neg_tabs[0]:
                st.markdown("#### 気分を下げる活動の詳細分析")
                
                # カテゴリー別のネガティブ感情分布
                if 'category' in negative_logs.columns:
                    neg_by_category = negative_logs['category'].value_counts().reset_index()
                    neg_by_category.columns = ['カテゴリー', '回数']
                    
                    fig_neg_cat = px.bar(
                        neg_by_category,
                        x='カテゴリー',
                        y='回数',
                        title="カテゴリー別のネガティブ感情発生頻度",
                        color='回数',
                        color_continuous_scale=["lightblue", "red"]
                    )
                    st.plotly_chart(fig_neg_cat, use_container_width=True)
                
                # 具体的な活動のワードクラウドまたはリスト
                st.markdown("#### 最も多くネガティブ感情と関連する活動")
                
                negative_activities = negative_logs['activity'].value_counts().head(10)
                
                for activity, count in negative_activities.items():
                    intensity_avg = negative_logs[negative_logs['activity'] == activity]['intensity'].mean()
                    
                    # インテンシティに基づいて色を変える
                    color = "rgba(255,0,0,{})".format(min(1.0, intensity_avg/10))
                    
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 5px 0; color: white;">
                        <h4>{activity} ({count}回)</h4>
                        <p>平均感情強度: {intensity_avg:.1f}/10</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with neg_tabs[1]:
                st.markdown("#### ネガティブ感情のパターン")
                
                # 感情タイプ別の分布
                neg_emotions = negative_logs['emotion'].value_counts().reset_index()
                neg_emotions.columns = ['感情', '回数']
                
                fig_emotions = px.pie(
                    neg_emotions,
                    values='回数',
                    names='感情',
                    title="ネガティブ感情の種類",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.plotly_chart(fig_emotions, use_container_width=True)
                
                # 感情強度の分布
                fig_intensity = px.histogram(
                    negative_logs,
                    x='intensity',
                    nbins=10,
                    title="ネガティブ感情の強度分布",
                    labels={'intensity': '感情強度', 'count': '回数'},
                    color_discrete_sequence=['red']
                )
                st.plotly_chart(fig_intensity, use_container_width=True)
            
            with neg_tabs[2]:
                st.markdown("#### 時間帯・曜日分析")
                
                # 日付データを変換して時間帯・曜日情報を抽出
                if 'date' in negative_logs.columns:
                    negative_logs['date'] = pd.to_datetime(negative_logs['date'])
                    
                    # 平日・週末の分析（できる場合）
                    negative_logs['dayofweek'] = negative_logs['date'].dt.dayofweek
                    negative_logs['is_weekend'] = negative_logs['dayofweek'] >= 5
                    
                    weekend_counts = negative_logs['is_weekend'].value_counts()
                    
                    if not weekend_counts.empty:
                        # 平日・週末のネガティブ感情比率
                        weekday_count = weekend_counts.get(False, 0)
                        weekend_count = weekend_counts.get(True, 0)
                        total_count = weekday_count + weekend_count
                        
                        if total_count > 0:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("平日のネガティブ感情", f"{weekday_count}回", 
                                        f"{weekday_count/total_count*100:.1f}%")
                            
                            with col2:
                                st.metric("週末のネガティブ感情", f"{weekend_count}回", 
                                        f"{weekend_count/total_count*100:.1f}%")
                            
                            # 平日の方が多いか週末の方が多いかの比較
                            if weekday_count > weekend_count * 2.5:  # 平日は5日、週末は2日なので比率調整
                                st.markdown("""
                                <div style="background-color: #FFF3E0; padding: 10px; border-radius: 5px; margin-top: 10px;">
                                    <p>📊 <strong>インサイト:</strong> 平日に不釣り合いに多くのネガティブ感情が発生しています。これは仕事やスケジュールの圧力が関係している可能性があります。平日のセルフケアを増やすことを検討してみましょう。</p>
                                </div>
                                """, unsafe_allow_html=True)
                            elif weekend_count > weekday_count / 2.5:
                                st.markdown("""
                                <div style="background-color: #FFF3E0; padding: 10px; border-radius: 5px; margin-top: 10px;">
                                    <p>📊 <strong>インサイト:</strong> 週末に不釣り合いに多くのネガティブ感情が発生しています。これは予定の不足や社会的孤立感が関係している可能性があります。週末の充実した活動計画を考えてみましょう。</p>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # 曜日別分析
                    negative_logs['weekday'] = negative_logs['date'].dt.day_name()
                    weekday_counts = negative_logs['weekday'].value_counts()
                    
                    # 英語の曜日名を日本語に変換
                    weekday_map = {
                        'Monday': '月曜日', 'Tuesday': '火曜日', 'Wednesday': '水曜日', 
                        'Thursday': '木曜日', 'Friday': '金曜日', 'Saturday': '土曜日', 'Sunday': '日曜日'
                    }
                    
                    weekday_df = weekday_counts.reset_index()
                    weekday_df.columns = ['曜日', '回数']
                    weekday_df['曜日_jp'] = weekday_df['曜日'].map(weekday_map)
                    
                    # 曜日順に並べ替え
                    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_df['order'] = weekday_df['曜日'].map({day: i for i, day in enumerate(weekday_order)})
                    weekday_df = weekday_df.sort_values('order')
                    
                    fig_weekday = px.bar(
                        weekday_df,
                        x='曜日_jp',
                        y='回数',
                        title="曜日別のネガティブ感情発生頻度",
                        color='回数',
                        color_continuous_scale=["lightblue", "red"]
                    )
                    st.plotly_chart(fig_weekday, use_container_width=True)
                    
                    # 最もネガティブ感情が多い曜日を特定
                    max_weekday = weekday_df.iloc[weekday_df['回数'].argmax()]
                    st.markdown(f"""
                    <div style="background-color: #FFE0E0; padding: 10px; border-radius: 5px;">
                        <p>⚠️ <strong>注目ポイント:</strong> {max_weekday['曜日_jp']}に最も多くのネガティブ感情が記録されています。この曜日に特に気をつけるとよいでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with neg_tabs[3]:
                st.markdown("#### 思考パターンの分析")
                
                # 思考内容のテキスト分析（シンプルな単語頻度分析）
                if 'thoughts' in negative_logs.columns:
                    all_thoughts = " ".join(negative_logs['thoughts'].dropna().astype(str))
                    
                    if all_thoughts:
                        # 簡易的な単語分割（形態素解析ライブラリがあるとより良い）
                        words = all_thoughts.split()
                        
                        # 頻出単語を抽出（ストップワードを除外するとより良い）
                        word_counts = pd.Series(words).value_counts().head(20)
                        
                        fig_words = px.bar(
                            word_counts.reset_index(),
                            x='index',
                            y='count',  # 修正: 数値の0ではなく列名を使用
                            title="ネガティブ感情時の頻出単語",
                            labels={'index': '単語', 'count': '出現回数'}
                        )
                        st.plotly_chart(fig_words, use_container_width=True)
                        
                        # 単語頻度からネガティブ思考パターンを推測
                        common_negative_patterns = {
                            "完璧主義": ["すべき", "ねばならない", "完璧", "失敗"],
                            "過度の一般化": ["いつも", "絶対に", "全く", "すべて", "誰も"],
                            "白黒思考": ["最悪", "最高", "絶対", "必ず"],
                            "自己批判": ["ダメ", "無理", "できない", "価値がない"],
                            "心の読みすぎ": ["思われている", "嫌われている", "批判されている"]
                        }
                        
                        # パターンの検出（単純なキーワードマッチング）
                        detected_patterns = []
                        for pattern, keywords in common_negative_patterns.items():
                            for keyword in keywords:
                                if keyword in all_thoughts:
                                    detected_patterns.append(pattern)
                                    break
                        
                        if detected_patterns:
                            st.markdown("#### 検出された思考パターン")
                            for pattern in set(detected_patterns):
                                st.markdown(f"- **{pattern}**")
                            
                            st.markdown("""
                            <div style="background-color: #E0F7FA; padding: 10px; border-radius: 5px; margin-top: 10px;">
                                <p>💡 <strong>ヒント:</strong> これらの思考パターンに気づくことが、ネガティブ感情への対処の第一歩です。思考パターンを認識し、より建設的な思考に置き換える練習をしてみましょう。</p>
                            </div>
                            """, unsafe_allow_html=True)
            
            with neg_tabs[4]:
                st.markdown("#### 対策提案")
                
                st.markdown("""
                ネガティブ感情への対処法として、以下のアプローチを検討してみましょう：
                """)
                
                # ネガティブ感情が多いカテゴリーとそれに対する対策を提案
                if 'category' in negative_logs.columns:
                    top_neg_categories = negative_logs['category'].value_counts().head(3)
                    
                    for category, count in top_neg_categories.items():
                        st.markdown(f"#### {category}に関連するネガティブ感情への対策")
                        
                        # カテゴリー別の対策提案
                        if category == "仕事・勉強":
                            st.markdown("""
                            - **タスク分割**: 大きなタスクを小さく分割して取り組みやすくする
                            - **ポモドーロテクニック**: 25分集中、5分休憩のサイクルで作業効率を上げる
                            - **優先順位付け**: 最も重要なタスクを特定し、それに集中する
                            - **完璧主義の緩和**: 「十分に良い」状態を受け入れる練習をする
                            - **成果の可視化**: 小さな進捗も記録して達成感を得る
                            """)
                        elif category == "家族・友人との時間":
                            st.markdown("""
                            - **境界設定**: 自分の限界や要望を明確に伝える練習をする
                            - **期待管理**: 他者や状況に対する非現実的な期待を見直す
                            - **コミュニケーション改善**: "I" メッセージを使って感情を伝える
                            - **マインドフルネス**: 会話中に現在の瞬間に集中する
                            - **共感と理解**: 相手の視点を考慮する習慣をつける
                            """)
                        elif category == "運動・健康":
                            st.markdown("""
                            - **目標調整**: より達成可能な小さな目標から始める
                            - **自己比較のみ**: 他者との比較ではなく、自分の過去と比較する
                            - **多様性**: 楽しめる様々な運動を試してみる
                            - **社会的要素**: 運動仲間を見つけてモチベーションを高める
                            - **ストレスなく続ける**: 義務ではなく、楽しみとして捉え直す
                            """)
                        else:
                            st.markdown("""
                            - **意識的な休息**: 活動の合間に意識的な休憩を取り入れる
                            - **期待値の調整**: 完璧を求めず、プロセスを楽しむことに焦点を当てる
                            - **マインドフルネス実践**: 現在の瞬間に集中する習慣をつける
                            - **認知の再構成**: ネガティブな思考を特定し、より均衡の取れた見方に置き換える
                            - **自己思いやり**: 自分自身に対して友人に接するような優しさを持つ
                            """)
                
                # 全般的な対策
                st.markdown("#### 全般的なネガティブ感情への対処法")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **即時対応策**:
                    - 深呼吸（4-7-8テクニック）
                    - 5分間の瞑想
                    - 短い散歩
                    - ジャーナリング（感情を書き出す）
                    - 信頼できる人に話す
                    """)
                
                with col2:
                    st.markdown("""
                    **長期的な対策**:
                    - 定期的な運動習慣
                    - 十分な睡眠
                    - バランスの取れた食事
                    - 定期的なマインドフルネス練習
                    - 必要に応じて専門家のサポートを求める
                    """)
                
                # パーソナライズされた提案（データに基づく）
                if not negative_logs.empty:
                    # 感情の種類と活動のクロス分析
                    if 'emotion' in negative_logs.columns and 'activity' in negative_logs.columns:
                        emotion_activity = pd.crosstab(negative_logs['emotion'], negative_logs['activity'])
                        
                        # 最も頻度の高い組み合わせを特定
                        max_emotion = ""
                        max_activity = ""
                        max_count = 0
                        
                        for emotion in emotion_activity.index:
                            for activity in emotion_activity.columns:
                                if emotion_activity.loc[emotion, activity] > max_count:
                                    max_emotion = emotion
                                    max_activity = activity
                                    max_count = emotion_activity.loc[emotion, activity]
                        
                        if max_count > 0:
                            st.markdown(f"""
                            <div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin-top: 15px;">
                                <h4>パーソナライズされた提案</h4>
                                <p>あなたのデータから、「<strong>{max_activity}</strong>」という活動が「<strong>{max_emotion}</strong>」という感情と特に強く関連していることがわかりました。</p>
                                <p>この組み合わせにターゲットを絞った対策としては：</p>
                            """, unsafe_allow_html=True)
                            
                            # 感情別の具体的な対策
                            if max_emotion in ["不安", "緊張"]:
                                st.markdown("""
                                1. **事前準備**: この活動に入る前に、準備を整え、不確実性を減らす
                                2. **リラクゼーション技法**: 活動前に5分間の呼吸法や瞑想を実践
                                3. **認知の再構成**: 「最悪の場合でも対処できる」と自分に言い聞かせる
                                4. **徐々に慣れる**: 短時間・小規模から始め、徐々に慣れていく
                                5. **サポートを得る**: 可能であれば、信頼できる人と一緒に活動する
                                """)
                            elif max_emotion in ["悲しみ", "落ち込み"]:
                                st.markdown("""
                                1. **活動の時間帯変更**: エネルギーレベルが高い時間帯に活動を移動
                                2. **社会的つながり**: 可能であれば、他者と一緒に活動する
                                3. **小さな目標設定**: 達成可能な小さな目標を設定し、達成感を得る
                                4. **感謝の実践**: 活動中の小さな肯定的な側面に注目する
                                5. **自己対話の改善**: 内なる批評家に気づき、より思いやりのある自己対話を心がける
                                """)
                            elif max_emotion in ["怒り", "イライラ"]:
                                st.markdown("""
                                1. **事前のクールダウン**: 活動前にリラクゼーション技法を実践
                                2. **トリガーの特定**: 活動中のどの瞬間が特に怒りを引き起こすか特定
                                3. **一時停止戦略**: イライラを感じたら一時停止して深呼吸
                                4. **別の視点**: 状況を異なる角度から見る練習
                                5. **エネルギーの別方向への向け方**: 運動など、怒りのエネルギーを健全に発散する方法を見つける
                                """)
                            else:
                                st.markdown("""
                                1. **自己観察**: どのような思考がネガティブ感情につながるか注目する
                                2. **代替活動**: 同じ目的を達成できる別の活動を探る
                                3. **環境の変更**: 活動の場所や状況を変えてみる
                                4. **マインドフルネス**: 活動中の思考と感情に注意を向ける
                                5. **活動の再構成**: 同じ活動でも、アプローチや期待を変更する
                                """)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                
                # 改善トラッキングの提案
                st.markdown("""
                #### 改善のトラッキング
                
                ネガティブ感情への対処法を実践した後は、その効果を追跡することが重要です：
                
                1. **感情ログを継続**: 対策を実践した後も感情を記録し続ける
                2. **改善を可視化**: このダッシュボードを定期的に確認し、傾向の変化を観察する
                3. **効果的な戦略をメモ**: 特に効果があった対処法を記録する
                4. **定期的な振り返り**: 月に一度、全体的な傾向を振り返る
                5. **柔軟に調整**: 効果がない戦略は別のアプローチに変更する
                """)
    


        # 感情ログの既存のコードに以下を追加して、削除・編集機能を実装します
            # show_emotion_log()関数内の「過去の感情ログ一覧」セクションを以下のコードに置き換えてください

            # 過去の感情ログ一覧
            st.markdown("### 過去の感情ログ一覧")

            if not emotion_logs_df.empty:
                # ソート・フィルタリングオプション
                col1, col2 = st.columns([1, 1])
                with col1:
                    sort_option = st.selectbox("並び順", ["新しい順", "古い順"], key="emotion_sort")
                with col2:
                    filter_option = st.selectbox("表示する感情タイプ", ["すべて", "ポジティブ", "ニュートラル", "ネガティブ"], key="emotion_filter")
                
                # 日付でソート
                sort_ascending = sort_option == "古い順"
                sorted_logs = emotion_logs_df.sort_values('date', ascending=sort_ascending)
                
                # 感情タイプでフィルタリング
                if filter_option != "すべて":
                    filter_map = {"ポジティブ": "positive", "ニュートラル": "neutral", "ネガティブ": "negative"}
                    sorted_logs = sorted_logs[sorted_logs['emotion_type'] == filter_map[filter_option]]

                # 最新30件のみ表示（この行を追加）
                sorted_logs = sorted_logs.head(30)    
                
                if sorted_logs.empty:
                    st.info(f"{filter_option}の感情ログはありません。")
                else:
                    # 感情ログを展開可能なセクションで表示
                    for i, (_, log) in enumerate(sorted_logs.iterrows()):
                        emotion_type = log['emotion_type']
                        card_class = f"emotion-card emotion-{emotion_type}"
                        
                        with st.expander(f"{log['date']} - {log['emotion']} (強さ: {log['intensity']})", expanded=False):
                            st.markdown(f"""
                            <div class="{card_class}">
                                <p><strong>活動:</strong> {log['activity']} (カテゴリ: {log['category']})</p>
                                <p><strong>思考:</strong> {log['thoughts']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 編集・削除ボタンを追加
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("編集", key=f"edit_{i}"):
                                    # 編集する行のインデックスをセッションステートに保存
                                    st.session_state.edit_emotion_index = i
                                    st.session_state.edit_emotion_data = log.to_dict()
                                    st.rerun()
                            
                            with col2:
                                if st.button("削除", key=f"delete_{i}"):
                                    if 'id' in log:
                                        # IDがある場合はそれを使用して削除
                                        emotion_logs_df = emotion_logs_df[emotion_logs_df['id'] != log['id']]
                                    else:
                                        # インデックスを使用して削除
                                        emotion_logs_df = emotion_logs_df.drop(log.name)
                                    
                                    save_emotion_logs(emotion_logs_df)
                                    st.success("感情ログを削除しました！")
                                    st.rerun()
                
                # 編集モードの表示
                if 'edit_emotion_index' in st.session_state and st.session_state.edit_emotion_index is not None:
                    st.markdown("### 感情ログの編集")
                    edit_data = st.session_state.edit_emotion_data
                    
                    with st.form("edit_emotion_form"):
                        # 感情選択
                        emotion_options = [
                            "喜び", "楽しさ", "満足", "安心", "希望", "感謝", "興味", "誇り",  # ポジティブ
                            "平静", "集中", "リラックス", "普通",  # ニュートラル
                            "悲しみ", "不安", "怒り", "恐れ", "疲労", "退屈", "混乱", "罪悪感"  # ネガティブ
                        ]
                        updated_emotion = st.selectbox("感情", emotion_options, index=emotion_options.index(edit_data['emotion']) if edit_data['emotion'] in emotion_options else 0)
                        
                        # 感情の強さ
                        updated_intensity = st.slider("感情の強さ", 1, 10, int(edit_data['intensity']))
                        
                        # 活動カテゴリ
                        activity_categories = [
                            "仕事・勉強", "家族・友人との時間", "趣味・娯楽", "運動・健康", 
                            "休息・リラックス", "創作活動", "社会活動", "その他"
                        ]
                        updated_category = st.selectbox("活動カテゴリー", activity_categories, 
                                                    index=activity_categories.index(edit_data['category']) if edit_data['category'] in activity_categories else 0)
                        
                        # 具体的な活動
                        updated_activity = st.text_input("何をしていましたか？", value=edit_data['activity'])
                        
                        # 思考内容
                        updated_thoughts = st.text_area("どんなことを考えていましたか？", value=edit_data['thoughts'])
                        
                        # 日付編集
                        updated_date = st.date_input("日付", datetime.strptime(edit_data['date'], "%Y-%m-%d") if isinstance(edit_data['date'], str) else edit_data['date'])
                        
                        # 保存または取り消しボタン
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            submit = st.form_submit_button("変更を保存")
                        with col2:
                            cancel = st.form_submit_button("編集をキャンセル")
                        
                        if submit:
                            # 変更内容を保存
                            if 'id' in edit_data:
                                idx = emotion_logs_df[emotion_logs_df['id'] == edit_data['id']].index[0]
                            else:
                                idx = st.session_state.edit_emotion_index
                            
                            # 感情タイプを再計算
                            positive_emotions = ["喜び", "楽しさ", "満足", "安心", "希望", "感謝", "興味", "誇り"]
                            negative_emotions = ["悲しみ", "不安", "怒り", "恐れ", "疲労", "退屈", "混乱", "罪悪感"]
                            updated_emotion_type = "positive" if updated_emotion in positive_emotions else \
                                                "negative" if updated_emotion in negative_emotions else "neutral"
                            
                            # データを更新
                            emotion_logs_df.at[idx, 'emotion'] = updated_emotion
                            emotion_logs_df.at[idx, 'emotion_type'] = updated_emotion_type
                            emotion_logs_df.at[idx, 'intensity'] = updated_intensity
                            emotion_logs_df.at[idx, 'category'] = updated_category
                            emotion_logs_df.at[idx, 'activity'] = updated_activity
                            emotion_logs_df.at[idx, 'thoughts'] = updated_thoughts
                            emotion_logs_df.at[idx, 'date'] = updated_date.strftime("%Y-%m-%d")
                            
                            # 保存
                            save_emotion_logs(emotion_logs_df)
                            st.success("感情ログを更新しました！")
                            
                            # 編集モードを終了
                            st.session_state.edit_emotion_index = None
                            st.session_state.edit_emotion_data = None
                            st.rerun()
                        
                        if cancel:
                            # 編集モードを終了
                            st.session_state.edit_emotion_index = None
                            st.session_state.edit_emotion_data = None
                            st.rerun()
            else:
                st.info("まだ感情ログがありません。上のフォームから最初の記録を追加しましょう！")

# 思考パターン分析ページ
def show_thought_pattern_analysis():
    st.markdown('<h2 class="sub-header">🧩 思考パターン分析</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    thought_patterns = load_thought_patterns()
    emotion_logs_df = load_emotion_logs()
    
    st.markdown("""
    思考パターンを分析することで、自分の思考の癖や傾向を知り、より健全な思考習慣を身につけることができます。
    ネガティブな思考パターンに気づくことが、自己認識を高める第一歩です。
    """)
    
    # 思考パターンの記録
    st.markdown("### 思考パターンを記録する")
    
    with st.form("thought_pattern_form"):
        st.markdown("""
        ネガティブな思考が浮かんだとき、それがどのタイプの思考パターンに当てはまるか考えてみましょう。
        以下から最も近いものを選んでください。
        """)
        
        pattern_options = [p["name"] for p in thought_patterns["patterns"]]
        selected_pattern = st.selectbox("思考パターン", pattern_options)
        
        pattern_example = st.text_area("具体的な思考内容", placeholder="例：「一度失敗したから、私は何をやってもダメだ」など")
        
        submit = st.form_submit_button("記録する")
        
        if submit:
            if not pattern_example:
                st.error("思考内容を入力してください。")
            else:
                # 選択したパターンを更新
                for i, pattern in enumerate(thought_patterns["patterns"]):
                    if pattern["name"] == selected_pattern:
                        thought_patterns["patterns"][i]["count"] += 1
                        thought_patterns["patterns"][i]["examples"].append({
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "content": pattern_example
                        })
                        break
                
                save_thought_patterns(thought_patterns)
                
                st.success("思考パターンを記録しました！")
                
                # アドバイスを表示
                if selected_pattern == "過度の一般化":
                    advice = "一つの出来事から全体を判断するのではなく、個別の状況として捉えてみましょう。"
                elif selected_pattern == "白黒思考":
                    advice = "物事は白か黒かの二択ではなく、グラデーションがあります。中間の視点を持ってみましょう。"
                elif selected_pattern == "心のフィルター":
                    advice = "ネガティブな面だけでなく、ポジティブな側面にも目を向けてみましょう。"
                elif selected_pattern == "マイナス思考":
                    advice = "ポジティブな出来事も認めて、バランスのとれた見方を心がけましょう。"
                elif selected_pattern == "結論の飛躍":
                    advice = "根拠のない結論を出す前に、実際の証拠に基づいて考えてみましょう。"
                elif selected_pattern == "感情的決めつけ":
                    advice = "感情と事実は別物です。感情に左右されず、客観的に状況を見てみましょう。"
                else:
                    advice = "思考パターンに気づけたこと自体が大きな一歩です。自分を観察し続けましょう。"
                
                st.markdown(f"""
                <div style="background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <p>💡 <strong>アドバイス：</strong> {advice}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 思考パターンの分析
    st.markdown("### 思考パターンの分析")
    
    # パターンの頻度をグラフ化
    pattern_counts = [(p["name"], p["count"]) for p in thought_patterns["patterns"]]
    pattern_df = pd.DataFrame(pattern_counts, columns=["pattern", "count"])
    
    if pattern_df["count"].sum() > 0:
        fig_patterns = px.bar(
            pattern_df.sort_values("count", ascending=False),
            x="pattern",
            y="count",
            title="思考パターンの頻度",
            labels={"pattern": "思考パターン", "count": "回数"},
            color="count",
            color_continuous_scale=["green", "yellow", "red"]
        )
        st.plotly_chart(fig_patterns, use_container_width=True)
        
        # 最も多い思考パターンを特定
        most_common_pattern = pattern_df.sort_values("count", ascending=False).iloc[0]
        
        if most_common_pattern["count"] > 0:
            st.markdown(f"""
            <div class="insight-box">
                <h4>あなたの主な思考パターン</h4>
                <p>「{most_common_pattern['pattern']}」が最も頻繁に現れる思考パターンです。このパターンに気づくことで、より健全な思考習慣を身につけるきっかけになります。</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 対策アドバイス
            st.markdown("### 思考パターンの改善方法")
            
            if most_common_pattern["pattern"] == "過度の一般化":
                st.markdown("""
                - 「常に」「全て」「絶対に」などの言葉を使っていないか確認する
                - 反例を探してみる（「でも、うまくいったこともある」など）
                - 具体的な状況に焦点を当てる
                """)
            elif most_common_pattern["pattern"] == "白黒思考":
                st.markdown("""
                - 中間の選択肢を積極的に探す
                - 「これもあれも」という視点を持つ
                - 完璧主義を手放し、「十分に良い」を認める
                """)
            elif most_common_pattern["pattern"] == "心のフィルター":
                st.markdown("""
                - 意識的にポジティブな側面を探す練習をする
                - 感謝日記をつける
                - 状況の全体像を見る習慣をつける
                """)
            elif most_common_pattern["pattern"] == "マイナス思考":
                st.markdown("""
                - ポジティブな出来事を日記に書き留める
                - 自分の成功や良い点をリストアップする
                - ネガティブな思考が浮かんだとき、反対の可能性も考える
                """)
            elif most_common_pattern["pattern"] == "結論の飛躍":
                st.markdown("""
                - 「これは事実か、それとも私の解釈か」と自問する
                - 他の可能性を3つ以上考えてみる
                - 思考を検証するための証拠を集める
                """)
            elif most_common_pattern["pattern"] == "感情的決めつけ":
                st.markdown("""
                - 感情と事実を区別する練習をする
                - 「今の私は感情的になっている」と認識する
                - 決断する前に冷静になる時間を取る
                """)
        
        # 感情との関連性
        if not emotion_logs_df.empty and 'emotion_type' in emotion_logs_df.columns:
            st.markdown("### 感情と思考パターンの関係")
            
            # 最近の感情ログに思考内容が記録されているものを抽出
            recent_logs = emotion_logs_df.sort_values('date', ascending=False).head(50)
            emotion_types = recent_logs['emotion_type'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 最近の感情タイプの分布")
                
                # 感情タイプの円グラフ
                fig_recent_emotions = px.pie(
                    emotion_types.reset_index(),
                    values=emotion_types.values,
                    names=emotion_types.index,
                    title="最近の感情タイプ",
                    color=emotion_types.index,
                    color_discrete_map={
                        "positive": "#4CAF50",
                        "neutral": "#FFC107",
                        "negative": "#F44336"
                    }
                )
                st.plotly_chart(fig_recent_emotions, use_container_width=True)
            
            with col2:
                # ネガティブ思考パターンと感情の関係についてのアドバイス
                negative_emotion_percent = emotion_types.get('negative', 0) / emotion_types.sum() * 100 if not emotion_types.empty else 0
                
                if negative_emotion_percent > 50:
                    st.markdown(f"""
                    <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                        <h4>思考と感情の関連性</h4>
                        <p>最近の記録では、ネガティブな感情が{negative_emotion_percent:.1f}%を占めています。これは、思考パターンがあなたの感情に大きく影響している可能性があります。</p>
                        <p>思考パターンを意識的に変えることで、感情もポジティブな方向に変化していくでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif negative_emotion_percent > 30:
                    st.markdown(f"""
                    <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                        <h4>思考と感情のバランス</h4>
                        <p>最近の記録では、ネガティブな感情が{negative_emotion_percent:.1f}%あります。バランスは取れていますが、さらに思考パターンを改善することで、よりポジティブな感情を増やせるでしょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>良好な思考と感情のサイクル</h4>
                        <p>最近の記録では、ポジティブな感情の割合が高くなっています。これは健全な思考パターンが定着している証拠かもしれません。この状態を維持していきましょう。</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("まだ思考パターンの記録がありません。上のフォームから記録を追加しましょう。")
    
    # 思考パターンの具体例
    st.markdown("### 記録された思考パターンの例")
    
    has_examples = False
    for pattern in thought_patterns["patterns"]:
        if pattern["examples"]:
            has_examples = True
            st.markdown(f"#### {pattern['name']} ({pattern['count']}回)")
            
            for example in pattern["examples"][-3:]:  # 最新の3つを表示
                st.markdown(f"""
                <div style="background-color: #F5F5F5; padding: 10px; border-radius: 5px; margin: 5px 0;">
                    <p><strong>{example['date']}:</strong> {example['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if len(pattern["examples"]) > 3:
                with st.expander(f"もっと見る ({len(pattern['examples']) - 3}件)"):
                    for example in pattern["examples"][:-3]:
                        st.markdown(f"""
                        <div style="background-color: #F5F5F5; padding: 10px; border-radius: 5px; margin: 5px 0;">
                            <p><strong>{example['date']}:</strong> {example['content']}</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    if not has_examples:
        st.info("まだ思考パターンの具体例が記録されていません。")    

# 得意なことリストページ
def show_strengths_list():
    st.markdown('<h2 class="sub-header">💪 得意なことリスト</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    strengths_data = load_strengths()
    
    st.markdown("""
    自分の強みや得意なことを意識することで、自己肯定感が高まります。
    小さなことでも、あなたが得意だと感じることをリストアップしていきましょう。
    """)
    
    # 新しい強みの追加
    st.markdown("### 強みや得意なことを追加")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("strengths_form"):
            st.markdown("#### 強み・得意なこと")
            
            strength = st.text_input("あなたの強みは？", placeholder="例：粘り強さ、共感力、計画性など")
            strength_desc = st.text_area("詳細や具体例", placeholder="例：困難な状況でも諦めずに取り組み続けることができる")
            
            strength_categories = ["思考力", "対人関係", "実行力", "感情管理", "創造性", "その他"]
            strength_category = st.selectbox("カテゴリー", strength_categories)
            
            submit_strength = st.form_submit_button("強みを追加")
            
            if submit_strength:
                if not strength:
                    st.error("強みを入力してください。")
                else:
                    # 新しい強みを追加
                    new_strength = {
                        "id": str(uuid.uuid4()),
                        "name": strength,
                        "description": strength_desc,
                        "category": strength_category,
                        "date_added": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    strengths_data["strengths"].append(new_strength)
                    save_strengths(strengths_data)
                    
                    st.success("強みを追加しました！")
    
    with col2:
        with st.form("skills_form"):
            st.markdown("#### スキル・特技")
            
            skill = st.text_input("あなたのスキルや特技は？", placeholder="例：プログラミング、料理、絵を描くことなど")
            skill_desc = st.text_area("詳細や習熟度", placeholder="例：Pythonを使ったデータ分析を3年経験")
            
            skill_categories = ["技術的", "芸術的", "言語", "身体的", "ビジネス", "その他"]
            skill_category = st.selectbox("カテゴリー", skill_categories)
            
            submit_skill = st.form_submit_button("スキルを追加")
            
            if submit_skill:
                if not skill:
                    st.error("スキルを入力してください。")
                else:
                    # 新しいスキルを追加
                    new_skill = {
                        "id": str(uuid.uuid4()),
                        "name": skill,
                        "description": skill_desc,
                        "category": skill_category,
                        "date_added": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    strengths_data["skills"].append(new_skill)
                    save_strengths(strengths_data)
                    
                    st.success("スキルを追加しました！")
    
    # 強みとスキルのリスト表示
    st.markdown("### あなたの強みとスキルのリスト")
    
    tab1, tab2 = st.tabs(["強み", "スキル"])
    
    with tab1:
        if strengths_data["strengths"]:
            # カテゴリー別に強みを整理
            strengths_by_category = {}
            for strength in strengths_data["strengths"]:
                category = strength.get("category", "その他")
                if category not in strengths_by_category:
                    strengths_by_category[category] = []
                strengths_by_category[category].append(strength)
            
            for category, strengths in strengths_by_category.items():
                st.markdown(f"#### {category}")
                
                for strength in strengths:
                    st.markdown(f"""
                    <div class="strength-card">
                        <h4>{strength['name']}</h4>
                        <p>{strength['description']}</p>
                        <p><small>追加日: {strength.get('date_added', '不明')}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("まだ強みが登録されていません。上のフォームから追加しましょう。")
    
    with tab2:
        if strengths_data["skills"]:
            # カテゴリー別にスキルを整理
            skills_by_category = {}
            for skill in strengths_data["skills"]:
                category = skill.get("category", "その他")
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill)
            
            for category, skills in skills_by_category.items():
                st.markdown(f"#### {category}")
                
                for skill in skills:
                    st.markdown(f"""
                    <div class="strength-card">
                        <h4>{skill['name']}</h4>
                        <p>{skill['description']}</p>
                        <p><small>追加日: {skill.get('date_added', '不明')}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("まだスキルが登録されていません。上のフォームから追加しましょう。")
    
    # 強みを活かすヒント
    if strengths_data["strengths"] or strengths_data["skills"]:
        st.markdown("### 強みとスキルを活かすヒント")
        
        # ワードクラウドで強みとスキルを視覚化
        if strengths_data["strengths"] or strengths_data["skills"]:
            words = " ".join([s["name"] for s in strengths_data["strengths"]] + [s["name"] for s in strengths_data["skills"]])
            
            if words:
                # ワードクラウドの生成
                try:
                    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(words)
                    
                    # Matplotlibのfigureに変換
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"ワードクラウドの生成でエラーが発生しました: {e}")
        
        # 自己PR文の自動生成
        st.markdown("#### 自己PR文の生成")
        
        if st.button("自己PR文を生成"):
            if strengths_data["strengths"] and strengths_data["skills"]:
                # 強みとスキルをランダムに選択
                selected_strengths = random.sample(strengths_data["strengths"], min(3, len(strengths_data["strengths"])))
                selected_skills = random.sample(strengths_data["skills"], min(2, len(strengths_data["skills"])))
                
                # 自己PR文の生成
                pr_text = "私の強みは"
                
                for i, strength in enumerate(selected_strengths):
                    if i == len(selected_strengths) - 1 and len(selected_strengths) > 1:
                        pr_text += f"そして{strength['name']}です。"
                    elif i == 0:
                        pr_text += f"{strength['name']}"
                    else:
                        pr_text += f"、{strength['name']}"
                
                if selected_strengths:
                    details = []
                    for strength in selected_strengths:
                        if strength.get("description"):
                            details.append(f"{strength['name']}については、{strength['description']}")
                    
                    if details:
                        pr_text += " " + " また、".join(details) + "。"
                
                if selected_skills:
                    pr_text += " スキルとしては"
                    
                    for i, skill in enumerate(selected_skills):
                        if i == len(selected_skills) - 1 and len(selected_skills) > 1:
                            pr_text += f"そして{skill['name']}があります。"
                        elif i == 0:
                            pr_text += f"{skill['name']}"
                        else:
                            pr_text += f"、{skill['name']}"
                    
                    details = []
                    for skill in selected_skills:
                        if skill.get("description"):
                            details.append(f"{skill['name']}については、{skill['description']}")
                    
                    if details:
                        pr_text += " " + " また、".join(details) + "。"
                
                pr_text += " これらの強みとスキルを活かして、積極的に貢献していきたいと考えています。"
                
                st.markdown(f"""
                <div style="background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin-top: 10px;">
                    <h4>あなたの自己PR文</h4>
                    <p>{pr_text}</p>
                    <p><small>※ この文章はあなたの登録した強みとスキルを基に自動生成されたものです。必要に応じて編集してご活用ください。</small></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("自己PR文を生成するには、強みとスキルを登録してください。")
        
        # 強みを活かすアドバイス
        st.markdown("#### 強みを活かすためのアドバイス")
        
        # 強みのカテゴリーに基づいたアドバイス
        strength_categories = set([s.get("category", "その他") for s in strengths_data["strengths"]])
        
        for category in strength_categories:
            if category == "思考力":
                st.markdown("""
                - **仕事での活かし方**: 問題解決が必要なプロジェクトや分析業務で力を発揮できます
                - **人間関係での活かし方**: チームの中で問題解決役として貢献できます
                - **自己成長への活かし方**: 複雑な課題に挑戦することで、さらに思考力を磨けます
                """)
            elif category == "対人関係":
                st.markdown("""
                - **仕事での活かし方**: チームリーダーや調整役、顧客対応など人との関わりが重要な役割に適しています
                - **人間関係での活かし方**: 周囲の人の橋渡し役になることで、良好な関係構築に貢献できます
                - **自己成長への活かし方**: コミュニケーションスキルをさらに磨くことで、より多様な人と良い関係を築けます
                """)
            elif category == "実行力":
                st.markdown("""
                - **仕事での活かし方**: 期限のあるプロジェクトや行動力が求められる場面で力を発揮できます
                - **人間関係での活かし方**: 計画を立てて実行する役割を担うことで、チームに貢献できます
                - **自己成長への活かし方**: 小さな目標を設定して達成を繰り返すことで、さらに実行力を高められます
                """)
            elif category == "感情管理":
                st.markdown("""
                - **仕事での活かし方**: ストレスの多い環境や冷静さが求められる場面で価値を発揮できます
                - **人間関係での活かし方**: 周囲が感情的になる状況で、安定した存在として関係を維持できます
                - **自己成長への活かし方**: マインドフルネスなどの実践を通じて、さらに感情管理能力を高められます
                """)
            elif category == "創造性":
                st.markdown("""
                - **仕事での活かし方**: 新しいアイデアやアプローチが求められる場面で力を発揮できます
                - **人間関係での活かし方**: 行き詰まった状況で新しい視点を提供できます
                - **自己成長への活かし方**: 芸術や表現活動に取り組むことで、さらに創造性を高められます
                """)
    else:
        st.info("強みとスキルを登録すると、それらを活かすヒントが表示されます。") 

# 価値観診断ページ
def show_values_diagnosis():
    st.markdown('<h2 class="sub-header">🧭 価値観診断</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    values_data = load_values()
    
    st.markdown("""
    あなたにとって何が大切か、どんな価値観を持っているかを把握することで、
    より自分らしい選択ができるようになります。
    """)
    
    # 価値観の重要度設定
    st.markdown("### あなたの価値観の重要度を設定")
    
    values_updated = False
    
    for i, value in enumerate(values_data["values"]):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <p class="slider-label">{value['name']} - {value['description']}</p>
            """, unsafe_allow_html=True)
            new_importance = st.slider(
                f"重要度（{value['name']}）",
                0, 100, int(value['importance']),
                label_visibility="collapsed"
            )
            
            if new_importance != value['importance']:
                values_data["values"][i]['importance'] = new_importance
                values_updated = True
        
        with col2:
            st.markdown(f"**{new_importance}%**")
    
    if values_updated:
        save_values(values_data)
        # 新しい行を追加: 価値観が更新されたら履歴に保存
        save_values_snapshot(values_data)
        st.success("価値観の重要度を更新しました！")
    
    # 新しい価値観の追加
    st.markdown("### 新しい価値観を追加")
    
    with st.form("new_value_form"):
        new_value_name = st.text_input("価値観の名前", placeholder="例：自由、冒険、学び、家族など")
        new_value_desc = st.text_input("説明", placeholder="この価値観の詳細や、あなたにとっての意味")
        new_value_importance = st.slider("重要度", 0, 100, 50)
        
        submit = st.form_submit_button("価値観を追加")
        
        if submit:
            if not new_value_name:
                st.error("価値観の名前を入力してください。")
            else:
                # 新しい価値観を追加
                new_value = {
                    "name": new_value_name,
                    "description": new_value_desc,
                    "importance": new_value_importance
                }
                
                values_data["values"].append(new_value)
                save_values(values_data)
                
                st.success("新しい価値観を追加しました！")
                st.rerun()
    
    # 価値観分析
    st.markdown("### あなたの価値観分析")
    
    # 重要度が高い価値観をランキング
    sorted_values = sorted(values_data["values"], key=lambda x: x['importance'], reverse=True)
    
    # 価値観の重要度をグラフで表示
    values_df = pd.DataFrame([
        {"name": value["name"], "importance": value["importance"]}
        for value in sorted_values
    ])
    
    fig = px.bar(
        values_df,
        x="name",
        y="importance",
        title="価値観の重要度ランキング",
        labels={"name": "価値観", "importance": "重要度 (%)"},
        color="importance",
        color_continuous_scale=["gray", "blue", "green"],
        range_color=[0, 100]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # トップ3の価値観
    top_values = sorted_values[:3]
    
    st.markdown(f"""
    <div class="insight-box">
        <h4>あなたの価値観トップ3</h4>
        <p>あなたが最も大切にしている価値観は：</p>
        <ol>
            <li><strong>{top_values[0]['name']}</strong> ({top_values[0]['importance']}%) - {top_values[0]['description']}</li>
            <li><strong>{top_values[1]['name']}</strong> ({top_values[1]['importance']}%) - {top_values[1]['description']}</li>
            <li><strong>{top_values[2]['name']}</strong> ({top_values[2]['importance']}%) - {top_values[2]['description']}</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # 価値観に基づくアドバイス
    st.markdown("### 価値観を活かすためのアドバイス")
    
    # トップの価値観に基づいたアドバイス
    top_value = top_values[0]
    
    if top_value["name"] == "仕事":
        st.markdown("""
        仕事を重視するあなたへのアドバイス：
        - 自分の強みを活かせる仕事や役割を意識的に選ぶ
        - 仕事の中で成長できる機会を積極的に探す
        - ワークライフバランスにも注意を払い、燃え尽き症候群を避ける
        - 仕事での成果を適切に評価してもらえる環境を選ぶ
        """)
    elif top_value["name"] == "人間関係":
        st.markdown("""
        人間関係を重視するあなたへのアドバイス：
        - 大切な人との時間を意識的に確保する
        - 人間関係の質を高めるためのコミュニケーションスキルを磨く
        - 新しい出会いの機会を積極的に作る
        - 自分を大切にしながら他者とつながるバランスを意識する
        """)
    elif top_value["name"] == "成長":
        st.markdown("""
        成長を重視するあなたへのアドバイス：
        - 継続的な学びの機会を意識的に取り入れる
        - 成長を実感できる目標設定と振り返りを行う
        - 異なる分野にも興味を広げ、多角的な成長を目指す
        - 自分の成長を記録し、可視化する習慣をつける
        """)
    elif top_value["name"] == "趣味":
        st.markdown("""
        趣味を重視するあなたへのアドバイス：
        - 趣味の時間を優先的にスケジュールに組み込む
        - 新しい趣味にも挑戦してみる
        - 趣味を通じた交流の場を探す
        - 趣味のスキルを向上させる目標を設定する
        """)
    elif top_value["name"] == "健康":
        st.markdown("""
        健康を重視するあなたへのアドバイス：
        - 日常的な運動と健康的な食事を習慣化する
        - 質の良い睡眠を確保する工夫をする
        - ストレス管理の方法を意識的に取り入れる
        - 定期的な健康チェックを行う
        """)
    elif top_value["name"] == "社会貢献":
        st.markdown("""
        社会貢献を重視するあなたへのアドバイス：
        - 自分の強みを活かせるボランティア活動を探す
        - 日常の小さな親切や行動から始める
        - 社会問題に関する情報を積極的に収集する
        - 同じ価値観を持つコミュニティとつながる
        """)
    elif top_value["name"] == "安定":
        st.markdown("""
        安定を重視するあなたへのアドバイス：
        - 長期的な視点で生活設計を行う
        - リスク管理を意識した選択を心がける
        - 定期的な見直しと調整の習慣をつける
        - 必要に応じて専門家のアドバイスも活用する
        """)
    else:
        st.markdown(f"""
        {top_value["name"]}を重視するあなたへのアドバイス：
        - 日常の選択において、この価値観を意識的に優先する
        - この価値観に沿った生活や環境を作るために必要な変化を考える
        - 同じ価値観を持つ人々とのつながりを探す
        - この価値観をさらに深めるための行動や学びの機会を作る
        """)
    
    # 価値観と現実のギャップチェック部分を修正
    # 価値観と現実のギャップチェック（重要度に対する反映度の比率で判定）
# 03_自己認識.py の show_values_diagnosis() 関数内の「価値観と現実のギャップチェック」セクションを以下のコードに置き換えてください

# 価値観と現実のギャップチェック部分を修正
    st.markdown("### 価値観と現実のギャップチェック")

    st.markdown("""
    あなたの価値観と現実の生活にギャップがあると、不満や違和感を感じることがあります。
    以下のチェックリストで、あなたの価値観と現実の生活の一致度を確認しましょう。
    """)

    # 価値観の重複を排除し、すべての価値観を表示
    # 名前でユニークにする
    unique_values = []
    unique_names = set()

    for value in values_data["values"]:
        if value["name"] not in unique_names:
            unique_names.add(value["name"])
            unique_values.append(value)

    # 各価値観について、現実との一致度をチェック
    alignment_scores = {}
    alignment_updated = False

    # values_dataに"alignment"キーがなければ初期化
    if "alignment" not in values_data:
        values_data["alignment"] = {}

    # 改善プランを保存するキーがなければ初期化
    if "improvement_plans" not in values_data:
        values_data["improvement_plans"] = {}

    for value in unique_values:  # すべての価値観をチェック
        value_name = value['name']
        value_importance = value['importance']
        
        st.markdown(f"#### {value_name} (重要度: {value_importance}%)")
        
        # 保存されている一致度を取得、なければデフォルト値50を使用
        current_alignment = values_data["alignment"].get(value_name, 50)
        
        # 以前の改善プランを取得
        previous_plan = values_data["improvement_plans"].get(value_name, "")
        
        # スライダーの値を取得
        new_alignment = st.slider(
            f"{value_name}の価値観は現在の生活にどの程度反映されていますか？",
            0, 100, 
            value=current_alignment,
            key=f"alignment_{value_name}"
        )
        
        # 値が変更された場合は更新フラグを立てる
        if new_alignment != current_alignment:
            values_data["alignment"][value_name] = new_alignment
            alignment_updated = True
        
        # 値を保存
        alignment_scores[value_name] = new_alignment
        
        # 重要度に対する反映度の比率を計算
        if value_importance > 0:
            alignment_ratio = (new_alignment / value_importance) * 100
        else:
            alignment_ratio = 100  # 重要度が0の場合は100%とする
        
        # ギャップを計算（重要度 - 反映度）
        gap_percentage = value_importance - new_alignment
        
        # 一致度を表示
        st.markdown(f"""
        <div style="background-color: #F5F5F5; padding: 8px; border-radius: 5px; margin: 5px 0;">
            <p><strong>一致度:</strong> {alignment_ratio:.1f}% 
            (重要度 {value_importance}% に対して反映度 {new_alignment}%)</p>
            <p><strong>ギャップ:</strong> {gap_percentage}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ギャップが20%以上の場合のみアドバイスと改善プラン入力欄を表示
        if gap_percentage >= 20:
            # ギャップの程度に応じてメッセージを変更
            if gap_percentage >= 50:
                st.markdown(f"""
                <div style="background-color: #FFEBEE; padding: 10px; border-radius: 5px; margin-top: 5px;">
                    <p>この価値観と現実の生活には大きなギャップ({gap_percentage}%)があります。
                    優先度を見直し、この価値観に沿った生活に近づける変化を検討してみましょう。</p>
                </div>
                """, unsafe_allow_html=True)
            elif gap_percentage >= 30:
                st.markdown(f"""
                <div style="background-color: #FFF3E0; padding: 10px; border-radius: 5px; margin-top: 5px;">
                    <p>この価値観と現実の生活には中程度のギャップ({gap_percentage}%)があります。
                    この価値観により意識を向けて、生活に取り入れる方法を考えてみましょう。</p>
                </div>
                """, unsafe_allow_html=True)
            else:  # 20-29%
                st.markdown(f"""
                <div style="background-color: #FFF9C4; padding: 10px; border-radius: 5px; margin-top: 5px;">
                    <p>この価値観は部分的に生活に反映されていますが、さらに一致させる余地({gap_percentage}%のギャップ)があります。
                    小さな改善から始めてみましょう。</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 改善プラン入力欄を表示
            improvement_plan = st.text_area(
                f"{value_name}の価値観をより生活に反映させるための小さな改善計画",
                value=previous_plan,
                placeholder="例：週に1回、この価値観に関連する活動に時間を割く",
                key=f"improvement_{value_name}"
            )
            
            # 改善プランが変更された場合は保存
            if improvement_plan != previous_plan:
                values_data["improvement_plans"][value_name] = improvement_plan
                alignment_updated = True
            
        else:
            # ギャップが20%未満の場合
            st.markdown(f"""
            <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin-top: 5px;">
                <p>この価値観は現在の生活によく反映されています(ギャップ: {gap_percentage}%)。このバランスを維持しましょう。</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ギャップが小さい場合は改善プラン入力欄を表示しない（既存のプランがあれば保存は継続）

    # 値が更新された場合、保存する
    if alignment_updated:
        save_values(values_data)

    # 総合的なアドバイス
    st.markdown("### 価値観と生活の一致度")

    # 重要度を考慮した加重平均一致度を計算
    if alignment_scores and unique_values:
        total_weighted_alignment = 0
        total_importance = 0
        
        for value in unique_values:
            value_name = value['name']
            value_importance = value['importance']
            value_alignment = alignment_scores.get(value_name, 50)
            
            total_weighted_alignment += value_alignment * value_importance
            total_importance += value_importance
        
        if total_importance > 0:
            weighted_average_alignment = total_weighted_alignment / total_importance
        else:
            weighted_average_alignment = 50
            
        # 全体のギャップも計算
        total_gap = 0
        gap_count = 0
        
        for value in unique_values:
            value_name = value['name']
            value_importance = value['importance']
            value_alignment = alignment_scores.get(value_name, 50)
            gap = value_importance - value_alignment
            if gap > 0:
                total_gap += gap
                gap_count += 1
        
        average_gap = total_gap / len(unique_values) if unique_values else 0
    else:
        weighted_average_alignment = 50
        average_gap = 0

    st.markdown(f"""
    <div class="value-card">
        <h4>総合一致度: {weighted_average_alignment:.1f}%</h4>
        <p>あなたの重要な価値観と現実の生活の重要度加重一致度は {weighted_average_alignment:.1f}% です。</p>
        <p>平均ギャップ: {average_gap:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

    if average_gap >= 40:
        st.markdown("""
        <p>全体的に、価値観と現実の生活には大きなギャップがあるようです。このギャップが不満や違和感の原因になっている可能性があります。以下の点を検討してみましょう：</p>
        <ul>
            <li>最も重要な価値観から優先的に改善に取り組む</li>
            <li>現在の環境や状況を見直し、価値観に合った選択ができるよう調整する</li>
            <li>小さな変化から始め、徐々に価値観に沿った生活に近づける</li>
            <li>現実的な制約がある場合は、その中でできる最善の方法を探す</li>
        </ul>
        """, unsafe_allow_html=True)
    elif average_gap >= 20:
        st.markdown("""
        <p>価値観と現実の生活は、ある程度一致していますが、まだ改善の余地があります。以下の点を検討してみましょう：</p>
        <ul>
            <li>ギャップが大きい価値観について、優先的に改善策を考える</li>
            <li>日々の選択において、自分の価値観を意識する習慣をつける</li>
            <li>定期的に振り返りを行い、必要な調整を行う</li>
            <li>価値観に沿った行動を増やすための具体的な計画を立てる</li>
        </ul>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <p>価値観と現実の生活がよく一致しています。このバランスを維持しながら、さらに充実した生活を目指しましょう：</p>
        <ul>
            <li>価値観に基づいた選択を継続する</li>
            <li>新たな価値観の発見や深化を楽しむ</li>
            <li>価値観の変化にも柔軟に対応する</li>
            <li>価値観を活かした新しい挑戦を考える</li>
        </ul>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ギャップが大きい価値観のハイライト
    significant_gaps = []
    for value in unique_values:
        value_name = value['name']
        value_importance = value['importance']
        value_alignment = alignment_scores.get(value_name, 50)
        gap = value_importance - value_alignment
        if gap >= 20:
            significant_gaps.append((value_name, gap, value_importance, value_alignment))

    if significant_gaps:
        st.markdown("### 優先的に取り組むべき価値観")
        
        # ギャップの大きい順にソート
        significant_gaps.sort(key=lambda x: x[1], reverse=True)
        
        for value_name, gap, importance, alignment in significant_gaps:
            st.markdown(f"""
            <div style="background-color: #FFF3E0; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid #FF9800;">
                <h5>{value_name}</h5>
                <p>重要度: {importance}% → 反映度: {alignment}% (ギャップ: {gap}%)</p>
            </div>
            """, unsafe_allow_html=True)

    # 改善プランの一覧表示（ギャップがある価値観のみ）
    if "improvement_plans" in values_data and any(values_data["improvement_plans"].values()):
        plans_with_gaps = {k: v for k, v in values_data["improvement_plans"].items() 
                        if v and any(value['name'] == k and value['importance'] - alignment_scores.get(k, 50) >= 20 
                                    for value in unique_values)}
        
        if plans_with_gaps:
            with st.expander("改善プラン一覧（ギャップのある価値観）", expanded=False):
                st.markdown("### 価値観を生活に取り入れるための改善プラン")
                
                for value_name, plan in plans_with_gaps.items():
                    # ギャップ情報も表示
                    value_info = next((v for v in unique_values if v['name'] == value_name), None)
                    if value_info:
                        importance = value_info['importance']
                        alignment = alignment_scores.get(value_name, 50)
                        gap = importance - alignment
                        
                        st.markdown(f"#### {value_name} (ギャップ: {gap}%)")
                        st.markdown(f"{plan}")
                        st.markdown("---")

    # 価値観の変化履歴を表示する新しいセクションを追加
    st.markdown("### 価値観の変化履歴")
    
    # 履歴データを読み込む
    history_data = load_values_history()
    
    if len(history_data) <= 1:
        st.info("まだ十分な履歴データがありません。価値観の変更を記録して、変化を追跡していきましょう。")
    else:
        # 表示期間を選択
        period_options = ["すべての履歴", "直近3回", "直近5回", "カスタム期間"]
        selected_period = st.selectbox("表示期間", period_options)
        
        # カスタム期間の選択（カスタム期間を選んだ場合のみ表示）
        if selected_period == "カスタム期間":
            history_dates = [item["date"] for item in history_data]
            start_date = st.selectbox("開始日", history_dates)
            end_date = st.selectbox("終了日", history_dates, index=len(history_dates)-1)
            
            # 期間内のデータをフィルタリング
            filtered_history = [
                item for item in history_data 
                if item["date"] >= start_date and item["date"] <= end_date
            ]
        elif selected_period == "直近3回":
            filtered_history = history_data[-3:]
        elif selected_period == "直近5回":
            filtered_history = history_data[-5:]
        else:  # すべての履歴
            filtered_history = history_data
        
        # 価値観を選択
        value_names = [value["name"] for value in values_data["values"]]
        selected_value = st.selectbox("追跡する価値観", value_names)
        
        # 変化グラフを作成
        importance_data = []
        
        for snapshot in filtered_history:
            date = snapshot["date"]
            for value in snapshot["values"]:
                if value["name"] == selected_value:
                    importance_data.append({
                        "date": date,
                        "importance": value["importance"]
                    })
                    break
        
        if importance_data:
            # データフレームに変換
            df = pd.DataFrame(importance_data)
            df["date"] = pd.to_datetime(df["date"])
            
            # 折れ線グラフの作成
            fig = px.line(
                df,
                x="date",
                y="importance",
                title=f"{selected_value}の重要度変化",
                labels={"date": "日付", "importance": "重要度 (%)"},
                markers=True
            )
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            # 変化の解釈
            if len(importance_data) >= 2:
                first_importance = importance_data[0]["importance"]
                last_importance = importance_data[-1]["importance"]
                change = last_importance - first_importance
                
                if abs(change) < 5:
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>ほとんど変化していません</h4>
                        <p>{selected_value}の重要度は{abs(change)}%の変化にとどまっています。この価値観に対する考えは安定しています。</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif change > 0:
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>重要度が増加しています</h4>
                        <p>{selected_value}の重要度は{change}%増加しています。この価値観があなたの中でより重要になってきています。</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>重要度が減少しています</h4>
                        <p>{selected_value}の重要度は{abs(change)}%減少しています。この価値観の優先順位が変わってきている可能性があります。</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 変化率の計算
                if first_importance > 0:  # ゼロ除算を避ける
                    change_rate = (change / first_importance) * 100
                    st.markdown(f"変化率: **{change_rate:.1f}%**")
        else:
            st.info(f"選択した期間に {selected_value} の履歴データはありません。")
            
        # 複数の価値観を比較する
        st.markdown("### 価値観の比較")
        
        # 比較する価値観を選択（複数選択可能）
        compare_values = st.multiselect(
            "比較する価値観を選択",
            value_names,
            default=[value_names[0]] if value_names else []
        )
        
        if compare_values:
            # 比較用のデータを準備
            comparison_data = []
            
            for snapshot in filtered_history:
                date = snapshot["date"]
                for value in snapshot["values"]:
                    if value["name"] in compare_values:
                        comparison_data.append({
                            "date": date,
                            "価値観": value["name"],
                            "重要度": value["importance"]
                        })
            
            if comparison_data:
                # データフレームに変換
                compare_df = pd.DataFrame(comparison_data)
                compare_df["date"] = pd.to_datetime(compare_df["date"])
                
                # 複数の価値観を表示するグラフ
                fig_compare = px.line(
                    compare_df,
                    x="date",
                    y="重要度",
                    color="価値観",
                    title="価値観の重要度比較",
                    labels={"date": "日付", "重要度": "重要度 (%)"},
                    markers=True
                )
                fig_compare.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_compare, use_container_width=True)
                
                # 価値観間の相関関係を分析
                if len(compare_values) > 1 and len(filtered_history) > 2:
                    st.markdown("### 価値観の相関関係")
                    st.write("選択した価値観の重要度変化の相関関係を分析します。")
                    
                    # ピボットテーブルを作成して相関係数を計算
                    pivot_df = compare_df.pivot_table(index="date", columns="価値観", values="重要度")
                    corr_matrix = pivot_df.corr()
                    
                    # ヒートマップで相関係数を可視化
                    fig_corr = px.imshow(
                        corr_matrix,
                        title="価値観間の相関係数",
                        color_continuous_scale="RdBu_r",
                        range_color=[-1, 1]
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # 相関関係の解釈
                    highest_corr = None
                    highest_val = 0
                    negative_corr = None
                    negative_val = 0
                    
                    for i in range(len(compare_values)):
                        for j in range(i+1, len(compare_values)):
                            val = corr_matrix.iloc[i, j]
                            if val > highest_val:
                                highest_val = val
                                highest_corr = (compare_values[i], compare_values[j])
                            if val < negative_val:
                                negative_val = val
                                negative_corr = (compare_values[i], compare_values[j])
                    
                    if highest_corr and highest_val > 0.5:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>強い正の相関</h4>
                            <p><strong>{highest_corr[0]}</strong>と<strong>{highest_corr[1]}</strong>の間に強い正の相関({highest_val:.2f})があります。
                            これらの価値観の重要度は一緒に変化する傾向があります。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if negative_corr and negative_val < -0.5:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>強い負の相関</h4>
                            <p><strong>{negative_corr[0]}</strong>と<strong>{negative_corr[1]}</strong>の間に強い負の相関({negative_val:.2f})があります。
                            一方の重要度が上がると、もう一方は下がる傾向があります。</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("選択した期間に比較データはありません。")
        else:
            st.info("比較する価値観を選択してください。")

# 未来ビジョンページ
def show_future_vision():
    st.markdown('<h2 class="sub-header">🔮 未来ビジョン</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    future_vision = load_future_vision()
    values_data = load_values()
    strengths_data = load_strengths()
    
    st.markdown("""
    「1年後の自分はどうありたいか」を具体的にイメージすることで、
    成長の方向性が明確になり、日々の選択がしやすくなります。
    """)
    
    # 未来ビジョンの設定・更新
    st.markdown("### 1年後の自分のビジョン")
    
    # 現在の未来ビジョン
    vision_text = future_vision.get("vision", "")
    new_vision = st.text_area(
        "1年後、あなたはどんな自分になっていたいですか？",
        value=vision_text,
        height=150,
        placeholder="例：1年後の私は、プログラミングスキルを向上させ、小規模なWebアプリを自力で作れるようになっています。また、週3回の運動習慣が定着し、体力が向上しています。職場では、チームのリーダーとして認められ、後輩の指導も任されるようになっています..."
    )
    
    if new_vision != vision_text:
        future_vision["vision"] = new_vision
        future_vision["creation_date"] = datetime.now().strftime("%Y-%m-%d")
        save_future_vision(future_vision)
        st.success("未来ビジョンを更新しました！")
    
    # 具体的な目標設定
    st.markdown("### 具体的な目標")
    
    st.markdown("""
    未来ビジョンを実現するための具体的な目標を設定しましょう。
    SMART（具体的、測定可能、達成可能、関連性がある、期限がある）な目標が効果的です。
    """)
    
    # 新しい目標の追加
    with st.form("new_goal_form"):
        goal_area_options = ["キャリア・仕事", "健康・運動", "学習・成長", "人間関係", "趣味・創作", "その他"]
        goal_area = st.selectbox("目標の分野", goal_area_options)
        
        goal_text = st.text_input("具体的な目標", placeholder="例：Pythonの基礎を学び、簡単なWebアプリを作成する")
        
        goal_deadline = st.date_input("達成期限", datetime.now() + timedelta(days=90))
        
        goal_milestones = st.text_area(
            "中間マイルストーン（各行に1つ記入）",
            placeholder="例：\nUdemyのPython基礎コースを完了する\n簡単なCLIアプリを作成する\nFlaskの基礎を学ぶ"
        )
        
        submit_goal = st.form_submit_button("目標を追加")
        
        if submit_goal:
            if not goal_text:
                st.error("目標を入力してください。")
            else:
                # 新しい目標を追加
                new_goal = {
                    "id": str(uuid.uuid4()),
                    "area": goal_area,
                    "text": goal_text,
                    "deadline": goal_deadline.strftime("%Y-%m-%d"),
                    "milestones": [m.strip() for m in goal_milestones.split("\n") if m.strip()],
                    "progress": 0,
                    "created_at": datetime.now().strftime("%Y-%m-%d")
                }
                
                if "goals" not in future_vision:
                    future_vision["goals"] = []
                
                future_vision["goals"].append(new_goal)
                save_future_vision(future_vision)
                
                st.success("新しい目標を追加しました！")
    
    # 目標リストと進捗管理
    if "goals" in future_vision and future_vision["goals"]:
        st.markdown("### 目標リストと進捗状況")
        
        # 目標を分野ごとに整理
        goals_by_area = {}
        for goal in future_vision["goals"]:
            area = goal.get("area", "その他")
            if area not in goals_by_area:
                goals_by_area[area] = []
            goals_by_area[area].append(goal)
        
        for area, goals in goals_by_area.items():
            st.markdown(f"#### {area}")
            
            for goal in goals:
                with st.expander(f"{goal['text']} (期限: {goal['deadline']})"):
                    # 進捗状況の更新
                    new_progress = st.slider(
                        "進捗状況",
                        0, 100, int(goal.get("progress", 0)),
                        key=f"progress_{goal['id']}"
                    )
                    
                    if new_progress != goal.get("progress", 0):
                        # 目標リストから該当する目標を見つけて更新
                        for i, g in enumerate(future_vision["goals"]):
                            if g["id"] == goal["id"]:
                                future_vision["goals"][i]["progress"] = new_progress
                                save_future_vision(future_vision)
                                st.success("進捗状況を更新しました！")
                                break
                    
                    # マイルストーン
                    if goal.get("milestones"):
                        st.markdown("##### マイルストーン")
                        for milestone in goal["milestones"]:
                            st.markdown(f"- {milestone}")
                    
                    # 残り日数の計算
                    deadline = datetime.strptime(goal["deadline"], "%Y-%m-%d").date()
                    days_left = (deadline - datetime.now().date()).days
                    
                    if days_left < 0:
                        st.markdown(f"""
                        <div style="background-color: #FFEBEE; padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <p>⚠️ 期限を{abs(days_left)}日過ぎています。目標の見直しか期限の延長を検討してください。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif days_left < 7:
                        st.markdown(f"""
                        <div style="background-color: #FFF9C4; padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <p>⏰ 期限まであと{days_left}日です。ラストスパートをかけましょう！</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <p>📅 期限まであと{days_left}日あります。計画的に進めましょう。</p>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("まだ目標が設定されていません。上のフォームから目標を追加しましょう。")
    
    # 理想の自分に近づくためのアドバイス
    st.markdown("### 理想の自分に近づくためのアドバイス")
    
    # 強み、価値観、ビジョンを組み合わせたアドバイス
    if vision_text and values_data["values"] and (strengths_data["strengths"] or strengths_data["skills"]):
        # トップの価値観を取得
        top_values = sorted(values_data["values"], key=lambda x: x['importance'], reverse=True)[:3]
        top_value_names = [v["name"] for v in top_values]
        
        # 強みのリストを取得
        strengths = [s["name"] for s in strengths_data["strengths"]]
        skills = [s["name"] for s in strengths_data["skills"]]
        
        st.markdown(f"""
        <div class="future-vision">
            <h4>ビジョン実現のためのアドバイス</h4>
            <p>あなたが描く未来ビジョンには、あなたの強み（{", ".join(strengths[:2] + skills[:1])}）を活かす要素が含まれています。
            また、あなたの重要な価値観（{", ".join(top_value_names)}）と一致する方向性です。</p>
            
            <p>以下のポイントを意識すると、理想の自分に近づきやすくなります：</p>
            <ul>
                <li>日々の小さな選択において、未来ビジョンを意識する</li>
                <li>進捗状況を定期的に振り返り、軌道修正を行う</li>
                <li>強みを意識的に活用する機会を探す</li>
                <li>価値観と一致した選択を優先する</li>
                <li>ビジョン実現の障害になりそうな習慣や思考パターンを特定し、改善する</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 理想の自分に近づいた度のスコア
        st.markdown("#### 理想の自分に近づいた度")
        
        self_ideal_score = st.slider(
            "あなたは今、理想の自分にどのくらい近づいていると感じますか？",
            0, 100, future_vision.get("self_understanding_score", 50)
        )
        
        if self_ideal_score != future_vision.get("self_understanding_score", 50):
            future_vision["self_understanding_score"] = self_ideal_score
            save_future_vision(future_vision)
            st.success("理想の自分に近づいた度を更新しました！")
        
        if self_ideal_score < 30:
            st.markdown("""
            <div style="background-color: #FFEBEE; padding: 10px; border-radius: 5px;">
                <p>理想の自分とのギャップを感じているようです。焦らず、小さな一歩から始めましょう。日々の小さな改善が、やがて大きな変化につながります。</p>
            </div>
            """, unsafe_allow_html=True)
        elif self_ideal_score < 70:
            st.markdown("""
            <div style="background-color: #FFF9C4; padding: 10px; border-radius: 5px;">
                <p>理想の自分に向かって着実に進んでいます。継続的な努力と定期的な振り返りを続けましょう。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #E8F5E9; padding: 10px; border-radius: 5px;">
                <p>理想の自分に近づいていると実感できていることは素晴らしいことです。この状態を維持しながら、さらなる高みを目指しましょう。</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("強み、価値観、未来ビジョンを設定すると、より具体的なアドバイスが表示されます。") 

# 自己認識の進歩ページ
def show_self_awareness_progress():
    st.markdown('<h2 class="sub-header">📈 自己認識の進歩</h2>', unsafe_allow_html=True)
    
    # データを読み込む
    emotion_logs_df = load_emotion_logs()
    future_vision = load_future_vision()
    
    st.markdown("""
    時間の経過とともに、あなたの自己認識がどのように変化しているかを振り返ります。
    過去と比較することで、成長や変化を実感できます。
    """)
    
    # 期間選択
    comparison_period = st.selectbox(
        "比較する期間",
        ["1ヶ月前", "3ヶ月前", "6ヶ月前", "1年前"]
    )
    
    # 感情ログの分析（時系列）
    if not emotion_logs_df.empty and len(emotion_logs_df) > 5:
        st.markdown("### 感情の変化")
        
        # 感情タイプの列を追加
        if 'emotion_type' not in emotion_logs_df.columns:
            emotion_logs_df['emotion_type'] = emotion_logs_df['emotion'].apply(get_emotion_type)
        
        # 日付を変換
        emotion_logs_df['date'] = pd.to_datetime(emotion_logs_df['date'])
        
        # 現在と過去の期間を設定
        today = datetime.now()
        
        if comparison_period == "1ヶ月前":
            past_start = today - timedelta(days=60)
            past_end = today - timedelta(days=30)
        elif comparison_period == "3ヶ月前":
            past_start = today - timedelta(days=120)
            past_end = today - timedelta(days=90)
        elif comparison_period == "6ヶ月前":
            past_start = today - timedelta(days=210)
            past_end = today - timedelta(days=180)
        else:  # 1年前
            past_start = today - timedelta(days=395)
            past_end = today - timedelta(days=365)
        
        current_start = today - timedelta(days=30)
        
        # 過去と現在のデータをフィルタリング
        past_data = emotion_logs_df[(emotion_logs_df['date'] >= past_start) & (emotion_logs_df['date'] <= past_end)]
        current_data = emotion_logs_df[emotion_logs_df['date'] >= current_start]
        
        if not past_data.empty and not current_data.empty:
            # 感情タイプの分布を計算
            past_emotion_types = past_data['emotion_type'].value_counts(normalize=True) * 100
            current_emotion_types = current_data['emotion_type'].value_counts(normalize=True) * 100
            
            # データフレームにまとめる
            comparison_df = pd.DataFrame({
                f"{comparison_period}": past_emotion_types,
                "現在": current_emotion_types
            }).fillna(0).reset_index()
            comparison_df.columns = ['emotion_type', 'past', 'current']
            
            # 変化量を計算
            comparison_df['change'] = comparison_df['current'] - comparison_df['past']
            
            # グラフで表示
            fig = px.bar(
                comparison_df,
                x="emotion_type",
                y=["past", "current"],
                barmode="group",
                title=f"感情タイプの分布比較: {comparison_period} vs 現在",
                labels={"emotion_type": "感情タイプ", "value": "割合 (%)", "variable": "期間"},
                color_discrete_map={"past": "#9E9E9E", "current": "#4CAF50"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # ポジティブ感情の変化
            if 'positive' in comparison_df['emotion_type'].values:
                positive_row = comparison_df[comparison_df['emotion_type'] == 'positive']
                if not positive_row.empty:
                    positive_change = positive_row.iloc[0]['change']
                    
                    if positive_change > 10:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>ポジティブ感情が増加しています！</h4>
                            <p>{comparison_period}と比べて、ポジティブな感情の割合が{positive_change:.1f}%増加しています。
                            これは、あなたの心の状態や環境が良い方向に変化している証拠かもしれません。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif positive_change > 0:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>ポジティブ感情がやや増加しています</h4>
                            <p>{comparison_period}と比べて、ポジティブな感情の割合が{positive_change:.1f}%増加しています。
                            少しずつ良い方向に変化しているようです。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif positive_change < -10:
                        st.markdown(f"""
                        <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                            <h4>ポジティブ感情が減少しています</h4>
                            <p>{comparison_period}と比べて、ポジティブな感情の割合が{abs(positive_change):.1f}%減少しています。
                            何か環境や状況の変化はありませんか？ストレスや課題に対処するサポートを求めることも検討してみてください。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif positive_change < 0:
                        st.markdown(f"""
                        <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                            <h4>ポジティブ感情がやや減少しています</h4>
                            <p>{comparison_period}と比べて、ポジティブな感情の割合が{abs(positive_change):.1f}%減少しています。
                            ストレスや変化に対処するセルフケアを意識してみましょう。</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>感情のバランスは安定しています</h4>
                            <p>{comparison_period}と比べて、感情のバランスに大きな変化はありません。
                            安定した状態を維持できています。</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info(f"{comparison_period}のデータが不足しているため、比較できません。継続的に記録を追加していきましょう。")
    else:
        st.info("感情ログのデータが少ないため、分析できません。「感情ログ」ページで記録を増やしましょう。")
    
    # 思考パターンの変化
    thought_patterns = load_thought_patterns()
    
    if any(p["count"] > 0 for p in thought_patterns["patterns"]):
        st.markdown("### 思考パターンの変化")
        
        st.markdown("""
        思考パターンに気づき、記録することで、あなたの思考の癖への理解が深まっています。
        思考パターンを認識できることは、自己認識の大きな進歩です。
        """)
        
        # 思考パターンの記録回数を可視化
        pattern_counts = [(p["name"], p["count"]) for p in thought_patterns["patterns"]]
        pattern_df = pd.DataFrame(pattern_counts, columns=["pattern", "count"])
        
        fig_patterns = px.pie(
            pattern_df,
            values="count",
            names="pattern",
            title="記録された思考パターンの分布",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_patterns, use_container_width=True)
        
        # 思考パターンへの気づきに関するアドバイス
        total_patterns = sum(p["count"] for p in thought_patterns["patterns"])
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>思考パターンへの気づき</h4>
            <p>これまでに{total_patterns}回の思考パターンを記録しました。これらのパターンに気づき、記録できることは、
            自己認識が高まっている証拠です。</p>
            <p>今後も継続的に記録し、パターンを認識することで、より健全な思考習慣を身につけていきましょう。</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 自己理解度の変化
    if "self_understanding_score" in future_vision:
        st.markdown("### 自己理解度の変化")
        
        current_score = future_vision["self_understanding_score"]
        creation_date = future_vision.get("creation_date", datetime.now().strftime("%Y-%m-%d"))
        
        st.markdown(f"""
        <div class="comparison-container">
            <div class="comparison-card">
                <h4>作成時の自己理解度</h4>
                <p class="progress-stat">50%</p>
                <p><small>基準値</small></p>
            </div>
            <div class="comparison-card">
                <h4>現在の自己理解度</h4>
                <p class="progress-stat">{current_score}%</p>
                <p><small>最終更新: {creation_date}</small></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 自己理解度の進捗バー
        st.progress(current_score / 100)
        
        # 変化に関するコメント
        change = current_score - 50  # 初期値を50%と仮定
        
        if change > 20:
            st.markdown(f"""
            <div class="insight-box">
                <h4>自己理解が大きく向上しています！</h4>
                <p>自己理解度が{change}%向上しています。これは、自己認識を高める活動や振り返りが効果を上げている証拠です。
                素晴らしい進歩です！</p>
            </div>
            """, unsafe_allow_html=True)
        elif change > 0:
            st.markdown(f"""
            <div class="insight-box">
                <h4>自己理解が徐々に向上しています</h4>
                <p>自己理解度が{change}%向上しています。着実に進歩していることを実感できるでしょう。
                このペースで継続していきましょう。</p>
            </div>
            """, unsafe_allow_html=True)
        elif change < -10:
            st.markdown(f"""
            <div class="insight-box" style="background-color: #FFEBEE; border-left: 5px solid #F44336;">
                <h4>自己理解度が低下しています</h4>
                <p>自己理解度が{abs(change)}%低下しています。新たな環境や状況の変化により、一時的に混乱を感じているのかもしれません。
                焦らず、基本に立ち返って自己認識を深める活動を続けましょう。</p>
            </div>
            """, unsafe_allow_html=True)
        elif change < 0:
            st.markdown(f"""
            <div class="insight-box" style="background-color: #FFF9C4; border-left: 5px solid #FFC107;">
                <h4>自己理解度がやや低下しています</h4>
                <p>自己理解度が{abs(change)}%低下しています。成長の過程では、一時的に混乱や不確かさを感じることもあります。
                継続的な振り返りと記録を続けましょう。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="insight-box">
                <h4>自己理解度は安定しています</h4>
                <p>自己理解度に大きな変化はありません。安定した自己認識を維持できています。
                新たな視点や気づきを得るために、異なる自己認識活動も試してみると良いでしょう。</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 総合的な進歩の振り返り
    st.markdown("### 総合的な成長の振り返り")
    
    progress_areas = []
    
    # 感情ログの記録数
    if not emotion_logs_df.empty:
        progress_areas.append(f"感情ログを{len(emotion_logs_df)}件記録しました")
    
    # 思考パターンの認識
    total_patterns = sum(p["count"] for p in thought_patterns["patterns"])
    if total_patterns > 0:
        progress_areas.append(f"{total_patterns}回の思考パターンを認識し記録しました")
    
    # 強みとスキルの認識
    strengths_data = load_strengths()
    total_strengths = len(strengths_data["strengths"])
    total_skills = len(strengths_data["skills"])
    if total_strengths > 0 or total_skills > 0:
        progress_areas.append(f"{total_strengths}個の強みと{total_skills}個のスキルを特定しました")
    
    # 価値観の優先順位付け
    values_data = load_values()
    if values_data["values"]:
        progress_areas.append("価値観の優先順位を明確にしました")
    
    # 未来ビジョンの設定
    if future_vision.get("vision"):
        progress_areas.append("1年後の未来ビジョンを設定しました")
    
    # 目標の設定
    total_goals = len(future_vision.get("goals", []))
    if total_goals > 0:
        progress_areas.append(f"{total_goals}個の具体的な目標を設定しました")
    
    if progress_areas:
        st.markdown("#### これまでの成果")
        
        for area in progress_areas:
            st.markdown(f"✅ {area}")
        
        st.markdown(f"""
        <div class="insight-box">
            <h4>自己認識の旅を続けましょう</h4>
            <p>これらの活動を通じて、あなたはすでに自己認識を高める大切な一歩を踏み出しています。
            この旅に「正解」や「到達点」はありません。自分自身への理解を深め、より自分らしく生きることが目的です。</p>
            <p>定期的に振り返り、記録を続けることで、さらに自己認識を高めていきましょう。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("まだ記録が少ないようです。各ページで積極的に記録を追加していくことで、自己認識が深まっていきます。") 

        # 選択したページを表示
if page == "感情ログ":
    show_emotion_log()
elif page == "思考パターン分析":
    show_thought_pattern_analysis()
elif page == "得意なことリスト":
    show_strengths_list()
elif page == "価値観診断":
    show_values_diagnosis()
elif page == "未来ビジョン":
    show_future_vision()
elif page == "自己認識の進歩":
    show_self_awareness_progress()