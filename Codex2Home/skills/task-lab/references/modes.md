# modes — general, bug, perf, plan

Mode is an optional internal gate specialization, not a task type and not part of TaskID. The
folder structure is identical for feature work, bugs, RND, research, localization, planning, and
other durable tasks. Use `general` unless a specialized baseline materially improves the work.
Record a later switch only when it changes gates or acceptance.

## Contents

- [Mode = general](#mode--general--advance-any-durable-task)
- [Mode = bug](#mode--bug--localize-and-fix-a-defect)
- [Mode = perf](#mode--perf--move-a-measurable-metric)
- [Mode = plan](#mode--plan--settle-a-design)
- [Switching mode](#switching-mode)

---

## mode = general — advance any durable task

Use the universal contract: verify the current state, record facts and unknowns, define one next
step with one verdict, execute it, and persist the result. The success condition comes from the
task itself. Switch to a specialized mode only when reproduction, measurement noise, or design
premises require stricter gates.

---

## mode = bug — localize and fix a defect

### Baseline: a deterministic reproduction

Step 01 is making the defect reproduce on demand, and **nothing else proceeds until it does**.
Every later verdict is "does the repro still fire", so a flaky repro turns every verdict into
noise. If it cannot be made deterministic, that fact itself reshapes the task: work from logs and
code reading, state explicitly that no gate is available, and lower every claim accordingly.

Record with the repro: the exact sequence, the state it needs, the observable symptom, and the
rate (`fires 5/5` vs `fires 2/10` — a 2/10 repro needs ten runs to say anything).

### Facts here

- what the code actually does, cited to `file.ext:123` at a named revision;
- what the logs show, with timestamps;
- what a bisect returned, with the two adjacent revisions;
- what a probe printed under the failing condition;
- **negative facts**: this is not it, and here is what showed that. These are half the value and
  the half most often left unwritten.

### Hypotheses here

Candidate **causes**, each with a *discriminating observation* — what is true if this cause is real
and false if it is not. A cause without a discriminator is a suspicion.

```markdown
## Expected effect
1. `viewModel.item` at the moment of the crash is the previous element, not the current one.
2. The faulting access happens after `didDisappear`, not before — order visible in the log.
3. Forcing the deferred path to run synchronously makes the repro fire 5/5 instead of 2/10.
```

Prediction 3 is the strongest kind: **make the defect worse on purpose.** If a hypothesis about a
race is right, removing the timing slack should make the defect deterministic. This turns a flaky
repro into a gate and is worth reaching for before anything expensive.

### Gates here, cheapest first

```text
read the code path         does the premise hold at all
a log line / a counter     is the order what the hypothesis claims
a conditional breakpoint   is the state what it claims at that moment
force the condition        does making it worse make the defect deterministic
git bisect                 which change introduced it   (needs a scripted repro)
a failing unit test        the mechanism, isolated from the app
```

### Acceptance

All three, or it is not fixed:

1. the repro no longer fires, at the rate the baseline established;
2. **the mechanism is named in the code** — this line, this call, this ordering. Not "it went
   away". A disappearance with no mechanism is a coincidence: record it as a fact about the
   observation and keep the hypothesis open;
3. the failing repro survives as a regression test, or a written reason why it cannot.

Plus: the fix is at the cause, not the symptom. A guard that hides a bad state is a decision with a
price — write it as `D-NN` and say what the real cause is and why it was not fixed.

### Typical invariants

```text
INV  fix the cause, not the symptom; a symptom guard requires a recorded decision
INV  one cause per commit, independently revertible
INV  the failing repro becomes a test before the fix is called done
INV  a repro rate below 5/5 requires N runs before and after — state N
INV  read <authoritative source>, not <the local copy that differs>
```

---

## mode = perf — move a measurable metric

### Baseline: N observations with a measured spread

One run is not a baseline. Report p10 / median / p90 and the CV for every metric you will use, and
write the band into `Context/00-START-HERE.md` under its own heading. Then never claim an effect
inside it (`references/gates.md`).

### Facts here

- the baseline set and its spread;
- **the shape of the defect**, which is the fact that reorders everything else. Is the cost spread
  evenly or concentrated in rare spikes? Is the system busy or waiting? These questions change what
  metric ranks candidates, and answering them late means having ranked wrong for weeks;
- the structural composition of the cost: which chains, at what share, of what total;
- what is comparable to what. Build modes, toolchains, datasets, and devices each fork the
  baseline, and mixing them silently produces confident nonsense.

### The ranking metric is a choice, and it can be wrong

Start with the obvious metric, and re-derive it as soon as the defect's shape is known.

Real example from the source system: candidates were ranked by *share of total main-thread work*.
Then measurement showed the thread was only 17,5 % busy, and the defect was concentration — 3,8 %
of frames carrying 30,3 % of the work. The ranking unit changed to *how much of a chain's work
lands on an over-budget frame*, and the whole queue re-sorted: the candidate that had been second
scored 2,8 % on the new metric, while a chain scoring 100 % had not been a hypothesis at all.

When the ranking metric changes: write the `D-NN`, re-score every hypothesis, re-sort the queue,
and say in the queue that it was re-sorted and by what.

### Priority classes beat a flat ranking

A flat "biggest first" list keeps surfacing candidates that cannot work. Classify by *what the
change does to the work*, in priority order:

```text
class 1   move the work somewhere it does not hurt
class 2   remove the work entirely
class 3   make the same work cheaper
```

Class 1 usually wins because it is often available and cheap, and class 3 is usually unmeasurable
per-candidate. **A candidate that fits no class is not queued.** And when a class as a whole is
refuted — the source system disproved "cache X" for a forward-only feed, where every item is new —
every candidate in that class is demoted at once. That is one measurement retiring five
hypotheses, which is the best return available.

### Gates here

Discovery (1 observation, composition) then acceptance (×N, rates). See `references/gates.md`. The
split is not optional in this mode: without it, every candidate is below noise and the task
deadlocks.

### Acceptance

The numeric threshold, the direction repeating in ≥4/5, no regression in the neighbouring
qualities, and **the price measured**. A change that halves the target metric and doubles a
resource cost is a trade — name it, quantify it, and let the user accept it knowingly.

### Typical invariants

```text
INV  one causal change per gated observation
INV  <mode A> numbers are never comparable to <mode B> numbers
INV  never change the target or the measurement to pass the check
INV  every metric as numerator / denominator / result
INV  an observation without <required instrumentation> is not analysable
INV  the observation window includes the tail where deferred work lands
```

---

## mode = plan — settle a design

### Baseline: what the subject does today, read and cited

Not remembered, not inferred from names, not assumed from convention. Read it. Every premise the
plan will rest on becomes a verified `F-NN` or a listed `Q-NN` — there is no third option, and a
plan whose premises are neither is not finished.

This is the mode where the most work is thrown away by skipping the baseline, because a plan for a
system that does not exist reads exactly like a plan for one that does.

### Facts here

What the subject does, cited to file and line. Its actual constraints — deployment target, API
availability, ownership, who else consumes the code. What was already tried and what happened.

### Hypotheses here

Design options, each with its **expected consequences** stated so they could be wrong:

```markdown
## Expected effect
1. Consumers A and B need no change; only C's call site moves.
2. The <X> path stops being invoked during <Y> — checkable by a counter before implementing.
3. Cost: <Z> becomes possible to get wrong in a way the current shape prevents.
```

Item 3 is not optional. **An option with no stated cost has not been thought through**; every real
design choice trades something.

### Gates here

There is no measurement, so the gate is a **structural check**: go read the subject and see whether
the option's premise holds.

```text
does the premise hold in the code                    minutes, and it kills options outright
does anything else depend on what we would change    grep the consumers, all of them
is there a contradiction in the requirements         two stated constraints that cannot both hold
would a 30-line spike answer this                    cheaper than an argument about it
who owns this decision                               if the answer is a person, stop measuring
```

Trust no one: **read the requirements against each other looking for contradictions**, and read
them against the code looking for premises that are already false. Both are common and both are
cheap to find. A contradiction found before the plan is written saves the plan.

### Acceptance

1. every premise is a verified fact or a listed open question — none is silent;
2. every option carries its cost;
3. the recommendation is **one** option with the reason, not a comparison table left for someone
   else to decide;
4. what would falsify the recommendation is written down;
5. the open questions that remain each say who or what closes them.

A plan is done when someone else could execute it without asking you what you meant, and would
know which of its assumptions to check first if it started going wrong.

### Typical invariants

```text
INV  no premise without a source
INV  plan mode changes no production code; artifacts are documents
INV  a product or ownership decision is routed to a person, not measured around
INV  one recommendation, alternatives kept in the queue
```

---

## Switching mode

| From → to | When | Do |
|---|---|---|
| `plan` → `bug` | the design work located an actual defect | `D-NN`, new baseline (the repro), keep every fact |
| `bug` → `perf` | the defect turned out to be "too slow", not "wrong" | `D-NN`, build the measured baseline before continuing; a bug-mode repro is not a perf baseline |
| `perf` → `bug` | a measurement exposed a correctness defect | `D-NN`, split it into its own task folder if it is independent |
| `bug` → `plan` | the fix requires a design decision first | `D-NN`, the plan becomes the current step; do not fix blind |

Facts survive a mode switch unchanged. Hypotheses usually need re-scoring, because the ranking unit
changes with the mode.
