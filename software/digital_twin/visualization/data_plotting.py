import os
import tempfile

import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px


def plot_incubator_data(data):
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)

    ax1.plot(data["time"], data["t1"], label="t1")
    ax1.plot(data["time"], data["t2"], label="t2")
    ax1.plot(data["time"], data["t3"], label="t3")
    ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
    ax1.legend()

    ax2.plot(data["time"], data["heater_on"], label="heater_on")
    ax2.plot(data["time"], data["fan_on"], label="fan_on")
    ax2.legend()

    ax3.plot(data["time"], data["execution_interval"], label="execution_interval")
    ax3.plot(data["time"], data["elapsed"], label="elapsed")
    ax3.legend()

    ax4.plot(data["time"], data["power_in"], label="power_in")
    ax4.legend()

    ax5.plot(data["time"], data["energy_in"], label="energy_in")
    ax5.plot(data["time"], data["potential_energy"], label="potential_energy")
    ax5.legend()


def plotly_incubator_data(data, compare_to=None, heater_T_data=None,
                          overlay_heater=True, show_actuators=False, show_sensor_temperatures=False):
    nRows = 2
    titles = ["Incubator Temperature", "Room Temperature"]
    if show_actuators:
        nRows += 1
        titles += "Actuators"
    if heater_T_data is not None:
        nRows += 1
        titles += "Heatbed Temperature"

    fig = make_subplots(rows=nRows, cols=1, shared_xaxes=True,
                        x_title="Time (s)",
                        subplot_titles=titles)

    if show_sensor_temperatures:
        fig.add_trace(go.Scatter(x=data["time"], y=data["t2"], name="t2 (right)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data["time"], y=data["t3"], name="t3 (top)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=data["time"], y=data["average_temperature"], name="avg_T"), row=1, col=1)
    if overlay_heater:
        fig.add_trace(go.Scatter(x=data["time"], y=[40 if b else 30 for b in data["heater_on"]], name="heater_on"), row=1, col=1)

    if compare_to is not None:
        for res in compare_to:
            if "T" in compare_to[res]:
                fig.add_trace(go.Scatter(x=compare_to[res]["time"], y=compare_to[res]["T"], name=f"avg_temp({res})"), row=1, col=1)

    fig.add_trace(go.Scatter(x=data["time"], y=data["t1"], name="room"), row=2, col=1)

    next_row = 3

    if show_actuators:
        fig.add_trace(go.Scatter(x=data["time"], y=data["heater_on"], name="heater_on"), row=next_row, col=1)
        fig.add_trace(go.Scatter(x=data["time"], y=data["fan_on"], name="fan_on"), row=next_row, col=1)
        next_row += 1

    if heater_T_data is not None:
        for trace in heater_T_data:
            fig.add_trace(go.Scatter(x=heater_T_data[trace]["time"], y=heater_T_data[trace]["T_heater"],
                                     name=f"T_heater({trace})"), row=next_row, col=1)
        next_row += 1

    fig.update_layout()

    return fig


def show_plotly(fig):
    fid, target_html = tempfile.mkstemp(".html")
    os.close(fid)
    fig.write_html(target_html, auto_open=True)
