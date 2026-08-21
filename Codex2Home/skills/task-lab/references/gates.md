# gates — designing a check that can settle something

A gate is an observation with a threshold, both fixed **before** the observation is made. That is
the whole idea, and it is the rule most often broken, because the numbers usually arrive first and
the criterion is easy to fit around them afterwards.

> **A criterion invented after the numbers were seen is not a gate.** It is a description of the
> numbers. Nothing is settled by it, and the hypothesis it "passed" is still a hypothesis.

## What a gate must have, before it runs

```text
1  the prediction        what will be observably true if the hypothesis holds
2  the discriminator     what would be observably true if it does NOT — and how the two differ
3  the threshold         the number or state that separates them, written down now
4  the validity test     what must be true of the observation for it to count at all
5  the cost              how long it takes and who has to do it
```

Missing 2 is the common case and the fatal one: a prediction with no distinguishable negative
is unfalsifiable, and running it produces a feeling of progress with no information.

Missing 4 is the expensive case: an observation taken under conditions that make it meaningless
still looks like data, and gets compared to good data later.

## Falsifiable effect — the test

| Not an effect | An effect |
|---|---|
| "scrolling will be smoother" | "share of `X::commit` drops by more than 2,4 pp" |
| "this should help" | "chain `A → B` disappears from the overdue frame: present in 6/6 baseline runs, absent in ≥2/3" |
| "the crash will stop" | "the repro sequence no longer faults, and `retainCount` at step 4 is 1, not 0" |
| "the code will be cleaner" | not a gate at all — this is a decision (`D-NN`), measure nothing |

Write the effect as a sentence that could turn out false. Then read it back and ask: *what
observation would make me abandon this?* If there is no such observation, the hypothesis is not
ready, and running an expensive check on it is waste.

State each prediction separately and numbered, because gates usually come back **partially**
passed. A gate with three numbered predictions where 1 and 3 hold and 2 fails is far more
informative than "mostly worked", and it tells you whether the failure was in the mechanism or in
your wording of the prediction. Both happen; they lead to opposite next moves.

## Order gates by cost, and the cheapest is usually reading

```text
1  read the subject           free    — does the premise even hold?
2  logic / arithmetic         minutes — does the mechanism produce the claimed magnitude?
3  structural observation     minutes — a log line, a counter, a breakpoint, a dry run
4  a targeted test            an hour — a unit test that fails on the mechanism
5  full measurement           hours   — the expensive comparable run
6  acceptance set             a day   — N runs, direction repeats
```

**A hypothesis can be refuted at level 1, before a line of it is written.** That is the single
highest-leverage move available, and it is skipped constantly because writing the change feels
like progress and reading feels like delay.

The pattern to look for: the hypothesis assumes the subject behaves a certain way. Go check that
assumption directly. Real example from the source system — a hypothesis proposed widening a
lifetime window so work would happen earlier; reading the framework showed the window did not
control the lifetime at all. The hypothesis died in twenty minutes instead of two days, and the
reading produced a fact that re-ranked four other candidates.

Corollary: **never spend level 5 on something level 1–3 could have killed.** Before any expensive
check, state which cheaper check you already ran and what it said.

## Discovery gate vs acceptance gate

These answer different questions and must not be conflated.

| | Discovery gate | Acceptance gate |
|---|---|---|
| Answers | *what to fix*; does the mechanism work | *did it actually get better* |
| Scope | 1 observation | N observations (≥5 where a rate is claimed) |
| Reads | composition, structure, presence/absence | aggregate rates, medians |
| Threshold | the chain moved / the counter changed / the branch is gone | past the numeric target, direction repeating in ≥4/5 |
| Cost | minutes to an hour | hours to a day |

Why the split matters: aggregate rates are noisy, and any single change is usually worth less than
the noise. If every candidate must clear the acceptance bar to be *considered*, nothing ever is —
you sit in a loop where each true improvement is indistinguishable from spread. Composition
signals do not have that problem: presence-vs-absence, or 100 % vs 3 %, is two orders of magnitude
above run-to-run variance.

So: **select by composition, accept by rate.** Batch small changes and accept them together.

## Noise floor

Measure it. Do not assume it, and do not inherit it from a different setup.

```text
take N baseline observations under identical conditions
report p10 / median / p90 and the coefficient of variation for each metric you will use
the band is (p90 − p10) / median
```

Then:

- **an effect inside the band is not an effect**, however much the mechanism makes sense;
- a metric whose CV is worse than the effect you expect cannot gate that effect — pick another
  metric or batch the changes;
- if the heaviest single candidate is worth less than the band, per-candidate rate gating is
  impossible in principle. Say so, and switch to composition (see above). Discovering this early
  is worth more than any single fix.

Write the noise floor into `Context/00-START-HERE.md` under its own heading, so no future claim
gets made below it.

## Validity — the observation has to count

Every measurement mode has conditions under which its output is meaningless. List them once, then
check them every time, mechanically if possible:

```text
enough samples / gestures / iterations, within a stated tolerance
the environment was in its normal state (not throttled, not warmed, not degraded)
the subject was the build you think it was — verify, do not infer from "I rebuilt"
one causal change only, matching change-log.md
required symbols / instrumentation actually present in the output
an internal arithmetic consistency check, where one exists
```

That last item earns its place: a run in the source system reported busy-time of 177,7 % of the
interval it was measured over — impossible for one thread, and it exposed a sampler stretched by
throttling. **Invent a self-consistency check for your metric and make it a blocker.** Ratios
that cannot exceed 1, counts that must match between two sources, totals that must sum — any of
these catches corruption that eyeballing does not.

A spoiled observation is marked invalid **with its reason** and kept. Never deleted, never
renamed, never quietly re-run into the same slot.

## One causal change per gate

Two changes in the subject and one observation means the verdict belongs to neither. There is no
statistical recovery from this; the run is a signature, not a gate.

Consequences in practice:

- before a gated observation, the subject differs from its baseline by exactly one causal change,
  and `change-log.md` says which;
- instrumentation is not a causal change — but it does affect timing, so it comes out before a
  timing measurement and stays in for a structural one. Note which;
- if several changes are already stacked, you can still get signatures out of the run. Label them
  as signatures, never as gates, and separate the changes before claiming anything per-change.

## Partial results and how to read them

| Outcome | Reading | Next move |
|---|---|---|
| all predictions hold | mechanism confirmed | proceed to acceptance |
| mechanism moved, aggregate did not | the change is real but below resolution | keep it, batch it, do not gate it alone again |
| mechanism did not move | the intercept was wrong, or the premise was | check where you hooked in before blaming the idea |
| aggregate moved, mechanism did not | something else changed. **Do not claim the win.** Find what |
| one prediction of three failed | check whether the prediction was wrongly worded or the mechanism is incomplete — these look identical and are not |

That fourth row is the one that flatters and deceives. An unexplained improvement is a fact about
the observation, not about the change.

## Acceptance is more than the metric

A change that passes its number and breaks behaviour has not passed. Define the full bar once in
`Context/verification-and-acceptance.md`, and require all of it:

```text
1  its own gate passed
2  the functional matrix is green — the behaviours this change could plausibly break, enumerated
   before the change, not after
3  no regression in the neighbouring qualities (memory, startup, other consumers of the same code)
4  the effect exceeds the measured noise, and the direction repeats
5  the change is ONE causal thing and can be reverted independently
```

And the honesty rule that outranks all five: **if a claim rests on one observation, say so.** "The
rate halved" from a single pair of runs is a discovery-gate result. Reporting it as acceptance is
the error the whole structure exists to prevent — write the number, write `one run vs one run`,
and write what acceptance would require.

## Cost registry

A change that improves the target metric at the expense of something else has a **price**, and the
price is part of the result. Measure it, name it, put it in the verdict. A trade the user did not
knowingly accept is a defect even when the number improved.
