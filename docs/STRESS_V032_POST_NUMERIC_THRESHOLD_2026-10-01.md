# v0.32 Post-Numeric-Threshold Stress Audit

**Claim class:** paired software-effect audit  
**Calibration:** no  
**Empirical validation:** no  
**Runs:** 300 × 520 ticks  
**Master seed:** 43  
**Numerical equality tolerance:** 1e-12

## Why this rerun exists

Repeated binary floating-point additions made 25 × 0.02 appear as a value
slightly above 0.5 and 30 × 0.02 slightly above 0.6. The old strict comparisons
therefore crossed crisis thresholds one tick earlier than the mathematical
decimal model implied.

The corrected helper treats values within a tiny numerical tolerance as equal
to the threshold. Probability draws and coalition theta/power comparisons were
not changed in this correction.

## Paired capture transition

| before numeric fix | after numeric fix | runs |
|---|---|---:|
| false | false | 0 |
| false | true | 7 |
| true | false | 9 |
| true | true | 284 |

- modeled capture rate before: 0.976667
- modeled capture rate after: 0.970000
- difference: -0.006667

## Proposal-count diagnostic

- proposal decisions before: 399600
- proposal decisions after: 398700
- total difference: -900
- mean difference per run: -3.000
- post-fix decisions per run: 1329.000

Under the stress construction, only gates 0/2/4 have sustained crisis-driven
proposal generation. The mathematical expectation after moving the first
proposal from the 25th to 26th shock is one fewer proposal tick × three gates
per run.

## Current post-fix diagnostics

- critical reports per run: 1314.000
- weighted proposal pass fraction: 0.876647
- coalition RMST mean across valid runs: 82.7117220102882
- emergency time share mean: 0.562167
- first-cartel member counts: {"0,2,4": 291}

## Other paired mean differences

- emergency time share: -0.000244
- legacy dissolved coalition duration: -1.286134
- internal legitimacy: +0.000023

## Provenance

- Git HEAD: `85feb934f5bcc3f1686391efae72c8c1699bbe4f`
- runner SHA256: `c687c1c02ef85e8f1ee40977967f09c1a8fc5b4b57bdb5df67afdba7e1c20b36`
- model SHA256: `9940f82e58903ee20539c3fff5f6adbca3a43eb539afa1815a0ea2db8bc3780a`
- config SHA256: `04638dab359df7a232943871b87dcca4d86e50fd0e88455a594c4bcc68fbb217`
- pre-numeric artifact SHA256: `9a9ff390ded2866a674a1f14a3a37964a416e73ae82cd4992d837d8779ef1132`

## Interpretation boundary

This is a paired audit of a numerical implementation correction inside an
uncalibrated model. It is not evidence for a real-world political outcome.
