"""Reproduce the OLS relation in Banerji et al. (2025), supplement Figure S9.

Input columns: time (UTC), maap637 (Mm^-1), ae660 (Mm^-1).
The distributed paired inputs precede the historical screening below.
Use --project to reconstruct those pairs from the original instrument exports.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_original(project):
    years, sources = [], []
    for year in range(2018, 2023):
        instruments = []
        for instrument, channel, target in [('ae33', 'Ba5_A81', 'ae660'), ('maap', 'XR_A21', 'maap637')]:
            source = project/'abs'/instrument/f'smr_{year}0101.csv'
            data = pd.read_csv(source, header=1, usecols=['DateTimeUTC', channel], low_memory=False)
            data = pd.DataFrame({'time': pd.to_datetime(data.DateTimeUTC, format='%Y-%m-%d %H:%M:%S', errors='coerce'),
                                 target: pd.to_numeric(data[channel], errors='coerce')})
            if instrument == 'maap':
                data['maap637'] *= 6.6
                data = data.dropna(subset=['maap637'])
            data = data.loc[data.time.between('2018-01-24 15:36:00', '2022-12-31 23:59:00')]
            if data.time.duplicated().any():
                raise ValueError('Duplicate timestamps in original source')
            instruments.append(data)
            sources.append(dict(source=f'abs/{instrument}/{source.name}', sha256=sha256(source)))
        years.append(instruments[0].merge(instruments[1], on='time', how='inner', validate='one_to_one'))
    return pd.concat(years, ignore_index=True).sort_values('time').reset_index(drop=True), sources


def select_hourly(data):
    if data.time.duplicated().any() or not data.time.is_monotonic_increasing:
        raise ValueError('Expected unique chronological UTC pairs')
    stages = [dict(stage='paired_before_screening', rows=len(data))]
    # Preserve the author's historical selection, including removal of the minimum.
    data = data.drop(index=data.ae660.idxmin()).copy()
    stages.append(dict(stage='remove_single_minimum_ae', rows=len(data)))
    for channel in ['maap637', 'ae660']:
        group = data[channel].ne(data[channel].shift()).cumsum()
        data = data.loc[group.map(group.value_counts()).lt(10)].copy()
        stages.append(dict(stage='remove_equal_runs_ge_10_'+channel, rows=len(data)))
    keep = (data.ae660 >= .05) & (data.maap637 >= .05)
    keep &= (data.ae660 < 10*data.maap637) & (data.maap637 < 10*data.ae660)
    data = data.loc[keep].set_index('time')
    stages.append(dict(stage='both_ge_005_and_strict_two_sided_ratio_lt_10', rows=len(data)))
    # This matches the data actually passed to the historical S9 plotting call.
    hourly = data[['maap637', 'ae660']].resample('h', offset='30min').median().dropna()
    stages.append(dict(stage='hourly_medians_offset_30min', rows=len(hourly)))
    return hourly, stages


def fit_and_plot(hourly, output):
    x, y = hourly.maap637.to_numpy(), hourly.ae660.to_numpy()
    model = linregress(x, y)
    independent = np.linalg.lstsq(np.column_stack([x, np.ones(len(x))]), y, rcond=None)[0]
    if not np.allclose(independent, [model.slope, model.intercept], rtol=1e-11, atol=1e-11):
        raise AssertionError('Independent OLS estimates disagree')
    fit = dict(method='ordinary least squares with a freely fitted intercept', n=len(x),
               x='MAAP absorption at 637 nm (Mm^-1)', y='AE33 absorption at 660 nm (Mm^-1)',
               slope=float(model.slope), intercept=float(model.intercept), r_squared=float(model.rvalue**2),
               independent_numpy_ols=True,
               published_rounded_match=(f'{model.slope:.2f}' == '2.33' and f'{model.intercept:.2f}' == '0.16'
                                        and f'{model.rvalue**2:.2f}' == '0.96'))
    fig, ax = plt.subplots(figsize=(12, 6), layout='constrained')
    ax.scatter(x, y, s=48, edgecolors='cornflowerblue', facecolors='none', linewidths=1.4, rasterized=True)
    line = np.array([x.min(), x.max()])
    ax.plot(line, model.slope*line+model.intercept, color='red', linewidth=2.4)
    ax.set_xlabel(r'$\sigma_{\mathrm{abs},637}$ from the MAAP (Mm$^{-1}$)', fontsize=15)
    ax.set_ylabel(r'$\sigma_{\mathrm{abs},660}$ from the AE33 (Mm$^{-1}$)', fontsize=15)
    ax.text(.05, .86, f'AE33 = {model.slope:.2f} · MAAP + {model.intercept:.2f}', transform=ax.transAxes, fontsize=17)
    ax.text(.05, .75, rf'$\mathrm{{R}}^2$ = {model.rvalue**2:.2f}', transform=ax.transAxes, fontsize=17)
    ax.grid(True, color='gray', linewidth=1.2, linestyle='--')
    ax.tick_params(axis='both', direction='out', length=7, width=1.2, labelsize=13)
    for spine in ax.spines.values():
        spine.set_color('black'); spine.set_linewidth(1.2)
    fig.savefig(output/'Figure_S9_reproduced.png', dpi=300)
    fig.savefig(output/'Figure_S9_reproduced.pdf', dpi=300)
    plt.close(fig)
    return fit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--paired-source', type=Path)
    source.add_argument('--project', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.project:
        paired, sources = read_original(args.project)
    else:
        paired = pd.read_csv(args.paired_source, parse_dates=['time'], float_precision='round_trip')
        sources = [dict(source=args.paired_source.name, sha256=sha256(args.paired_source))]
    hourly, stages = select_hourly(paired)
    hourly.to_csv(args.output/'hourly_median_pairs.csv', float_format='%.17g')
    report = dict(reference='https://acp.copernicus.org/articles/25/16895/2025/acp-25-16895-2025-supplement.pdf',
                  figure='S9', sources=sources, stages=stages, fit=fit_and_plot(hourly, args.output),
                  inverse_used='(AE33 - 0.16) / 2.33', constants='published rounded constants retained',
                  historical_note='The final mean-named plotting block reuses the preceding hourly-median x_clean/y_clean.',
                  sign_note='Figure S9 displays a positive intercept; the article prose prints a negative sign.',
                  interpretation='Replicates the historical fit; does not establish a new absolute or wavelength-specific calibration.')
    (args.output/'OLS_REPLICATION.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if not report['fit']['published_rounded_match']:
        raise AssertionError('The published Figure S9 relation was not reproduced')
    print(json.dumps(report['fit'], indent=2))


if __name__ == '__main__':
    main()
