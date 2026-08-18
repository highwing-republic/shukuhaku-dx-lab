import streamlit as st

st.set_page_config(
    page_title="宿泊DXラボ",
    page_icon="🏨",
    layout="wide",
)

st.link_button(
    "← 誠コンサルティング公式サイトへ戻る",
    "https://lab.ugatta-llc.com/",
)
st.title("🏨 宿泊DXラボ")
st.write("宿泊施設の経営課題をデータで可視化するダッシュボードです。")

st.info("分析したいメニューを選択してください。")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 人手不足シミュレーション")
    st.write("人手不足による機会損失と、DX導入による改善効果を確認できます。")
    st.page_link(
        "pages/1_人手不足シミュレーション.py",
        label="シミュレーションを開く",
        icon="📊",
    )

with col2:
    st.subheader("🌍 インバウンド分析")
    st.write("都道府県・国籍別の外国人宿泊者数を分析できます。")
    st.page_link(
        "pages/2_インバウンド分析.py",
        label="インバウンド分析を開く",
        icon="🌍",
    )

with col3:
    st.subheader("📈 客室稼働率の長期推移")
    st.write("客室稼働率の長期的な推移を可視化できます。")
    st.page_link(
        "pages/3_客室稼働率の長期推移.py",
        label="長期推移を表示",
        icon="📈",
    )


st.divider()

st.link_button(
    "🚀 宿泊DXラボへのお問い合わせはこちら",
    "https://forms.gle/9Ae3mSqKB2Vnztks7",
    width="stretch",
    type="primary",
)