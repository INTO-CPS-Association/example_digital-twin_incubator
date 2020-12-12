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


def plotly_incubator_data(data):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Incubator Temperature",
                                        "Room Temperature",
                                        "Actuators"))

    fig.add_trace(go.Scatter(x=data["time"], y=data["t2"], name="t2"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data["time"], y=data["t3"], name="t3"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data["time"], y=data["average_temperature"], name="average_temperature"), row=1, col=1)

    fig.add_trace(go.Scatter(x=data["time"], y=data["t1"], name="room"), row=2, col=1)

    fig.add_trace(go.Scatter(x=data["time"], y=data["heater_on"], name="heater_on"), row=3, col=1)
    fig.add_trace(go.Scatter(x=data["time"], y=data["fan_on"], name="fan_on"), row=3, col=1)

    return fig


def show_plotly(fig):
    fid, target_html = tempfile.mkstemp(".html")
    os.close(fid)
    fig.write_html(target_html, auto_open=True)
