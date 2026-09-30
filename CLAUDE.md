# tep-sim

Tennessee Eastman Process 的 **agent-agnostic、forkable process sandbox**。

先讀：

- `AGENTS.md` — repo 邊界與 coding-agent 規則
- `docs/architecture.md` — environment architecture
- `docs/roadmap.md` — 4-phase critical path
- `docs/specs/` — canonical testable contracts
- `docs/ecosystem/implementation-plan.md` — 跨 repo branch/implementation 順序

## 本 repo 負責

- 包裝 `vendor/tep-sim-upstream` 成穩定 environment API；
- reproducible reset / observe / step / rollout；
- canonical XMEAS / XMV / IDV registry；
- typed disturbance / intervention；
- snapshot / fork / replay；
- machine-readable capability + deterministic safety evaluation；
- DEXPI/process-data -> compact `ProcessGraph`；
- process entity <-> XMEAS/XMV/IDV binding；
- run/branch provenance 與 artifacts。

## 本 repo 不負責

- LLM provider / LangGraph / agent orchestration；
- dynamic subagents / prompts / memory；
- RCA / HAZOP / recovery reasoning；
- P&ID OCR / YOLO / U-Net / generic model generation；
- 3D plant reconstruction。

不要因為 integration experiment 需要這些能力，就把它們加進 `tep-sim`。

## Canonical specs

實作前讀對應 spec：

```text
docs/specs/environment-api-v0.md
docs/specs/snapshot-fork-replay-v0.md
docs/specs/dexpi-binding-v0.md
docs/specs/safety-capability-v0.md
```

如果 upstream 實際行為證明 spec 假設錯誤，先更新 proposal/ADR，再改 contract；不要讓 code 和 docs 靜默分叉。

## Simulator 定案

- upstream：`vendor/tep-sim-upstream`（jkitchin/tennessee-eastman-profbraatz submodule）。
- 不重寫 TEP physics；建立穩定 adapter。
- Windows 目前使用 `.venv` + `.pth` 指向 upstream `src`，避免 editable-install/meson compiler 問題。
- Direct MV intervention 使用 `ControlMode.MANUAL` 或合適 custom controller；`CLOSED_LOOP` PI 可能在下一 step 覆寫手動 XMV。
- runtime metadata source of truth = vendored simulator/generated registry，不是 paper appendix、DEXPI 猜測或 prompt。

## DEXPI 邊界

DEXPI/process data 只提供靜態 topology/engineering semantics；TEP simulator 仍是 dynamics source of truth。

```text
DEXPI / ProcessGraph
        |
        v
binding registry
entity <-> XMEAS/XMV/IDV
        |
        v
TEPSimulator
```

不要做 drawing OCR。不要用 LLM 在 environment runtime 動態猜 binding。

## Environment API 方向

```text
construct(config)
reset()
observe()
step()
apply(intervention)
capabilities()
snapshot()
fork(snapshot)
rollout(horizon)
evaluate_safety(result)
replay(...)
```

API 必須 typed、可測、可重播、失敗時不偷偷 mutation。

## Scenario / HAZOP-facing 邊界

`tep-sim` 可以 deterministic 地回答：

1. semantic deviation 是否可由目前 TEP physics 表示？
2. 若可，對應哪個受支援 intervention？
3. rollout 後 numeric process/safety state 發生什麼？

它不判斷正式 HAZOP finding，也不能把 pipe rupture、dispersion、fire、explosion 等未建模 physics 當成 simulation fact。

## Critical path

```text
Environment API
-> Snapshot/Fork/Replay
-> DEXPI/ProcessGraph binding
-> Capability/Safety
```

完成後優先把能力交給 `tep-agent-lab`，不要先加 UI/3D/更多 agent-specific feature。

## 高價值測試

至少驗證：

1. same seed/config reproducibility；
2. validation failure 不改 state；
3. snapshot/fork isolation + 明確 fidelity；
4. XMEAS/XMV/IDV registry 與 upstream 一致；
5. DEXPI/process binding 不指向未知 runtime variable；
6. unsupported scenario 在 mutation 前明確失敗；
7. run/branch provenance 足以 replay / audit。
