# tep-sim

Tennessee Eastman Process 的 **agent-agnostic simulation sandbox**。

完整設計見 `docs/architecture.md`，實作順序見 `docs/roadmap.md`，跨 coding-agent 規則見 `AGENTS.md`，多 repo 邊界見 `docs/ecosystem/README.md`。

## 這個 repo 負責什麼

- 包裝 `vendor/tep-sim-upstream` 成穩定的 environment API；
- reproducible reset / step / rollout；
- canonical XMEAS / XMV / IDV registry；
- disturbance / intervention；
- telemetry；
- snapshot / fork / replay；
- capability discovery；
- deterministic safety evaluation；
- scenario/result persistence；
- read-only visualization adapter。

## 這個 repo 不負責什麼

- LLM provider；
- LangGraph / agent orchestration；
- dynamic subagents；
- prompts / memory；
- HAZOP/RCA reasoning；
- P&ID image recognition；
- generic P&ID -> simulation compiler。

不要因為某個 integration experiment 需要這些功能，就把它們加進 `tep-sim`。

## Simulator 定案

- upstream：`vendor/tep-sim-upstream`（jkitchin/tennessee-eastman-profbraatz，git submodule）。
- 不重寫 TEP physics；先建立穩定 adapter。
- Windows 開發環境目前使用 `.venv` + `.pth` 指向 upstream `src`，避免 meson-python compiler 問題。
- Direct MV intervention 使用 `ControlMode.MANUAL` 或合適的 custom controller；`CLOSED_LOOP` 的 PI controller 可能在下一 step 覆寫手動 XMV。
- runtime metadata 的 source of truth 必須來自 vendored simulator，而不是 paper appendix 或 prompt。

## Environment API 方向

```text
reset(seed, config)
observe()
capabilities()
snapshot()
fork(snapshot)
inject(intervention)
step(n)
rollout(horizon)
evaluate_safety(result)
replay(run_id)
```

API 要 typed、可測、可重播。

## HAZOP 支援的正確邊界

`tep-sim` 可以提供 HAZOP workflow 所需的 simulation primitive，但不執行 HAZOP reasoning。

例如 integration layer 可以提出：

```text
node = reactor_cooling_loop
parameter = flow
guide_word = LESS
magnitude = 20%
```

本 repo 的 scenario compiler 只回答：

1. 這個 deviation 是否能由目前 TEP physics 表示？
2. 若可以，對應哪一個 deterministic intervention？
3. rollout 後 process/safety state 發生什麼？

若要求的是 pipe rupture、toxic dispersion、fire、explosion 等目前模型沒有的 physics，必須明確回 unsupported，不可讓 agent 或程式自行腦補。

## 第一個 milestone

```text
reset
-> baseline rollout
-> snapshot
-> fork
-> inject IDV(4)
-> rollout
-> collect XMEAS/XMV/safety trace
-> replay same seed/config
-> verify reproducibility
```

接著再建立 generalized scenario contract 和 HAZOP-friendly deviation compiler。

## 驗證

```bash
.venv/Scripts/activate && python -c "from tep import TEPSimulator; s=TEPSimulator(); s.initialize(); print(s.step())"
```

至少需要 automated tests 驗證：

1. same seed/config 可重現；
2. snapshot/fork 不互相污染；
3. XMV registry 與 upstream 一致；
4. invalid intervention 被 schema/bounds 擋下；
5. unsupported hazard 明確失敗；
6. 每個 run 有完整 provenance。
