"""Held-out check of MACE-Field against the Harmonic Phonon Database.

The materials have Born charges in the database (pheasy docs) and no Materials
Project dielectric document, so they are likely not in the MACE-Field training
data (MP-Dielectric). The "mp-dielectric" head is compared with the DFPT Born
charges and high-frequency dielectric tensor of each doc, on the doc structure.

Usage: python heldout.py MACEField-MH-0-omat-dielectric.model
"""

import json
import random
import sys
from pathlib import Path

import numpy as np
from mace.calculators import MACECalculator
from mp_api.client import MPRester
from pymatgen.io.ase import AseAtomsAdaptor

MODEL = sys.argv[1]
OUTPUT = Path(__file__).parent / "results" / "heldout.json"
N_MATERIALS = 50
SEED = 0


def select(mpr, elements):
    dielectric = {
        str(doc.material_id)
        for doc in mpr.materials.dielectric.search(
            fields=["material_id"], chunk_size=1000, num_chunks=30
        )
    }
    candidates = {
        str(doc.material_id)
        for doc in mpr.materials.summary.search(
            has_props=["phonon"],
            band_gap=(0.5, None),
            num_sites=(1, 20),
            fields=["material_id"],
            chunk_size=1000,
            num_chunks=60,
        )
    }
    held_out = sorted(candidates - dielectric)
    print(
        f"{len(dielectric)} dielectric docs, {len(candidates)} candidates, "
        f"{len(held_out)} without a dielectric doc"
    )
    random.Random(SEED).shuffle(held_out)

    selected, skipped = {}, {}
    for mp_id in held_out:
        if len(selected) == N_MATERIALS:
            break
        docs = mpr.materials.phonon.search(
            material_ids=[mp_id],
            phonon_method="pheasy",
            fields=["phonon_method", "structure", "born", "epsilon_static"],
            num_chunks=1,
            chunk_size=10,
        )
        docs = [doc for doc in docs if "pheasy" in str(doc.phonon_method).lower()]
        if not docs:
            skipped[mp_id] = "no pheasy doc"
            continue
        doc = docs[0]
        if doc.born is None or np.allclose(doc.born, 0.0):
            skipped[mp_id] = "no Born charges"
        elif doc.epsilon_static is None or np.allclose(
            doc.epsilon_static, np.eye(3), atol=1e-3
        ):
            skipped[mp_id] = "epsilon_static is the identity"
        elif len(doc.born) != len(doc.structure):
            skipped[mp_id] = "Born charges do not cover every site"
        elif not set(doc.structure.atomic_numbers) <= elements:
            skipped[mp_id] = "element not in the model"
        else:
            selected[mp_id] = doc
    return selected, skipped


def main():
    calc = MACECalculator(
        model_paths=MODEL,
        model_type="MACEField",
        device="cpu",
        default_dtype="float64",
        head="mp-dielectric",
    )
    with MPRester() as mpr:
        selected, skipped = select(mpr, set(calc.z_table.zs))
    print(f"selected {len(selected)}, skipped {len(skipped)}")
    reasons = {}
    for reason in skipped.values():
        reasons[reason] = reasons.get(reason, 0) + 1
    print("skip reasons", reasons)

    rows = {}
    for mp_id, doc in selected.items():
        atoms = AseAtomsAdaptor.get_atoms(doc.structure)
        atoms.calc = calc
        atoms.get_potential_energy()
        born = np.array(calc.results["becs"]).reshape(-1, 3, 3)
        eps = np.eye(3) + np.array(calc.results["polarizability"]).reshape(3, 3)
        born_ref = np.array(doc.born)
        eps_ref = np.array(doc.epsilon_static)
        trace = np.trace(born, axis1=1, axis2=2) / 3
        trace_ref = np.trace(born_ref, axis1=1, axis2=2) / 3
        eig = np.linalg.eigvalsh((eps + eps.T) / 2)
        eig_ref = np.linalg.eigvalsh((eps_ref + eps_ref.T) / 2)
        rows[mp_id] = {
            "formula": doc.structure.composition.reduced_formula,
            "nsites": len(doc.structure),
            "born_tensor_mae": float(np.abs(born - born_ref).mean()),
            "born_trace_mae": float(np.abs(trace - trace_ref).mean()),
            "mean_abs_trace_ref": float(np.abs(trace_ref).mean()),
            # a DFPT entry with flipped signs looks like a broken database entry
            "sign_agreement": float(np.mean(np.sign(trace) == np.sign(trace_ref))),
            "asr_ref": float(np.abs(born_ref.sum(axis=0)).max()),
            "eps_mean": float(eig.mean()),
            "eps_mean_ref": float(eig_ref.mean()),
            "eps_eig_rel_err": float(np.mean(np.abs(eig - eig_ref) / eig_ref)),
        }
        row = rows[mp_id]
        print(
            f"{mp_id:>12} {row['formula']:>12} n={row['nsites']:>2} "
            f"Z trace MAE {row['born_trace_mae']:.3f} e "
            f"(mean |Z| {row['mean_abs_trace_ref']:.2f}), "
            f"signs {row['sign_agreement']:.2f}, ASR ref {row['asr_ref']:.2f}, "
            f"eps {row['eps_mean']:.2f} vs {row['eps_mean_ref']:.2f}"
        )

    def summary(keys, label):
        if not keys:
            return
        born_mae = np.mean([rows[k]["born_tensor_mae"] for k in keys])
        trace_mae = np.mean([rows[k]["born_trace_mae"] for k in keys])
        trace_ref = np.mean([rows[k]["mean_abs_trace_ref"] for k in keys])
        eps_err = [rows[k]["eps_eig_rel_err"] for k in keys]
        print(
            f"\n{label}: {len(keys)} materials. Born tensor MAE {born_mae:.3f} e, "
            f"trace MAE {trace_mae:.3f} e on mean |Z| {trace_ref:.2f} e "
            f"({100 * trace_mae / trace_ref:.0f}%). eps_inf eigenvalue error "
            f"mean {100 * np.mean(eps_err):.1f}%, median "
            f"{100 * np.median(eps_err):.1f}%, above 20% for "
            f"{sum(e > 0.2 for e in eps_err)}"
        )

    summary(list(rows), "all")
    summary([k for k in rows if rows[k]["sign_agreement"] == 1.0], "same signs")

    with open(OUTPUT, "w") as file:
        json.dump({"skipped": skipped, "results": rows}, file, indent=1)
    print(f"\nwritten {OUTPUT}")


if __name__ == "__main__":
    main()
