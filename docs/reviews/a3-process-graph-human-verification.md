# A3 ProcessGraph / binding — human-verification review package

Status: **HUMAN_SIGNOFF_RECORDED**. The decisions of human reviewer `chengting` were
recorded on 2026-10-01 (§10). **Fixture promotion is still pending.** No verified
fixture exists yet.
Package: `a3-process-graph-human-verification` 0.1.0
Base commit: `4261dc7ab4994348778133190964c6d59b17bb82` · Upstream: `9a6c8e5fcef4a2850778704e7793c87b0a187005`
Owning spec: [`docs/specs/dexpi-binding-v0.md`](../specs/dexpi-binding-v0.md)
Machine-readable matrix (canonical decision record): [`a3-process-graph-binding-review-v0.json`](a3-process-graph-binding-review-v0.json)

> **Who prepared this.** An automated coding agent collected and cross-checked the
> evidence below. It is **not** the human reviewer. Every `human reviewer decision`
> is the decision the human reviewer `chengting` stated explicitly. The agent only
> transcribed those decisions, on the reviewer's instruction (§10). Nothing here
> promotes any binding to `HUMAN_VERIFIED_MAPPING` or the fixture to a
> human-verified status. That happens only in the separate promotion change (§8). Tests in `tests/test_a3_review_package.py`
> show that the evidence exists and is consistent. They do not prove the semantics are correct.

> **Evaluator-only boundary.** This document and the JSON matrix contain no
> disturbance identities, no disturbance names, and no evaluator-only mappings
> (tested). The single evaluator-scope corroboration for XMEAS(22) is kept apart in
> [`evaluator-only/a3-xmeas22-evaluator-corroboration.md`](evaluator-only/a3-xmeas22-evaluator-corroboration.md).
> That file must never be loaded into a blind Agent context, and the conclusion in
> §5 does not depend on it.

## 1. Subject

| Fixture | Version | Canonical sha256 (pinned) | LF file sha256 | Status |
|---|---|---|---|---|
| `src/tep_sim/fixtures/tep_process_graph_v0.json` | `tep-process-graph` 0.1.0 | `2b4adf94…d01f2b` | `66fec5a1…4988ba` | `PENDING_HUMAN_REVIEW`, all bindings `CURATED_MAPPING` |
| `src/tep_sim/fixtures/tep_evaluator_disturbance_bindings_v0.json` | 0.1.0, `EVALUATOR_ONLY` | `b497fdca…9b6a22` | `92afc404…6e79e8` | boundary check only |

Both fixtures are unchanged on this branch. Tests check their byte content (as LF)
and their pinned canonical hashes.

Scope: 17 nodes, 18 edges, 53 Agent-visible bindings (41 XMEAS + 12 XMV).

## 2. Sources inspected and evidence hierarchy

| Rank | Source id | What it is | Locator | Pin |
|---|---|---|---|---|
| 1 | `sim_python_backend` | upstream pure-Python backend: the code tep-sim **executes** | `vendor/tep-sim-upstream/src/tep/python_backend.py` | rev `9a6c8e5` |
| 1 | `sim_fortran` | original TEP Fortran model (comments + equations) | `vendor/tep-sim-upstream/teprob.f` | rev `9a6c8e5` |
| 1 | `upstream_constants` | runtime names/units | `vendor/tep-sim-upstream/src/tep/constants.py` | rev `9a6c8e5` |
| 2 | `canonical_registry` | `tep_sim.registry.REGISTRY` (derived from rank 1) | `src/tep_sim/registry.py` | — |
| 3 | `downs_vogel_1993` | Downs & Vogel 1993: Fig. 1 (p. 246), Tables 1/3/4/5 (pp. 247–249) | `docs/papers/Downs1993_TEP.pdf` | sha256 `5f19b0bf…` |
| 4 | `bathelt_ricker_jelali_2015` | Bathelt, Ricker & Jelali 2015, IFAC ADCHEM: Fig. 3 P&ID with unit-coded tags (p. 311) | `docs/papers/Reinartz2021_RevisedTEP.pdf` (**misnamed**, F-11) | sha256 `3e1d75ea…` |
| 4 | `reinartz_kulahci_ravn_2021` | Reinartz, Kulahci & Ravn 2021, Comput. Chem. Eng. 149:107281 | `docs/papers/Bathelt2015_ExtendedTEP.pdf` (**misnamed**, F-11) | sha256 `4c0f6e88…` |
| 4 | `ricker_1996` | Ricker 1996, J. Proc. Cont. 6(4) | `docs/papers/Ricker1996_DecentralizedTEP.pdf` | sha256 `d78863e9…` |
| 5 | prior curated mapping | the 0.1.0 fixture itself | — | **not used as evidence for itself** (tested) |

These were not used as evidence:

- `docs/papers/TEP_Variables_Appendix*.md`: a secondary note derived from Rieth 2017.
  Its base values come from a different operating point (e.g. XMEAS(22) 90.045 against
  D&V 77.297; the simulator gives 77.29).
- `docs/papers/Reinartz2021_TEPTestbed.pdf`: actually Capaci et al. 2019, and also
  misnamed.

Figure readings (D&V Fig. 1, Bathelt Fig. 3) are **visual readings by the automated
agent** and must be confirmed by the human reviewer.

In the JSON, every evidence item names a `source_id`, whose `locator` and pin live
once in `sources`:

- Vendored code evidence always has `line` + literal `anchor`. The test asserts that
  the anchor is on that line and that the submodule is checked out at `9a6c8e5`.
- PDF evidence has `where` (page/figure/table). The test asserts the PDF's sha256.
- Figure readings are flagged `visual_reading: true` (tested), for binding rows and
  topology rows alike.

## 3. Method

1. Runtime identity: each `runtime_variable_id` was resolved in `REGISTRY`. The
   registry name was compared with `constants.py`, and the runtime computation was
   traced in `python_backend.py` and `teprob.f`.
2. Semantics/topology: the quantity each runtime equation reports (stream index,
   vessel state, or utility loop) was compared with the fixture attachment, D&V
   Tables 3–5, and the instrument location in D&V Fig. 1 and Bathelt Fig. 3.
3. Flow direction: each edge was checked against the per-unit energy balances in
   `teprob.f`:
   - `YP(9)` reactor
   - `YP(18)` separator
   - `YP(27)` stripper
   - `YP(36)` vapor/feed zone
   - `YP(37)`/`YP(38)` cooling-water loops
4. Causal probe (XMEAS(21)/(22) only): a same-seed, `MANUAL`, python-backend +2 %
   MV step was run for 36 s. The result is in §5.3 and is locked by
   `test_cooling_water_outlet_temperatures_respond_to_their_own_loop_flow`.

Runtime identity correctness ≠ semantic/topological correctness. The two are
recorded as separate columns: `runtime_identity_check` in the JSON and the
`nomenclature`/`topology` columns in the tables below.

Column legend:

- `nomen.`: nomenclature agreement between runtime name and fixture semantics.
- `topo.`: topology agreement between fixture attachment and runtime + flowsheet
  evidence.
- Disposition: `ACCEPT_CANDIDATE` (evidence consistent; still needs a human ACCEPT)
  or `HUMAN_DECISION_REQUIRED` (a discrepancy the agent must not resolve).
- Evidence key: `py:L` = `python_backend.py` line, `f77:L` = `teprob.f` line,
  `DV T4` = Downs & Vogel Table 4, `F1` = D&V Fig. 1, `BRJ` = Bathelt Fig. 3 tag.

## 4. Binding verification matrix (53 Agent-visible bindings)

| ID | Semantic entity | Runtime var | Kind | Relation | Fixture attachment | Runtime name | Evidence (location) | Nomen. | Topo. | Assessment | Proposed disposition | Human decision | Agent notes | Human review notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B-01 | `stream_1.flow_measurement` | `XMEAS(1)` | XMEAS | MEASURES | `stream_1` | A Feed (stream 1) | const:L257; py:L1135; f77:L679; DV T4; F1: FI on stream 1; BRJ FI 1001 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-02 | `stream_2.flow_measurement` | `XMEAS(2)` | XMEAS | MEASURES | `stream_2` | D Feed (stream 2) | const:L258; py:L1136; f77:L680; DV T4; F1: FI on stream 2; BRJ FI 1002 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-03 | `stream_3.flow_measurement` | `XMEAS(3)` | XMEAS | MEASURES | `stream_3` | E Feed (stream 3) | const:L259; py:L1137; f77:L681; DV T4; F1: FI on stream 3; BRJ FI 1003 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-04 | `stream_4.flow_measurement` | `XMEAS(4)` | XMEAS | MEASURES | `stream_4` | A and C Feed (stream 4) | const:L260; py:L1138; f77:L682; DV T4; F1: FI on stream 4; BRJ FI 1004 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-05 | `stream_8.flow_measurement` | `XMEAS(5)` | XMEAS | MEASURES | `stream_8` | Recycle Flow (stream 8) | const:L261; py:L1139; f77:L683; DV T4; F1: FI on stream 8 (compressor discharge, downstream of recycle-valve spillback); BRJ FI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-06 | `stream_6.flow_measurement` | `XMEAS(6)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Rate (stream 6) | const:L262; py:L1140; f77:L684; DV T4; F1: FI on stream 6; BRJ FI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-07 | `reactor.pressure_measurement` | `XMEAS(7)` | XMEAS | MEASURES | `reactor` | Reactor Pressure | const:L263; py:L1141; f77:L685; DV T4; F1: PI on reactor; BRJ PIAZ+ 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-08 | `reactor.level_measurement` | `XMEAS(8)` | XMEAS | MEASURES | `reactor` | Reactor Level | const:L264; py:L1142; f77:L686; DV T4; F1: LI on reactor; BRJ LIAZ+- 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-09 | `reactor.temperature_measurement` | `XMEAS(9)` | XMEAS | MEASURES | `reactor` | Reactor Temperature | const:L265; py:L1143; f77:L687; DV T4; F1: TI on reactor; BRJ TIAZ+ 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-10 | `stream_9.flow_measurement` | `XMEAS(10)` | XMEAS | MEASURES | `stream_9` | Purge Rate (stream 9) | const:L266; py:L1144; f77:L688; DV T4; F1: FI on stream 9; BRJ FI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-11 | `separator.temperature_measurement` | `XMEAS(11)` | XMEAS | MEASURES | `separator` | Product Sep Temp | const:L267; py:L1145; f77:L689; DV T4; F1: TI on separator; BRJ TI 1301 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-12 | `separator.level_measurement` | `XMEAS(12)` | XMEAS | MEASURES | `separator` | Product Sep Level | const:L268; py:L1146; f77:L690; DV T4; F1: LI on separator; BRJ LIAZ+- 1301 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-13 | `separator.pressure_measurement` | `XMEAS(13)` | XMEAS | MEASURES | `separator` | Prod Sep Pressure | const:L269; py:L1147; f77:L691; DV T4; F1: PI on separator; BRJ PI 1301 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-14 | `stream_10.flow_measurement` | `XMEAS(14)` | XMEAS | MEASURES | `stream_10` | Prod Sep Underflow (stream 10) | const:L270; py:L1148; f77:L692; DV T4; F1: FI on stream 10; BRJ FI 1301 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-15 | `stripper.level_measurement` | `XMEAS(15)` | XMEAS | MEASURES | `stripper` | Stripper Level | const:L271; py:L1149; f77:L693; DV T4; F1: LI on stripper; BRJ LIAZ+- 1501 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-16 | `stripper.pressure_measurement` | `XMEAS(16)` | XMEAS | MEASURES | `stripper` | Stripper Pressure | const:L272; py:L1150; f77:L694; DV T4; F1: PI drawn on stripper overhead line 5; BRJ PI 1501 | YES | PARTIAL | MODERATE | HUMAN_DECISION_REQUIRED | ACCEPT | F-02: Runtime computes XMEAS(16) from PTV, the pressure of the compressor-discharge/reactor-feed vapor zone (fixture node reactor_feed_mixer); the model has no separate stripper pressure state. D&V Fig. 1 draws the PI on the stripper overhead line 5. Attachment to the stripper node matches the nomenclature but not the runtime state it reports. | Q2: keep attachment on stripper (canonical name and D&V Fig. 1 instrument are stripper pressure). Runtime value is sourced from the PTV vapor-zone state; record this in the promoted fixture provenance. Do not move the attachment to the mixer. |
| B-17 | `stream_11.flow_measurement` | `XMEAS(17)` | XMEAS | MEASURES | `stream_11` | Stripper Underflow (stream 11) | const:L273; py:L1151; f77:L695; DV T4; F1: FI on stream 11; BRJ FI 1502 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-18 | `stripper.temperature_measurement` | `XMEAS(18)` | XMEAS | MEASURES | `stripper` | Stripper Temperature | const:L274; py:L1152; f77:L696; DV T4; F1: TI on stripper; BRJ TI 1501 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-19 | `stripper_steam.flow_measurement` | `XMEAS(19)` | XMEAS | MEASURES | `stripper_steam` | Stripper Steam Flow | const:L275; py:L1153; f77:L697; DV T4; F1: FI on steam supply line to stripper reboiler; BRJ FI 1501 | YES | YES | MODERATE | ACCEPT_CANDIDATE | ACCEPT | F-08: Runtime derives the reported steam flow from the stripper heat duty QUC (driven by XMV(9)); there is no separate steam-flow state. Attachment to the stripper_steam utility edge matches D&V and the figures. | Q5 / Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-20 | `compressor.work_measurement` | `XMEAS(20)` | XMEAS | MEASURES | `compressor` | Compressor Work | const:L276; py:L1154; f77:L699; DV T4; F1: JI on compressor; BRJ JI 1401 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-21 | `reactor_cooling.outlet_temperature` | `XMEAS(21)` | XMEAS | MEASURES | `reactor_cooling_water_out` | Reactor Cooling Water Outlet Temp | const:L277; py:L1155; f77:L700; DV T4; F1: TI on reactor cooling-water return line 12; BRJ TI 1103 (unit 11 = reactor) | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-22 | `condenser_cooling.outlet_temperature` | `XMEAS(22)` | XMEAS | MEASURES | `condenser_cooling_water_out` | Separator Cooling Water Outlet Temp | const:L278; py:L1156; f77:L701; DV T4; F1: TI on condenser cooling-water return line 13; BRJ TI 1202 (unit 12 = condenser) | NO | YES | STRONG_FOR_LOOP_IDENTITY | HUMAN_DECISION_REQUIRED | ACCEPT | F-01: Special review item. Upstream/Fortran/D&V Table 4 name it 'Separator cooling water outlet temperature'; runtime state TWS is the outlet of the cooling loop whose flow is XMV(11) 'Condenser cooling water flow'; both figures place the TI on the condenser cooling-water return line 13. See XMEAS(22) adjudication package. | Q1: Option A, retain the condenser attachment. Runtime loop (XMV(11)), D&V flowsheet and Bathelt Fig. 3 all point to the condenser cooling-water loop; the 'Separator cooling water outlet' label is treated as a lumping/naming legacy of the original model. The runtime name is not renamed. |
| B-23 | `stream_6.composition_a_measurement` | `XMEAS(23)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component A | const:L279; py:L1184; f77:L717; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-24 | `stream_6.composition_b_measurement` | `XMEAS(24)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component B | const:L280; py:L1185; f77:L718; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-25 | `stream_6.composition_c_measurement` | `XMEAS(25)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component C | const:L281; py:L1186; f77:L719; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-26 | `stream_6.composition_d_measurement` | `XMEAS(26)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component D | const:L282; py:L1187; f77:L720; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-27 | `stream_6.composition_e_measurement` | `XMEAS(27)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component E | const:L283; py:L1188; f77:L721; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-28 | `stream_6.composition_f_measurement` | `XMEAS(28)` | XMEAS | MEASURES | `stream_6` | Reactor Feed Component F | const:L284; py:L1189; f77:L722; DV T5; F1: analyzer on reactor feed header (stream 6); BRJ XI 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-29 | `stream_9.composition_a_measurement` | `XMEAS(29)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component A | const:L285; py:L1190; f77:L723; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-30 | `stream_9.composition_b_measurement` | `XMEAS(30)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component B | const:L286; py:L1191; f77:L724; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-31 | `stream_9.composition_c_measurement` | `XMEAS(31)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component C | const:L287; py:L1192; f77:L725; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-32 | `stream_9.composition_d_measurement` | `XMEAS(32)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component D | const:L288; py:L1193; f77:L726; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-33 | `stream_9.composition_e_measurement` | `XMEAS(33)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component E | const:L289; py:L1194; f77:L727; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-34 | `stream_9.composition_f_measurement` | `XMEAS(34)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component F | const:L290; py:L1195; f77:L728; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-35 | `stream_9.composition_g_measurement` | `XMEAS(35)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component G | const:L291; py:L1196; f77:L729; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-36 | `stream_9.composition_h_measurement` | `XMEAS(36)` | XMEAS | MEASURES | `stream_9` | Purge Gas Component H | const:L292; py:L1197; f77:L730; DV T5; F1: analyzer on purge line (stream 9); BRJ XI 1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-37 | `stream_11.composition_d_measurement` | `XMEAS(37)` | XMEAS | MEASURES | `stream_11` | Product Component D | const:L293; py:L1198; f77:L731; DV T5; F1: analyzer on product line (stream 11); BRJ XI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-38 | `stream_11.composition_e_measurement` | `XMEAS(38)` | XMEAS | MEASURES | `stream_11` | Product Component E | const:L294; py:L1199; f77:L732; DV T5; F1: analyzer on product line (stream 11); BRJ XI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-39 | `stream_11.composition_f_measurement` | `XMEAS(39)` | XMEAS | MEASURES | `stream_11` | Product Component F | const:L295; py:L1200; f77:L733; DV T5; F1: analyzer on product line (stream 11); BRJ XI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-40 | `stream_11.composition_g_measurement` | `XMEAS(40)` | XMEAS | MEASURES | `stream_11` | Product Component G | const:L296; py:L1201; f77:L734; DV T5; F1: analyzer on product line (stream 11); BRJ XI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-41 | `stream_11.composition_h_measurement` | `XMEAS(41)` | XMEAS | MEASURES | `stream_11` | Product Component H | const:L297; py:L1202; f77:L735; DV T5; F1: analyzer on product line (stream 11); BRJ XI 1006 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-42 | `stream_2.flow_actuator` | `XMV(1)` | XMV | ACTUATES | `stream_2` | D Feed Flow (stream 2) | const:L313; py:L1000; f77:L96; DV T3; F1: control valve on stream 2; BRJ V-1002 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-43 | `stream_3.flow_actuator` | `XMV(2)` | XMV | ACTUATES | `stream_3` | E Feed Flow (stream 3) | const:L314; py:L1001; f77:L97; DV T3; F1: control valve on stream 3; BRJ V-1003 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-44 | `stream_1.flow_actuator` | `XMV(3)` | XMV | ACTUATES | `stream_1` | A Feed Flow (stream 1) | const:L315; py:L1002; f77:L98; DV T3; F1: control valve on stream 1; BRJ V-1001 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-45 | `stream_4.flow_actuator` | `XMV(4)` | XMV | ACTUATES | `stream_4` | A and C Feed Flow (stream 4) | const:L316; py:L1003; f77:L99; DV T3; F1: control valve on stream 4; BRJ V-1004 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-46 | `compressor.recycle_valve_actuator` | `XMV(5)` | XMV | ACTUATES | `compressor` | Compressor Recycle Valve | const:L317; py:L1044; f77:L100; DV T3; F1: valve on spillback loop around the compressor; BRJ V-1401 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT | F-09: Spillback/recycle valve around the compressor; runtime subtracts the valve flow from the compressor throughput that becomes stream 8. | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-47 | `stream_9.purge_valve_actuator` | `XMV(6)` | XMV | ACTUATES | `stream_9` | Purge Valve (stream 9) | const:L318; py:L1028; f77:L101; DV T3; F1: control valve on stream 9; BRJ V-1005 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-48 | `stream_10.flow_actuator` | `XMV(7)` | XMV | ACTUATES | `stream_10` | Separator Pot Liquid Flow | const:L319; py:L1004; f77:L102; DV T3; F1: control valve on stream 10; BRJ V-1301 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-49 | `stream_11.flow_actuator` | `XMV(8)` | XMV | ACTUATES | `stream_11` | Stripper Liquid Product Flow | const:L320; py:L1005; f77:L103; DV T3; F1: control valve on stream 11; BRJ V-1501 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-50 | `stripper_steam.valve_actuator` | `XMV(9)` | XMV | ACTUATES | `stripper_steam` | Stripper Steam Valve | const:L321; py:L1007; f77:L104; DV T3; F1: control valve on steam supply to stripper reboiler; BRJ V-1502 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| B-51 | `reactor_cooling.flow_actuator` | `XMV(10)` | XMV | ACTUATES | `reactor_cooling_water_in` | Reactor Cooling Water Flow | const:L322; py:L1008; f77:L105; DV T3; F1: control valve on reactor cooling-water RETURN line 12; BRJ V-1101 (on line 12) | YES | PARTIAL | STRONG_FOR_LOOP_IDENTITY | HUMAN_DECISION_REQUIRED | ACCEPT | F-03: Correct cooling loop. Both figures place the control valve on the RETURN (outlet) line 12; fixture attaches the actuator to reactor_cooling_water_in. Flow is identical along the single-path loop; human decides whether the inlet-edge attachment is acceptable. | Q3: accept the inlet-edge attachment for v0. On the single-path cooling loop the flow is identical; ACTUATES is a functional-control relation in v0, not physical valve coordinates. The return-side valve location stays recorded as a note. |
| B-52 | `condenser_cooling.flow_actuator` | `XMV(11)` | XMV | ACTUATES | `condenser_cooling_water_in` | Condenser Cooling Water Flow | const:L323; py:L1009; f77:L106; DV T3; F1: control valve on condenser cooling-water RETURN line 13; BRJ V-1201 (on line 13) | YES | PARTIAL | STRONG_FOR_LOOP_IDENTITY | HUMAN_DECISION_REQUIRED | ACCEPT | F-03: Correct cooling loop. Both figures place the control valve on the RETURN (outlet) line 13; fixture attaches the actuator to condenser_cooling_water_in. Same question as XMV(10). | Q3: accept the inlet-edge attachment for v0 (same rationale as B-51). |
| B-53 | `reactor.agitator_speed_actuator` | `XMV(12)` | XMV | ACTUATES | `reactor` | Agitator Speed | const:L324; py:L1010; f77:L107; DV T3; F1: SC (speed controller) on reactor agitator; BRJ SC 1101 | YES | YES | STRONG | ACCEPT_CANDIDATE | ACCEPT |  | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |

Summary:

| | Count |
|---|---|
| Bindings reviewed | 53 |
| Proposed `ACCEPT_CANDIDATE` | 49 |
| Proposed `HUMAN_DECISION_REQUIRED` | 4 (XMEAS(16), XMEAS(22), XMV(10), XMV(11)) |
| Proposed `NEEDS_SOURCE` | 0 |
| Human decision `PENDING` | 53 |

## 5. XMEAS(22) adjudication package (special review item)

### 5.1 Recorded state

- Runtime name (`REGISTRY`, `constants.py:278`, `teprob.f:132`):
  `Separator Cooling Water Outlet Temp`.
- Fixture 0.1.0: `condenser_cooling.outlet_temperature`, attached to
  `condenser_cooling_water_out` (`CURATED_MAPPING`, `PENDING_HUMAN_REVIEW`).

### 5.2 What the runtime variable physically is

| Evidence | Location | Finding |
|---|---|---|
| `XMEAS(22)=TWS` / `self._xmeas[21] = tp.tws` | `teprob.f:701`, `python_backend.py:1156` | XMEAS(22) is state `TWS` (`YY(38)`) |
| `FWS=VPOS(11)*VRNG(11)/100.0` / `tp.fws = vpos[10] …` | `teprob.f:574`, `python_backend.py:1009` | the loop flow `FWS` is XMV(11) "Condenser Cooling Water Flow" |
| `YP(38)=(FWS*500.53*(TCWS-TWS)-QUS*1.D6/1.8)/HWS` | `teprob.f:791-792`, `python_backend.py:1239` | `TWS` is the outlet temperature of the loop carrying `FWS` and removing duty `QUS` |
| `QUS=UAS*(TWS-TST(8))`, `UAS` a function of `FTM(8)` | `teprob.f:674-675`, `python_backend.py:1128` | the duty is exchanged with the **reactor effluent** (`TST(8)=TCR`, flow `FTM(8)` = D&V stream 7), which is the condenser's service |
| `YP(18)=HST(8)*FTM(8)-…+QUS` | `teprob.f:773-777`, `python_backend.py:1233` | the model has no condenser holdup. The condenser duty is **lumped into the separator energy balance**, which is why the Fortran variables carry the separator suffix `S` (`TWS`, `FWS`, `QUS`, `HWS`; `constants.py:69` "Separator cooling water heat transfer coefficient") |
| D&V Table 1 (p. 247) | unit operation data | heat duty is listed under **Condenser** (−2140.6 kW). The Separator has no duty ("—"). The utility line reads "Condenser cooling water flow 49.37 m³/h" |
| D&V Table 4 (p. 249) | XMEAS(22) | **"Separator cooling water outlet temperature"**, base 77.297 °C (the simulator gives 77.29 °C) |
| D&V Fig. 1 (p. 246) | condenser | CWS → condenser → line **13** with TI and control valve → CWR. No separator cooling loop is drawn |
| Bathelt et al. 2015 Fig. 3 (p. 311) | condenser | original (black) measurement **TI 1202** on condenser CW return line 13. The text defines the first two tag digits: 11 reactor, **12 condenser**, 13 separator |
| Ricker 1996 (p. 10, loop 19) | control text | "Control of reactor liquid level relies on control of the temperature in the separator. If the condenser coolant valve saturates…": the separator temperature is controlled with the condenser coolant |

### 5.3 Causal probe (runtime, mechanical)

Same seed 1234, `ControlMode.MANUAL`, python backend. Each arm is a +2 % MV step;
the table shows the mean of the last 6 of 36 one-second samples, minus baseline:

| Arm | ΔXMEAS(9) | ΔXMEAS(11) | ΔXMEAS(21) | ΔXMEAS(22) |
|---|---|---|---|---|
| XMV(10) +2 % (reactor CW flow) | −0.064 | −0.000 | **−0.465** | −0.005 |
| XMV(11) +2 % (condenser CW flow) | −0.001 | −0.020 | −0.000 | **−0.285** |

XMEAS(22) responds only to XMV(11). Its first process-side effect is on separator
temperature XMEAS(11), not the reactor. The test locks only the signs and the
isolation of the two loops (thresholds −0.1 / ±0.02), not the exact values in the
table. A further corroboration that uses evaluator-scope data is kept in the
evaluator-only note linked in the header.

### 5.4 Options

**Option A: retain the condenser attachment** (`condenser_cooling_water_out`).

- For: every runtime equation identifies `TWS` as the outlet of the loop actuated
  by XMV(11) "Condenser Cooling Water Flow", serving the reactor-effluent condenser.
- For: D&V Fig. 1 and Bathelt Fig. 3 place this TI on the condenser CW return
  (line 13, tag TI 1202, unit 12 = condenser).
- For: D&V Table 1 attributes the duty to the condenser.
- For: the causal probe isolates the loop.
- Against: it contradicts the literal Table 4/runtime label "Separator…". That label
  stays authoritative as the runtime *name*, and the fixture does not rename it.

**Option B: change to a separator attachment.**

- For: matches the literal label in D&V Table 4, `teprob.f`, `constants.py`, and
  `REGISTRY`.
- For: the model lumps the condenser duty into the separator energy balance.
- Against: there is no separator cooling-water loop in either figure.
- Against: attaching the measurement to the separator node would place a
  cooling-water temperature on a process vessel and break the
  measurement ↔ actuator (XMV(11)) loop pairing on the same utility path.
- Against: it would require a new `separator_cooling_water_*` utility path that no
  source draws, i.e. an invented entity.

**Option C: unresolved / insufficient evidence.**

- For: the primary paper's own measurement table uses "separator". A reviewer may
  hold that the authors' label outranks figure readings unless an author-issued tag
  list or instrument index confirms TI-on-line-13 = XMEAS(22). No such list is
  vendored. Bathelt Fig. 3 is a later revision, not the original authors' document.
- Against: the label disagreement is explained by the model's lumping, and every
  topological source agrees.

**Advisory — agent's evidence assessment (not a decision; the reviewer should weigh
the options above first):** the evidence is strong that
XMEAS(22) belongs to the condenser cooling-water loop, which favours Option A. The
label disagreement looks historical/nomenclatural and comes from the original
paper; it is not an upstream port error. The human reviewer must choose A, B, or C.

## 6. Topology review

### 6.1 Nodes

| ID | Node | Kind | Material upstream | Material downstream | Evidence | Finding / notes | Proposed disposition | Human decision | Human review notes |
|---|---|---|---|---|---|---|---|---|---|
| N-01 | `compressor` | COMPRESSOR | separator | reactor_feed_mixer | DV Fig. 1 (p. 246) | Compressor throughput and work CPDH computed from PTV-PTS. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-02 | `condenser` | CONDENSER | reactor | separator | DV Fig. 1 (p. 246) | F-05: D&V Fig. 1 and Table 1 (condenser heat duty -2140.6 kW) define the unit; runtime has no condenser holdup - its duty QUS is lumped into the separator energy balance. Static topology node is justified by the flowsheet, not by a dynamic state. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-03 | `condenser_cooling_water_return` | UTILITY_SINK | — | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-04 | `condenser_cooling_water_supply` | UTILITY_SOURCE | — | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-05 | `feed_a_supply` | FEED_SOURCE | — | reactor_feed_mixer | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-06 | `feed_ac_supply` | FEED_SOURCE | — | stripper | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-07 | `feed_d_supply` | FEED_SOURCE | — | reactor_feed_mixer | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-08 | `feed_e_supply` | FEED_SOURCE | — | reactor_feed_mixer | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-09 | `product_outlet` | PRODUCT_SINK | stripper | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-10 | `purge_outlet` | PRODUCT_SINK | separator | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-11 | `reactor` | REACTOR | reactor_feed_mixer | condenser | DV Fig. 1 (p. 246); f77:L771 | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-12 | `reactor_cooling_water_return` | UTILITY_SINK | — | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-13 | `reactor_cooling_water_supply` | UTILITY_SOURCE | — | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-14 | `reactor_feed_mixer` | MIXER | compressor, feed_a_supply, feed_d_supply, feed_e_supply, stripper | reactor | DV Fig. 1 (p. 246); f77:L783 | F-06: Runtime models a vapor holdup 'V' (UCVV/ETV, pressure PTV; upstream constant VTV 'Compressor volume') that receives streams 1, 2, 3, 5, 8 and discharges stream 6. D&V Fig. 1 draws only a piping header; the node is a modeled zone, not drawn equipment. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-15 | `separator` | SEPARATOR | condenser | compressor, purge_outlet, stripper | DV Fig. 1 (p. 246); f77:L773 | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| N-16 | `stripper` | STRIPPER | feed_ac_supply, separator | product_outlet, reactor_feed_mixer | DV Fig. 1 (p. 246); f77:L778 | F-08: Reboiler is lumped into the stripper; D&V Fig. 1 also shows a condensate return that the fixture does not model. | ACCEPT_CANDIDATE | ACCEPT | Q5: accept the lumped reboiler and the missing condensate return for v0. |
| N-17 | `stripper_steam_supply` | UTILITY_SOURCE | — | — | DV Fig. 1 (p. 246) | Flowsheet terminal/unit. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |

### 6.2 Edges

| ID | Edge | Kind | Source → target | Stream # | Direction | Evidence | Finding / notes | Proposed disposition | Human decision | Human review notes |
|---|---|---|---|---|---|---|---|---|---|---|
| E-01 | `condenser_cooling_water_in` | UTILITY_STREAM | condenser_cooling_water_supply → condenser | — | AGREES | DV Fig. 1 (p. 246); f77:L574 | F-03: Carries XMV(11) in the fixture; both figures put the control valve on the return line 13. | HUMAN_DECISION_REQUIRED | ACCEPT | Q3: accept the actuator on this inlet edge for v0. |
| E-02 | `condenser_cooling_water_out` | UTILITY_STREAM | condenser → condenser_cooling_water_return | — | AGREES | DV Fig. 1 (p. 246); f77:L791 | F-04: Numbered line 13 in D&V Fig. 1 and BRJ Fig. 3; fixture stream_number is null. Carries XMEAS(22). | HUMAN_DECISION_REQUIRED | ACCEPT | Q1: Option A (carries XMEAS(22)). Q4: stream_number stays null; D&V Table 1 process streams are 1-11 and figure utility line numbers are not stream numbers. |
| E-03 | `condenser_outlet` | MATERIAL_STREAM | condenser → separator | — | AGREES | DV Fig. 1 (p. 246); f77:L675 | F-05: No runtime stream: the condenser is lumped into the separator. Unnumbered in D&V Fig. 1 and Table 1. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-04 | `reactor_cooling_water_in` | UTILITY_STREAM | reactor_cooling_water_supply → reactor | — | AGREES | DV Fig. 1 (p. 246); f77:L573 | F-03: Carries XMV(10) in the fixture; both figures put the control valve on the return line 12. | HUMAN_DECISION_REQUIRED | ACCEPT | Q3: accept the actuator on this inlet edge for v0. |
| E-05 | `reactor_cooling_water_out` | UTILITY_STREAM | reactor → reactor_cooling_water_return | — | AGREES | DV Fig. 1 (p. 246); f77:L789 | F-04: Numbered line 12 in D&V Fig. 1 and BRJ Fig. 3; fixture stream_number is null. | HUMAN_DECISION_REQUIRED | ACCEPT | Q4: stream_number stays null (same rationale as E-02). |
| E-06 | `separator_vapor` | MATERIAL_STREAM | separator → compressor | — | AGREES | DV Fig. 1 (p. 246); f77:L594 | Unnumbered in D&V; runtime compressor suction is separator vapor (XST(.,9)=XVS). | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-07 | `stream_1` | MATERIAL_STREAM | feed_a_supply → reactor_feed_mixer | 1 | AGREES | DV Fig. 1 (p. 246) stream 1; Table 1 (p. 247); f77:L567 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-08 | `stream_10` | MATERIAL_STREAM | separator → stripper | 10 | AGREES | DV Fig. 1 (p. 246) stream 10; Table 1 (p. 247); f77:L570 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-09 | `stream_11` | MATERIAL_STREAM | stripper → product_outlet | 11 | AGREES | DV Fig. 1 (p. 246) stream 11; Table 1 (p. 247); f77:L571 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-10 | `stream_2` | MATERIAL_STREAM | feed_d_supply → reactor_feed_mixer | 2 | AGREES | DV Fig. 1 (p. 246) stream 2; Table 1 (p. 247); f77:L565 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-11 | `stream_3` | MATERIAL_STREAM | feed_e_supply → reactor_feed_mixer | 3 | AGREES | DV Fig. 1 (p. 246) stream 3; Table 1 (p. 247); f77:L566 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-12 | `stream_4` | MATERIAL_STREAM | feed_ac_supply → stripper | 4 | AGREES | DV Fig. 1 (p. 246) stream 4; Table 1 (p. 247); f77:L568 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-13 | `stream_5` | MATERIAL_STREAM | stripper → reactor_feed_mixer | 5 | AGREES | DV Fig. 1 (p. 246) stream 5; Table 1 (p. 247); f77:L649 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-14 | `stream_6` | MATERIAL_STREAM | reactor_feed_mixer → reactor | 6 | AGREES | DV Fig. 1 (p. 246) stream 6; Table 1 (p. 247); f77:L579 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-15 | `stream_7` | MATERIAL_STREAM | reactor → condenser | 7 | AGREES | DV Fig. 1 (p. 246) stream 7; Table 1 (p. 247); f77:L584 | Runtime flow FTM(8) goes reactor -> separator energy balance directly; the condenser is lumped (F-05). | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-16 | `stream_8` | MATERIAL_STREAM | compressor → reactor_feed_mixer | 8 | AGREES | DV Fig. 1 (p. 246) stream 8; Table 1 (p. 247); f77:L600 | Connection and direction agree with D&V Fig. 1 and the runtime unit balances. | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-17 | `stream_9` | MATERIAL_STREAM | separator → purge_outlet | 9 | AGREES | DV Fig. 1 (p. 246) stream 9; Table 1 (p. 247); f77:L588 | D&V Fig. 1 draws the purge off the separator vapor line upstream of the compressor; fixture connects separator -> purge_outlet directly (no junction node). Runtime purge composition is separator vapor and its flow is driven by separator pressure, so the attachment is equivalent (finding F-07). | ACCEPT_CANDIDATE | ACCEPT | Q9: ACCEPT (bulk acceptance of ACCEPT_CANDIDATE rows after the reviewer personally confirmed all visual figure readings, Q6). |
| E-18 | `stripper_steam` | UTILITY_STREAM | stripper_steam_supply → stripper | — | AGREES | DV Fig. 1 (p. 246); f77:L572 | F-08: Steam supply only; D&V Fig. 1 also shows a condensate return (Cond) that is not modeled as an edge. | ACCEPT_CANDIDATE | ACCEPT | Q5: accept the missing condensate return for v0. |

Checks performed. Automated consistency is necessary but not sufficient:

- Wrong equipment attachment: none found except the HUMAN_DECISION items below.
- Reversed flow direction: none. Every edge direction matches the runtime unit
  balances and D&V Fig. 1.
- Duplicated entities: none. The loader also rejects them.
- Missing critical stream relation: none among streams 1–11. Two minor omissions
  are noted: the steam condensate return (F-08), and the CW line numbers 12/13
  (F-04).
- Measurement on wrong entity: XMEAS(16) (F-02) and XMEAS(22) (F-01) are flagged.
- Actuator on wrong stream/equipment: XMV(10)/XMV(11) are on the inlet rather than
  the return edge (F-03).
- Ambiguous source semantics: the condenser lumping (F-05) and the
  `reactor_feed_mixer` modeled zone (F-06).
- Unsupported semantics invented by the fixture: none found. The condenser node,
  `condenser_outlet`, and `separator_vapor` are flowsheet entities without their own
  runtime state; that is acceptable for a static graph (spec: DEXPI presence does
  not imply dynamics).

## 7. Findings

| ID | Severity | Finding | Proposed handling |
|---|---|---|---|
| F-01 | review item | XMEAS(22) label "Separator…" vs condenser attachment (§5) | human chooses Option A/B/C |
| F-02 | review item | XMEAS(16) "Stripper pressure" is computed from `PTV` (`python_backend.py:1150`, `teprob.f:694`), the pressure of the compressor-discharge/reactor-feed vapor zone. The model has no stripper pressure state. D&V Fig. 1 draws the PI on stripper overhead line 5; Bathelt shows PI 1501 at the stripper | human decides: keep `stripper` (nomenclature) or attach to `stream_5`/`reactor_feed_mixer` (runtime state) |
| F-03 | review item | XMV(10)/XMV(11) are attached to `*_cooling_water_in`. Both figures place the CW control valves on the **return** lines 12/13 (V-1101, V-1201). The flow is the same along the single-path loop | human decides whether the inlet-edge attachment is acceptable |
| F-04 | metadata | CW return lines are numbered 12 and 13 in D&V Fig. 1 and Bathelt Fig. 3, but the fixture has `stream_number: null`. D&V Table 1 lists only process streams 1–11 | human decides whether figure line numbers belong in `stream_number` |
| F-05 | info | The condenser has no runtime holdup. Its duty is lumped into the separator energy balance | accept as a static-topology abstraction |
| F-06 | info | `reactor_feed_mixer` is a modeled vapor zone (`VTV` "Compressor volume", `PTV`). D&V draws only a header | accept; the name is descriptive, no tag |
| F-07 | info | The purge is drawn off the separator vapor line; the fixture uses separator → purge directly | accept as equivalent (runtime purge = separator vapor) |
| F-08 | info | The stripper reboiler is lumped. There is no condensate-return edge. XMEAS(19) is derived from the stripper duty | accept, or add a condensate sink in a later version |
| F-09 | info | XMV(5) is a compressor spillback valve, attached to `compressor` | accept |
| F-10 | provenance | The fixture's `source_refs` cite only `downs_vogel_1993` and `upstream_constants`. The equation-level and Bathelt evidence lives only in this package | if promoted, cite the vendored model source and Bathelt Fig. 3 in the new fixture |
| F-11 | provenance | The vendored paper filenames do not match their content: `Bathelt2015_ExtendedTEP.pdf` = Reinartz et al. 2021; `Reinartz2021_RevisedTEP.pdf` = Bathelt et al. 2015; `Reinartz2021_TEPTestbed.pdf` = Capaci et al. 2019. They are not renamed here; this package cites them by sha256 + true bibliography | human decides on a rename in a separate change |
| F-12 | info | Upstream comments are not reliable semantics. Example: `constants.py:64` labels `VTC` "Stripper (condenser) total volume" | none; supports treating labels as names, not topology |

### Evaluator-only boundary (mechanical)

- The Agent graph fixture contains no IDV spelling, no IDV name, and no
  fault/disturbance vocabulary (existing loader check + new test).
- No graph/projection query exposes a disturbance relation (existing test). Every
  review-matrix row uses only the `MEASURES`/`ACTUATES` relations (tested).
- `tep_sim.evaluator_bindings` is imported by no other `tep_sim` module and is not
  re-exported (new AST test + existing namespace test).
- The visible fixture file name and provenance strings reveal no candidate causes.
  The evaluator fixture is bound to graph hash `2b4adf94…`, and no Agent-visible
  path loads it.

## 8. Fixture versions and verification promotion

**No fixture is created or changed in this package.** The rules below follow the
owning spec (`docs/specs/dexpi-binding-v0.md`). A human-verified mapping must be
published as a new fixture version with its own provenance and pin.

1. **Baseline stays immutable.** `tep-process-graph` 0.1.0 (canonical sha256
   `2b4adf94…d01f2b`) and its evaluator fixture 0.1.0 are never edited. 0.1.0
   permanently represents the curated, `PENDING_HUMAN_REVIEW`, `CURATED_MAPPING`
   baseline.
2. **The evidence package was published unsigned.** Package 0.1.0 (PR #10) was
   `PENDING_HUMAN_SIGNOFF` with every row `PENDING`. The human decisions were
   recorded afterwards in a separate sign-off change (§10).
3. **No automated promotion.** No automated component may create a human-verified
   fixture, set `HUMAN_VERIFIED_MAPPING`, or change `review_status` to a verified
   value. The tests enforce this for this package.
4. **Promotion always means a new version.** After the human decisions are recorded
   (§10), a separate human-authored promotion change **MUST** publish a new verified
   fixture version (e.g. `tep-process-graph` 0.2.0 with its own pin). This applies
   **even if no topology or binding changes.** Verification provenance is itself
   versioned engineering truth, and that is sufficient reason for a new fixture
   version.
5. **Provenance per row.** The promoted fixture records the human review provenance:
   - reviewer;
   - date;
   - this package id/version;
   - the decision record.

   It uses `HUMAN_VERIFIED_MAPPING` **only** for rows the human reviewer explicitly
   accepted. Every other row keeps its curated method and status.
6. **Semantic changes only in the new version.** If the reviewer rejects rows and
   mappings change (e.g. Q2, Q3, Q4, Q5), those changes also appear only in the new
   fixture version.
7. **Evaluator follows the graph hash.** The evaluator fixture is bound to the
   graph's canonical content hash. Whenever the promoted graph hash changes, a
   corresponding new evaluator fixture version must be published, bound to that
   hash. Promotion always changes the graph hash, because provenance/method/status
   are part of the hashed content.

The evidence does not show any current mapping to be *wrong*:

- F-01 most likely confirms the current attachment.
- F-02, F-03 and F-04 are representational choices that need a human decision.

Whether the promoted version also carries semantic changes is the reviewer's call.
That it is a new version is not optional.

## 9. Questions requiring human sign-off

1. **XMEAS(22)**: choose Option A (retain condenser), B (separator), or C (unresolved).
2. **XMEAS(16)**: keep it on `stripper`, or bind it to the runtime vapor zone / stream 5?
3. **XMV(10)/XMV(11)**: accept the actuator on the CW inlet edges, or move it to the
   return edges where the figures draw the valves (this needs evaluator fixture
   re-publication)?
4. **CW line numbers 12/13**: record them as `stream_number`, or keep `null`?
5. **Condensate return / reboiler** (F-08): accept the omission for v0?
6. Confirm the agent's **visual figure readings** (Fig. 1 instruments, Bathelt tags)
   in the matrix.
7. **MS-1**: is the official DEXPI `TennesseeEastman.xml` required before D0, or is
   the curated equivalent acceptable? (Currently `NEEDS_SOURCE`, and it blocks no
   binding.)
8. **F-11**: approve renaming the misnamed paper PDFs (separate change)?
9. For each of the 49 `ACCEPT_CANDIDATE` binding rows and 31 topology rows: record
   ACCEPT / REJECT / NEEDS_SOURCE.

## 10. Sign-off

Evidence package 0.1.0 (PR #10) was published unsigned (`PENDING_HUMAN_SIGNOFF`).
This sign-off is the separate change that §10 of that package required. It:

1. Sets `human_reviewer_decision`, `reviewer`, and `review_notes` per row in the JSON,
   adds a `signoff` record, and changes `status` to `HUMAN_SIGNOFF_RECORDED`.
2. Updates the guard test so it checks this signed-off state.
3. Re-renders the decision columns in this document. The column-by-column
   mirroring test still applies.
4. Leaves fixture publication to a separate, human-authored promotion change. That
   change MUST publish a new verified graph fixture version, together with the
   matching evaluator fixture version, even though no mapping changed (§8). The
   0.1.0 baseline is never edited.

### Recorded decisions (reviewer: chengting, 2026-10-01)

| Question | Decision |
|---|---|
| Q1 XMEAS(22) | **Option A**: retain the condenser attachment. The "Separator…" label is a lumping/naming legacy of the original model, and the runtime name is not renamed |
| Q2 XMEAS(16) | Keep the attachment on `stripper`. The promoted fixture provenance records that the runtime value is sourced from the `PTV` vapor-zone state |
| Q3 XMV(10)/XMV(11) | Accept the inlet-edge attachment for v0. ACTUATES is a functional-control relation in v0, not physical valve coordinates. The return-side valve location stays a note |
| Q4 CW lines 12/13 | `stream_number` stays `null`. Figure utility line numbers are not process stream numbers |
| Q5 Condensate return / reboiler | Omission accepted for v0 |
| Q6 Visual readings | **Personally checked** by the reviewer against D&V Fig. 1 and Bathelt et al. Fig. 3, and confirmed correct |
| Q7 Official DEXPI XML (MS-1) | Not required for D0; the curated equivalent graph is accepted. MS-1 is now `NOT_REQUIRED_FOR_D0` |
| Q8 F-11 PDF misnaming | Rename approved, to be done in a separate provenance-hygiene PR |
| Q9 Row decisions | Bulk ACCEPT of 49 binding and 31 topology `ACCEPT_CANDIDATE` rows. The 4 binding and 4 topology `HUMAN_DECISION_REQUIRED` rows are ACCEPT per Q1–Q5. Result: **88 / 88 ACCEPT** |

| Field | Value |
|---|---|
| Human reviewer | chengting |
| Date | 2026-10-01 |
| Recorded by | automated coding agent, transcribing the reviewer's explicitly stated decisions on the reviewer's instruction (the agent made no decision) |
| Package decision | ACCEPT |
| Resulting fixture version | _none yet_: promotion is a separate change (§8) |

Follow-ups this sign-off implies (none of them is done here):

- **Promotion change.** Publish a new `tep-process-graph` version with
  `HUMAN_VERIFIED_MAPPING` for the 53 accepted bindings and the human review
  provenance, plus a matching evaluator fixture version.
- **Spec/ADR.** Record the Q2 and Q3 interpretations before or with that change:
  - MEASURES attachment is the engineering semantic location, even when the runtime
    state comes from elsewhere;
  - ACTUATES is a functional-control relation in v0.

  The v0 binding provenance schema has no free-text field for the Q2 note, so the
  promotion must either extend the schema (a spec change) or reference this decision
  record.
- **F-11 rename PR.**

The A3 human-review milestone in `docs/ecosystem/implementation-plan.md` stays
**HUMAN REVIEW PENDING** until the verified fixture version is published.
