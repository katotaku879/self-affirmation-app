import json
import pandas as pd
from datetime import datetime

# データファイルのパス
EMOTION_LOGS_FILE = "emotion_logs.json"

def load_emotion_logs():
    """感情ログデータを読み込む"""
    try:
        with open(EMOTION_LOGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {EMOTION_LOGS_FILE}")
        return []

def filter_by_date(data, start_date_str):
    """指定日以降のデータをフィルタリング"""
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    if 'date' not in df.columns:
        print("データに日付情報がありません")
        return pd.DataFrame()
    
    # 日付をdatetime型に変換
    df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date_str)
    
    # フィルタリング
    filtered_df = df[df['date'] >= start_date]
    
    return filtered_df

def export_to_csv(df, output_file):
    """DataFrameをCSVファイルにエクスポート"""
    if df.empty:
        print("エクスポートするデータがありません")
        return
    
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nデータを {output_file} に出力しました")
    print(f"合計 {len(df)} 件のデータ")

def show_summary(df, start_date_str):
    """データの概要を表示"""
    if df.empty:
        print("\n指定期間のデータがありません")
        return
    
    print("\n" + "="*50)
    print(f"📊 感情ログデータの概要 ({start_date_str}以降)")
    print("="*50)
    
    print(f"\n総件数: {len(df)}件")
    
    if 'date' in df.columns:
        print(f"期間: {df['date'].min().strftime('%Y-%m-%d')} 〜 {df['date'].max().strftime('%Y-%m-%d')}")
    
    if 'emotion' in df.columns:
        print("\n感情の種類別集計:")
        emotion_counts = df['emotion'].value_counts()
        for emotion, count in emotion_counts.items():
            print(f"  {emotion}: {count}件")

def main():
    print("🌟 期間指定 感情ログデータ取得ツール")
    print("="*50)
    
    # 開始日を設定（2025/10/10から）
    start_date = "2025-10-10"
    
    print(f"\n取得期間: {start_date} 以降")
    
    # データを読み込む
    emotion_data = load_emotion_logs()
    
    if not emotion_data:
        return
    
    # 期間でフィルタリング
    filtered_df = filter_by_date(emotion_data, start_date)
    
    if filtered_df.empty:
        print(f"\n{start_date} 以降のデータが見つかりませんでした")
        return
    
    # 概要を表示
    show_summary(filtered_df, start_date)
    
    # CSVに出力
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"emotion_logs_from20251010_{timestamp}.csv"
    export_to_csv(filtered_df, output_file)
    
    print(f"\n✅ ファイルの場所:")
    print(f"   C:\\Users\\mkykr\\Pythonプログラム\\自己肯定アプリ\\streamlit_app.py\\{output_file}")
    
    # エクスプローラーで開く
    import os
    os.system('explorer "C:\\Users\\mkykr\\Pythonプログラム\\自己肯定アプリ\\streamlit_app.py"')

if __name__ == "__main__":
    main()