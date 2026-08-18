import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 初期設定 ---
st.set_page_config(page_title="旅館DX提案ダッシュボード", layout="wide")

st.link_button(
    "← 誠コンサルティング公式サイトへ戻る",
    "https://lab.ugatta-llc.com/",
)
st.title("📊 宿泊業 人手不足・機会損失 可視化ダッシュボード")
st.caption("提供：宿泊DXラボ（※デモデータによるシミュレーション）")

# --- データ生成（商談のストーリーに合わせたリアルな推移） ---
# 2019年〜2026年の「稼働率」と「従業員数（指数）」のギャップを作る
years = [f"20{i}年" for i in range(19, 27)]
data = {
    "年": years,
    "客室稼働率(%)": [75, 35, 40, 55, 78, 85, 88, 90], # コロナ禍で落ち込み、現在は急回復
    "従業員数(2019=100)": [100, 80, 75, 70, 68, 65, 63, 62] # 離職が進み、戻ってこない
}
df = pd.DataFrame(data).set_index("年")

# --- UI構築：セクション1 現状の課題 ---
st.header("1. 需要回復と人手不足の「ギャップ」")
st.markdown("現在、インバウンド需要の増加により稼働率はコロナ前を超えていますが、**従業員数は減少し続けており、現場の負担が限界**に達しています。")

# 2つのグラフを横に並べて表示
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 客室稼働率の推移 (需要)")
    occupancy_fig = go.Figure(
        go.Scatter(
            x=df.index,
            y=df["客室稼働率(%)"],
            mode="lines+markers",
            line=dict(color="#E45756", width=4),
            marker=dict(size=8, color="#FFFFFF", line=dict(color="#E45756", width=3)),
            hovertemplate="%{x}<br>客室稼働率: %{y}%<extra></extra>",
        )
    )
    occupancy_fig.update_layout(
        template="plotly_white", height=380, margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False, hovermode="x unified",
        font=dict(family="BIZ UDPGothic, sans-serif"),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title="稼働率（%）", range=[0, 100], gridcolor="#E9ECEF"),
    )
    st.plotly_chart(occupancy_fig, use_container_width=True, config={"displaylogo": False})

with col2:
    st.subheader("📉 従業員数の推移 (供給)")
    staff_fig = go.Figure(
        go.Scatter(
            x=df.index,
            y=df["従業員数(2019=100)"],
            mode="lines+markers",
            line=dict(color="#0068C9", width=4),
            marker=dict(size=8, color="#FFFFFF", line=dict(color="#0068C9", width=3)),
            hovertemplate="%{x}<br>従業員数指数: %{y}<extra></extra>",
        )
    )
    staff_fig.update_layout(
        template="plotly_white", height=380, margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False, hovermode="x unified",
        font=dict(family="BIZ UDPGothic, sans-serif"),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title="従業員数指数（2019年=100）", range=[0, 110], gridcolor="#E9ECEF"),
    )
    st.plotly_chart(staff_fig, use_container_width=True, config={"displaylogo": False})

st.error("⚠️ 結論：マンパワー（人力）での対応はすでに限界を超えており、機会損失が発生しています。")
st.divider()

# --- UI構築：セクション2 課題解決シミュレーション ---
st.header("2. DX（IT化）による利益改善シミュレーション")
st.markdown("宿泊DXラボが提供するシステムを導入し、業務の一部を自動化した場合の効果を計算します。")

# インタラクティブなスライダー
col3, col4 = st.columns([1, 2])

with col3:
    st.subheader("現状の入力")
    rooms = st.number_input("総客室数", min_value=10, max_value=300, value=30, step=10)
    adr = st.number_input("平均客室単価 (円)", min_value=5000, max_value=100000, value=25000, step=1000)
    
    st.markdown("---")
    st.subheader("システム導入効果")
    # スライダーで自動化の割合を動かせる
    automation_rate = st.slider("Web予約・自動化による業務削減率 (%)", min_value=5, max_value=50, value=20, step=5)

with col4:
    # 削減できた時間・コストの計算（※営業用の簡易シミュレーション）
    saved_hours_per_day = (rooms * 0.5) * (automation_rate / 100) # 1部屋あたり30分の業務と仮定
    saved_cost_per_month = saved_hours_per_day * 30 * 1500 # 時給1500円換算
    
    st.success(f"### ✨ 毎月 約 {int(saved_cost_per_month):,} 円 の人件費相当を削減可能")
    
    st.markdown("""
    #### 💡 浮いた時間とコストで実現できること
    *   **OTA手数料の削減:** 自社サイトからの直接予約システムを強化し、じゃらん・楽天への手数料（約10%）を削減。
    *   **顧客満足度の向上:** フロント業務を自動化し、スタッフは「おもてなし（接客）」に集中。
    """)
    
    # 提案内容（本業への誘導）
    st.info("""
    **🔧 宿泊DXラボからのご提案プラン**
    1. **爆速・多言語対応公式サイトリニューアル**（Next.js活用）
    2. **自社予約エンジンの組み込み**（直販比率UP）
    3. **AIチャットボット導入**（電話問い合わせを50%削減）
    """)

# --- 最後のCTA ---
st.markdown("---")
st.link_button(
    "🚀 宿泊DXラボへのお問い合わせこちら",
    "https://forms.gle/9Ae3mSqKB2Vnztks7",
    use_container_width=True,
    type="primary"
)
