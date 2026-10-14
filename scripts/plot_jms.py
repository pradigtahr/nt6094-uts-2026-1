"""Figures for the JMS-format manuscript: Arial lettering, no titles inside figures, panel letters, 600 dpi."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(os.path.join(root, "data", "results.json")))
D = json.load(open(os.path.join(root, "data", "datasets.json")))
keys = sorted(R, key=lambda k: int(k[1:3]))
g = [int(k[1:3]) for k in keys]
C1, C2, INK, GRID = "#2a6fdb", "#d9822b", "#222222", "#dddddd"
MM = 1 / 25.4
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": "#666", "axes.linewidth": 0.6,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.fontsize": 7.5})
out = lambda n: os.path.join(root, "figures", n)


def style(ax, xlabel, ylabel, letter):
    ax.grid(color=GRID, lw=0.4); ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel(xlabel, fontstyle="italic"); ax.set_ylabel(ylabel, fontstyle="italic")
    ax.text(-0.17, 1.03, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom")


# Fig: features vs g
fig, axs = plt.subplots(2, 2, figsize=(174 * MM, 120 * MM))
a = axs[0, 0]
a.plot(g, [R[k]["ypeak"] for k in keys], "-o", color=C1, lw=1.2, ms=4.5, label="Peak")
a.plot(g, [R[k]["ylast"] for k in keys], "--s", color=C2, lw=1.2, ms=4, label="Last point")
a.legend(frameon=False); style(a, "g", "y", "a")
a = axs[0, 1]
a.plot(g, [R[k]["xpeak"] for k in keys], "-o", color=C1, lw=1.2, ms=4.5, label="Peak")
a.plot(g, [R[k]["xlast"] for k in keys], "--s", color=C2, lw=1.2, ms=4, label="Last point")
a.legend(frameon=False); style(a, "g", "x", "b")
a = axs[1, 0]
a.plot(g, [R[k]["m"] for k in keys], "-o", color=C1, lw=1.2, ms=4.5); style(a, "g", "m", "c")
a = axs[1, 1]
a.plot(g, [R[k]["b"] for k in keys], "-o", color=C1, lw=1.2, ms=4.5); style(a, "g", "b", "d")
for a in axs.flat:
    a.set_xticks(g)
fig.tight_layout(); fig.savefig(out("jms_fig_features_vs_g.png"), dpi=600)

# Fig: all raw curves
fig, ax = plt.subplots(figsize=(174 * MM, 85 * MM))
cmap = plt.get_cmap("Blues")
for i, k in enumerate(keys):
    v, r = D[k], R[k]
    ax.plot(v["X"], v["Y"], color=cmap(0.35 + 0.65 * i / (len(keys) - 1)), lw=0.9)
    ax.annotate(k, (r["xpeak"], r["ypeak"]), xytext=(3, 3), textcoords="offset points", fontsize=7, color=INK)
ax.grid(color=GRID, lw=0.4); ax.spines[["top", "right"]].set_visible(False)
ax.set_xlabel("x", fontstyle="italic"); ax.set_ylabel("y", fontstyle="italic")
fig.tight_layout(); fig.savefig(out("jms_fig_all_curves.png"), dpi=600)

# Fig: each dataset with regression window and fit
fig, axs = plt.subplots(5, 2, figsize=(174 * MM, 225 * MM))
for n, (ax, k) in enumerate(zip(axs.flat, keys)):
    v, r = D[k], R[k]; ds = v["ds"]
    ax.plot([p[2] for p in ds], [p[3] for p in ds], ".", color="#9db7e0", ms=2.5, label="Data (sampled)")
    seg = ds[r["lini"]:r["linf"] + 1]
    ax.plot([p[2] for p in seg], [p[3] for p in seg], ".", color=C1, ms=3, label="Regression points")
    xa = ds[max(r["lini"] - 15, 0)][2]; xb = ds[min(r["linf"] + 15, len(ds) - 1)][2]
    ax.plot([xa, xb], [r["m"] * xa + r["b"], r["m"] * xb + r["b"]], "--", color=C2, lw=1.0, label="y = mx + b")
    ax.plot(r["xpeak"], r["ypeak"], "^", color=INK, ms=5, label="Peak")
    ax.plot(r["xlast"], r["ylast"], "s", mfc="white", mec=INK, ms=4.5, label="Last point")
    ax.text(0.02, 0.95, k, transform=ax.transAxes, fontsize=7.5, va="top")
    style(ax, "x" if n >= 8 else "", "y" if n % 2 == 0 else "", "abcdefghij"[n])
axs[0, 0].legend(frameon=False, fontsize=6.5, loc="center left")
fig.tight_layout(); fig.savefig(out("jms_fig_fits.png"), dpi=600)
print("ok")
