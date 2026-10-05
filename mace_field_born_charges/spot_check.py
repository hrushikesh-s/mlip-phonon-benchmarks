"""Compare MACE-Field Born charges and eps_inf with Materials Project DFPT data.

References, both from mp-api:
- the Harmonic Phonon Database (phonon_method="pheasy"): born and epsilon_static
  of the DFPT run in that workflow, on the structure of that doc
- the MP dielectric data: the electronic dielectric tensor, on the MP structure

MACE-Field gives the Born charges in results["becs"] and the electronic
susceptibility chi in results["polarizability"], so eps_inf = 1 + chi.

Usage: python spot_check.py MACEField-MH-0-omat-dielectric.model
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from mace.calculators import MACECalculator
from mp_api.client import MPRester
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

MODEL = sys.argv[1]
OUTPUT = Path(__file__).parent / "results" / "spot_check.json"
N_MATERIALS = 5
# finite-temperature phonon tutorial first, then the CTE tutorial
FT_TUTORIAL = {
    "Ca3Ir4Sn13": "mp-1200211",
    "AlAsPt5": "mp-1025306",
    "Zn3P2": "mp-2071",
    "Bi4S3N2": "mp-1245549",
    "Er5Tl3": "mp-1105965",
}
CTE_TUTORIAL = {
    "NaCl": "mp-22862",
    "KCl": "mp-23193",
    "MgO": "mp-1265",
    "CaO": "mp-2605",
    "GaAs": "mp-2534",
    "Si": "mp-149",
}


def get_pheasy_doc(mpr, mp_id):
    docs = mpr.materials.phonon.search(
        material_ids=[mp_id],
        phonon_method="pheasy",
        fields=["identifier", "phonon_method", "structure", "born", "epsilon_static"],
        num_chunks=1,
        chunk_size=10,
    )
    docs = [doc for doc in docs if "pheasy" in str(doc.phonon_method).lower()]
    return docs[0] if docs else None


def has_nac(doc):
    return doc.born is not None and not np.all(np.isclose(doc.born, 0.0))


def predict(calc, structure):
    atoms = AseAtomsAdaptor.get_atoms(structure)
    atoms.calc = calc
    start = time.perf_counter()
    atoms.get_potential_energy()
    seconds = time.perf_counter() - start
    becs = np.array(calc.results["becs"]).reshape(-1, 3, 3)
    chi = np.array(calc.results["polarizability"]).reshape(3, 3)
    return becs, np.eye(3) + chi, seconds


def compare_becs(pred, ref, structure):
    """Compare per atom if born covers every site, else per inequivalent atom."""
    ref = np.array(ref)
    if len(ref) == len(structure):
        indices = list(range(len(structure)))
        mapping = "all sites"
    else:
        groups = SpacegroupAnalyzer(structure).get_symmetrized_structure()
        indices = [group[0] for group in groups.equivalent_indices]
        mapping = f"{len(indices)} inequivalent sites"
        if len(indices) != len(ref):
            return {"mapping": f"cannot map {len(ref)} Born charges"}
    pred = pred[indices]
    trace_pred = np.trace(pred, axis1=1, axis2=2) / 3
    trace_ref = np.trace(ref, axis1=1, axis2=2) / 3
    return {
        "mapping": mapping,
        "tensor_mae": float(np.abs(pred - ref).mean()),
        "tensor_max_error": float(np.abs(pred - ref).max()),
        "trace_mae": float(np.abs(trace_pred - trace_ref).mean()),
        "mean_abs_ref_trace": float(np.abs(trace_ref).mean()),
        "species": [str(structure[i].specie) for i in indices],
        "trace_pred": trace_pred.round(3).tolist(),
        "trace_ref": trace_ref.round(3).tolist(),
    }


def main():
    with MPRester() as mpr:
        selected, skipped = {}, {}
        for name, mp_id in {**FT_TUTORIAL, **CTE_TUTORIAL}.items():
            if len(selected) == N_MATERIALS:
                break
            doc = get_pheasy_doc(mpr, mp_id)
            if doc is None:
                skipped[name] = "no pheasy doc"
            elif not has_nac(doc):
                skipped[name] = "no Born charges"
            else:
                selected[name] = (mp_id, doc)
        print("skipped:", skipped)
        print("selected:", {name: value[0] for name, value in selected.items()})
        ids = [mp_id for mp_id, _ in selected.values()]
        dielectric = {
            str(doc.material_id): doc.electronic
            for doc in mpr.materials.dielectric.search(
                material_ids=ids, fields=["material_id", "electronic"]
            )
        }
        # the dielectric docs have no structure, so the MP structure is used
        mp_structures = {
            mp_id: mpr.get_structure_by_material_id(mp_id) for mp_id in ids
        }

    model = torch.load(MODEL, map_location="cpu", weights_only=False)
    heads = list(getattr(model, "heads", ["Default"]))
    del model
    print("heads:", heads)

    results = {}
    for head in heads:
        calc = MACECalculator(
            model_paths=MODEL,
            model_type="MACEField",
            device="cpu",
            default_dtype="float64",
            head=head,
        )
        for name, (mp_id, doc) in selected.items():
            becs, eps, seconds = predict(calc, doc.structure)
            row = {
                "mp_id": mp_id,
                "head": head,
                "natoms": len(doc.structure),
                "seconds": round(seconds, 2),
                "acoustic_sum_rule_max": float(np.abs(becs.sum(axis=0)).max()),
                "born": compare_becs(becs, doc.born, doc.structure),
                "eps_inf_pred": np.round(eps, 3).tolist(),
                "eps_inf_pheasy_db": np.round(doc.epsilon_static, 3).tolist()
                if doc.epsilon_static is not None
                else None,
            }
            if dielectric.get(mp_id) is not None:
                _, eps_mp_struct, _ = predict(calc, mp_structures[mp_id])
                row["eps_inf_pred_mp_structure"] = np.round(eps_mp_struct, 3).tolist()
                row["eps_inf_mp_dielectric"] = np.round(dielectric[mp_id], 3).tolist()
            results[f"{name} | {head}"] = row

            born = row["born"]
            eps_ref = row["eps_inf_pheasy_db"]
            print(
                f"\n{name} ({mp_id}), head {head}, {row['natoms']} atoms, "
                f"{seconds:.1f} s"
            )
            print(
                f"  Born: {born.get('mapping')}, tensor MAE "
                f"{born.get('tensor_mae', float('nan')):.3f} e, max error "
                f"{born.get('tensor_max_error', float('nan')):.3f} e, trace MAE "
                f"{born.get('trace_mae', float('nan')):.3f} e "
                f"(mean |Z| {born.get('mean_abs_ref_trace', float('nan')):.3f} e), "
                f"ASR {row['acoustic_sum_rule_max']:.3f} e"
            )
            print(f"  Z trace pred {born.get('trace_pred')}")
            print(f"  Z trace ref  {born.get('trace_ref')}  {born.get('species')}")
            print(f"  eps_inf diag pred {np.diag(eps).round(2).tolist()}")
            if eps_ref is not None:
                print(f"  eps_inf diag pheasy DB {np.diag(eps_ref).round(2).tolist()}")
            if "eps_inf_mp_dielectric" in row:
                # eigenvalues, since the MP structure may be oriented differently
                eig_mp = np.linalg.eigvalsh(row["eps_inf_mp_dielectric"])
                eig_pred = np.linalg.eigvalsh(row["eps_inf_pred_mp_structure"])
                print(
                    f"  eps_inf eigenvalues MP dielectric {eig_mp.round(2).tolist()}, "
                    f"pred on the MP structure {eig_pred.round(2).tolist()}"
                )

    with open(OUTPUT, "w") as file:
        json.dump({"skipped": skipped, "results": results}, file, indent=1)
    print(f"\nwritten {OUTPUT}")


if __name__ == "__main__":
    main()
