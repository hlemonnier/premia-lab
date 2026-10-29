"""Wave 3 variants (research/v3/WAVE3_PLAN_20261029.md), built on the unchanged handoff_v3 package.

python research/v3/wave3.py --data DIR --variant {V3,M2,H1,J} [--out research/v3/results]
Scores with the original scorer and saves <variant>_rows.npy, <variant>_certs.json and
<variant>_summary.json. handoff_v3 is imported, never edited.
"""
import argparse, importlib.util, json, os, sys, time
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
from model_v3 import engine as E  # noqa: E402
from model_v3.allocator import allocate_factor  # noqa: E402
from model_v3.policy import Book, ScorePolicy  # noqa: E402

BASE_SLEEVE = 0.05


# ---------------------------------------------------------------- M2: volatility-managed sleeve
class M2Policy(ScorePolicy):
    def forecast(self, returns_history, characteristics_history):
        self.m_sums = {63: 0.0, 1008: 0.0}; self.m_mass = {63: 0.0, 1008: 0.0}
        self.m_obs = 0; self.m_rows = 0; self.sleeve_path = []
        self.sleeve = BASE_SLEEVE
        return super().forecast(returns_history, characteristics_history)

    def _update_market(self, R):
        while self.m_rows < len(R):                     # each published row once, in order
            mk = float(R[self.m_rows].mean())
            for hl in self.m_sums:
                dec = 2.0 ** (-1.0 / hl)
                self.m_sums[hl] = dec * self.m_sums[hl] + mk * mk
                self.m_mass[hl] = dec * self.m_mass[hl] + 1.0
            self.m_rows += 1; self.m_obs += 1

    def rebalance(self, held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        R = np.asarray(returns_history)
        if self.m_rows > len(R):
            raise RuntimeError("market history went backwards within a session")
        self._update_market(R)
        if self.m_obs < 63:
            mult = 1.0
        else:
            q63 = self.m_sums[63] / self.m_mass[63]; q1008 = self.m_sums[1008] / self.m_mass[1008]
            mult = float(np.clip((max(q1008, 1e-12) / max(q63, 1e-12)) ** 0.5, 0.5, 2.0))
        self.sleeve = BASE_SLEEVE * mult
        self.sleeve_path.append(self.sleeve)
        return super().rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)


# ---------------------------------------------------------------- H1: latent residual factors in risk
class HybridState(E._RiskState):
    def __init__(self, n, k, cfg, K=10, window=1008, refresh=21, min_rows=252):
        super().__init__(n, k, cfg)
        self.K, self.window, self.refresh, self.min_rows = K, window, refresh, min_rows
        self.buf = np.zeros((window, n)); self.count = 0; self.since = 0; self.P = None; self.lam = None

    def absorb(self, R, X, s):
        # identical to E._RiskState.absorb, plus storing the residual u
        beta = E._window_beta(R[:s], self.cfg["beta_window"])
        D = E.risk_loadings(X[s - 1], beta, self.cfg)
        e = R[s] - beta * R[s].mean(); e = e - e.mean()
        G = D.T @ D / len(e)
        f = np.linalg.solve(G + 1e-10 * np.eye(G.shape[0]), D.T @ e / len(e))
        u = e - D @ f
        self.S2 = self.aF * self.S2 + np.outer(f, f); self.wF = self.aF * self.wF + 1
        self.U2 = self.aS * self.U2 + u * u; self.wS = self.aS * self.wS + 1
        self.buf[self.count % self.window] = u; self.count += 1; self.since += 1
        self.upto = s + 1

    def latent(self):
        if self.count < self.min_rows:
            return None, None
        if self.P is None or self.since >= self.refresh:
            W = self.buf[:min(self.count, self.window)]
            if self.P is None:
                Q = np.linalg.qr(W[-self.K:].T)[0]; iters = 30
            else:
                Q = self.P; iters = 3
            for _ in range(iters):
                Q = np.linalg.qr(W.T @ (W @ Q))[0]
            lam = np.mean((W @ Q) ** 2, axis=0)
            order = np.argsort(lam)[::-1]
            self.P, self.lam = Q[:, order], lam[order]; self.since = 0
        return self.P, self.lam


class HybridBook(Book):
    def rebalance(self, held, mu, R, X, costs, gamma, cap):
        cfg = {**self.cfg, "risk_aversion": gamma, "weight_cap": cap}
        T, n = R.shape
        if self.state is None or self.state.upto > T:
            self.state = HybridState(n, 26, self.cfg)
        while self.state.upto < T:
            self.state.absorb(R, X, self.state.upto)
        L, d = self.state.model()
        P, lam = self.state.latent()
        beta = E._window_beta(R, cfg["beta_window"])
        D = E.risk_loadings(X[T - 1], beta, cfg)
        if P is not None:
            d = np.maximum(d - (P ** 2) @ lam, 0.5 * d)
            k0 = L.shape[1]; K = P.shape[1]
            Lb = np.zeros((k0 + K, k0 + K)); Lb[:k0, :k0] = L; Lb[k0:, k0:] = np.diag(np.sqrt(lam))
            D, L = np.hstack([D, P]), Lb
        info = {}
        w = allocate_factor(mu, held, d, D, L, beta, np.asarray(costs, dtype=np.float64) / cfg["cost_horizon"],
                            gamma, cap, warm=self.state.warm, info=info, beta_target=0.0)
        gross = float(np.abs(w).sum()); info["gross_action"] = "none"
        if gross > cfg["gross_cap"]:
            w = w * (cfg["gross_cap"] / gross); info["gross_action"] = "scaled"
        E._final_check(w, beta, 0.0, cfg)
        self.target = w
        return w, info


class H1Policy(ScorePolicy):
    def forecast(self, returns_history, characteristics_history):
        out = super().forecast(returns_history, characteristics_history)
        n = np.shape(returns_history)[1]
        self.virtual, self.inner = HybridBook(self.cfg, n), HybridBook(self.cfg, n)
        return out


class JPolicy(M2Policy, H1Policy):
    pass                                            # MRO: M2 sleeve logic, then H1 books, then ScorePolicy


# ---------------------------------------------------------------- scoring
def make(variant):
    import strategy as S                            # handoff_v3 config, engine configured on import
    cls = {"V3": ScorePolicy, "M2": M2Policy, "H1": H1Policy, "J": JPolicy}[variant]
    return cls(dict(E.CONFIG), sleeve=BASE_SLEEVE, outer_gross_cap=5.0)


def load(d):
    R = np.ascontiguousarray(pd.read_csv(f"{d}/returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(f"{d}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    c = pd.read_csv(f"{d}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    return R, X, c


def scorer():
    spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def score_policy(pol, R, X, c):
    shim = type("Sh", (), {"forecast": staticmethod(pol.forecast), "rebalance": staticmethod(pol.rebalance)})
    return scorer().run(shim, R, X, c)


STAGES = {"s1": (253, 2016), "s2": (2016, 3024), "s3": (3024, 3779)}   # day index t of each scored row = 253 + i


def summary(rows):
    net = rows[:, 0] - rows[:, 1]; m = rows[:, 3]; t = 253 + np.arange(len(net))
    sh = lambda x: float(np.sqrt(252) * x.mean() / x.std())
    out = {"net_sharpe": sh(net), "gross_sharpe": sh(rows[:, 0]), "beta": float(np.cov(net, m)[0, 1] / m.var(ddof=1)),
           "ann_return": float(252 * net.mean()), "ann_vol": float(np.sqrt(252) * net.std()), "ann_fee": float(252 * rows[:, 1].mean()),
           "mean_gross": float(rows[:, 2].mean()), "rebalance_ms": float(1e3 * rows[:, 4].mean()),
           "rebalance_ms_max": float(1e3 * rows[:, 4].max())}
    for k, (a, b) in STAGES.items():
        k_ = (t >= a) & (t < b); out[f"{k}_net_sharpe"] = sh(net[k_])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--variant", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "v3", "results")); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R, X, c = load(a.data)
    pol = make(a.variant)
    t0 = time.perf_counter(); rows, fsec = score_policy(pol, R, X, c); wall = time.perf_counter() - t0
    s = summary(rows); s.update({"variant": a.variant, "forecast_s": fsec, "wall_s": wall,
                                 "cert_statuses": sorted({x["status"] for x in pol.certificates}), "solves": len(pol.certificates)})
    if hasattr(pol, "sleeve_path"):
        sp = np.array(pol.sleeve_path); s.update({"sleeve_mean": float(sp.mean()), "sleeve_min": float(sp.min()), "sleeve_max": float(sp.max())})
    np.save(os.path.join(a.out, f"{a.variant}_rows.npy"), rows)
    json.dump(s, open(os.path.join(a.out, f"{a.variant}_summary.json"), "w"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
