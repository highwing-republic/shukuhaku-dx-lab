import streamlit as st
import pandas as pd
import requests
import numpy as np
import google.generativeai as genai
import plotly.express as px

# --- 初期設定 ---
st.set_page_config(page_title="インバウンド宿泊者分析ダッシュボード", layout="wide")

# ▼▼▼ カスタムCSS（フォントと背景色の変更） ▼▼▼
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=BIZ+UDPGothic&display=swap');

/* 全体のフォントをBIZ UDPゴシックに変更 */
html, body, [class*="css"] {
    font-family: 'BIZ UDPGothic', sans-serif !important;
}

/* アプリの背景色を薄いベージュに変更 */
.stApp {
    background-color: #F8F5EE;
}

/* 白背景のウィジェット類（表や入力欄など）が背景と同化しないよう調整 */
div[data-testid="stExpander"] div[role="button"] p {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
# ▲▲▲ カスタムCSS ここまで ▲▲▲

# APIキーの設定
APP_ID = st.secrets["ESTAT_APP_ID"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

BASE_URL = "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# --- データ取得・整形関数 ---
@st.cache_data
def get_inbound_data(app_id):
    params = {
        "appId": app_id,
        "statsDataId": "0003425244",
        "metaGetFlg": "Y",
        "cntGetFlg": "N"
    }
    
    try:
        if app_id == "あなたの_appId_をここに入力してください":
            raise ValueError("ID未設定")
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        raise NotImplementedError("商談用デモデータへフォールバック")
        
    except Exception as e:
        years = [f"202{i}年" for i in range(2, 7)]
        prefs = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        nations = ["台湾", "米国", "韓国", "オーストラリア", "中国", "その他"]
        
        records = []
        for year in years:
            for pref in prefs:
                for nation in nations:
                    if pref in ["東京都", "大阪府", "京都府", "北海道", "沖縄県", "福岡県"]:
                        base = np.random.randint(50000, 300000)
                    else:
                        base = np.random.randint(1000, 50000)
                        
                    if nation in ["台湾", "米国", "オーストラリア"] and year >= "2024年":
                        base = int(base * 1.8)
                    
                    records.append({
                        "年": year,
                        "都道府県": pref,
                        "国籍": nation,
                        "宿泊者数": base
                    })
        return pd.DataFrame(records)

# --- UI構築（ダッシュボード画面） ---

st.link_button(
    "← 誠コンサルティング公式サイトへ戻る",
    "https://lab.ugatta-llc.com/",
)
st.title("🌍 都道府県別 インバウンド（国籍別）宿泊者分析")
st.caption("データソース: e-Stat 宿泊旅行統計調査（※デモモード稼働中）")

with st.spinner("データを読み込み中..."):
    df = get_inbound_data(APP_ID)

st.markdown("---")
st.subheader("🔍 お客様の施設があるエリアを選択してください")

selected_pref = st.selectbox("都道府県", df["都道府県"].unique())
st.markdown("---")

df_pref = df[df["都道府県"] == selected_pref]
df_pivot = df_pref.pivot_table(index="年", columns="国籍", values="宿泊者数", aggfunc="sum")

st.header(f"📊 {selected_pref} の外国人宿泊者数の推移（国籍別）")
chart_data = df_pivot.reset_index().melt(
    id_vars="年",
    var_name="国籍",
    value_name="宿泊者数",
)

inbound_fig = px.bar(
    chart_data,
    x="年",
    y="宿泊者数",
    color="国籍",
    barmode="group",
    color_discrete_sequence=["#0068C9", "#E45756", "#2A9D8F", "#F4A261", "#7B61FF", "#6C757D"],
)
inbound_fig.update_traces(
    hovertemplate="%{x}<br>%{fullData.name}: %{y:,.0f}人<extra></extra>",
)
inbound_fig.update_layout(
    template="plotly_white",
    height=520,
    margin=dict(l=20, r=20, t=20, b=20),
    hovermode="x unified",
    font=dict(family="BIZ UDPGothic, sans-serif"),
    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(title=None, showgrid=False),
    yaxis=dict(title="外国人宿泊者数（人）", tickformat=",", gridcolor="#E9ECEF"),
)
st.plotly_chart(inbound_fig, use_container_width=True, config={"displaylogo": False})

with st.expander("詳細なクロス集計表を見る"):
    st.dataframe(df_pivot.style.format("{:,} 人"))

st.divider()

# --- ▼▼▼ Gemini APIによる分析・営業提案セクション ▼▼▼ ---
st.header("💡 AI コンサルタントによる提案")
st.markdown("集計されたデータに基づき、最適なアプローチをAIが瞬時に分析・作成します。")

# ボタンの行 (if st.button...) を削除し、直接実行するように変更しました

if GEMINI_API_KEY == "あなたの_Gemini_API_KEY_をここに入力してください":
    st.error("Gemini APIキーが設定されていません。コード上部の `GEMINI_API_KEY` を書き換えてください。")
else:
    with st.spinner("Geminiがデータを分析し、提案を作成しています..."):
        try:
            # 1. APIキーのセットアップ
            genai.configure(api_key=GEMINI_API_KEY)
            
            # 2. モデルを最新の「gemini-2.5-flash」に指定
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 3. AIに渡すためのデータとプロンプトを作成
            data_csv = df_pivot.to_csv()
            prompt = f"""
            あなたは「宿泊DXラボ」というWeb制作・DX支援会社の優秀なコンサルタントです。
            以下のデータは、{selected_pref}における国籍別の外国人宿泊者数の推移データ（CSV）です。
            
            {data_csv}
            
            このデータを分析し、このエリアにある旅館の経営者に向けて、以下の構成で営業提案を書いてください。
            ・文字数：400文字程度
            ・トーン：プロフェッショナルで説得力があり、経営者が「なるほど」と納得する熱量のある文章
            
            【構成】
            1. データの分析結果からの鋭い洞察（一番伸びている客層、またはポテンシャルのある客層に言及）
            2. 現状のWebサイト（日本語のみ）のまま放置することへの警鐘（機会損失）
            3. 宿泊DXラボが提供する解決策（特定国向けの専用LP制作、多言語サイトのリニューアル、自社予約エンジンの導入やPMSの刷新などDX全般）
            """
            
            # 4. Gemini APIを呼び出してテキストを生成
            response = model.generate_content(prompt)
            
            # 5. 生成されたテキストを取り出し、画面に表示
            st.success("Gemini 2.5 Flashによる分析が完了しました。")
            st.info(response.text)
            
        except Exception as e:
            st.error(f"AI提案の生成中にエラーが発生しました: {e}")
# ----------------------------------------------------
st.markdown("---")

# st.button から st.link_button に変更し、URLを指定します
st.link_button(
    "🚀 宿泊DXラボへのお問い合わせこちら",
    "https://forms.gle/9Ae3mSqKB2Vnztks7",
    use_container_width=True,
    type="primary"
)