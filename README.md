# MLIP phonon benchmarks

Benchmarks of machine-learned interatomic potentials (MLIPs) for lattice
dynamics. Each study compares the potentials with DFT or ab initio MD and
gives its numbers, figures and scripts. The workflows behind them are in
[atomate2](https://github.com/materialsproject/atomate2).

## Studies

### [Finite-temperature phonons](finite_temperature_phonons)

Effective harmonic phonons from MD at 100 to 900 K with three MACE foundation
potentials, for five crystals that are unstable or polar at 0 K. Compared with
ab initio MD at 300 K, the best potential for each material is within 0.07 to
0.15 THz on average over the band path. No potential is best for all five.

![Highest frequency against temperature](finite_temperature_phonons/figures/max_frequency.png)

### [Born charges from MACE-Field](mace_field_born_charges)

Born effective charges and high-frequency dielectric constants from MACE-Field,
compared with DFPT for 50 materials that are not in its training data. The
Born charge trace is off by 0.26 e on average, 11% of its mean size. The
dielectric constant is off by 8.2% on average.

## Reference data

The DFT reference comes from the Materials Project's Harmonic Phonon Database
(H. Sahasrabuddhe et al., ChemRxiv (2026),
[doi:10.26434/chemrxiv.15004632/v1](https://doi.org/10.26434/chemrxiv.15004632/v1)).
It is read with [mp-api](https://github.com/materialsproject/api). The ab
initio MD reference of the first study is not public yet. Only its summary
numbers are given.

## Plotting

```
pip install -r requirements.txt
python finite_temperature_phonons/plot.py
python mace_field_born_charges/plot.py
```

## License

MIT. The MACE models have their own licenses.
