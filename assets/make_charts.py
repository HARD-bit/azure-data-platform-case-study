"""Genera i grafici del case study. Dati DIDATTICI/illustrativi, non dati reali del cliente."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

C = {"blue": "#2a6fdb", "gray": "#8a94a6", "red": "#d1495b", "green": "#2f9e6e"}
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

# 1) ISF: ratio per taglia nella stessa famiglia
fig, ax = plt.subplots(figsize=(7.5, 3.6))
labels = ["D2s", "D4s", "D8s", "D16s"]
ratios = [1, 2, 4, 8]
ax.bar(labels, ratios, color=C["blue"])
for i, r in enumerate(ratios):
    ax.text(i, r + .15, f"{r}x", ha="center")
ax.set_ylabel("unità base equivalenti")
ax.set_title("ISF: ogni VM è espressa in unità base della sua famiglia")
fig.tight_layout(); fig.savefig("isf-normalization.png", dpi=160); plt.close()

# 2) Needed vs Bought (esempio)
fig, ax = plt.subplots(figsize=(6.5, 3.2))
vals = [20, 20, 40]
ax.barh(["To Buy", "Bought", "Needed"], vals, color=[C["red"], C["gray"], C["blue"]])
for y, v in enumerate(vals):
    ax.text(v + .6, y, str(v), va="center")
ax.set_title("Esempio: 10 VM D8s = 40 unità; 20 già acquistate → 20 da comprare")
fig.tight_layout(); fig.savefig("needed-vs-bought.png", dpi=160); plt.close()

# 3) Incidente: righe per mese (100 = mese sano)
months = ["M-3", "M-2", "M-1", "M (outage)", "M+1 (outage)"]
rows = [100, 100, 100, 3, 0]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
ax.bar(months, rows, color=[C["green"]] * 3 + [C["red"]] * 2)
ax.set_ylabel("righe di costo (100 = mese sano)")
ax.set_title("Cleanup condizionato a 'Completed': lo storico veniva cancellato")
fig.tight_layout(); fig.savefig("incident-row-counts.png", dpi=160); plt.close()
