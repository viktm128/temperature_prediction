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
        row_num = int(input.station_name())
        
        ts = df.loc[row_num,:]
        ts = ts.loc[max(5, ts.first_valid_index()):ts.last_valid_index()]
        
        dr = pd.date_range(start = '1/15/' + str(df.loc[row_num, 1]), periods=len(ts), freq='MS') + pd.DateOffset(days=14)
        ts.index = dr

        return (ts[ts != -9999] / 100).plot(
            title="Temperature at " + df.loc[row_num, 0],
            labels=dict(index="time", value="degrees")
        )


app = App(app_ui, server)