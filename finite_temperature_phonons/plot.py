"""Plot the finite-temperature phonon results in results.json.

Usage: python plot.py
The figures are written to figures/.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
FIGURES = HERE / "figures"
RESULTS = json.loads((HERE / "results.json").read_text())
MODELS = list(RESULTS["models"])
LABELS = RESULTS["models"]
TEMPERATURES = RESULTS["temperatures_K"]
MATERIALS = RESULTS["materials"]


def legend_below(fig, ax, ncol=3):
    """Put one legend for all panels below the figure."""
    fig.legend(
        *ax.get_legend_handles_labels(),
        loc="upper center",
        ncol=ncol,
        bbox_to_anchor=(0.5, 0.0),
        frameon=False,
    )


def plot_max_frequency():
    """Highest frequency against temperature in the PBEsol cell, with AIMD at 300 K."""
    fig, axes = plt.subplots(1, len(MATERIALS), figsize=(16, 3.4))
    for ax, (name, data) in zip(axes, MATERIALS.items(), strict=True):
        for model in MODELS:
            ax.plot(
                TEMPERATURES,
                data["pbesol_cell"]["max_frequency_THz"][model],
                "o-",
                label=LABELS[model],
            )
        ax.plot(
            300,
            data["aimd_300K"]["max_frequency_THz"],
            "k*",
            ms=12,
            label="AIMD, 300 K",
        )
        ax.set_title(name)
        ax.set_xlabel("Temperature (K)")
    axes[0].set_ylabel("Highest frequency (THz)")
    fig.tight_layout()
    legend_below(fig, axes[0], ncol=4)
    fig.savefig(FIGURES / "max_frequency.png", dpi=200, bbox_inches="tight")


def plot_mae_300k():
    """Mean absolute difference from AIMD at 300 K over the whole band path."""
    names = list(MATERIALS)
    x = np.arange(len(names))
    width = 0.27
    fig, ax = plt.subplots(figsize=(7, 3.4))
    for idx, model in enumerate(MODELS):
        values = [MATERIALS[name]["aimd_300K"]["mae_THz"][model] for name in names]
        ax.bar(x + (idx - 1) * width, values, width, label=LABELS[model])
    ax.set_xticks(x, names)
    ax.set_ylabel("Difference from AIMD (THz)")
    ax.set_title("Mean absolute difference from AIMD at 300 K")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "mae_300K.png", dpi=200, bbox_inches="tight")


def plot_volume():
    """Volume relative to PBEsol: relaxed 0 K cell, then the NPT cell."""
    fig, axes = plt.subplots(1, len(MATERIALS), figsize=(16, 3.4))
    for ax, (name, data) in zip(axes, MATERIALS.items(), strict=True):
        for model in MODELS:
            ax.plot(
                (0, *TEMPERATURES),
                data["npt_cell"]["volume_ratio_0K_then_T"][model],
                "o-",
                label=LABELS[model],
            )
        ax.axhline(1, color="black", ls="--", lw=0.8)
        ax.set_title(name)
        ax.set_xlabel("Temperature (K)")
    axes[0].set_ylabel("Volume / PBEsol volume")
    fig.tight_layout()
    legend_below(fig, axes[0])
    fig.savefig(FIGURES / "volume.png", dpi=200, bbox_inches="tight")


def plot_cell_effect():
    """Highest frequency in the PBEsol cell, the relaxed 0 K cell and the NPT cell."""
    fig, axes = plt.subplots(
        len(MODELS), len(MATERIALS), figsize=(16, 8.5), sharex=True
    )
    cells = (
        ("PBEsol cell", "pbesol_cell", "o-"),
        ("relaxed 0 K cell", "relaxed_cell", "s--"),
        ("NPT cell", "npt_cell", "^:"),
    )
    for col, (name, data) in enumerate(MATERIALS.items()):
        for row, model in enumerate(MODELS):
            ax = axes[row, col]
            for label, key, style in cells:
                ax.plot(
                    TEMPERATURES,
                    data[key]["max_frequency_THz"][model],
                    style,
                    label=label,
                )
            if row == 0:
                ax.set_title(name)
            if col == 0:
                ax.set_ylabel(f"{LABELS[model]}\nHighest frequency (THz)")
            if row == len(MODELS) - 1:
                ax.set_xlabel("Temperature (K)")
    fig.tight_layout()
    legend_below(fig, axes[0, 0])
    fig.savefig(FIGURES / "cell_effect.png", dpi=200, bbox_inches="tight")


def plot_md_settings():
    """Difference from AIMD for KNaICl at 300 K against MD length and snapshots."""
    grid = RESULTS["md_settings_grid"]
    fig, axes = plt.subplots(1, len(MODELS), figsize=(13, 3.6))
    for ax, model in zip(axes, MODELS, strict=True):
        mae = np.array(grid["mae_THz"][model])
        image = ax.imshow(mae, cmap="viridis", vmin=0.08, vmax=0.20)
        for i in range(mae.shape[0]):
            for j in range(mae.shape[1]):
                mark = " *" if grid["imaginary_modes"][model][i][j] else ""
                ax.text(
                    j, i, f"{mae[i, j]:.3f}{mark}", ha="center", va="center", color="w"
                )
        ax.set_xticks(range(len(grid["n_snapshots"])), grid["n_snapshots"])
        ax.set_yticks(
            range(len(grid["md_time_ps"])), [f"{t} ps" for t in grid["md_time_ps"]]
        )
        ax.set_xlabel("Number of snapshots")
        ax.set_title(LABELS[model])
    fig.colorbar(image, ax=axes, label="Difference from AIMD (THz)")
    fig.savefig(FIGURES / "md_settings_KNaICl.png", dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    plot_max_frequency()
    plot_mae_300k()
    plot_volume()
    plot_cell_effect()
    plot_md_settings()
