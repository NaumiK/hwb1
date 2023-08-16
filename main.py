from typing import Callable
import streamlit as st
import pandas as pd
import numpy as np, scipy as sp
import plotly.express as px

class App:
    __numerics = ["int16", "int32", "int64", "float16", "float32", "float64"]
    plot_functions: list[dict[str: Callable[[pd.DataFrame, tuple[str]],None]]] = [
            dict(),
            {
                "Violin plot x2":   lambda df, xy: px.violin    (df, x=xy[0], y=xy[1]),
                "Box plot x2":      lambda df, xy: px.box       (df, x=xy[0], y=xy[1]),
                "Scatter plot":     lambda df, xy: px.scatter   (df, x=xy[0], y=xy[1])
            },
            dict()
        ]

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
        dimension = st.number_input("Set dimension", 1, 3)
        cols = self.choose_columns(dimension)
        if cols is not None:
            type_of_plot = st.selectbox("Type of plot", App.plot_functions[dimension - 1].keys())
            draw_plot = st.button("Plot!")
            if draw_plot:
                fig = App.plot_functions[dimension - 1][type_of_plot](self.dataframe, cols)
                st.plotly_chart(fig)

    def main(self) -> None:
        st.title("Промежуточная аттестация")
        self.upload_dataframe()
        if self.dataframe is not None:
            check_show_info = st.checkbox("Info")
            if check_show_info: self.show_info()
            check_show_plot = st.checkbox("Plot")
            if check_show_plot: self.plot()


if __name__ == "__main__":
    app = App()
    app.main()