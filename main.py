from typing import Callable
import streamlit as st
import pandas as pd
import scipy as sp
import plotly.express as px
import plotly.graph_objects as go


class App:
    __numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    col_key = 0

    def __check_category(df: pd.DataFrame, xy: tuple[str],
                         func: Callable[[pd.DataFrame, tuple[str]], go.Figure]
                         ) -> go.Figure | None:

        if all(map(lambda x: df.dtypes[x] in App.__numerics, xy)):
            return func(df, xy)
        else:
            st.error("Column type must be numeric, check out INFO section")
            return None

    plot_functions: dict[int:
                         dict[str:
                              Callable[[pd.DataFrame, tuple[str]], go.Figure | None]]] = {
            # Default
            0: {
                "Corr Heatmap": lambda df, xy: App.__check_category(df,
                                                                    xy,
                                                                    lambda a, b: px.imshow(a[list(b)].corr())),
            },
            1: {
                "Box plot": lambda df, xy: px.box(df,
                                                  x=xy[0]),
                "Violin plot": lambda df, xy: px.violin(df,
                                                        x=xy[0]),
                "Histogram plot": lambda df, xy: px.histogram(df,
                                                              x=xy[0]),
                "Density histogram": lambda df, xy:
                px.histogram(df,
                             x=xy[0],
                             histnorm="probability density")
            },
            2: {
                "Violin plot x2": lambda df, xy: px.violin(df,
                                                           x=xy[0],
                                                           y=xy[1]),
                "Box plot x2": lambda df, xy: px.box(df,
                                                     x=xy[0],
                                                     y=xy[1]),
                "Scatter plot": lambda df, xy: px.scatter(df,
                                                          x=xy[0],
                                                          y=xy[1]),
                "Pie chart": lambda df, xy: px.pie(df,
                                                   values=xy[0],
                                                   names=xy[1]),
            },
            3: {
                "Scatter plot + color": lambda df, xy: px.scatter(df,
                                                                  x=xy[0],
                                                                  y=xy[1],
                                                                  color=xy[2]),
            },
        }

    def ttest(col1: pd.Series, col2: pd.Series) -> None:
        st.subheader("T-Test")
        st.write(r"Let $X_1, \dots, X_{n_1} \sim N(\mu_1, \sigma_1)$, $Y_1, \dots, Y_{n_2} \sim N(\mu_2, \sigma_2)$")
        st.write(r"$H_0 \colon \mathbb{E}X=\mathbb{E}Y$")
        alternatives = {
                r"𝔼X ≠ 𝔼Y": "two-sided", r"𝔼X > 𝔼Y": "greater", r"𝔼X < 𝔼Y": "less"
                }
        alternative_choice =\
            alternatives[st.selectbox(r"$H_1 \colon$", alternatives.keys())]
        st.write(r"$\alpha: 0.05$")
        confirm = st.button("Confirm", key="T-Test confirm")
        if confirm:
            try:
                _, p_value = sp.stats.ttest_ind(col1.dropna(), col2.dropna(),
                                                equal_var=False,
                                                alternative=alternative_choice)
                st.write(f"p-value: {p_value}")
                if p_value < 0.05:
                    st.write(r"Поскольку $\text{p-value} < 0,05$, мы отвергаем нулевую гипотезу ($H_0 \colon \mathbb{E}X=\mathbb{E}Y$).")
                else:
                    st.write(r"Поскольку $\text{p-value} > 0,05$, мы не отвергаем нулевую гипотезу ($H_0 \colon \mathbb{E}X=\mathbb{E}Y$).")

            except Exception as e:
                st.error(f"Wrong input data: {e}")

    def utest(col1: pd.Series, col2: pd.Series) -> None:
        st.write("U-Test")
        st.write(r"$H_0 \colon A=B$ ")
        alternatives = {
                r"A ≠ B": "two-sided",
                r"A > B": "greater",
                r"A < B": "less"
                        }

        alternative_choice = alternatives[st.selectbox(r"$H_1 \colon$",
                                                       alternatives.keys())]
        st.write(r"$\alpha: 0.05$")
        if st.button("Confirm", key="T-Test confirm"):
            try:
                _, p_value = sp.stats.mannwhitneyu(col1.dropna(),
                                                   col2.dropna(),
                                                   alternative=alternative_choice
                                                   )
                st.write(f"p-value: {p_value}")
                if p_value < 0.05:
                    st.write(r"Поскольку $\text{p-value} > 0,05$, мы отвергаем нулевую гипотезу ($A = B$).")
                else:
                    st.write(r"Поскольку $\text{p-value} < 0,05$, мы не отвергаем нулевую гипотезу ($A = B$).")

            except Exception as e:
                st.error(f"Wrong input data: {e}")

    test_functions: dict[str, Callable] = {
            "T-Test": ttest,
            "U-Test": utest,
        }

    def __init__(self) -> None:
        self.dataframe:     pd.DataFrame = None
        self.column_type:   pd.Series = None

    def upload_dataframe(self) -> None:
        upload_file = st.file_uploader("Choose a file")
        if upload_file is not None:
            try:
                self.dataframe = pd.read_csv(upload_file)
                self.column_type = self.dataframe.dtypes.copy()
            except Exception as e:
                st.error(str(e))
                self.dataframe = None

    def show_info(self) -> None:
        if self.column_type is None:
            return
        info = self.column_type.copy().to_frame()
        info["Cat/Num"] = info[0].map(lambda x: "Number" if x in App.__numerics else "Category")
        info = info.rename(columns={0: "Type"})
        st.write(info)
        del info

    def choose_columns(self, dimension: int) -> tuple[str]:
        if self.column_type is None:
            return
        return tuple(st.selectbox(
            f"Column {i + 1}",
            self.column_type.index,
            key=str(i + dimension * App.col_key)) for i in range(dimension))

    def choose_selection(self, dimension: int) -> tuple[(str, str)]:
        if self.column_type is None:
            return
        App.col_key += 1
        return tuple((st.text_input(f"Query {i + 1}"), st.selectbox(f"Column {i + 1}", self.column_type.index, key=str(i + dimension * App.col_key))) for i in range(dimension))

    def plot(self) -> None:
        st.header("Plot")
        if self.column_type is None:
            return
        query = st.text_input("Query")
        dimension = st.number_input("Set dimension", min_value=1)
        cols = self.choose_columns(dimension)
        if cols is not None:
            type_of_plot = st.selectbox("Type of plot",
                                        (list(App.plot_functions[dimension].keys())
                                         if dimension in App.plot_functions else []) +
                                        list(App.plot_functions[0].keys()))
            draw_plot = st.button("Plot!")
            accepted_query_df = App.query_df(self.dataframe, query)
            if draw_plot:
                if dimension in App.plot_functions and type_of_plot in App.plot_functions[dimension]:
                    fig = App.plot_functions[dimension][type_of_plot](accepted_query_df, cols)
                else:
                    fig = App.plot_functions[0][type_of_plot](accepted_query_df, cols)
                if fig is not None:
                    st.plotly_chart(fig)

    def query_df(df: pd.DataFrame, query: str) -> pd.DataFrame | None:
        res = None
        try:
            res = df.query(query) if query else df
        except Exception as e:
            st.error(f"Wrong query, \n {e}")
        return res

    def query_column(self, query: str, column: str) -> pd.Series:
        return App.query_df(self.dataframe, query)[column]

    def a_b_test(self) -> None:
        if self.column_type is None:
            return
        st.header("A/B test")
        st.write("Составление 2-х выборок:")
        col1, col2 = self.choose_selection(2)
        type_of_test = st.selectbox("Type of test", App.test_functions.keys())
        if col1 is not None and col2 is not None:
            App.test_functions[type_of_test](self.query_column(*col1),
                                             self.query_column(*col2))

    def main(self) -> None:
        st.title("Промежуточная аттестация")
        self.upload_dataframe()
        if self.dataframe is not None:
            check_show_info = st.checkbox("Info")
            if check_show_info:
                self.show_info()
            check_show_plot = st.checkbox("Plot")
            if check_show_plot:
                self.plot()
            check_show_ab_t = st.checkbox("A/B test")
            if check_show_ab_t:
                self.a_b_test()


if __name__ == "__main__":
    app = App()
    app.main()
