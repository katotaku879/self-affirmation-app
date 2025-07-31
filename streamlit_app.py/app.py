import warnings
warnings.filterwarnings("ignore")
import streamlit as st

st.set_page_config(
    page_title="自己肯定アプリ",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# メインページ streamlit run app.py
st.markdown("# 🌱 自己肯定アプリ")
st.markdown("""
自己肯定感を高めるためのアプリケーションです。サイドバーから機能を選択してください。

## 主な機能
1. **成長の可視化** - 自分の成長を記録し、視覚的に確認できます
2. **ポジティブな習慣の定着** - 良い習慣を継続しやすくする仕組みを提供します
3. **自己認識の向上**      
4. **目標達成サポート**
5. ** モチベーション管理**
6. **自己分析**
7. **AIサポート**                                                     

左側のサイドバーから各機能にアクセスしてください。
""")