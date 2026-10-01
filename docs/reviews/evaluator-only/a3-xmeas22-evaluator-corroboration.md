# EVALUATOR-ONLY — A3 XMEAS(22) evaluator-scope corroboration

> **Never load this file into a blind Agent context.** It names disturbance
> identities and evaluator-only bindings, which would leak the injected-fault
> candidate space. It supports the human reviewer of
> [`../a3-process-graph-human-verification.md`](../a3-process-graph-human-verification.md).
> The conclusion there does not depend on this file.

Status: PENDING_HUMAN_SIGNOFF · prepared by an automated coding agent, not a human reviewer.

## 1. Loop identity via the inlet-temperature disturbance

- `teprob.f:414`: `TCWS=TESUB8(6,TIME)+IDV(5)*5.D0`. IDV(5), "Condenser Cooling
  Water Inlet Temperature (Step)", sets the inlet temperature `TCWS` of the loop whose
  outlet state is `TWS` = XMEAS(22) (`teprob.f:791-792`).
- Same causal probe as review §5.3 (seed 1234, `MANUAL`, python backend, 36 s,
  mean of the last 6 samples, minus baseline):

| Arm | ΔXMEAS(9) | ΔXMEAS(11) | ΔXMEAS(21) | ΔXMEAS(22) |
|---|---|---|---|---|
| IDV(4) (reactor CW inlet temperature) | +0.146 | +0.002 | **+0.909** | +0.011 |
| IDV(5) (condenser CW inlet temperature) | +0.002 | +0.033 | +0.000 | **+0.405** |

The upstream catalog names IDV(5)/(12) "Condenser …" for the same loop that
`teprob.f`/Table 4 call "Separator cooling water" at XMEAS(22). This is further
evidence that the two words denote one loop. Reinartz et al. 2021 (p. 4) likewise
call IDV(12) "Cooling water inlet temperature of separator" and IDV(15) "Cooling
water outlet valve of separator".

## 2. Evaluator fixture consistency with review finding F-03

`tep_evaluator_disturbance_bindings_v0.json` (0.1.0, hash-bound to graph
`2b4adf94…`) attaches:

- IDV(4), IDV(11), IDV(14) to `reactor_cooling_water_in`;
- IDV(5), IDV(12), IDV(15) to `condenser_cooling_water_in`.

IDV(14)/(15) are valve-sticking faults. D&V Fig. 1 and Bathelt Fig. 3 draw those
valves on the **return** lines 12/13, and Reinartz et al. 2021 name them "outlet
valve". If the human reviewer moves XMV(10)/XMV(11) to the return edges (F-03), the
valve-sticking attachments must move with them. The evaluator fixture must then be
re-published as a new version bound to the new graph hash. The inlet-temperature
disturbances stay on the inlet edges.

Human decision: PENDING.
