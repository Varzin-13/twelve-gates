# Twelve Gates | دوازده گیت

**Research framework under audit — not an implementation-ready governance plan.**

**چارچوب پژوهشی تحت ممیزی — نه طرح آمادهٔ اجرا برای حکمرانی.**

Twelve Gates is an auditable research framework and executable **hypothesis model** for a proposed decentralized, twelve-gate institutional design for Iran. The written proposal examines rotating council roles, Gate Zero, Mirror-13, emergency authority, and risks of concentrated material power. Code and stored simulations make selected assumptions inspectable; they do not establish that the institutions would work in practice or predict political outcomes.

دوازده گیت یک چارچوب پژوهشی برای طراحی و نقد نهادی است. شبیه‌سازی‌ها رفتار مدل را **تحت فرض‌های مشخص** نشان می‌دهند، نه اعتبار تجربی طرح یا پیش‌بینی آیندهٔ ایران.

## Research framework | چارچوب پژوهش

The design documents ask how a decentralized council might distribute authority while facing coalition capture, prolonged emergency powers, coordination failure, and infrastructure disruption. They also retain unresolved problems and rejected proposals. Start with the [current design and audit history](CHANGELOG.md), the [public project framing](index.html), and the [contribution guide](CONTRIBUTING.md). Written proposals, software behavior, simulation outputs, and real-world evidence are different kinds of claims.

## Executable model | مدل اجرایی

[simulations/twelve_gates_model.py](simulations/twelve_gates_model.py) implements a twelve-gate agent-based **hypothesis model** with manually staged updates, coalition and emergency logic, and simplified institutional components. It does not require the Mesa package. Gate Zero's appeal board is a placeholder, and other institutional behaviors are simplified. The executable model is intended to make assumptions inspectable and hypotheses testable in code. **It is not empirically calibrated for real-world prediction.**

[simulations/run_model.py](simulations/run_model.py) provides an `argparse` CLI with `--config`, `--n-runs`, `--max-ticks`, `--seed`, `--shock`, `--shock-magnitude`, `--out`, and `--list-params`. It normalizes numeric JSON dictionary keys and performs partial config validation. The CLI warns if a config lacks `claim_label: hypothesis`; it does not make an uncalibrated config valid for prediction.

## Parameter provenance | منشأ پارامترها

The [parameter register](simulations/param_provenance.py) classifies **18 tracked parameter groups: 6 `DOCUMENT`, 3 `DESIGN`, and 9 `ARBITRARY`/uncalibrated**.

| Label | Meaning | Evidential boundary |
|---|---|---|
| `DOCUMENT` | An explicit rule or value in the project's source design document | Source-document provenance, **not** empirical calibration |
| `DESIGN` | An engineered project choice | Documented choice, not a measured constant |
| `ARBITRARY` | A scenario assumption without supporting calibration data | Its numerical effect must be tested and reported conditionally |

The majority of tracked parameter groups are uncalibrated; consequential examples include coalition thresholds, initial executive power, trust matrices, and institutional-response assumptions. The model and stored baseline config retain `claim_label: hypothesis`. **فرضیه، نه پیش‌بینی:** source-document rules and runnable code do not turn scenario parameters into measured facts.

## Three documented independent simulation questions | سه پرسش شبیه‌سازی مستقل

[simulations/README.md](simulations/README.md) identifies **three explicitly documented preregistered independent simulation questions/scripts**. The scripts state questions and failure criteria; an external, timestamped preregistration record has not been verified from this repository. Their outputs are simulation-only and depend on stipulated inputs.

| Script and question | Stored result under its assumptions | Essential limitation |
|---|---|---|
| [Scenario 1: coalition capture](simulations/scenario1_coalition_capture.py) — does a security–energy–economy coalition remain influential after proposed mitigations? | [Stored output](simulations/results/scenario1_results.json): mean modeled capture `0.2815 → 0.2392` (about 15.0% reduction); mitigated random-trio control `0.0990`. | Collusion, leverage, and mitigation effects are assumed; this is not a measured capture rate. |
| [Scenario 2: emergency institutionalization](simulations/scenario2_emergency_institutionalization.py) — does a 14-day fuse with judicial review prevent prolonged emergency powers? | [Stored output](simulations/results/scenario2_results.json): mean emergency share of **war-active cycles** `0.7601 → 0.6982` with the modeled judicial check. | War continuation and judicial independence are assumed. The mean with review does **not** meet the script's stated `>80%` failure threshold; its separate `>50%` observation must not be confused with that threshold. |
| [Scenario 3: simultaneous failure](simulations/scenario3_simultaneous_failure.py) — does geographic distribution shorten modeled recovery after a single-city disaster? | [Stored output](simulations/results/scenario3_results.json): mean modeled recovery `39.36`, `32.22`, and `20.56` days for one, two, and three cities. | The script stipulates which components are damaged and uses assumed repair times; it omits wider network failures. |

These figures are **committed results, not independently rerun results in this README**. They describe program outputs under specified assumptions, not forecasts for Iran.

## Additional scenarios and diagnostics | سناریوها و ابزارهای دیگر

The repository also contains [scenario 4](simulations/scenario4_guardian_model_deadline.py) and [scenario 5](simulations/scenario5_ncri_coalition.py), which model other transition proposals. Their headers use preregistration language, but they are **additional scripts**, not part of the three-script set explicitly identified by `simulations/README.md`; their external registration status and empirical calibration are not established here. Other diagnostic artifacts include [baseline](simulations/run_baseline.py), [stress](simulations/run_stress.py), and [sensitivity](simulations/sensitivity_analysis.py) runners. Do not pool their outputs or treat a comparison of hypothetical designs as evidence about a real organization.

The [stored baseline](simulations/results/mesa_baseline_results.json) and [stored stress output](simulations/results/mesa_stress_results.json) both carry `claim_label: hypothesis`. `run_baseline.py` is configured for **300 runs**, reduced from a **3,000-run specification** for computational-time reasons; a 3,000-run baseline is not claimed. `run_stress.py` describes its run as a **functional sanity check**, not empirical validation. Its header says the shock begins at tick 52, while the current driver code does not visibly gate the shock by tick; treat the timing as unresolved.

The [stored sensitivity output](simulations/results/sensitivity_results.json) changes sharply with some assumed inputs: modeled cartel capture is `1.0` at coalition threshold `0.60` and `0.0` at `0.65` in its recorded runs. This demonstrates parameter dependence within the model, **not** empirical validity. The sensitivity script's header describes 150 runs per variant, but its current executable setting is `N_RUNS = 40` and `MAX_TICKS = 400`; use the executable settings when describing that artifact.

## Reproduce and inspect | بازتولید و بررسی

From the repository root, use a Python environment with NumPy for the model and Matplotlib for chart-producing scenario scripts. This repository does not currently provide a pinned dependency manifest. FreeSerif improves Persian chart rendering but is not required for numerical execution.

```bash
cd simulations
python3 test_model.py
python3 param_provenance.py
python3 run_model.py --list-params
python3 run_model.py --config results/baseline_config.json --n-runs 1 --max-ticks 10 --seed 42 --out /tmp/twelve-gates-demo.json
```

The committed [baseline configuration](simulations/results/baseline_config.json) has twelve gates, passes the CLI's current validator, and declares `claim_label: hypothesis`. The [model guide](README_mesa.md) gives further context; its example config path should be read as `results/baseline_config.json` when run from `simulations/`. The existing [test script](simulations/test_model.py) has **22 checks in eight test functions**; it checks selected software properties, not the political model's empirical validity. Several batch/scenario scripts write outputs to hard-coded `/home/claude/` paths, so they may need an appropriate output environment before rerunning unchanged. Stored JSON results and charts remain available under `simulations/results/` and `simulations/`.

**Reproducibility means that computational procedures and assumptions are exposed for inspection and rerunning; it does not establish empirical validity of the underlying institutional assumptions.**

**بازتولیدپذیری محاسباتی، جایگزین کالیبراسیون و آزمون تجربی نهادی نیست.**

## Repository map | راهنمای مخزن

- `README.md`, [README_mesa.md](README_mesa.md), [CHANGELOG.md](CHANGELOG.md), and [CONTRIBUTING.md](CONTRIBUTING.md): project overview, model guide, corrective history, and critique process.
- `index.html` and Persian design/legal/history documents: public presentation and documentary proposals; these are not executable or legally adopted institutions.
- `simulations/twelve_gates_model.py`, `run_model.py`, and `param_provenance.py`: model, CLI, and parameter register.
- `simulations/scenario*.py`, `run_baseline.py`, `run_stress.py`, and `sensitivity_analysis.py`: distinct scenarios and diagnostics.
- `simulations/results/`: committed configuration and reported output JSON; inspect each result with its own script and assumptions.

## Limits and claim discipline | محدودیت‌ها و مرز ادعا

No real-world parameter calibration, institutional pilot, legal adoption, or predictive accuracy is established by this repository. The model includes placeholders; simulation behavior may change materially with parameter choices. The written record preserves negative and corrective findings and open phases in [CHANGELOG.md](CHANGELOG.md). Claims of external audit completion, implementation readiness, or real-world success require evidence beyond runnable code and internal results.

Licensing scope is **unreconciled**: [LICENSE](LICENSE) states MIT terms for code and written research material, while [LICENSE.md](LICENSE.md) states CC BY-SA 4.0 for documents, code, and related content. Neither file is silently selected as the repository-wide rule here.

## Contribute and critique | مشارکت و نقد

The project invites counterexamples, code or statistical error reports, missed sources, and identified overclaims through [Issues and the contribution guide](CONTRIBUTING.md). Cite the specific script, config, result file, or document section when discussing a claim; preserve its date, assumptions, and correction history. Author/contact information appears in [LICENSE.md](LICENSE.md); a preferred formal citation has not been established in this README.
