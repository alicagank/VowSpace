# core/normalization.py

import numpy as np
import pandas as pd

# Cite: Remirez, Emily. 2022, October 20. Vowel plotting in Python. Linguistics Methods Hub. (https://lingmethodshub.github.io/content/python/vowel-plotting-py). doi: 10.5281/zenodo.7232005

# Lobanov's method was one of the earlier vowel-extrinsic formulas to appear, but it remains among the best.
# Implementation: Following Nearey (1977) and Adank et al. (2004), NORM uses the formula (see the General Note below):
# Fn[V]N = (Fn[V] - MEANn)/Sn
def lobanov_normalization(df, formants, group_column='speaker'):
    def zscore(x):
        return (x - x.mean()) / x.std()

    for formant in formants:
        z_name = f"zsc_{formant}"
        if z_name not in df.columns:
            df[z_name] = df.groupby(group_column)[formant].transform(zscore)
    return df

def bark_difference(df):
    def bark(f):
        return 26.81 / (1 + 1960 / f) - 0.53

    for formant in ['f1', 'f2', 'f3']:
        name = f"bark_{formant}"
        if name not in df.columns:
            df[name] = bark(df[formant])

    df['Z3_minus_Z1'] = df['bark_f3'] - df['bark_f1']
    df['Z3_minus_Z2'] = df['bark_f3'] - df['bark_f2']
    df['Z2_minus_Z1'] = df['bark_f2'] - df['bark_f1']
    return df

# Cite: Remirez, Emily. 2022, October 20. Vowel plotting in Python. Linguistics Methods Hub. (https://lingmethodshub.github.io/content/python/vowel-plotting-py). doi: 10.5281/zenodo.7232005


# Cite: https://github.com/drammock/phonR/blob/master/R/phonR.R
def nearey1(df, formants, group_column='speaker'):
    def norm_logmean(f, group=None):
        if group is None:
            return np.log(f) - np.log(f.mean())
        grouped = f.groupby(group)
        result = pd.concat([(np.log(g) - np.log(g.mean())) for _, g in grouped])
        return result.sort_index()

    log_data = norm_logmean(df[formants], group=df[group_column])
    for f in formants:
        df[f"logmean_{f}"] = log_data[f]
    return df


def nearey2(df, formants, group_column='speaker'):
    def norm_shared_logmean(f, group=None):
        if group is None:
            return np.log(f) - np.mean(np.log(f), axis=0)
        grouped = f.groupby(group)
        result = grouped.apply(lambda x: np.log(x) - np.mean(np.log(x), axis=0)).reset_index(drop=True)
        return result

    norm_data = norm_shared_logmean(df[formants], group=df[group_column])
    for i, f in enumerate(formants):
        df[f"slogmean_{f}"] = norm_data.iloc[:, i]
    return df

# Bark Difference Metric - Zi = 26.81/(1+1960/Fi) - 0.53 (Traunmüller, 1997)
def bark_transform(df, formants):
    def bark(f): return 26.81 / (1 + 1960 / f) - 0.53

    for f in formants:
        name = f"bark_{f}"
        if name not in df.columns:
            df[name] = bark(df[f])
    return df

def log_transform(df, formants):
    for f in formants:
        df[f"log_{f}"] = np.log10(df[f])
    return df


def mel_transform(df, formants):
    for f in formants:
        df[f"mel_{f}"] = 2595 * np.log10(1 + df[f] / 700)
    return df


def erb_transform(df, formants):
    for f in formants:
        df[f"erb_{f}"] = 21.4 * np.log10(1 + 0.00437 * df[f])
    return df
