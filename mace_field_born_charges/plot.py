"""Plot the held-out MACE-Field results in results/heldout.json.

Usage: python plot.py
The figure is written to figures/heldout.png and a summary is printed.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
ROWS = json.loads((HERE / "results" / "heldout.json").read_text())["results"]


def main():
    rows = list(ROWS.values())
    z_ref = np.array([row["mean_abs_trace_ref"] for row in rows])
    z_mae = np.array([row["born_trace_mae"] for row in rows])
    eps = np.array([row["eps_mean"] for row in rows])
    eps_ref = np.array([row["eps_mean_ref"] for row in rows])
    eps_err = np.array([row["eps_eig_rel_err"] for row in rows])

    fig, (ax_z, ax_eps) = plt.subplots(1, 2, figsize=(10, 4.2))

    ax_z.scatter(z_ref, z_mae, s=18)
    ax_z.set_xlabel("Mean |Z*| from DFPT (e)")
    ax_z.set_ylabel("MAE of the Born charge trace (e)")
    ax_z.set_title("Born effective charges")

    ax_eps.scatter(eps_ref, eps, s=18)
    low = 0.9 * min(eps.min(), eps_ref.min())
    top = 1.1 * max(eps.max(), eps_ref.max())
    line = np.array([low, top])
    ax_eps.plot(line, line, "k-", lw=0.8)
    ax_eps.plot(line, 1.2 * line, "k:", lw=0.8, label="20%")
    ax_eps.plot(line, 0.8 * line, "k:", lw=0.8)
    ax_eps.set_xscale("log")
    ax_eps.set_yscale("log")
    ax_eps.set_xlim(low, top)
    ax_eps.set_ylim(low, top)
    ticks = [t for t in (1, 2, 3, 5, 10, 20, 30, 50) if low <= t <= top]
    ax_eps.minorticks_off()
    ax_eps.set_xticks(ticks, ticks)
    ax_eps.set_yticks(ticks, ticks)
    ax_eps.set_aspect("equal")
    ax_eps.set_xlabel(r"$\varepsilon_\infty$ from DFPT")
    ax_eps.set_ylabel(r"$\varepsilon_\infty$ from MACE-Field")
    ax_eps.set_title("High-frequency dielectric constant")
    ax_eps.legend(frameon=False)

    # label the materials with the largest errors
    for idx in np.argsort(z_mae)[-1:]:
        ax_z.annotate(
            rows[idx]["formula"],
            (z_ref[idx], z_mae[idx]),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
        )
    for idx in np.argsort(eps_err)[-2:]:
        ax_eps.annotate(
            rows[idx]["formula"],
            (eps_ref[idx], eps[idx]),
            xytext=(0, -6),
            textcoords="offset points",
            # left of the point in the upper half of the range, else right of it
            ha="right" if eps_ref[idx] > np.sqrt(low * top) else "left",
            va="top",
            fontsize=8,
        )

    fig.tight_layout()
    (HERE / "figures").mkdir(exist_ok=True)
    fig.savefig(HERE / "figures" / "heldout.png", dpi=200, bbox_inches="tight")

    print(
        f"{len(rows)} materials. Born tensor MAE "
        f"{np.mean([row['born_tensor_mae'] for row in rows]):.3f} e, trace MAE "
        f"{z_mae.mean():.2f} e on mean |Z*| {z_ref.mean():.2f} e "
        f"({100 * z_mae.mean() / z_ref.mean():.0f}%). eps_inf error mean "
        f"{100 * eps_err.mean():.1f}%, median {100 * np.median(eps_err):.1f}%, "
        f"above 20% for {int((eps_err > 0.2).sum())}"
    )


if __name__ == "__main__":
    main()
