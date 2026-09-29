---
name: experiment-discipline
description: Rules for designing and running experiments, benchmarks, training runs, soaks, and performance comparisons so they produce trustworthy evidence at low cost. Load before designing or running any of these.
---

# Experiment Discipline

- **Discriminate first.** Use the smallest experiment that can tell the hypotheses apart; a handful of discriminating samples beats a long run that merely accumulates.
- **Soaks come late.** Long soaks, powered comparisons, and multi-hour gates confirm a system that already works; run early, they buy confidence in something not yet worth confirming while the core stands still.
- **Fast first signal.** A stage on a scarce resource must give its first discriminating signal within about five minutes, or restructure it rather than wait. Kill a run early on a null signal rather than completing it for tidiness.
- **One stage per exclusive resource.** Hold a device, emulator, or benchmark host for one stage at a time, and schedule nothing that competes with a measurement in progress.
- **Suppression is not causation.** An experiment that removes a component shows correlation; confirm in the configuration that will ship before removing anything on that basis.
- **Replicate cold, then ablate.** A result measured twice in one session is one observation with shared hidden state. Before building on it, reproduce it from its written recipe in a fresh session, then ablate one lever at a time to learn which are necessary.
- **Control confounds.** A speed or throughput comparison must control for what moves with the thing under test — system phase, work-item size, parallelism — or it measures the wrong thing while looking rigorous.
