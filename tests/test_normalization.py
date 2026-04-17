# test_normalization.py
# Ensures that the normalization calculations are working as expected

import numpy as np
import pandas as pd

from vowspace.core.normalization import (
    lobanov_normalization,
    bark_difference,
    nearey1,
    nearey2,
    bark_transform,
    log_transform,
    mel_transform,
    erb_transform,
)


def make_test_df():
    return pd.DataFrame({
        "speaker": ["s1", "s1", "s2", "s2"],
        "vowel": ["i", "a", "i", "a"],
        "f1": [300.0, 700.0, 320.0, 680.0],
        "f2": [2200.0, 1200.0, 2100.0, 1250.0],
        "f3": [3000.0, 2500.0, 2950.0, 2550.0],
    })


def test_lobanov_adds_zscore_columns():
    df = make_test_df()
    result = lobanov_normalization(df.copy(), ["f1", "f2"])

    assert "zsc_f1" in result.columns
    assert "zsc_f2" in result.columns
    assert len(result) == len(df)
    assert result["zsc_f1"].notna().all()
    assert result["zsc_f2"].notna().all()


def test_lobanov_groupwise_mean_is_zero():
    df = make_test_df()
    result = lobanov_normalization(df.copy(), ["f1"], group_column="speaker")

    grouped_means = result.groupby("speaker")["zsc_f1"].mean()
    assert np.allclose(grouped_means.values, 0.0, atol=1e-7)


def test_bark_difference_adds_expected_columns():
    df = make_test_df()
    result = bark_difference(df.copy())

    expected = [
        "bark_f1", "bark_f2", "bark_f3",
        "Z3_minus_Z1", "Z3_minus_Z2", "Z2_minus_Z1"
    ]
    for col in expected:
        assert col in result.columns

    assert len(result) == len(df)
    assert np.isfinite(result["Z3_minus_Z1"]).all()


def test_nearey1_adds_expected_columns():
    df = make_test_df()
    result = nearey1(df.copy(), ["f1", "f2"])

    assert "logmean_f1" in result.columns
    assert "logmean_f2" in result.columns
    assert len(result) == len(df)
    assert result["logmean_f1"].notna().all()
    assert result["logmean_f2"].notna().all()


def test_nearey2_adds_expected_columns():
    df = make_test_df()
    result = nearey2(df.copy(), ["f1", "f2"])

    assert "slogmean_f1" in result.columns
    assert "slogmean_f2" in result.columns
    assert len(result) == len(df)
    assert result["slogmean_f1"].notna().all()
    assert result["slogmean_f2"].notna().all()


def test_bark_transform_adds_columns():
    df = make_test_df()
    result = bark_transform(df.copy(), ["f1", "f2"])

    assert "bark_f1" in result.columns
    assert "bark_f2" in result.columns
    assert np.isfinite(result["bark_f1"]).all()
    assert np.isfinite(result["bark_f2"]).all()


def test_log_transform_adds_columns():
    df = make_test_df()
    result = log_transform(df.copy(), ["f1", "f2"])

    assert "log_f1" in result.columns
    assert "log_f2" in result.columns
    assert np.allclose(result["log_f1"], np.log10(df["f1"]))
    assert np.allclose(result["log_f2"], np.log10(df["f2"]))


def test_mel_transform_adds_columns():
    df = make_test_df()
    result = mel_transform(df.copy(), ["f1", "f2"])

    assert "mel_f1" in result.columns
    assert "mel_f2" in result.columns
    assert np.isfinite(result["mel_f1"]).all()
    assert np.isfinite(result["mel_f2"]).all()


def test_erb_transform_adds_columns():
    df = make_test_df()
    result = erb_transform(df.copy(), ["f1", "f2"])

    assert "erb_f1" in result.columns
    assert "erb_f2" in result.columns
    assert np.isfinite(result["erb_f1"]).all()
    assert np.isfinite(result["erb_f2"]).all()
