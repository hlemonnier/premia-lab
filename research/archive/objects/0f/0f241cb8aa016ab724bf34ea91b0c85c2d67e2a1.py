#!/usr/bin/env python3
"""Build shareable figures and an exact archive from completed frozen evidence.

This reports saved results and packages identical source bytes. It never imports
or runs a trading strategy, changes a selection, or reads raw market panels.
"""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import platform
import sys
import zipfile

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(path.read_text())


def ledger(path, start, stop):
    with path.open(newline='') as stream:
        rows = [r for r in csv.DictReader(stream) if start <= int(r['return_index']) < stop]
    assert [int(r['return_index']) for r in rows] == list(range(start, stop))
    values = np.array([float(r['net_return']) for r in rows])
    assert np.isfinite(values).all() and np.all(values > -1)
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = [
        'evidence/validation_C06_001/daily.csv', 'evidence/validation_C09_001/daily.csv',
        'evidence/audit_C09_001/daily.csv', 'evidence/validation_uncertainty_001/summary.json',
        'evidence/audit_uncertainty_001/summary.json', 'evidence/handoff_discovery_001/package_manifest.json',
        'research/VALIDATION_SELECTION.json', 'research/AUDIT_NOMINATION.json',
    ]
    source_hashes = {name: digest(root/name) for name in sources}
    validation = load(root/sources[3]); audit = load(root/sources[4])
    assert all(s['status'] == 'EXECUTED_PASS_SCOPE_ONLY' and s['exit_code'] == 0 for s in (validation, audit))
    assert validation['mode'] == 'validation' and audit['mode'] == 'audit'
    selection = load(root/'research/VALIDATION_SELECTION.json')
    package = load(root/'evidence/handoff_discovery_001/package_manifest.json')
    assert package['candidate_id'] == selection['selected_candidate_id'] == 'C09_additive_long_memory'
    assert package['selection_sha256'] == source_hashes['research/VALIDATION_SELECTION.json']
    actual = {str(p.relative_to(root/'handoff')): digest(p) for p in (root/'handoff').rglob('*') if p.is_file()}
    assert actual == package['files']
    assert set(actual) == {'strategy.py','model/__init__.py','model/strategy.py','model/portfolio.py'}

    net = {
        'validation_C06': ledger(root/sources[0], 2016, 3023),
        'validation_C09': ledger(root/sources[1], 2016, 3023),
        'audit_C09': ledger(root/sources[2], 3024, 3779),
    }
    ranges = []
    for label, report, period in [('Validation', validation, 'pooled_validation'), ('Audit', audit, 'locked_audit')]:
        point = report['candidates']['C09']['metrics'][period]['net_sharpe']
        for b in report['bootstrap']:
            interval = b['candidates']['C09']['net_sharpe']
            assert interval['finite_replicates'] == 1000 and interval['undefined_replicates'] == 0
            ranges.append({'period':label, 'block_length':b['block_length'], 'point':point,
                           'lower':interval['lower_2_5_percent'], 'upper':interval['upper_97_5_percent']})
    (out/'research_plot_data.json').write_text(json.dumps({'net_returns':{k:v.tolist() for k,v in net.items()},
        'c09_sharpe_ranges':ranges,'source_sha256':source_hashes}, indent=2)+'\n')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'continual-research-C09'})
    fig, axes = plt.subplots(1,3,figsize=(15,4.8))
    fig.subplots_adjust(left=.055,right=.985,top=.77,bottom=.23,wspace=.32)
    teal, blue, grey = '#087f8c', '#596e9b', '#718096'
    fig.text(.055,.94,'Selected C09: protected results after full trading costs',fontsize=17,weight='bold',color='#152f43')
    fig.text(.055,.875,'Frozen policy | Validation: 1,007 observations | Separate audit: 755 observations',fontsize=11,color='#486071')
    for key,label,color in [('validation_C06','C06',blue),('validation_C09','C09 selected',teal)]:
        growth=np.r_[0.,np.cumprod(1+net[key])-1]
        axes[0].plot(np.arange(len(growth)),growth,label=label,color=color,lw=1.8)
    axes[0].axvline(504,color=grey,lw=.8,ls='--',alpha=.8)
    axes[0].set(title='Validation: two frozen policies',xlabel='Scored observation',ylabel='Cumulative net return')
    axes[0].legend(frameon=False,loc='upper left',fontsize=9)
    growth=np.r_[0.,np.cumprod(1+net['audit_C09'])-1]
    axes[1].plot(np.arange(len(growth)),growth,color=teal,lw=1.8)
    axes[1].set(title='Audit: selected C09 only',xlabel='Scored observation',ylabel='Cumulative net return')
    for ax in axes[:2]:
        ax.axhline(0,color=grey,lw=.7)
        ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0))
        ax.set_xlim(left=0)
    for y,r in enumerate(ranges):
        color=blue if r['period']=='Validation' else teal
        axes[2].hlines(y,r['lower'],r['upper'],color=color,lw=2.6)
        axes[2].scatter([r['lower'],r['upper']],[y,y],color=color,marker='|',s=70)
        axes[2].scatter([r['point']],[y],color=color,s=34,zorder=3)
    axes[2].set_yticks(range(4),[f"{r['period']} · L={r['block_length']}" for r in ranges])
    axes[2].invert_yaxis()
    axes[2].axvline(0,color=grey,lw=.9,ls='--')
    axes[2].set(title='C09 estimate and uncertainty',xlabel='Annualized net Sharpe')
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',color='#dbe3e8',lw=.55,alpha=.8)
        ax.set_axisbelow(True)
    fig.text(.055,.105,'Lines: compounded saved net returns, rebased only for display. Actual learning and holdings remained continuous.',fontsize=9,color='#486071')
    fig.text(.055,.055,'Ranges: empirical 95% moving-block bootstrap percentiles; 1,000 draws per fixed length. They do not remove all selection or regime uncertainty.',fontsize=9,color='#486071')
    fig.savefig(out/'research_summary.png',dpi=160,facecolor='white')
    fig.savefig(out/'research_summary.svg',facecolor='white',metadata={'Date':None})
    plt.close(fig)

    archive=out/'continual_research_C09.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for relative in sorted(actual):
            info=zipfile.ZipInfo(relative,date_time=(2026,10,27,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,(root/'handoff'/relative).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        restored={name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
        assert restored==actual and len(z.namelist())==4
    (out/'handoff_archive_manifest.json').write_text(json.dumps({
        'status':'EXACT_FROZEN_PACKAGE_ARCHIVE','archive':archive.name,'bytes':archive.stat().st_size,
        'sha256':digest(archive),'files':restored,
        'package_manifest_sha256':source_hashes['evidence/handoff_discovery_001/package_manifest.json'],
        'configuration_sha256':selection['config_sha256'],'raw_market_data_included':False,
        'note_or_source_changed':False,'external_submission':False},indent=2)+'\n')
    assert all(digest(root/name)==h for name,h in source_hashes.items())
    manifest={'status':'ARTIFACTS_BUILT_FROM_FROZEN_RESULTS','created_utc':datetime.now(timezone.utc).isoformat(),
              'command':f'{sys.executable} {Path(__file__).resolve()} --project {root} --out {out}',
              'builder_sha256':digest(Path(__file__)),'source_sha256':source_hashes,
              'environment':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
              'outputs':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()},
              'model_executions':0,'new_parameters_or_selection':False}
    (out/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'archive_sha256':digest(archive),'archive_bytes':archive.stat().st_size,'files':len(actual)}))


if __name__=='__main__':
    main()
