"""Plot peak, last, m, b as function of g (small multiples) and overview of all curves."""
import json, sys, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(root, "data", "results.json")))
D = json.load(open(os.path.join(root, "data", "datasets.json")))
keys = sorted(R, key=lambda k: int(k[1:3]))
g = [int(k[1:3]) for k in keys]
C1, C2, INK, GRID = "#2a6fdb", "#d9822b", "#333333", "#dddddd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": "#888", "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK})

def style(ax, ylabel, title):
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("g"); ax.set_ylabel(ylabel); ax.set_title(title, loc="left", fontsize=10)
    ax.set_xticks(g)

fig, axs = plt.subplots(2, 2, figsize=(9, 6.6))
a = axs[0, 0]
a.plot(g, [R[k]["ypeak"] for k in keys], "-o", color=C1, lw=1.5, ms=6, label="peak")
a.plot(g, [R[k]["ylast"] for k in keys], "--s", color=C2, lw=1.5, ms=5, label="last")
a.legend(frameon=False); style(a, "y", "(a) y of peak and last point")
a = axs[0, 1]
a.plot(g, [R[k]["xpeak"] for k in keys], "-o", color=C1, lw=1.5, ms=6, label="peak")
a.plot(g, [R[k]["xlast"] for k in keys], "--s", color=C2, lw=1.5, ms=5, label="last")
a.legend(frameon=False); style(a, "x", "(b) x of peak and last point")
a = axs[1, 0]
a.plot(g, [R[k]["m"] for k in keys], "-o", color=C1, lw=1.5, ms=6)
style(a, "m", "(c) slope m of linear region")
a = axs[1, 1]
a.plot(g, [R[k]["b"] for k in keys], "-o", color=C1, lw=1.5, ms=6)
style(a, "b", "(d) intercept b of linear region")
fig.tight_layout(); fig.savefig(os.path.join(root, "figures", "results_vs_g.png"), dpi=200)

# overview of all ten curves (raw data), sequential single hue light->dark with g
fig, ax = plt.subplots(figsize=(9, 4.6))
cmap = plt.get_cmap("Blues")
for i, k in enumerate(keys):
    v = D[k]; r = R[k]
    ax.plot(v["X"], v["Y"], color=cmap(0.35 + 0.65 * i / (len(keys) - 1)), lw=1.2)
    ax.annotate(k, (r["xpeak"], r["ypeak"]), xytext=(3, 3), textcoords="offset points", fontsize=7, color=INK)
ax.grid(color=GRID, lw=0.6); ax.spines[["top", "right"]].set_visible(False)
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_title("All ten datasets, y vs x (raw data, darker = larger g)", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(root, "figures", "all_datasets.png"), dpi=200)

# per-dataset fit check
fig, axs = plt.subplots(5, 2, figsize=(9, 13))
for ax, k in zip(axs.flat, keys):
    v = D[k]; r = R[k]; ds = v["ds"]
    ax.plot([p[2] for p in ds], [p[3] for p in ds], ".", color="#9db7e0", ms=3, label="data")
    seg = ds[r["lini"]:r["linf"] + 1]
    ax.plot([p[2] for p in seg], [p[3] for p in seg], ".", color=C1, ms=4, label="regression points")
    xa = ds[max(r["lini"] - 15, 0)][2]; xb = ds[min(r["linf"] + 15, len(ds) - 1)][2]
    ax.plot([xa, xb], [r["m"] * xa + r["b"], r["m"] * xb + r["b"]], "--", color=C2, lw=1.3, label="y = mx + b")
    ax.plot(r["xpeak"], r["ypeak"], "^", color=INK, ms=7, label="peak")
    ax.plot(r["xlast"], r["ylast"], "s", mfc="white", mec=INK, ms=6, label="last")
    ax.set_title(f"{k}: m = {r['m']:.1f}, b = {r['b']:.1f}, R² = {r['R2']:.4f}", loc="left", fontsize=9)
    ax.grid(color=GRID, lw=0.6); ax.spines[["top", "right"]].set_visible(False)
axs[0, 0].legend(frameon=False, fontsize=7)
for ax in axs[-1]: ax.set_xlabel("x")
for ax in axs[:, 0]: ax.set_ylabel("y")
fig.tight_layout(); fig.savefig(os.path.join(root, "figures", "fits_all.png"), dpi=160)
