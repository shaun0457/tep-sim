# tep-sim

Tennessee Eastman Process 動態模擬 + event-driven LLM agent 診斷 / 受控介入。

完整設計見 `docs/architecture.md`，實作順序見 `docs/roadmap.md`，跨 coding-agent 規則見 `AGENTS.md`。

## 定案

- 模擬器：`vendor/tep-sim-upstream`（jkitchin/tennessee-eastman-profbraatz，git submodule）。
  不重寫模型、不換 Rust；瓶頸在 LLM 決策延遲，不在積分器（純 Python 已 ~1000 steps/s）。
- 安裝：**不要 `pip install -e vendor/...`**——meson-python 在 Windows 即使 `-Dfortran=disabled`
  也要 C compiler。改用 `.venv` + 把 `vendor/tep-sim-upstream/src` 寫進 site-packages 的
  `tep_upstream.pth`。依賴只有 numpy。
- Agent 控制：必須用 `ControlMode.MANUAL` 或自訂 `BaseController` plugin。
  `CLOSED_LOOP` 下 `set_mv()` 會在下一個 `step()` 被內建 PI 控制器覆寫。
- **CLI coding agents 只負責開發 repo，不作為線上 plant-control runtime。**
- 線上 runtime 採 hybrid：simulation / telemetry / detector / safety / action gate 為 deterministic Python；LLM 只在 incident slow path 做診斷與 recovery proposal。
- Healthy path 必須做到 **0 model calls**。
- LLM 不得直接呼叫 `set_mv()`；只輸出 typed proposal，由 deterministic gate 驗證 target、range、delta/rate、cooldown、permission、safety 後才可執行。
- 先用單一 reasoning agent；只有在可量化證明有幫助時才加入 bounded subagents。不要先建立 Supervisor/DataEngineer/DataScientist 等固定角色鏈。
- LangGraph 只包 incident reasoning workflow；不要把每秒 simulation step 放進 graph。先以 plain Python FSM 完成 MVP，真的需要 checkpoint/resume、human interrupt、bounded retry 或 stateful branching 再引入 LangGraph。
- 不要在 prompt 裡手寫/記憶 XMEAS/XMV mapping。runtime source of truth 來自 vendored simulator metadata/constants；目前對照見 `docs/runtime-variable-map.md`。
- `data/raw/`（3.2 GB Rieth 資料集）不進 git；本機路徑見 .gitignore 註解。
- `docs/papers/` 是出版社論文 → repo 保持 private。
- Blender / DEXPI / Omniverse 視覺化是展示層，在模擬器 + incident + gate + recovery verification 迴圈跑通之後才做。
  公開的 TEP DEXPI 檔不存在，要自己建立 process topology / DEXPI representation。

## 第一個端到端 milestone

```text
normal run
-> inject one TEP disturbance
-> deterministic detection
-> compact IncidentContext
-> agent diagnosis + ActionProposal
-> deterministic action gate
-> apply/reject bounded XMV action
-> deterministic post-action verification
-> persist complete run trace
```

建議第一個 fault path 使用 reactor cooling-water scenario，因為 vendored simulator 的關係清楚：

- XMEAS(9) = Reactor Temperature
- XMEAS(21) = Reactor Cooling Water Outlet Temperature
- XMV(10) = Reactor Cooling Water Flow
- IDV(4) = Reactor Cooling Water Inlet Temperature step disturbance

做 blind diagnosis eval 時，不要把 ground-truth IDV 直接給 agent。

## 驗證

```bash
.venv/Scripts/activate && python -c "from tep import TEPSimulator; s=TEPSimulator(); s.initialize(); print(s.step())"
```

後續至少要有 automated tests 驗證：

1. healthy run = 0 LLM calls；
2. XMV registry 與 upstream 一致；
3. invalid proposal 永遠碰不到 `set_mv()`；
4. failed recovery 有 bounded retry，最後進 safe hold；
5. 每個 applied action 都可追溯到 incident、proposal、gate decision 與 verification outcome。
