from shiny import App, ui, render
from shinywidgets import output_widget, render_widget
from pmdarima import auto_arima
import pandas as pd
import numpy as np
import os

df = pd.read_csv("temperatures.csv", nrows=5, names=list(range(4000)))
pd.options.plotting.backend = "plotly"

app_ui = ui.page_fluid(
    ui.panel_title("Vikram Mathew's Personal Projects"),
    ui.navset_tab_card(
        ui.nav("Prediction Models and Global Temperatures",
            ui.input_selectize("station_name", "Station Name", df.loc[:, 0]),
            ui.input_selectize("years", "# of Years for predictions", list(range(1, 11))),
            output_widget("time_series_plot"),
            output_widget("predictions")
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
        
        dr = pd.date_range(start = '1/15/' + str(df.loc[row_num, 2]), periods=len(ts), freq='MS') + pd.DateOffset(days=14)
        ts.index = dr
        ts = ts[ts != -9999] / 100

        fig = ts.plot(
            title=title,
            color_discrete_sequence=['blue'],
            labels=dict(index="time", value="degrees", variable="ID")
        )
        fig.update_layout(showlegend=False)


        return fig


    @output
    @render_widget
    def validate_arima():
        row_num = int(input.station_name())
        
        ts = df.loc[row_num, 6:]
        ts = ts.loc[:ts.last_valid_index()]
        
        dr = pd.date_range(start = '1/15/' + str(df.loc[row_num, 2]), periods=len(ts), freq='MS') + pd.DateOffset(days=14)
        ts.index = dr
        ts = ts[ts != -9999] / 100
        ts = pd.to_numeric(ts)

        model = auto_arima(ts)
        train = ts.loc[:'2010-12-15']
        test = ts.loc['2011-01-15':]

        model.fit(train)
        fc = model.predict(n_periods = len(test))

        fc = pd.DataFrame(fc, columns=['Predictions'])
        fc.index = test.index
        ndf = pd.concat([test, fc], axis=1)
        ndf.rename({0: 'Data'}, axis = 1, inplace = True)

        return ndf.plot()


    @output
    @render_widget
    def predictions():
        row_num = int(input.station_name())
        
        ts = df.loc[row_num, 6:]
        ts = ts.loc[:ts.last_valid_index()]
        
        dr = pd.date_range(start = '1/15/' + str(df.loc[row_num, 2]), periods=len(ts), freq='MS') + pd.DateOffset(days=14)
        ts.index = dr
        ts = ts[ts != -9999] / 100
        ts = pd.to_numeric(ts)

        arima = auto_arima(ts)
        arima.fit(ts)

        n_periods = 12 * int(input.years())
        arima_pred = arima.predict(n_periods = n_periods)
        lin_pred = linear_regression_predictions(ts, n_periods)
        print(lin_pred)

        pred_dr = pd.date_range(start = dr[-1] + pd.DateOffset(month=1), periods = n_periods, freq='MS') + pd.DateOffset(days=14)
        arima_pred.index = pred_dr
        lin_pred.index = pred_dr
        ndf = pd.concat([arima_pred, lin_pred], axis = 1)

        return ndf.plot()


def linear_regression_predictions(ts, n_periods):
    n = len(ts)
    x = np.array(range(n), dtype='float64')
    y = np.array(ts, dtype='float64')

    m_x = np.mean(x)
    m_y = np.mean(y)

    SS_xy = np.sum(y * x) - n * m_x * m_y
    SS_xx = np.sum(x * x) - n * m_x * m_x

    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1 * m_x

    pred_x = np.array(range(n, n + n_periods))
    return pd.Series(b_0 + b_1 * pred_x)


app = App(app_ui, server)