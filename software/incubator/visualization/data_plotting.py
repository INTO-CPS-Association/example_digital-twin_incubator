import os
import tempfile

import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go


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


def plotly_incubator_data(data, compare_to=None, heater_T_data=None, events=None,
                          overlay_heater=True, show_actuators=False, show_sensor_temperatures=False,
                          show_hr_time=False):
    nRows = 2
    titles = ["Incubator Temperature (°C)", "Room Temperature (°C)"]
    if show_actuators:
        nRows += 1
        titles.append("Actuators")
    if heater_T_data is not None:
        nRows += 1
        titles.append("Heatbed Temperature (°C)")

    x_title = "Timestamp" if show_hr_time else "Time (s)"

    time_field = "timestamp_ns" if show_hr_time else "time"

    fig = make_subplots(rows=nRows, cols=1, shared_xaxes=True,
                        x_title=x_title,
                        subplot_titles=titles)

    assert not show_sensor_temperatures
    if show_sensor_temperatures:
        fig.add_trace(go.Scatter(x=data[time_field], y=data["t1"], name="t1"), row=1, col=1)
        fig.add_trace(go.Scatter(x=data[time_field], y=data["t2"], name="t2"), row=1, col=1)

    fig.add_trace(go.Scatter(x=data[time_field], y=data["average_temperature"], name="avg_T"), row=1, col=1)
    if overlay_heater:
        fig.add_trace(go.Scatter(x=data[time_field], y=[40 if b else 30 for b in data["heater_on"]], name="heater_on"), row=1, col=1)

    if events is not None:
        for i, r in events.iterrows():
            # Get the closest timestamp_ns to the event time
            closest_ts = min(data[time_field], key=lambda x:abs(x-r[time_field]))
            # Get the average temperature for that timestamp_ns
            avg_temp = data.iloc[data.index[data[time_field] == closest_ts]]["average_temperature"].iloc[0]

            fig.add_annotation(x=r[time_field], y=avg_temp,
                               text=r["event"],
                               showarrow=True,
                               arrowhead=1)

    if compare_to is not None:
        for res in compare_to:
            if "T" in compare_to[res]:
                fig.add_trace(go.Scatter(x=compare_to[res][time_field], y=compare_to[res]["T"], name=f"avg_temp({res})"), row=1, col=1)
            if "T_object" in compare_to[res]:
                fig.add_trace(go.Scatter(x=compare_to[res][time_field], y=compare_to[res]["T_object"], name=f"T_object({res})"), row=1, col=1)

    fig.add_trace(go.Scatter(x=data[time_field], y=data["T_room"], name="room"), row=2, col=1)

    next_row = 3

    if show_actuators:
        fig.add_trace(go.Scatter(x=data[time_field], y=data["heater_on"], name="heater_on"), row=next_row, col=1)
        fig.add_trace(go.Scatter(x=data[time_field], y=data["fan_on"], name="fan_on"), row=next_row, col=1)

        if compare_to is not None:
            for res in compare_to:
                if "in_lid_open" in compare_to[res]:
                    fig.add_trace(go.Scatter(x=compare_to[res][time_field], y=compare_to[res]["in_lid_open"], name=f"in_lid_open({res})"), row=next_row, col=1)

        next_row += 1

    if heater_T_data is not None:
        for trace in heater_T_data:
            fig.add_trace(go.Scatter(x=heater_T_data[trace][time_field], y=heater_T_data[trace]["T_heater"],
                                     name=f"T_heater({trace})"), row=next_row, col=1)
        next_row += 1

    fig.update_layout()

    return fig


def show_plotly(fig):
    fid, target_html = tempfile.mkstemp(".html")
    os.close(fid)
    fig.write_html(target_html, auto_open=True)
