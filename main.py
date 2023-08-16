from typing import Callable
import streamlit as st
import pandas as pd
import numpy as np, scipy as sp
import plotly.express as px
import plotly.graph_objects as go

class App:
    __numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    def __check_category(df: pd.DataFrame, xy: tuple[str], func: Callable[[pd.DataFrame, tuple[str]], go.Figure]) -> go.Figure | None:
        if all(map(lambda x: df.dtypes[x] in App.__numerics, xy)):
            return func(df, xy)
        else:
            st.error("Column type must be numeric, check out INFO section")
            return None

    plot_functions: dict[int: dict[str: Callable[[pd.DataFrame, tuple[str]], go.Figure | None]]] = {
            # Default 
            0: {
                "Corr Heatmap":     lambda df, xy: App.__check_category(df, xy, 
                                        lambda a, b: px.imshow (a[list(b)].corr())),
            },
            2: {
                "Violin plot x2":   lambda df, xy: px.violin    (df, x=xy[0], y=xy[1]),
                "Box plot x2":      lambda df, xy: px.box       (df, x=xy[0], y=xy[1]),
                "Scatter plot":     lambda df, xy: px.scatter   (df, x=xy[0], y=xy[1]),
            },
        }

    def __init__(self) -> None:
        self.dataframe:     pd.DataFrame    = None
        self.column_type:   pd.Series       = None
        

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
        if self.column_type is None: return
        info = self.column_type.copy().to_frame()
        info["Cat/Num"] = info[0].map(lambda x: "Number" if x in App.__numerics else "Category")
        info = info.rename(columns={0: "Type"})
        st.write(info)
        del info

    def choose_columns(self, dimension: int) -> tuple[str]:
        if self.column_type is None: return
        return tuple(st.selectbox(f"Column {i + 1}", self.column_type.index) for i in range(dimension))

    def plot(self) -> None:
        st.header("Plot")
        if self.column_type is None: return
        dimension = st.number_input("Set dimension", min_value=1)
        cols = self.choose_columns(dimension)
        if cols is not None:
            type_of_plot = st.selectbox("Type of plot", 
                                        (list(App.plot_functions[dimension].keys()) if dimension in App.plot_functions else []) + 
                                        list(App.plot_functions[0].keys()))
            draw_plot = st.button("Plot!")
            if draw_plot:
                if dimension in App.plot_functions and type_of_plot in App.plot_functions[dimension]:
                    fig = App.plot_functions[dimension][type_of_plot](self.dataframe, cols)
                else:
                    fig = App.plot_functions[0][type_of_plot](self.dataframe, cols)
                if fig is not None: st.plotly_chart(fig)

    def main(self) -> None:
        st.title("Промежуточная аттестация")
        self.upload_dataframe()
        self.show_info()
        if self.dataframe is not None:
            check_show_plot = st.checkbox("Plot")
            if check_show_plot: self.plot()

if __name__ == "__main__":
    app = App()
    app.main()