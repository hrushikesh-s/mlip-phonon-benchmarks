## Hi, I'm Hrushikesh

[Google Scholar](https://scholar.google.com/citations?user=Ukq_tbUAAAAJ&hl=en) · [LinkedIn](https://www.linkedin.com/in/hrushikesh-s-096965149/) · hpsahasrabuddhe@lbl.gov

I am a PhD candidate in Materials Science and Engineering at UC Berkeley and Lawrence Berkeley National Laboratory, in [Anubhav Jain's group](https://github.com/hackingmaterials).
I work on machine learning for materials at scale.
I built the Materials Project's Harmonic Phonon Database, with the phonons of about 26,000 inorganic crystals from about 238,000 node-hours on NERSC Perlmutter and NREL Kestrel.
I benchmark and fine-tune machine-learned interatomic potentials such as MACE for phonons and thermal expansion.
Most of my code goes into [atomate2](https://github.com/materialsproject/atomate2) and the [Materials Project](https://next-gen.materialsproject.org).

### Selected papers

1. **A High-Throughput ab initio Database of Harmonic Phonon Properties for Inorganic Crystals.** H. Sahasrabuddhe et al. ChemRxiv (2026), under review at Scientific Data. [doi:10.26434/chemrxiv.15004632/v1](https://doi.org/10.26434/chemrxiv.15004632/v1)
2. **Atomate2: modular workflows for materials science.** A. M. Ganose et al. Digital Discovery (2025). [doi:10.1039/D5DD00019J](https://doi.org/10.1039/D5DD00019J)
3. **Zatom-1: Towards a Multimodal Foundation Model for 3D Molecules and Materials.** A. Morehead et al. arXiv (2026). [arXiv:2602.22251](https://arxiv.org/abs/2602.22251)
4. **AlabOS: a Python-based reconfigurable workflow management framework for autonomous laboratories.** Y. Fei et al. Digital Discovery (2024). [doi:10.1039/D4DD00129J](https://doi.org/10.1039/D4DD00129J)

### Benchmarks

[mlip-phonon-benchmarks](https://github.com/hrushikesh-s/mlip-phonon-benchmarks) computes phonons from 100 to 900 K with three MACE potentials and compares them with ab initio MD at 300 K.
It also checks the Born charges and dielectric constants of MACE-Field against DFPT for 50 held-out materials.

### Workflows in atomate2

| Pull request | Status |
|---|---|
| [Lattice dynamics workflow using Pheasy](https://github.com/materialsproject/atomate2/pull/1063) | merged Sep 2026 |
| [Harmonic lattice dynamics workflow using hiPhive](https://github.com/materialsproject/atomate2/pull/1062) | merged Sep 2026 |
| [Thermal expansion workflow (CTEMaker)](https://github.com/materialsproject/atomate2/pull/1559) | merged Oct 2026 |
| [Finite-temperature phonon workflow](https://github.com/materialsproject/atomate2/pull/1560) | in review |

### New features

| Pull request | Status |
|---|---|
| [Force field Born charges and dielectric tensors with MACE-Field (atomate2)](https://github.com/materialsproject/atomate2/pull/1573) | approved |
| [JobStore document format as a pydantic model (jobflow)](https://github.com/materialsproject/jobflow/pull/424) | merged Oct 2023 |
| [Integration of Matbench Discovery (matbench)](https://github.com/materialsproject/matbench/pull/236) | merged Mar 2023 |
| ["Go to page" navigation in the web GUI (FireWorks)](https://github.com/materialsproject/fireworks/pull/572) | merged Mar 2026 |
| [New mock decorator and config update (alabos)](https://github.com/CederGroupHub/alabos/pull/49) | merged Feb 2024 |

### Bug fixes

| Pull request | Status |
|---|---|
| [Fix pheasy anharmonic fitting and add fit options (atomate2)](https://github.com/materialsproject/atomate2/pull/1558) | merged Oct 2026 |
| [Fix the acoustic sum rule in PhononBSDOSDoc (emmet)](https://github.com/materialsproject/emmet/pull/1447) | merged May 2026 |
| [Fix the Clarke thermal conductivity key between pymatgen and atomate2 (atomate2)](https://github.com/materialsproject/atomate2/pull/1448) | merged Mar 2026 |
| Pydantic v2 migration of atomate2 ([#558](https://github.com/materialsproject/atomate2/pull/558), [#565](https://github.com/materialsproject/atomate2/pull/565), [#566](https://github.com/materialsproject/atomate2/pull/566), [#567](https://github.com/materialsproject/atomate2/pull/567)) | merged Oct 2023 |
| [Use dumpfn as the default JSON writer (matbench)](https://github.com/materialsproject/matbench/pull/251) | merged Apr 2023 |

### Documentation and citations

- atomate2: [phonon database preprint in the pheasy docs](https://github.com/materialsproject/atomate2/pull/1551), [Zenodo DOI](https://github.com/materialsproject/atomate2/pull/1211), [ChemRxiv citation](https://github.com/materialsproject/atomate2/pull/1107)
- matbench: [scaled error formula for classification tasks](https://github.com/materialsproject/matbench/pull/257), [link to Matbench Discovery on the leaderboard](https://github.com/materialsproject/matbench/pull/253)
- alabos: [tooling to streamline the commit and PR flow](https://github.com/CederGroupHub/alabos/pull/37), [installation docs](https://github.com/CederGroupHub/alabos/pull/46)
