import os
import tempfile
import unittest

from plotly.subplots import make_subplots

from tests.cli_mode_test import CLIModeTest
# Standard plotly imports
import plotly.graph_objects as go
import numpy as np
import plotly.express as px


class TestPlotly(CLIModeTest):

    def test_create_scatter(self):
        fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
        if self.ide_mode():
            fid, target_html = tempfile.mkstemp(".html")
            os.close(fid)
            fig.write_html(target_html, auto_open=True)

    def test_plotly(self):
        # Create figure
        fig = go.Figure()

        # Add traces, one for each slider step
        for step in np.arange(0, 5, 0.1):
            fig.add_trace(
                go.Scatter(
                    visible=False,
                    line=dict(color="#00CED1", width=6),
                    name="𝜈 = " + str(step),
                    x=np.arange(0, 10, 0.01),
                    y=np.sin(step * np.arange(0, 10, 0.01))))

        # Make 10th trace visible
        fig.data[10].visible = True

        # Create and add slider
        steps = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                      {"title": "Slider switched to step: " + str(i)}],  # layout attribute
            )
            step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [dict(
            active=10,
            currentvalue={"prefix": "Frequency: "},
            pad={"t": 50},
            steps=steps
        )]

        fig.update_layout(
            sliders=sliders
        )

        if self.ide_mode():
            fid, target_html = tempfile.mkstemp(".html")
            os.close(fid)
            fig.write_html(target_html, auto_open=True)

    def test_subplots(self):
        fig = make_subplots(rows=1, cols=2)

        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[4, 5, 6]),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=[20, 30, 40], y=[50, 60, 70]),
            row=1, col=2
        )

        fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")

        if self.ide_mode():
            fid, target_html = tempfile.mkstemp(".html")
            os.close(fid)
            fig.write_html(target_html, auto_open=True)


if __name__ == '__main__':
    unittest.main()
