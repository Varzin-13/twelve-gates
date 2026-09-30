# Stress v0.32 Execution-Audit Rerun

**Claim label:** hypothesis  
**Not empirical validation:** yes  
**Runs:** 300  
**Ticks per run:** 520  
**Master seed:** 43  
**Git HEAD:** `a63f83f4efce5a0721047a3edc619339b436700f`

## Provenance

- runner SHA256: `df758a33bb6f79978929ae92cc13cb0b8b4a05fa8abfae7c0bb9bf3dc1b37bd3`
- model SHA256: `89728d8b1614e9c9577ed9421e81ced17e27cb88c345f825ae431a676fad6588`
- canonical baseline-config SHA256: `43723b4bbdebd21c46138230dee299adae7c4695a34209afa8ba4e901b604d4e`
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
