import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="客室稼働率の長期推移",
    page_icon="🏨",
    layout="wide",
)

st.link_button(
    "← 誠コンサルティング公式サイトへ戻る",
    "https://lab.ugatta-llc.com/",
)

st.title("🏨 客室稼働率の長期推移")
st.caption("データソース：観光庁 宿泊旅行統計調査")

# 例示データ。実装時はe-Stat APIの取得結果へ置き換えます。
df = pd.DataFrame({
    "年": list(range(2015, 2026)),
    "客室稼働率": [60.5, 61.2, 62.8, 64.1, 62.7, 34.6, 37.2, 46.5, 57.4, 60.3, 62.1],
})

fig = px.line(
    df,
    x="年",
    y="客室稼働率",
    markers=True,
)

fig.update_traces(
    line=dict(color="#0068C9", width=4),
    marker=dict(size=8),
    hovertemplate="%{x}年<br>客室稼働率: %{y:.1f}%<extra></extra>",
)

fig.add_vrect(
    x0=2020,
    x1=2022,
    fillcolor="#E45756",
    opacity=0.1,
    line_width=0,
    annotation_text="コロナ期間",
)

fig.update_layout(
    template="plotly_white",
    height=520,
    hovermode="x unified",
    xaxis_title=None,
    yaxis_title="客室稼働率（%）",
)

fig.update_yaxes(range=[0, 100])

st.plotly_chart(fig, width="stretch")