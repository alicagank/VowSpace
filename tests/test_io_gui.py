# test_io_gui.py
# Ensures that the IO functions work as expected under different circumstances

import pandas as pd
import pytest

from vowspace.vowel_space_visualizer import VowelSpaceVisualizer


class DummyDFEditor:
    def __init__(self, data, visualizer=None):
        self.data = data
        self.visualizer = visualizer

    def show(self):
        pass


@pytest.fixture
def visualizer(qtbot, monkeypatch):
    # no popup during tests
    monkeypatch.setattr("vowspace.vowel_space_visualizer.DFEditor", DummyDFEditor)
    monkeypatch.setattr("vowspace.vowel_space_visualizer.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("vowspace.vowel_space_visualizer.QMessageBox.critical", lambda *args, **kwargs: None)

    widget = VowelSpaceVisualizer()
    qtbot.addWidget(widget)
    return widget


def test_save_data_csv(visualizer, monkeypatch, tmp_path):
    visualizer.data = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": [300.0, 700.0],
        "f2": [2200.0, 1200.0],
        "speaker": ["s1", "s2"],
        "empty_col": [None, None],
    })

    out_file = tmp_path / "output.csv"

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(out_file), "CSV Files (*.csv)")
    )

    visualizer.save_data()

    assert out_file.exists()

    reloaded = pd.read_csv(out_file)
    assert "vowel" in reloaded.columns
    assert "f1" in reloaded.columns
    assert "f2" in reloaded.columns
    assert "speaker" in reloaded.columns
    assert "empty_col" not in reloaded.columns
    assert len(reloaded) == 2


def test_save_data_excel(visualizer, monkeypatch, tmp_path):
    visualizer.data = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": [300.0, 700.0],
        "f2": [2200.0, 1200.0],
        "speaker": ["s1", "s2"],
    })

    out_file = tmp_path / "output.xlsx"

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(out_file), "Excel Files (*.xlsx)")
    )

    visualizer.save_data()

    assert out_file.exists()

    reloaded = pd.read_excel(out_file)
    assert list(reloaded.columns) == ["vowel", "f1", "f2", "speaker"]
    assert len(reloaded) == 2
    assert reloaded.loc[0, "vowel"] == "i"


def test_import_data_csv(visualizer, monkeypatch, tmp_path):
    in_file = tmp_path / "input.csv"

    df = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": ["300", "700"],
        "f2": ["2200", "1200"],
        "speaker": ["s1", "s2"],
    })
    df.to_csv(in_file, index=False)

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(in_file), "CSV Files (*.csv)")
    )

    visualizer.import_data()

    assert len(visualizer.data) == 2
    assert pd.to_numeric(visualizer.data["f1"], errors="coerce").notna().all()
    assert pd.to_numeric(visualizer.data["f2"], errors="coerce").notna().all()
    assert list(visualizer.data["vowel"]) == ["i", "a"]


def test_import_data_excel(visualizer, monkeypatch, tmp_path):
    in_file = tmp_path / "input.xlsx"

    df = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": ["300", "700"],
        "f2": ["2200", "1200"],
        "speaker": ["s1", "s2"],
    })
    df.to_excel(in_file, index=False)

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(in_file), "Excel Files (*.xlsx)")
    )

    visualizer.import_data()

    assert len(visualizer.data) == 2
    assert pd.to_numeric(visualizer.data["f1"], errors="coerce").notna().all()
    assert pd.to_numeric(visualizer.data["f2"], errors="coerce").notna().all()


def test_import_creates_speaker_column_if_missing(visualizer, monkeypatch, tmp_path):
    in_file = tmp_path / "missing_speaker.csv"

    df = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": [300, 700],
        "f2": [2200, 1200],
    })
    df.to_csv(in_file, index=False)

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(in_file), "CSV Files (*.csv)")
    )

    visualizer.import_data()

    assert "speaker" in visualizer.data.columns


def test_import_drops_invalid_rows(visualizer, monkeypatch, tmp_path):
    in_file = tmp_path / "bad_rows.csv"

    df = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": ["300", "bad"],
        "f2": ["2200", "1200"],
        "speaker": ["s1", "s2"],
    })
    df.to_csv(in_file, index=False)

    monkeypatch.setattr(
        "vowspace.vowel_space_visualizer.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(in_file), "CSV Files (*.csv)")
    )

    visualizer.import_data()

    assert len(visualizer.data) == 1
    assert visualizer.data.iloc[0]["vowel"] == "i"