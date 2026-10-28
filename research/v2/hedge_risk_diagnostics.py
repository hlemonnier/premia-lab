"""Reviewer diagnostics (REVIEWER_NEXT_DECISION_20261028.md §2 and §3) on frozen books.

python research/v2/hedge_risk_diagnostics.py --data DIR --book {V2,B0,B05}   # capture + per-day records
python research/v2/hedge_risk_diagnostics.py --data DIR --summarize           # statistics from saved records

Per decision after close t = 252..3777 (earning row t+1), with the book's exact target w_t:
 §2  b_raw = OLS beta on the last 252 rows through t; eta_t from pairs with s+252 <= t+1
     (the engine's tracker at prefix length t+1); b_corr = (1-eta) b_raw + eta mean(b_raw).
     rbar = mean of the last 252 rows through t, mbar = mean(rbar).
     H_j = (g - w'rbar - p_j (m - mbar))^2 with g = w'R[t+1], m = mean(R[t+1]), p_j = w'b_j.
 §3  Joint second-moment state of x_s = (m_s, f_s) with the policy's own residualization,
     loadings and factor fit, decay = factor half-life; factor block must equal the engine's F.
     q_resid = w'diag(d)w + z'F z;  q_raw = q_resid + p^2 Om00 + 2 p Om0f z  (physical scale 1),
     z = D_t'w, p = b_policy'w. Remainder 2 p w'E[u m] reported, not added.
"""
import argparse, importlib.util, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
import strategy as V2  # noqa: E402
from model_v2 import engine  # noqa: E402

BOOKS = {"V2": {}, "B0": {"beta_shrinkage": True, "beta_target": 0.0}, "B05": {"beta_shrinkage": True, "beta_target": 0.05}}
STAGES = {"full": (253, 3779), "discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}
OUT = os.path.join(ROOT, "research/v2/results/hedge_risk")


def load(d):
    R = np.ascontiguousarray(pd.read_csv(f"{d}/returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(f"{d}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    c = pd.read_csv(f"{d}/costs.csv", index_col="stock")["cost"].to_numpy()
    return R, X, c


def capture(R, X, c, over):
    engine.configure({**V2._CONFIG, **over})
    spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
    score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
    W = {}
    def reb(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        w = engine.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
        W[len(returns_history) - 1] = np.array(w, copy=True); return w
    shim = type("S", (), {"forecast": staticmethod(engine.forecast), "rebalance": staticmethod(reb)})
    rows, _ = score.run(shim, R, X, c)
    return W, rows


class JointState(engine._RiskState):
    """Engine risk state plus the joint (market, factor) second moment and E[u m]."""
    def __init__(self, n, k, cfg):
        super().__init__(n, k, cfg); self.Om = np.zeros((k + 1, k + 1)); self.UM = np.zeros(n)

    def absorb(self, R, X, s):
        beta = engine._window_beta(R[:s], self.cfg["beta_window"])
        D = engine.risk_loadings(X[s - 1], beta, self.cfg)
        if self.cfg["beta_shrinkage"]:
            beta = engine._correct(beta, self.eta.eta(R, s))
        e = R[s] - beta * R[s].mean(); e = e - e.mean()
        G = D.T @ D / len(e)
        f = np.linalg.solve(G + 1e-10 * np.eye(G.shape[0]), D.T @ e / len(e))
        u = e - D @ f
        x = np.concatenate([[R[s].mean()], f])
        self.S2 = self.aF * self.S2 + np.outer(f, f); self.wF = self.aF * self.wF + 1
        self.U2 = self.aS * self.U2 + u * u; self.wS = self.aS * self.wS + 1
        self.Om = self.aF * self.Om + np.outer(x, x)
        self.UM = self.aF * self.UM + u * R[s].mean()
        self.upto = s + 1


def per_day(R, X, W, over):
    cfg = {**engine.CONFIG, **V2._CONFIG, **over, "factor_risk_scale": 1.0}   # engine defaults first (attempt 001 omitted them)
    T, n = R.shape
    st = JointState(n, 26, cfg); tr = engine._EtaTracker(cfg["beta_window"])
    recs = []
    for t in range(252, 3778):
        w = W[t]
        while st.upto < t + 1:
            st.absorb(R, X, st.upto)
        b_raw = engine._window_beta(R[:t + 1], cfg["beta_window"])
        eta = tr.eta(R, t + 1)
        b_cor = engine._correct(b_raw, eta)
        rbar = R[max(0, t - 251):t + 1].mean(axis=0); mbar = rbar.mean()
        g = float(w @ R[t + 1]); m = float(R[t + 1].mean())
        p_raw, p_cor = float(w @ b_raw), float(w @ b_cor)
        base = g - float(w @ rbar)
        H_raw = (base - p_raw * (m - mbar)) ** 2; H_cor = (base - p_cor * (m - mbar)) ** 2
        # §3 with the policy's own risk definitions
        L, d = st.model()
        D = engine.risk_loadings(X[t], b_raw, cfg)
        b_pol = b_cor if cfg["beta_shrinkage"] else b_raw
        z = D.T @ w; p = float(b_pol @ w)
        Om = st.Om / st.wF; Fblk = st.S2 / st.wF
        spec_ = float(w @ (d * w)); fac = float(z @ Fblk @ z)
        msq = p * p * Om[0, 0]; cross = 2 * p * float(Om[0, 1:] @ z)
        rem = 2 * p * float(w @ (st.UM / st.wF))
        recs.append((t, t + 1, g, m, p_raw, p_cor, eta, float(w.sum()), float(np.abs(w).sum()), float(w @ rbar), mbar,
                     H_raw, H_cor, spec_ + fac, spec_ + fac + msq + cross, msq, cross, rem,
                     float(np.max(np.abs(Om[1:, 1:] - Fblk)))))
    cols = ["t", "earn", "g", "m", "p_raw", "p_cor", "eta", "net_inv", "gross", "w_rbar", "mbar",
            "H_raw", "H_cor", "q_resid", "q_raw", "market_square", "factor_market_cross", "um_remainder", "omega_vs_F_maxdiff"]
    return pd.DataFrame(recs, columns=cols)


def prefix_invariance(R, X, W, over, cut=2500):
    """Decision inputs at t < cut must not depend on rows >= cut."""
    R2 = R.copy(); R2[cut:] = np.random.default_rng(1).normal(0, .03, R2[cut:].shape)
    X2 = X.copy(); X2[cut:] = np.random.default_rng(2).normal(0, 1, X2[cut:].shape)
    a = per_day(R, X, W, over); b = per_day(R2, X2, W, over)
    k = a["t"] < cut - 1     # decisions after close t <= cut-2 earn row <= cut-1: outcomes also unchanged
    protected = ["p_raw", "p_cor", "eta", "w_rbar", "mbar", "q_resid", "q_raw", "market_square", "factor_market_cross", "um_remainder"]
    return bool(all(np.array_equal(a.loc[k, c].to_numpy(), b.loc[k, c].to_numpy()) for c in protected)), int(k.sum())


def block_ci(x, L, draws=2000, seed=20261027):
    n = len(x); rng = np.random.default_rng(seed); nb = int(np.ceil(n / L))
    st = rng.integers(0, n - L + 1, size=(draws, nb)); idx = (st[:, :, None] + np.arange(L)).reshape(draws, -1)[:, :n]
    v = x[idx].mean(axis=1); return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def hac(y, X, lags=10):
    XtXi = np.linalg.inv(X.T @ X); b = XtXi @ X.T @ y; u = y - X @ b
    S = (X * u[:, None]).T @ (X * u[:, None])
    for L in range(1, lags + 1):
        G = (X[L:] * u[L:, None]).T @ (X[:-L] * u[:-L, None]); S += (1 - L / (lags + 1)) * (G + G.T)
    se = np.sqrt(np.diag(XtXi @ S @ XtXi)); return b, se


def summarize():
    res = {}
    led = {k: np.load(os.path.join(ROOT, f"research/v2/results/ledgers/{f}")) for k, f in
           (("V2", "net_fr_beta_phi03_x5.npy"), ("B0", "net_V2_B0_beta_neutral.npy"), ("B05", "net_V2_B05_explicit_beta.npy"))}
    for book in BOOKS:
        df = pd.read_csv(os.path.join(OUT, f"{book}.csv")); earn = df["earn"].to_numpy()
        dH = (df["H_cor"] - df["H_raw"]).to_numpy()
        r = {"primary_mean_H_cor_minus_raw": float(dH.mean()), "relative_to_mean_H_raw": float(dH.mean() / df["H_raw"].mean()),
             "block_ci_95": {L: block_ci(dH, L) for L in (21, 63, 126)},
             "stages": {s: float(dH[(earn >= a) & (earn < b)].mean()) for s, (a, b) in STAGES.items() if s != "full"},
             "eta_range": [float(df["eta"].min()), float(df["eta"].max())]}
        day, net = led[book][0], led[book][1]; assert np.array_equal(day, earn)
        for lab, ret in (("gross", df["g"].to_numpy()), ("net", net)):
            for j in ("p_raw", "p_cor"):
                y = ret - df[j].to_numpy() * df["m"].to_numpy(); X = np.column_stack([np.ones(len(y)), df["m"].to_numpy()])
                b, se = hac(y, X)
                r[f"residual_beta_{lab}_{j}"] = {"slope": float(b[1]), "hac10_95": [float(b[1] - 1.96 * se[1]), float(b[1] + 1.96 * se[1])],
                                                 "intercept_ann_pct": float(25200 * b[0])}
        g = df["g"].to_numpy(); nz = np.abs(df["gross"].to_numpy()) > 0
        def loss(q):
            q = np.maximum(q, 1e-16); l = np.log(q) + g * g / q; l[~nz] = 0.0; return l
        dl = loss(df["q_raw"].to_numpy()) - loss(df["q_resid"].to_numpy())
        r["risk_mean_loss_raw_minus_resid"] = float(dl.mean())
        r["risk_block_ci_95"] = {L: block_ci(dl, L) for L in (21, 63, 126)}
        r["risk_stages"] = {s: float(dl[(earn >= a) & (earn < b)].mean()) for s, (a, b) in STAGES.items() if s != "full"}
        qr = df["q_resid"].to_numpy()
        r["added_terms_share_of_q_resid"] = {"market_square": float((df["market_square"] / qr).mean()),
                                             "factor_market_cross": float((df["factor_market_cross"] / qr).mean()),
                                             "um_remainder_signed": float((df["um_remainder"] / qr).mean()),
                                             "um_remainder_abs": float((df["um_remainder"].abs() / qr).mean())}
        r["calibration_g2_over_q"] = {"resid": float((g * g).mean() / qr.mean()), "raw": float((g * g).mean() / df["q_raw"].mean())}
        r["omega_factor_block_max_diff"] = float(df["omega_vs_F_maxdiff"].max())
        res[book] = r
    d = led["B05"][1] - led["B0"][1]; m = led["B0"][4]
    b, se = hac(d, np.column_stack([np.ones(len(d)), m]))
    res["B05_minus_B0"] = {"beta": float(b[1]), "r2": float(1 - np.var(d - b[0] - b[1] * m) / np.var(d)), "level_error_B0": res["B0"]["residual_beta_net_p_raw"]}
    json.dump(res, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data"); ap.add_argument("--book"); ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    if a.summarize:
        summarize(); sys.exit(0)
    R, X, c = load(a.data); over = BOOKS[a.book]
    W, rows = capture(R, X, c, over)
    df = per_day(R, X, W, over); df.to_csv(os.path.join(OUT, f"{a.book}.csv"), index=False)
    inv, nprot = prefix_invariance(R, X, W, over)
    json.dump({"book": a.book, "prefix_invariance": inv, "protected_decisions": nprot,
               "capture_sharpe": float(np.sqrt(252) * (rows[:, 0] - rows[:, 1]).mean() / (rows[:, 0] - rows[:, 1]).std())},
              open(os.path.join(OUT, f"{a.book}_meta.json"), "w"), indent=1)
    print(a.book, "prefix invariance", inv, "protected", nprot)
