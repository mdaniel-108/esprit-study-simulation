"""Build results/figure_power_uptake.png from results/results.csv.

Power of the within-learner design as a function of assistant uptake, for d = 0.3 and d = 0.2.
Lines show the midpoint and bands the range over the intraclass correlation (rho = 0.3-0.5);
open markers show 70% uptake when help-seeking depends on prior knowledge, policy and difficulty.
"""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

rows = list(csv.DictReader(open('results/results.csv')))
family = 'Inter' if any('Inter' in f.name for f in font_manager.fontManager.ttflist) else 'DejaVu Sans'
plt.rcParams.update({'font.family': family, 'font.size': 8.5, 'axes.edgecolor': '#c9c8c3',
                     'axes.labelcolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})

SCEN = [('Conservative', 'Conservative: 25 completers', '#2a78d6', 'o'),
        ('Moderate', 'Moderate: 40', '#eb6834', 's'),
        ('Optimistic', 'Optimistic: 60', '#1baf7a', '^')]
UPTAKE = [0.5, 0.7, 0.9, 1.0]

def power(scen, d, uptake, dep=False):
    if uptake == 1.0:
        v = [r for r in rows if r['analysis'] == 'main' and r['scenario'] == scen and r['design'] == 'within' and float(r['d']) == d]
    else:
        v = [r for r in rows if r['analysis'] == 'uptake' and r['scenario'] == scen and float(r['d']) == d
             and abs(float(r['uptake']) - uptake) < 1e-9 and r['nonuse_dep'] == str(dep)]
    p = [float(r['reject_model']) for r in v]
    return min(p), max(p)

fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.5), sharey=True)
for ax, d in zip(axes, (0.3, 0.2)):
    ax.axhline(0.8, color='#9b9a94', lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(0.505, 0.815, '80% power', color='#52514e', fontsize=8, va='bottom')
    for scen, label, col, mk in SCEN:
        lo, hi = zip(*[power(scen, d, u) for u in UPTAKE])
        mid = [(a + b) / 2 for a, b in zip(lo, hi)]
        ax.fill_between(UPTAKE, lo, hi, color=col, alpha=0.16, lw=0, zorder=2)
        ax.plot(UPTAKE, mid, color=col, lw=2, marker=mk, ms=6, mec='#fcfcfb', mew=1.5, zorder=4, label=label)
        dlo, dhi = power(scen, d, 0.7, dep=True)
        ax.errorbar([0.715], [(dlo + dhi) / 2], yerr=[[(dlo + dhi) / 2 - dlo], [dhi - (dlo + dhi) / 2]],
                    fmt=mk, mfc='#fcfcfb', mec=col, ecolor=col, ms=6, mew=1.5, capsize=0, lw=1.2, zorder=5)
        ax.text(1.03, mid[-1], scen.lower(), color='#52514e', fontsize=8, va='center')
    ax.set_title(f'Effect when used: d = {d}', fontsize=9, color='#0b0b0b', loc='left', pad=8)
    ax.set_xlim(0.47, 1.16)
    ax.set_xticks(UPTAKE, ['50%', '70%', '90%', '100%'])
    ax.set_xlabel('Assistant uptake (share of activities)')
    ax.set_ylim(0, 1.02)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], ['0', '0.2', '0.4', '0.6', '0.8', '1.0'])
    ax.grid(axis='y', color='#ecebe7', lw=0.8, zorder=0)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
axes[0].set_ylabel('Power (α = 0.05, two-sided)')
handles, labels = axes[0].get_legend_handles_labels()
dep = plt.Line2D([], [], ls='none', marker='o', mfc='#fcfcfb', mec='#52514e', mew=1.5, ms=6)
fig.legend(handles + [dep], labels + ['70% uptake, dependent help-seeking'],
           loc='lower center', ncol=4, frameon=False, fontsize=7.5, handletextpad=0.4, columnspacing=1.2, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig('results/figure_power_uptake.png', dpi=300, bbox_inches='tight', facecolor='#ffffff')
print('results/figure_power_uptake.png written')
