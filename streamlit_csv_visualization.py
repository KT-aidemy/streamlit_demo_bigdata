# streamlit_csv_visualization.py
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# キャッシュを利用して CSV 読み込みを高速化
@st.cache_data

def load_data(file_path):
    """
    CSV ファイルを読み込み、DataFrame を返します。
    大規模ファイルにも対応できるようキャッシュします。
    """
    return pd.read_csv(file_path)

st.title("CSV ファイルの読み込みと可視化ツール")
uploaded_file = st.file_uploader("CSV ファイルをアップロードしてください", type=["csv"])

if uploaded_file is not None:
    with st.spinner("CSV を読み込んでいます..."):
        df = load_data(uploaded_file)
    
    st.subheader("データプレビューと統計情報")
    st.write(f"総行数: {len(df)}, 総列数: {len(df.columns)}")
    st.dataframe(df.head(100))
    st.write(df.describe())

    # 数値カラムリスト
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.warning("数値カラムが存在しないため、可視化できません。")
    else:
        # 相関行列の描画
        if st.checkbox("相関行列を表示する"):
            st.subheader("相関行列ヒートマップ")
            # 大きすぎる場合はサブセットを選択
            if len(numeric_cols) > 50:
                st.info("表示する列が多いため、表示するカラムを選択してください。")
                selected = st.multiselect("表示する数値カラムを選択", numeric_cols, default=numeric_cols[:20])
            else:
                selected = numeric_cols

            corr = df[selected].corr()
            fig = px.imshow(
                corr,
                labels=dict(x="カラム", y="カラム", color="相関係数"),
                x=selected,
                y=selected,
                text_auto=True,
                aspect="auto"
            )
            st.plotly_chart(fig, use_container_width=True)

        # 散布図の描画
        if len(numeric_cols) >= 2:
            st.subheader("散布図（Altair）")
            x_axis = st.selectbox("X 軸を選択", numeric_cols)
            y_axis = st.selectbox("Y 軸を選択", numeric_cols, index=1)

            chart = alt.Chart(df).mark_circle(size=60).encode(
                x=x_axis,
                y=y_axis,
                tooltip=numeric_cols
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("散布図には数値カラムが2つ以上必要です。")

    # パフォーマンスへの注意喚起
    if len(df) > 500000:
        st.warning("非常に大きなデータセットです。可視化や操作のパフォーマンスに注意してください。")
