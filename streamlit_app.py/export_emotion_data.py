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
    except json.JSONDecodeError:
        print("JSONファイルの読み込みに失敗しました")
        return []

def export_to_csv(data, output_file="emotion_logs_export.csv"):
    """感情ログをCSVファイルにエクスポート"""
    if not data:
        print("データがありません")
        return
    
    # DataFrameに変換
    df = pd.DataFrame(data)
    
    # CSVに出力
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"データを {output_file} に出力しました")
    print(f"合計 {len(df)} 件のデータ")

def show_summary(data):
    """データの概要を表示"""
    if not data:
        print("データがありません")
        return
    
    df = pd.DataFrame(data)
    
    print("\n" + "="*50)
    print("📊 感情ログデータの概要")
    print("="*50)
    
    print(f"\n総件数: {len(df)}件")
    
    # 日付範囲
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        print(f"期間: {df['date'].min()} 〜 {df['date'].max()}")
    
    # 感情の種類別集計
    if 'emotion' in df.columns:
        print("\n感情の種類別集計:")
        emotion_counts = df['emotion'].value_counts()
        for emotion, count in emotion_counts.items():
            print(f"  {emotion}: {count}件")
    
    # 最近のデータを表示
    print("\n最新の感情ログ（上位5件）:")
    print(df.head().to_string())

def export_to_excel(data, output_file="emotion_logs_export.xlsx"):
    """感情ログをExcelファイルにエクスポート"""
    if not data:
        print("データがありません")
        return
    
    df = pd.DataFrame(data)
    
    # Excelに出力
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"データを {output_file} に出力しました")

def main():
    """メイン処理"""
    print("🌟 感情ログデータ取得ツール")
    print("="*50)
    
    # データを読み込む
    emotion_data = load_emotion_logs()
    
    if not emotion_data:
        return
    
    # 概要を表示
    show_summary(emotion_data)
    
    # メニュー表示
    print("\n" + "="*50)
    print("データのエクスポート")
    print("="*50)
    print("1. CSVファイルに出力")
    print("2. Excelファイルに出力")
    print("3. JSON形式で保存（元データのコピー）")
    print("4. 終了")
    
    choice = input("\n選択してください (1-4): ")
    
    if choice == "1":
        output_name = input("出力ファイル名（拡張子なし、Enter で既定値）: ").strip()
        if not output_name:
            output_name = f"emotion_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        export_to_csv(emotion_data, f"{output_name}.csv")
    
    elif choice == "2":
        output_name = input("出力ファイル名（拡張子なし、Enter で既定値）: ").strip()
        if not output_name:
            output_name = f"emotion_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        export_to_excel(emotion_data, f"{output_name}.xlsx")
    
    elif choice == "3":
        output_name = input("出力ファイル名（拡張子なし、Enter で既定値）: ").strip()
        if not output_name:
            output_name = f"emotion_logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(f"{output_name}.json", 'w', encoding='utf-8') as f:
            json.dump(emotion_data, f, ensure_ascii=False, indent=2)
        print(f"データを {output_name}.json に出力しました")
    
    elif choice == "4":
        print("終了します")
    
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()