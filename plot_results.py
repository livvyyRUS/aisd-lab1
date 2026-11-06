"""
Две группы графиков:
  A. {algorithm}_{scenario}_n={n}.png — m vs time для конкретного алгоритма.
  B. compare_{scenario}_n={n}.png    — все алгоритмы на одном полотне (m vs time).
  C. compare_{scenario}_all_n.png    — все алгоритмы × все n (обзорный).

Все оси — логарифмические.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_PATH = "test_results.csv"
OUT_DIR = Path("plots_by_n")
OUT_DIR.mkdir(exist_ok=True)

ALGOS = ["two_pointers", "binary_search", "exp_search", "double_binary"]
SCENARIOS = ["RANDOM", "WORST_CASE", "BEST_CASE", "DUPLICATES"]

COLOR_BY_ALGO = {
    "two_pointers":  "tab:blue",
    "binary_search": "tab:orange",
    "exp_search":    "tab:green",
    "double_binary": "tab:red",
}
MARKER_BY_ALGO = {
    "two_pointers":  "o",
    "binary_search": "s",
    "exp_search":    "^",
    "double_binary": "D",
}
STYLE_BY_ALGO = {
    "two_pointers":  "-",
    "binary_search": "--",
    "exp_search":    "-.",
    "double_binary": ":",
}

# ---------------------------------------------------------------------
# Загрузка
# ---------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)
df["m"] = df["m"].astype(int)
df["n"] = df["n"].astype(int)
df["execution_time_ms"] = df["execution_time_ms"].astype(float)

available_algos = [a for a in ALGOS if a in df["algorithm"].unique()]
available_scenarios = [s for s in SCENARIOS if s in df["scenario_name"].unique()]
available_n = sorted(df["n"].unique())

print(f"Строк: {len(df)}")
print(f"Алгоритмы: {available_algos}")
print(f"Сценарии:  {available_scenarios}")
print(f"Значения n: {available_n}")

missing = [a for a in ALGOS if a not in available_algos]
if missing:
    print(f"⚠  Нет данных для {missing} — перезапустите pytest "
          f"с test_double_binary, чтобы они появились.")

# ---------------------------------------------------------------------
# Утилита: наклон log-log по точкам
# ---------------------------------------------------------------------
def loglog_slope(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = (x > 0) & (y > 0) & np.isfinite(y)
    if mask.sum() < 2:
        return float("nan")
    s, _ = np.polyfit(np.log10(x[mask]), np.log10(y[mask]), 1)
    return s


# =====================================================================
# A. Индивидуальные графики: {algorithm}_{scenario}_n={n}.png
# =====================================================================
count_a = 0
for algo in available_algos:
    for scenario in available_scenarios:
        for n_val in available_n:
            sub = df[
                (df.algorithm == algo)
                & (df.scenario_name == scenario)
                & (df.n == n_val)
            ].sort_values("m")
            if sub.empty:
                continue

            fig, ax = plt.subplots(figsize=(9, 6))
            ax.plot(
                sub["m"], sub["execution_time_ms"],
                marker=MARKER_BY_ALGO[algo],
                color=COLOR_BY_ALGO[algo],
                lw=2, ms=8, label=f"{algo} / {scenario}",
            )
            for m_val, t_val in zip(sub["m"], sub["execution_time_ms"]):
                ax.annotate(
                    f"{m_val:.0e}", (m_val, t_val),
                    textcoords="offset points", xytext=(6, 6),
                    fontsize=7, alpha=0.8,
                )

            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("m (log scale)")
            ax.set_ylabel("execution_time_ms (log scale)")
            ax.set_title(f"{algo} | {scenario} | n = {n_val:,}".replace(",", " "))
            ax.grid(True, which="both", alpha=0.3)
            ax.legend(loc="best", fontsize=9)

            slope = loglog_slope(sub["m"].values, sub["execution_time_ms"].values)
            if np.isfinite(slope):
                ax.text(
                    0.02, 0.98, f"наклон log-log ≈ {slope:.2f}",
                    transform=ax.transAxes, va="top",
                    fontsize=9,
                    bbox=dict(boxstyle="round", fc="white", alpha=0.8),
                )

            plt.tight_layout()
            plt.savefig(OUT_DIR / f"{algo}_{scenario}_n={n_val}.png",
                        dpi=130, bbox_inches="tight")
            plt.close()
            count_a += 1
print(f"\n[A] Индивидуальных графиков: {count_a}")


# =====================================================================
# B. Сравнение всех алгоритмов: compare_{scenario}_n={n}.png
# =====================================================================
count_b = 0
for scenario in available_scenarios:
    for n_val in available_n:
        sub_n = df[
            (df.scenario_name == scenario) & (df.n == n_val)
        ]
        if sub_n.empty:
            continue

        fig, ax = plt.subplots(figsize=(10, 6.5))
        any_line = False
        for algo in available_algos:
            s = sub_n[sub_n.algorithm == algo].sort_values("m")
            if s.empty:
                continue
            any_line = True
            slope = loglog_slope(s["m"].values, s["execution_time_ms"].values)
            slope_txt = f"  (наклон≈{slope:.2f})" if np.isfinite(slope) else ""
            ax.plot(
                s["m"], s["execution_time_ms"],
                marker=MARKER_BY_ALGO[algo],
                color=COLOR_BY_ALGO[algo],
                linestyle=STYLE_BY_ALGO[algo],
                lw=2, ms=7,
                label=f"{algo}{slope_txt}",
            )
        if not any_line:
            plt.close(fig)
            continue

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("m (log scale)")
        ax.set_ylabel("execution_time_ms (log scale)")
        ax.set_title(
            f"Сравнение алгоритмов | {scenario} | n = {n_val:,}".replace(",", " ")
        )
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=9, loc="best")
        plt.tight_layout()
        plt.savefig(OUT_DIR / f"compare_{scenario}_n={n_val}.png",
                    dpi=130, bbox_inches="tight")
        plt.close()
        count_b += 1
print(f"[B] Сравнительных графиков: {count_b}")


# =====================================================================
# C. Обзорный график: все алгоритмы × все n для одного сценария
#    compare_{scenario}_all_n.png
# =====================================================================
count_c = 0
for scenario in available_scenarios:
    sub = df[df.scenario_name == scenario]
    if sub.empty:
        continue
    ns = sorted(sub["n"].unique())

    fig, ax = plt.subplots(figsize=(12, 8))
    # разные n — разные оттенки (alpha); разные алгоритмы — разные цвета
    for algo in available_algos:
        for i, n_val in enumerate(ns):
            s = sub[(sub.algorithm == algo) & (sub.n == n_val)].sort_values("m")
            if s.empty:
                continue
            alpha = 0.35 + 0.65 * (i / max(len(ns) - 1, 1))
            ax.plot(
                s["m"], s["execution_time_ms"],
                marker=MARKER_BY_ALGO[algo],
                color=COLOR_BY_ALGO[algo],
                linestyle=STYLE_BY_ALGO[algo],
                lw=1.5, ms=5, alpha=alpha,
                label=f"{algo} | n={n_val:,}".replace(",", " ") if i == 0 else None,
            )
    # Легенда только по алгоритмам (по одному пункту на цвет)
    handles, labels = ax.get_legend_handles_labels()
    # отфильтруем дубли по метке
    seen, uniq_h, uniq_l = set(), [], []
    for h, l in zip(handles, labels):
        if l and l not in seen:
            seen.add(l)
            uniq_h.append(h)
            uniq_l.append(l)
    ax.legend(uniq_h, uniq_l, fontsize=9, loc="upper left",
              title="алгоритм (оттенок = n)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("m (log scale)")
    ax.set_ylabel("execution_time_ms (log scale)")
    ax.set_title(
        f"{scenario}: все алгоритмы × все n\n"
        f"(цвет = алгоритм, стиль = алгоритм, оттенок = n, тусклее = меньше n)"
    )
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"compare_{scenario}_all_n.png",
                dpi=130, bbox_inches="tight")
    plt.close()
    count_c += 1
print(f"[C] Обзорных графиков: {count_c}")


# =====================================================================
# D. Текстовая сводка: победитель по каждому (scenario, n)
# =====================================================================
print("\n=== Победитель при каждом (scenario, n) — по медиане времени ===")
rows = []
for scenario in available_scenarios:
    for n_val in available_n:
        sub = df[(df.scenario_name == scenario) & (df.n == n_val)]
        if sub.empty:
            continue
        med = sub.groupby("algorithm")["execution_time_ms"].median()
        if med.empty:
            continue
        winner = med.idxmin()
        rows.append({
            "scenario": scenario,
            "n": n_val,
            **{f"{a}": f"{med.get(a, float('nan')):.4f}" for a in available_algos},
            "winner": winner,
        })

summary = pd.DataFrame(rows)
print(summary.to_string(index=False))

# Сохраним сводку в CSV — пригодится для отчёта
summary.to_csv(OUT_DIR / "winners.csv", index=False)
print(f"\nСводка сохранена в {OUT_DIR / 'winners.csv'}")
print(f"Всего файлов в {OUT_DIR.resolve()}: "
      f"{len(list(OUT_DIR.glob('*.png')))} PNG + winners.csv")
