"""Generates the case study charts. ILLUSTRATIVE data, not real customer data."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = {"blue": "#2a6fdb", "gray": "#8a94a6", "red": "#d1495b", "green": "#2f9e6e"}
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# 1) ISF: ratio per size within the same family
fig, ax = plt.subplots(figsize=(7.5, 3.6))
labels = ["D2s", "D4s", "D8s", "D16s"]
ratios = [1, 2, 4, 8]
ax.bar(labels, ratios, color=C["blue"])
for i, r in enumerate(ratios):
    ax.text(i, r + .15, f"{r}x", ha="center")
ax.set_ylabel("equivalent base units")
ax.set_title("ISF: every VM is expressed in base units of its family")
fig.tight_layout(); fig.savefig("isf-normalization.png", dpi=160); plt.close()

# 2) Needed vs Bought (example)
fig, ax = plt.subplots(figsize=(6.5, 3.2))
vals = [20, 20, 40]
ax.barh(["To Buy", "Bought", "Needed"], vals, color=[C["red"], C["gray"], C["blue"]])
for y, v in enumerate(vals):
    ax.text(v + .6, y, str(v), va="center")
ax.set_title("Example: 10 D8s VMs = 40 units; 20 already bought -> 20 to buy")
fig.tight_layout(); fig.savefig("needed-vs-bought.png", dpi=160); plt.close()

# 3) Incident: rows per month (100 = healthy month)
months = ["M-3", "M-2", "M-1", "M (outage)", "M+1 (outage)"]
rows = [100, 100, 100, 3, 0]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.bar(months, rows, color=[C["green"]] * 3 + [C["red"]] * 2)
ax.set_ylabel("cost rows (100 = healthy month)")
ax.set_title("Cleanup conditioned on 'Completed': history was being deleted")
fig.tight_layout(); fig.savefig("incident-row-counts.png", dpi=160); plt.close()
