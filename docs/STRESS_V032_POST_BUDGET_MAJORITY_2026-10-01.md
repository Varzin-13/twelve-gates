# v0.32 Post-Budget-Majority Stress Audit

**Claim class:** paired software-effect audit  
**Calibration:** no  
**Empirical validation:** no  
**Runs:** 300 × 520 ticks  
**Master seed:** 43  
**Required budget yes votes:** [8]

## Why this rerun exists

The documented/configured budget reallocation rule was two thirds, but the old
implementation passed proposals at 7/12 votes. The corrected implementation
requires 8/12.

This rerun uses the same 300 seeds as the immediately preceding v0.32 stress
artifact so the before/after comparison is paired.

## Paired capture transition

| pre-budget code | corrected code | runs |
|---|---|---:|
| false | false | 4 |
| false | true | 4 |
| true | false | 3 |
| true | true | 289 |

- pre-budget modeled capture rate: 0.973333
- post-fix modeled capture rate: 0.976667
- difference: +0.003333

## Current corrected-code summaries

- emergency time share mean: 0.562410
- legacy dissolved-only coalition duration mean: 31.629582
- censoring-aware coalition RMST mean across valid runs: 86.15282795880591
- proposal decisions: 399600
- proposal passes: 350051
- proposal failures: 49549
- weighted proposal pass fraction: 0.8760035035035035

## Other paired mean differences

- emergency time share: +0.000058
- legacy coalition duration: -1.141209
- internal legitimacy: +0.000005

## Provenance

- Git HEAD: `f20acf64006ecf59f3edf68b837fdf9bf7a3693e`
- runner SHA256: `8febfd00a588036880712e0a17673d7d58e0dca196d4a27bbd0b70023daf6fef`
- model SHA256: `15f93ce1719939c1d7544e3b36adfb693aac8137f13a18968b63ec2a4662f6ef`
- canonical config SHA256: `04638dab359df7a232943871b87dcca4d86e50fd0e88455a594c4bcc68fbb217`
- pre-budget artifact SHA256: `78c4dfb54fffb8f7db135c4a385278016053c911d2ab57a0d355f74dc1768b41`

## Interpretation boundary

This document measures how a specific implementation correction changes the
output of the coded, uncalibrated model under matched seeds. It is not evidence
for the real-world probability of any political outcome.
