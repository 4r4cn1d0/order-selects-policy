# The geometry program (ICML-era; consolidated 2026-08-18)

## How many axes is too many -- the compass analogy
The model's internal space is a compass rose: name as many directions as you
like, but only a limited number are genuinely independent; every further named
direction is a blend. Each trained value = a direction in activation space.
Measure it: train values separately, fit a probe per direction, check angles.
Two hand-authored axes coming out nearly parallel = the model implements them
as one thing. "Too many" = every new value's direction is forced to be a blend
-- found via the EFFECTIVE RANK of the stacked directions.

Past capacity: values stop being independently adjustable -- training value k+1
necessarily drags values 1..k (interference matrix lights up off-diagonal,
crowding, fragmentation). Past capacity there is no such thing as teaching a
model ONE value: the alignment-relevant claim the program yields for free.

## The visualization ladder
1. Formation curves -- S at every 4-step checkpoint (rise, reversal, drift):
   a learning curve for a value. (= E5, validation-gated.)
2. Value-plane trajectories (needs axis 2) -- every run a path through 2D value
   space; same data, different road, different destination. ICML Fig-1
   candidate: the figure that IS the thesis.
3. The geometry itself -- angles between probe directions; effective-rank curve
   as axes accumulate ("how many hangers does the closet have").
4. The interference heatmap -- k x k, train-on-row/measure-on-column; diagonal
   = intended effect, off-diagonal = values dragging each other.

## The axis ladder
1 axis (done: existence proof) -> 2 orthogonal axes (ICML: generality +
action-polarity confound-kill; working choice rule-vs-circumstance) ->
interference matrix at k=2 (add axes only as matrix cells demand) ->
DISCOVERED geometry: stop hand-authoring axes; probes reveal how many
independent value dimensions the model actually has.

## Status after E7 v1 (prereg_workshop_hardening.md, gates run 2026-08-18)
Naive diff-in-means direction FAILED null controls: held-out r=0.729 vs
shuffled-label null95=0.752 (random-direction null95=0.639) -- at this
resolution any direction tracks generic fine-tuning drift. Cross-seed cosine
~0.86 = real shared structure exists, unresolved from drift. Workshop reports
E7 as registered-and-gated-out.

## ICML redesign requirements
- Per-stage mean-centering (strip generic drift BEFORE direction fitting).
- Contrastive / CCS-style probes as alternative fits.
- CAUSAL steering as the admission standard: no geometric claim unless pushing
  along the direction moves judged behavior (dose-response, pre-registered
  direction), with shuffled/random nulls retained.
- Fresh pre-registration before any v2 number is computed.
