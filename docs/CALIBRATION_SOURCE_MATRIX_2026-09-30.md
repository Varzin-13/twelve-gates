# Twelve Gates — Calibration Source Matrix

**Date:** 2026-09-30  
**Status:** source-screening artifact.  
**Accepted empirical parameter mappings:** **0**

This matrix prevents a common modeling error: finding a reputable dataset and
copying one of its scores directly into a model parameter whose construct,
population, time scale, or uncertainty is different.

## Admission rule

A source can enter a calibration mapping only after all of the following are
specified:

1. modeled construct;
2. source construct;
3. unit of observation;
4. population/case coverage;
5. time period;
6. transformation/mapping function;
7. measurement uncertainty;
8. structural uncertainty;
9. calibration/validation split;
10. falsification criterion.

Until then, the source remains contextual or a candidate target.

| Source | What it measures / unit | Potential Twelve Gates use | Direct parameter mapping now? | Main boundary |
|---|---|---|---|---|
| V-Dem | Country-year indicators; many difficult-to-observe concepts are expert-coded latent estimates with credible regions | Candidate cross-case institutional patterns; uncertainty-aware contextual targets | **NO** | A latent point estimate is not a behavioral probability |
| International IDEA GSoD v10 | Country-year democracy attributes/subattributes assembled from 155 indicators / 23 data sets | Candidate broad institutional validation patterns and triangulation | **NO** | Composite measures mix source types and are not a micro-behavior model |
| World Bank WGI | Annual composite perception-based measures of six governance dimensions, with uncertainty | Broad external context or coarse cross-case patterns | **NO** | World Bank documentation itself cautions that WGI can be too coarse for specific institutional reform design |
| World Values Survey | Population survey responses using common questionnaire and sampling rules | Candidate bounded evidence for attitudes, trust or perceived legitimacy when exact item/population matches | **NO** | Survey item wording, sampling, wave/date, nonresponse and construct mapping must match the modeled variable |
| UCDP GED | Event-level lethal organized violence at specific time/place | Candidate external-shock/event-pattern input for conflict-specific scenarios | **NO** | UCDP event definition covers lethal organized violence, not a generic "crisis load" |
| OECD representative deliberative-process evidence | Process design/evaluation of representative deliberation, including random selection/stratification practices | Pilot-design benchmark and process-evaluation criteria | **NO** | Evidence about deliberative processes does not validate the Twelve Gates national architecture |

## Source notes

### V-Dem
Methodology:
https://www.v-dem.net/about/v-dem-project/methodology/

V-Dem uses expert coding for many latent concepts and a measurement model that
produces point estimates plus uncertainty. A Twelve Gates mapping must therefore
propagate uncertainty and justify construct equivalence.

**Current status:** CONTEXT / CANDIDATE TARGET. No parameter promoted.

### International IDEA — Global State of Democracy Indices v10
Methodology:
https://www.idea.int/publications/catalogue/html/global-state-democracy-indices-methodology-version-10-2026

Technical procedures:
https://www.idea.int/publications/catalogue/global-state-democracy-indices-technical-procedures-guide-version-10-2026

The 2026 methodology describes 155 indicators from 23 data sets and multiple
source types, including expert surveys, standards-based coding, observational
data and composite measures.

**Current status:** CONTEXT / TRIANGULATION. No direct micro-parameter mapping.

### World Bank — Worldwide Governance Indicators
Documentation:
https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation

The WGI are broad composite governance estimates based on multiple survey and
expert sources, with model-based uncertainty. The World Bank documentation
explicitly notes that such aggregate indicators are often too coarse for
specific institutional reform design.

**Current status:** CONTEXT ONLY unless a specific disaggregated source and
mapping are justified.

### World Values Survey
Sampling/fieldwork:
https://www.worldvaluessurvey.org/WVSContents.jsp?CMSID=FieldworkSampling

WVS can potentially provide population-level survey evidence, but only an exact
question/wave/sample matching the modeled construct can be considered. A
generic national trust score must not be substituted for a GateAgent pairwise
trust probability.

**Current status:** CANDIDATE FOR FUTURE ITEM-LEVEL MAPPING; not accepted.

### UCDP Georeferenced Event Dataset
Documentation:
https://ucdp.uu.se/downloads/ged/ged251.pdf

The basic unit is a lethal organized-violence event tied to time and place.
This is potentially useful for external-event scenarios, but it cannot directly
identify the model's generic `crisis_delta`.

**Current status:** CANDIDATE EXTERNAL-EVENT SOURCE; mapping unresolved.

### OECD representative deliberation
Representative-process guidance:
https://www.oecd.org/en/publications/evaluation-guidelines-for-representative-deliberative-processes_10ccbfcb-en/full-report/component-9.html

**Current status:** PILOT DESIGN / EVALUATION BENCHMARK, not national-model
calibration.

## Negative mapping examples

The following are explicitly disallowed unless a separate validated mapping is
created:

- `V-Dem score = coalition theta`;
- `WGI Government Effectiveness = bureaucracy.service_continuity`;
- `WVS institutional trust = GateAgent pairwise trust`;
- `UCDP event count = crisis_delta`;
- `GSoD participation score = public_legitimacy_signal`.

These pairs differ in construct, scale, unit, or data-generating process.

## Next evidence task

The next calibration step is **not** to download all datasets. It is to choose
one model output and write a mapping protocol before seeing whether the desired
data make the model look favorable.

Candidate first targets should be selected by:
- construct match;
- availability of uncertainty;
- replicability;
- temporal/case coverage;
- ability to reserve holdout evidence.

Any accepted mapping must be added to
`simulations/calibration_registry.json` with source/version/method/uncertainty.
