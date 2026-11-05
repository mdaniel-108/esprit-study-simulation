"""Verify that the fast estimator equals the direct dummy-variable implementation on identical data."""
import numpy as np, importlib.util, sys
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
fast = load('fast', 'simulate.py'); ref = load('ref', 'reference_slow.py')

def slow_estimate(D, p):
    n, i_, j_, t_, z, y = D['n'], D['i'], D['j'], D['t'], D['z'], D['y']
    K = 6; inter = p.get('test') == 'interaction'
    if p['design'] == 'within':
        X = np.column_stack([t_] + ([t_ * z[i_]] if inter else []) + [np.eye(n)[i_], np.eye(K)[j_][:, 1:]]); idx = 1 if inter else 0
    else:
        X = np.column_stack([np.ones(len(y)), t_] + ([t_ * z[i_], z[i_]] if inter else []) + [np.eye(K)[j_][:, 1:]]); idx = 2 if inter else 1
    XtX_inv = np.linalg.pinv(X.T @ X); b = XtX_inv @ X.T @ y; res = y - X @ b
    out = dict(est=b[idx], se_cr2=ref.cr2_se(X, res, i_, XtX_inv, idx), se_cr0=ref.cr0_se(X, res, i_, XtX_inv, idx, n))
    if p['design'] == 'within':
        r = np.linalg.matrix_rank(X); out['se_model'] = np.sqrt(res @ res / (len(y) - r) * XtX_inv[idx, idx]); out['df_model'] = len(y) - r
    return out

rng = np.random.default_rng(1)
cases = [dict(design='within'), dict(design='by_learner'), dict(design='within', test='interaction', g=0.25),
         dict(design='by_learner', test='interaction', g=0.25), dict(design='within', bounded=True),
         dict(design='within', nonuse=0.3, nonuse_dep=True), dict(design='within', gi_drop=0.1, mnar=True)]
worst = 0.0
for c in cases:
    for n in (41, 66, 117):
        p = dict(n=n, h=0.15, rho=0.3, d=0.3, **c)
        for _ in range(5):
            D = fast.simulate_data(rng, p)
            a, b = fast.estimate(D, p), slow_estimate(D, p)
            for k in ('est', 'se_cr2', 'se_cr0', 'se_model', 'df_model'):
                if k in b:
                    diff = abs(float(a[k]) - float(b[k])) / max(1e-12, abs(float(b[k])))
                    worst = max(worst, diff)
                    if diff > 1e-8:
                        print('MISMATCH', c, n, k, a[k], b[k])
print('cases checked:', len(cases) * 3 * 5, 'largest relative difference:', f'{worst:.2e}')
