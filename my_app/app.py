from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import os

df = pd.read_csv("temperatures.csv", names=list(range(4000)))
pd.options.plotting.backend = "plotly"

app_ui = ui.page_fluid(
    ui.input_selectize("station_name", "Station Name", df.loc[:, 0]),
    #ui.output_plot("time_series_plot")
    output_widget("time_series_plot")

)

def server(input, output, session):
    @output
    @render_widget
    def time_series_plot():
        year = df.loc[0, 1]
        dr = pd.date_range(start = '1/1/1961', end='12/1/2013', freq='MS')
        ts = df.loc[0, 5:640]
        ts.index = dr

        return (ts[ts != -9999] / 100).plot()



app = App(app_ui, server)