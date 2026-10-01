# Twelve Gates | دوازده گیت — v0.32

**چارچوب پژوهشی قابل‌ممیزی برای طراحی نهادی — نه طرح آمادهٔ اجرا و نه پیش‌بینی سیاسی.**

Twelve Gates is an auditable institutional-design research project with an executable hypothesis model, formal/software checks, parameter-provenance tracking, sensitivity analysis and frozen reproducibility artifacts.

> Current scientific boundary: the model is reproducible, but it is not empirically calibrated for real-world political prediction. The calibration registry currently accepts **0 empirical parameter mappings**.

## Start here | شروع از اینجا

- **[Final v0.32 Research Status](docs/FINAL_RESEARCH_STATUS_v0.32.md)** — current technical summary
- **[Public project page](https://varzin-13.github.io/twelve-gates/)** — public landing page
- **[Scientific execution audit](docs/SCIENTIFIC_EXECUTION_AUDIT_2026-09-30.md)**
- **[ABM v2 ODD specification](docs/ABM_V2_ODD_SPEC.md)**
- **[Formal execution specification](docs/FORMAL_EXECUTION_SPEC_v0_1.md)**
- **[Calibration & validation plan](docs/ABM_V2_CALIBRATION_VALIDATION_PLAN.md)**

## Current technical status

| Layer | v0.32 status |
|---|---|
| Executable twelve-gate ABM | Implemented as a hypothesis model |
| Regression / interface / invariant checks | Automated in GitHub Actions |
| Parameter provenance | Machine-readable |
| Active vs inert mechanism audit | Machine-readable |
| Frozen result artifacts | Protected by Git blob hashes |
| Formal layer | TLA+ research skeleton + finite-state checker |
| Accepted empirical calibration mappings | **0** |
| Real-world predictive validity | **Not established** |
| Implementation readiness | **Not established** |## Key model findings — with claim boundary

These are properties/results of the model under its assumptions, not probabilities of real political outcomes.

- Latest frozen 300×520 stress lineage after implementation/numeric corrections: coded capture endpoint **0.9700**.
- Post-budget LHS screening: coded capture spans **0–1** across the exploratory parameter space; strongest rank associations are theta_pair ≈ **−0.707** and material-power multiplier ≈ **+0.577**.
- The coded material-triad power boundary is mathematically **1.8 / 2.30 = 0.7826086957...**
- Refined phase mapping shows zero modeled capture immediately below that power boundary and theta-dependent behavior immediately above it.
- Structural alternatives for bilateral coalition-score aggregation change some outputs, showing structural-model uncertainty.
- The fixed +6 audit schedule covers 12 of 132 possible non-self ordered coordinator-to-auditor pairs in one cycle.

Full details and provenance: **[Final v0.32 Research Status](docs/FINAL_RESEARCH_STATUS_v0.32.md)**.

## Reproduce

Requirements: Python 3 and NumPy.

    cd simulations
    python3 test_model.py
    python3 test_institutional_interfaces.py
    python3 validate_calibration_registry.py
    python3 validate_parameter_usage_registry.py
    python3 validate_frozen_artifacts.py
    python3 audit_schedule.py

Then:

    cd ..
    python3 formal/abstract_model_check.py

The active CI workflow is .github/workflows/execution-audit.yml.
Completed one-off experiment workflows are intentionally removed after their results are frozen.

## Repository map

- index.html — public GitHub Pages landing page
- docs/FINAL_RESEARCH_STATUS_v0.32.md — single current status document
- docs/ — formal, methodological and audit documentation
- simulations/twelve_gates_model.py — executable ABM core
- simulations/run_model.py — CLI runner
- simulations/results/ — frozen and versioned result artifacts
- simulations/results/FROZEN_ARTIFACT_MANIFEST.json — artifact integrity manifest
- formal/ — formal-specification research layer
- CHANGELOG.md — correction and development history## Claim discipline

This repository distinguishes:
- software/mathematical properties;
- simulation results conditional on model assumptions;
- empirical institutional claims;
- normative/constitutional choices.

Evidence from one class is not automatically promoted into another.

The project does not claim that code, algebra, cryptography or simulation can manufacture founding legitimacy, public acceptance, compliance, or successful political transition.

Historical scripts/results remain where necessary for reproducibility and are not the recommended starting point for new readers.

## License

- Software/code: [MIT](LICENSE)
- Research prose/documentation: [CC BY-SA 4.0](LICENSE.md)

## Critique and contributions

Counterexamples, reproducibility problems, statistical errors, missed sources and identified overclaims are welcome through GitHub Issues and [CONTRIBUTING.md](CONTRIBUTING.md).
