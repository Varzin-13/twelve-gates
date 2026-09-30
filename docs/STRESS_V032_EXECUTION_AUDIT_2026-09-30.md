# Stress v0.32 Execution-Audit Rerun

**Claim label:** hypothesis  
**Not empirical validation:** yes  
**Runs:** 300  
**Ticks per run:** 520  
**Master seed:** 43  
**Git HEAD:** `05f1ed155fa49a571fb07ea83a2ef19818e9d389`

## Provenance

- runner SHA256: `cd673733f63f8600597c1a0ea932e54cd6514ad47474c16f838f24ec66b2d981`
- model SHA256: `538ec17f277d949b17e382c5af350574891fce804c3723a167b70b0ce814d020`
- canonical baseline-config SHA256: `c83c03fe5953c312df2bd5c2de49356aec52a775dae5bc7565344d3e42507181`
- stress start tick: `52`
- stressed gates: `[0, 2, 4]`

## Historical artifact vs current implementation

| Metric | Historical stored stress | v0.32 current rerun | Difference |
|---|---:|---:|---:|
| Cartel capture rate | 1.000000 | 0.973333 | -0.026667 |
| Emergency time share | 0.635615 | 0.562353 | -0.073263 |
| Mean coalition duration | 43.330846 | 32.770791 | -10.560055 |
| Internal legitimacy | 0.617225 | 0.617157 | -0.000068 |
| Mean capture pressure | 0.580667 | 0.579971 | -0.000696 |

## Interpretation boundary

This rerun measures behavior of the current code under the current uncalibrated
scenario assumptions. It does not estimate the probability of a real political
outcome.

The current implementation differs from the historical artifact in several
software-logical respects, including:
- stress timing is actually gated at tick 52;
- resource shares are conserved;
- emergency extension uses explicit individual simulated votes plus a threshold;
- coalition pair scores preserve both directions rather than execution-order overwrite;
- cartel duration and consecutive passed decisions are distinct criteria;
- failed coalition decisions reset the consecutive-decision streak;
- dissent recording no longer consumes an unused extra random draw.

Because the implementation changed, historical output must not be relabeled as
if it came from this version. The old artifact remains preserved separately.
