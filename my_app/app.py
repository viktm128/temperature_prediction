from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import os

df = pd.read_csv("temperatures.csv", names=list(range(4000)))
pd.options.plotting.backend = "plotly"

app_ui = ui.page_fluid(
    ui.panel_title("Vikram Mathew's Personal Projects"),
    ui.navset_tab_card(
        ui.nav("Prediction Models and Global Temperatures",
            ui.input_selectize("station_name", "Station Name", df.loc[:, 0]),
            output_widget("time_series_plot")
        ),
        ui.nav("Next Project",

        )

    )
)

def server(input, output, session):
    @output
    @render_widget
    def time_series_plot():
        row_num = int(input.station_name())
        
        ts = df.loc[row_num, 6:]
        title="Temperature at " + df.loc[row_num, 1]
        ts = ts.loc[:ts.last_valid_index()]

        #x = np.array(ts[ts != -9999].index)
        #y = np.array(ts[ts != -9999] / 100, dtype='float64')
        #A = np.vstack([x, np.ones(len(x))]).T
        #m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        
        dr = pd.date_range(start = '1/15/' + str(df.loc[row_num, 2]), periods=len(ts), freq='MS') + pd.DateOffset(days=14)
        ts.index = dr
        ts = ts[ts != -9999] / 100

        fig = ts.plot(
            kind='scatter',
            title=title,
            color_discrete_sequence=['blue'],
            trendline='ols',
            trendline_color_override="black",
            labels=dict(index="time", value="degrees", variable="ID")
        )
        fig.update_layout(showlegend=False)


        return fig

app = App(app_ui, server)