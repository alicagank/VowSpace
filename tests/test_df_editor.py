# test_df_editor.py

import pandas as pd
import pytest

from components.df_editor import DFEditor


class DummyVisualizer:
    def __init__(self):
        self.called = False

    def update_scatterplot(self):
        self.called = True


@pytest.fixture
def df_editor(qtbot):
    df = pd.DataFrame({
        "vowel": ["i", "a"],
        "f1": [300.0, 700.0],
        "speaker": ["s1", "s2"]
    })

    visualizer = DummyVisualizer()
    widget = DFEditor(df, visualizer=visualizer)
    qtbot.addWidget(widget)

    return widget, df, visualizer


def test_table_creation(df_editor):
    widget, df, _ = df_editor

    table = widget.table_widget

    assert table.rowCount() == len(df)
    assert table.columnCount() == len(df.columns)
    assert table.horizontalHeaderItem(0).text() == "vowel"


def test_save_changes_updates_dataframe(df_editor):
    widget, df, visualizer = df_editor

    # editing a cell
    widget.table_widget.item(0, 1).setText("500")

    widget.save_changes()

    assert df.iloc[0, 1] == 500.0
    assert visualizer.called is True


def test_save_changes_handles_text(df_editor):
    widget, df, _ = df_editor

    widget.table_widget.item(0, 0).setText("u")

    widget.save_changes()

    assert df.iloc[0, 0] == "u"