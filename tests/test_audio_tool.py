# test_audio_tool.py

import pytest

from vowspace.components.audio_tool import AudioAnalysisTool


class DummyPitch:
    def __init__(self):
        self.selected_array = {"frequency": [100.0, 110.0, 120.0]}

    def xs(self):
        return [0.0, 0.1, 0.2]


class DummyIntensity:
    def __init__(self):
        self.values = [[60.0, 62.0, 64.0]]

    def xs(self):
        return [0.0, 0.1, 0.2]


class DummyFormants:
    def xs(self):
        return [0.0, 0.1, 0.2]

    def get_value_at_time(self, formant_number, t):
        values = {
            1: 500.0,
            2: 1500.0,
            3: 2500.0,
            4: 3500.0,
        }
        return values[formant_number]


class DummySpectrogram:
    ymin = 0
    ymax = 5000

    def x_grid(self):
        return [0.0, 0.1, 0.2]

    def y_grid(self):
        return [0, 1000, 2000]

    @property
    def values(self):
        return [
            [1.0, 2.0, 3.0],
            [2.0, 3.0, 4.0],
            [3.0, 4.0, 5.0],
        ]


class DummySound:
    def __init__(self, file_name):
        self.file_name = file_name
        self.sampling_frequency = 44100
        self.xmin = 0.0
        self.xmax = 0.2
        self.values = [[0.1], [0.2], [0.3]]

    def to_pitch(self):
        return DummyPitch()

    def to_intensity(self):
        return DummyIntensity()

    def to_formant_burg(self):
        return DummyFormants()

    def to_spectrogram(self):
        return DummySpectrogram()

    def xs(self):
        return [0.0, 0.1, 0.2]


class DummyVisualizer:
    def __init__(self):
        self.called = False
        self.args = None

    def update_input_fields_audio(self, f1, f2, f3, f4, audio_title):
        self.called = True
        self.args = (f1, f2, f3, f4, audio_title)


class DummyEvent:
    def __init__(self, xdata=None, ydata=None, button=None, inaxes=True):
        self.xdata = xdata
        self.ydata = ydata
        self.button = button
        self.inaxes = inaxes


@pytest.fixture
def audio_tool(qtbot, monkeypatch):
    monkeypatch.setattr("vowspace.components.audio_tool.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("vowspace.components.audio_tool.QMessageBox.critical", lambda *args, **kwargs: None)
    monkeypatch.setattr("vowspace.components.audio_tool.Sound", DummySound)

    widget = AudioAnalysisTool()
    qtbot.addWidget(widget)
    return widget


def test_audio_tool_initializes(audio_tool):
    assert audio_tool.show_pitch is False
    assert audio_tool.show_intensity is False
    assert audio_tool.pitch is None
    assert audio_tool.intensity is None
    assert audio_tool.formants is None


def test_read_audio_file_sets_analysis_objects(audio_tool, monkeypatch):
    monkeypatch.setattr(
        "vowspace.components.audio_tool.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: ("/tmp/test.wav", "Audio Files (*.wav)")
    )

    audio_tool.read_audio_file()

    assert audio_tool.audio_file == "/tmp/test.wav"
    assert audio_tool.pitch is not None
    assert audio_tool.intensity is not None
    assert audio_tool.formants is not None
    assert "test.wav" in audio_tool.audio_title_label.text()
    assert "44100" in audio_tool.sampling_rate_label.text()


def test_toggle_pitch_changes_state(audio_tool, monkeypatch):
    monkeypatch.setattr(audio_tool, "redraw_plots", lambda: None)

    assert audio_tool.show_pitch is False
    audio_tool.toggle_pitch()
    assert audio_tool.show_pitch is True
    audio_tool.toggle_pitch()
    assert audio_tool.show_pitch is False


def test_toggle_intensity_changes_state(audio_tool, monkeypatch):
    monkeypatch.setattr(audio_tool, "redraw_plots", lambda: None)

    assert audio_tool.show_intensity is False
    audio_tool.toggle_intensity()
    assert audio_tool.show_intensity is True
    audio_tool.toggle_intensity()
    assert audio_tool.show_intensity is False


def test_handle_click_updates_visualizer(monkeypatch, qtbot):
    monkeypatch.setattr("vowspace.components.audio_tool.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("vowspace.components.audio_tool.QMessageBox.critical", lambda *args, **kwargs: None)

    visualizer = DummyVisualizer()
    widget = AudioAnalysisTool(visualizer=visualizer)
    qtbot.addWidget(widget)

    widget.audio_file = "/tmp/example.wav"
    widget.formants = DummyFormants()

    event = DummyEvent(xdata=0.1, button=3, inaxes=True)
    widget.handle_click(event)

    assert visualizer.called is True
    assert visualizer.args == (500.0, 1500.0, 2500.0, 3500.0, "example")


def test_save_graph_calls_figure_savefig(audio_tool, monkeypatch, tmp_path):
    out_file = tmp_path / "graph.jpeg"

    monkeypatch.setattr(
        "vowspace.components.audio_tool.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(out_file), "JPEG files (*.jpeg)")
    )

    called = {"saved": False}

    def fake_savefig(path, format=None, dpi=None):
        called["saved"] = True
        with open(path, "wb") as f:
            f.write(b"fake image")

    monkeypatch.setattr(audio_tool.figure, "savefig", fake_savefig)

    audio_tool.save_graph()

    assert called["saved"] is True
    assert out_file.exists()