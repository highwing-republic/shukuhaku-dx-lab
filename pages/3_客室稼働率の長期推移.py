"""宿泊DXラボ｜客室稼働率の長期推移ダッシュボード。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).resolve().parents[1] / "occupancy_history.csv"
SOURCE_PAGE = "https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html"
SOURCE_FILE = "https://www.mlit.go.jp/kankocho/content/002002831.xlsx"

SERIES_LABELS = {
    "全施設": "全施設（2011〜2025年）",
    "従業者10人以上": "長期比較・従業者10人以上（2009〜2025年）",
}

FACILITY_ORDER = [
    "全体",
    "旅館",
    "リゾートホテル",
    "ビジネスホテル",
    "シティホテル",
    "簡易宿所",
    "会社・団体の宿泊所",
]


st.set_page_config(
    page_title="宿泊DXラボ｜客室稼働率の長期推移",
    page_icon="🏨",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_history() -> pd.DataFrame:
    """同梱CSVを読み込み、必要な列と型を検証する。"""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"{DATA_FILE.name} がプロジェクト直下にありません。")

    data = pd.read_csv(DATA_FILE)
    required = {"系列", "年", "地域", "施設タイプ", "客室稼働率"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError("CSVに必要な列がありません: " + ", ".join(sorted(missing)))

    data["年"] = pd.to_numeric(data["年"], errors="coerce").astype("Int64")
    data["客室稼働率"] = pd.to_numeric(data["客室稼働率"], errors="coerce")
    return data.dropna(subset=["年", "客室稼働率"]).copy()


def format_pct(value: float | None) -> str:
    return "データなし" if value is None else f"{value:.1f}%"


def first_value(frame: pd.DataFrame) -> float | None:
    if frame.empty:
        return None
    return float(frame.iloc[0]["客室稼働率"])


def diagnosis(gap: float | None, change: float | None) -> str:
    if gap is None:
        return "全国比較に必要なデータがありません。別の年または施設タイプを選んでください。"

    if gap >= 5:
        comparison = "全国平均を大きく上回っています。好調の要因を販売チャネル・商品・価格帯に分け、再現できる形に整理する価値があります。"
    elif gap >= 2:
        comparison = "全国平均を上回っています。強い需要を直販比率や付帯売上の向上につなげられるか確認しましょう。"
    elif gap > -2:
        comparison = "全国平均とほぼ同水準です。稼働率だけでなく、ADRやRevPARと合わせて収益性を確認すると次の打ち手が見えます。"
    elif gap > -5:
        comparison = "全国平均をやや下回っています。需要不足と、自施設の在庫・価格・販売経路の問題を切り分けてみましょう。"
    else:
        comparison = "全国平均を大きく下回っています。地域需要の推移と自施設実績を重ね、販売開始時期や在庫開放を点検する余地があります。"

    if change is None:
        return comparison
    trend = (
        f"表示期間の最初の年からは{change:+.1f}ポイントです。"
        "単年の上下だけでなく、複数年の傾向として判断してください。"
    )
    return comparison + trend


st.link_button(
    "← 誠コンサルティング公式サイトへ戻る",
    "https://lab.ugatta-llc.com/",
)

st.title("🏨 都道府県・施設タイプ別 客室稼働率の長期推移")
st.caption("観光庁『宿泊旅行統計調査』推移表を、宿泊DXラボ向けに年次比較できる形へ整形")

try:
    history = load_history()
except Exception as exc:
    st.error("同梱データの読み込みに失敗しました。")
    st.code(str(exc))
    st.info("occupancy_history.csvをプロジェクト直下に置いてください。")
    st.stop()

with st.sidebar:
    st.header("操作パネル")
    series = st.selectbox(
        "集計対象",
        list(SERIES_LABELS),
        format_func=SERIES_LABELS.get,
    )

    series_data = history[history["系列"] == series].copy()
    prefectures = sorted(
        region for region in series_data["地域"].unique() if region != "全国"
    )
    default_prefecture = "長野県" if "長野県" in prefectures else prefectures[0]
    prefecture = st.selectbox(
        "都道府県",
        prefectures,
        index=prefectures.index(default_prefecture),
    )

    available_facilities = [
        facility
        for facility in FACILITY_ORDER
        if facility in series_data["施設タイプ"].unique()
    ]
    facility = st.selectbox("施設タイプ", available_facilities)

    filtered = series_data[series_data["施設タイプ"] == facility]
    available_years = sorted(int(year) for year in filtered["年"].unique())
    selected_year = st.select_slider(
        "比較する年",
        options=available_years,
        value=available_years[-1],
    )

    st.divider()
    compare_own = st.toggle("自施設の稼働率と比較")
    own_occupancy = None
    if compare_own:
        own_occupancy = st.number_input(
            f"自施設の{selected_year}年 客室稼働率（％）",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=0.1,
        )

selected_history = filtered[
    filtered["地域"].isin([prefecture, "全国"])
].copy()

pref_history = selected_history[selected_history["地域"] == prefecture].sort_values("年")
national_history = selected_history[selected_history["地域"] == "全国"].sort_values("年")

pref_year = first_value(pref_history[pref_history["年"] == selected_year])
national_year = first_value(national_history[national_history["年"] == selected_year])
gap = (
    pref_year - national_year
    if pref_year is not None and national_year is not None
    else None
)

first_pref = first_value(pref_history)
change = pref_year - first_pref if pref_year is not None and first_pref is not None else None
peak_row = (
    pref_history.loc[pref_history["客室稼働率"].idxmax()]
    if not pref_history.empty
    else None
)

metrics = st.columns(4)
metrics[0].metric(
    f"{selected_year}年・{prefecture}",
    format_pct(pref_year),
)
metrics[1].metric(
    f"{selected_year}年・全国",
    format_pct(national_year),
    delta=f"地域差 {gap:+.1f}pt" if gap is not None else None,
)
metrics[2].metric(
    "表示期間の最高値",
    (
        f"{peak_row['客室稼働率']:.1f}%"
        if peak_row is not None
        else "データなし"
    ),
    delta=(f"{int(peak_row['年'])}年" if peak_row is not None else None),
    delta_color="off",
)
metrics[3].metric(
    "最初の年からの変化",
    f"{change:+.1f}pt" if change is not None else "データなし",
    delta_color="off",
)

if compare_own and own_occupancy is not None and pref_year is not None:
    st.info(
        f"自施設は{selected_year}年の{prefecture}・{facility}平均に対して "
        f"**{own_occupancy - pref_year:+.1f}ポイント**です。"
    )

st.subheader(f"{facility}の客室稼働率推移")
chart = (
    selected_history.pivot(index="年", columns="地域", values="客室稼働率")
    .sort_index()
    .rename_axis("年")
)
chart_columns = [column for column in [prefecture, "全国"] if column in chart.columns]
st.line_chart(chart[chart_columns], height=390)

st.subheader("読み取りコメント")
st.success(diagnosis(gap, change))

left, right = st.columns([1, 1])

with left:
    st.subheader(f"{selected_year}年の施設タイプ比較")
    type_comparison = series_data[
        (series_data["年"] == selected_year)
        & (series_data["地域"].isin([prefecture, "全国"]))
        & (series_data["施設タイプ"] != "全体")
    ].pivot(index="施設タイプ", columns="地域", values="客室稼働率")
    ordered_index = [name for name in FACILITY_ORDER if name in type_comparison.index]
    type_comparison = type_comparison.reindex(ordered_index)
    comparison_columns = [
        column for column in [prefecture, "全国"] if column in type_comparison.columns
    ]
    st.bar_chart(type_comparison[comparison_columns], horizontal=True, height=430)

with right:
    st.subheader(f"{selected_year}年・{facility}の全国順位")
    ranking = series_data[
        (series_data["年"] == selected_year)
        & (series_data["施設タイプ"] == facility)
        & (series_data["地域"] != "全国")
    ][["地域", "客室稼働率"]].sort_values("客室稼働率", ascending=False)
    ranking.insert(0, "順位", range(1, len(ranking) + 1))
    ranking["選択"] = ranking["地域"].eq(prefecture).map({True: "◀", False: ""})
    st.dataframe(
        ranking,
        hide_index=True,
        width="stretch",
        height=430,
        column_config={
            "客室稼働率": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

with st.expander("年次データを見る・CSVをダウンロード"):
    display_history = selected_history.pivot(
        index="年", columns="地域", values="客室稼働率"
    ).sort_index(ascending=False)
    st.dataframe(
        display_history,
        width="stretch",
        column_config={
            column: st.column_config.NumberColumn(format="%.1f%%")
            for column in display_history.columns
        },
    )
    st.download_button(
        "選択中の推移をCSVで保存",
        selected_history.sort_values(["年", "地域"]).to_csv(
            index=False, encoding="utf-8-sig"
        ),
        file_name=f"客室稼働率_{series}_{prefecture}_{facility}.csv",
        mime="text/csv",
    )

st.divider()
st.markdown(
    f"""
**データについて**

- 全施設の年次比較は2011〜2025年です。
- 従業者10人以上の長期系列は、公式表の客室稼働率に数値がある2009〜2025年を収録しています（2007・2008年は空欄）。
- 簡易宿所など、調査年によって値がない施設タイプはグラフが途中から始まります。
- 2026年から調査の層化基準が「従業者数」から「客室数」に変わったため、2025年以前と単純連結せず別系列として扱うのが安全です。

[観光庁「宿泊旅行統計調査」公式ページ]({SOURCE_PAGE})  ｜  [公式推移表Excel]({SOURCE_FILE})
"""
)
