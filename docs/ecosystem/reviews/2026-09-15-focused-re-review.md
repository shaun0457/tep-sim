# Focused Re-review — Design Review Closure

Status: review record (not a spec)
Date: 2026-09-15
Reviewed ref: `architecture/hybrid-agent-runtime` @ `9db3110`
Original review: `2026-09-15-independent-spec-review.md` (reviewed `9a1316d`)
Disposition record: `../design-review-adjudication.md`
Reviewer: independent architecture/spec review (Claude Opus 5)

Scope: the six items in `design-review-adjudication.md`「Focused re-review contract」only. This is not a repeat of the full architecture review.

路徑縮寫：`RT/` = `docs/ecosystem/blueprints/industrial-agent-runtime/`，`LAB/` = `docs/ecosystem/blueprints/tep-agent-lab/`。

---

## 判定：READY WITH CONDITIONS

三個原 BLOCKER 全部關閉；十項原 MAJOR 中九項已落入 owning spec；未發現新的跨文件矛盾；舊詞（`EvidenceBundle`、full-DAG v0 requirement、K0–K4 canonical schema、排程中的 LangGraph adapter、SIMULATE reference-mutation 例外、host-policy authority 例外）在 canonical/entry 文件中均已不具權威（grep 只剩「not required / superseded / shorthand」語境）。

剩下一個 implementation-defining MAJOR（R1），落在 runtime B1 與 lab C1 的接縫上；未定案前兩者仍會各自發明。R1 是單一、範圍明確的 spec 編輯；修完即可視為 READY FOR DESIGN FREEZE（runtime/lab 範圍）。

---

## 1. 原 BLOCKER 關閉核對

| 原 finding | 狀態 | 證據 |
|---|---|---|
| A-1 Verifier 前/後 | 關閉 | `RT/docs/specs/runtime-v0.md`「Pre/post validation split」、`RT/docs/specs/hybrid-orchestration-v0.md`「Post-execution Verifier」、`RT/docs/specs/deterministic-gates-v0.md` 開頭明寫 pre-execution only；README/architecture 圖已改為 gates → Executor → `verify_result` → `apply`。consumer hook 收斂為 `validate_request`（pre）+ `verify_result`（post）兩個簽名 |
| A-2 Coordinator 擁有 lab state 無介面 | 關閉 | `runtime-v0.md` 定義 `TaskStatus`（7 值）/ `StateDelta` / `ContextProjection` / `TaskStateStore`（`revision/status/project/apply`）；`LAB/docs/specs/investigation-state-v0.md` 改為「Implements: TaskStateStore」，`RcaState.generic_status` 用 runtime enum，budget 權威回歸 runtime；D-021 |
| A-3 Dynamic DAG node 語意 | 關閉（採原審 B 路） | `WorkBatch` / `WorkItem(kind=TOOL\|SUBTASK, depends_on)`；無 ANALYSIS/MERGE；失敗 → `SKIPPED_DEPENDENCY`、無 silent retry、平行受 `max_parallel_width`；SUBTASK 計入 cumulative `max_subagents`；D-009 |

## 2. 原 MAJOR 關閉核對（accepted 且 implementation-defining 者）

| 原 finding | 狀態 | owning spec |
|---|---|---|
| A-4 複合工具預算旁路 | 關閉 | `Budget.extra_dimensions`、`ToolSpec.declared_budget_draw / max_budget_draw`、G2 reservation + 事後 reconcile、複合工具 = SIMULATE（gates / tool-bridge / D-026） |
| A-5 typed Prediction | 關閉 | `hypothesis-experiment-v0.md` `Prediction` + 12 個 feature + `PredictionEvaluation`；`expected_outcomes` 已消失 |
| A-6 候選集洩漏 / C0 | 關閉 | `get_related_disturbances` 移出 blind allowlist；C0 定義為 enumerate/simulate/match 且「不得弱化」；semantic case ID 改 MUST；D-030 |
| A-7 K0–K4 三軸 | 關閉 | `origin × validation × authority`；lab policy = `POLICY/REVIEWED`；K 標籤僅 shorthand；D-023 |
| A-8 ablation 混淆 | 關閉 | `evaluation-v0.md` 唯一 canonical；subagents 只在 O 軸；O2/O3 差異已定義；tool exposure 固定；`rca-v0.md` 明寫不維護第三份清單；D-029 |
| A-9 trace 全文 projection | 關閉 | `TraceEvent` MODEL_TURN MUST 附 `context_projection_ref` + prompt/model/sampling/tool-set 版本 |
| A-10 semantic stopping | 關閉 | v0 = finish proposal + 結構檢查；information-gain 標 OPEN_RESEARCH |
| G-2 host-policy authority 例外 | 關閉 | 已刪；gates G1 明寫「no host-policy exception」 |
| B-11 SIMULATE 例外 | 關閉 | tool-surface「There is no recovery exception」；D-013 |
| C-4 CausalClaim / NO_ABNORMAL_CAUSE | 關閉 | `rca-v0.md`；精確 match 規則留給 `scoring_config`（D0 事項，不擋 C1） |
| C-12 Engineering records | 關閉 | 新 `engineering-records-v0.md`：InvestigationReport / DecisionRecord / ExperimentRecord；archive-only |
| C-13 experiment dedup key | 關閉 | `canonical_experiment_key` 基於 content checksum |
| C-16 MUTATE revision binding | 關閉 | gates「mandatory, not optional TOCTOU hardening」 |

## 3. 新矛盾檢查

未發現新的跨文件 / 跨 repo 矛盾。抽查項目：

- `max_subagents` cumulative 語意（runtime-v0 / subagents / hybrid / AGENTS）一致；
- `TaskStatus` 值集（runtime-v0 / investigation-state）一致；
- `validation` / `authority` enum（rule registry / adjudication / decision register）一致；
- Prediction feature 詞彙與 tool-bridge `compute_response_features` 對齊；
- C/O 軸在 evaluation / rca / implementation-plan / adjudication 一致；
- spec status 全部為 `proposal`；`accepted working policy` 為 `documentation-standard.md` 明列允許的例外；
- `RT/docs/decisions/ADR-001-minimal-explicit-executor.md` 仍含 Dynamic DAG / LangGraph 字句，但其 status 為 superseded，不具權威。

## 4. Deferred / OPEN_RESEARCH 非阻塞確認

promotion 五物件、`RecoveryStrategy` DSL、LangGraph adapter、MCP、information-gain stopping、cross-incident memory：在 implementation-plan / roadmap / decision-register 均明確標記，且不再是任何 v0 branch 的隱含依賴。

---

## 5. 剩餘 finding

### MAJOR-R1 — Main Agent 的狀態提案如何變成 `StateDelta`，未定義

**位置**

- `RT/docs/specs/runtime-v0.md`「Provider abstraction」：`generate(...) -> ModelTurn`，`ModelTurn` 無欄位定義；
- `RT/docs/specs/hybrid-orchestration-v0.md`「Reference runtime loop」：ROUTE_DECISION 只有 `TOOL_REQUEST | WORK_BATCH | FINISH_PROPOSAL`；
- `LAB/docs/specs/investigation-state-v0.md`「`apply`」；
- `LAB/docs/specs/hypothesis-experiment-v0.md`「Model interpretation」`proposed_evidence_links[]`。

**問題**

新增 hypothesis、提出 `HypothesisEvidenceLink`、提交 `ExperimentInterpretation`、更新 `WorkingExplanation`——這些是 RCA 的核心動作，全都是模型提出的狀態變更，但沒有任何 route 承載它們。`runtime-v0.md` 說 Main Agent「Cannot update TaskStateStore directly without validated delta」，暗示模型可以產生 delta；loop 圖卻只在 `verify_result` 之後才 `apply(delta)`，暗示 delta 只由工具結果衍生。整個 `docs/ecosystem/` 找不到任何一句說明 delta 的產生路徑。

實作者至少有三種互不相容的做法：

1. `ModelTurn` 直接帶 `state_deltas[]`，經 `verify_result` 後 apply（是否經 G0–G3？經哪些？）；
2. lab 註冊 `propose_hypothesis` / `link_evidence` 等 TOOL（side-effect class 是 PROPOSE 還是 COMPUTE？tool-surface 的 PROPOSE 定義是「candidate intervention/plan data」，不含 hypothesis）；
3. 只在 FINISH_PROPOSAL 時一次性 apply。

三者的 trace 事件序、budget 計費（是否吃 `max_tool_calls`）、E3「useful evidence links per model/tool call」的分母都不同。

同一缺口的兩個附帶點：

- **`ObservationRecord` 是自動還是選擇性登記**：`investigation-state-v0.md` 寫「may be registered」且限「relevant」結果；`design-review-adjudication.md` 與 `information-plane.md` 寫「ToolResult → ObservationRecord」（自動）。E3「unused observation rate」只有在自動登記下才有意義。
- **平行 WorkBatch 的 `base_revision`**：模型在 revision 10 提出 3 個平行 TOOL item，結果回來要 apply 三個 delta；若 `base_revision` 都是 10，第二、三個依 optimistic check 會被判 stale。需明寫：工具衍生 delta 的 `base_revision` 由 Coordinator 在 apply 時填當前 revision，只有模型提出的 delta 才綁模型看到的 projection revision。

**為何是 MAJOR 而非 BLOCKER**

任一做法都能建出可運作的系統；但 B1 的 `ModelTurn` schema 與 fake provider、C1 的 `apply()` 合法操作集合，都依賴這個決定，兩個 branch 若平行開工必然對不起來。

**建議修法**（估計是 runtime-v0 加一節、investigation-state 加一段）

- `ModelTurn = { tool_requests[], work_batch?, state_deltas[], finish_proposal?, prose }`；
- 模型提出的 `state_deltas` 走 G0（schema）+ `validate_request`（lab 檢查 ref 可見性 / 合法路徑）→ apply；不佔 `max_tool_calls`，但計入 `max_steps`；
- `ObservationRecord` 對所有成功 ToolResult 自動登記，由 Executor / run log 產生，`base_revision` 由 Coordinator 填；
- `hypothesis-experiment-v0.md` 的 `proposed_evidence_links` 明寫等價於一組 `StateDelta(operation=ADD_EVIDENCE_LINK)`。

---

## 6. 開工條件

| 範圍 | 建議 |
|---|---|
| `tep-sim` A1–A4 | GO（不變） |
| runtime B1 | 補上 R1 的 `ModelTurn` / delta 路徑後 GO；其餘 B1 契約（InformationRef、Budget、ToolSpec、TaskStateStore、WorkBatch、TraceEvent、fake provider）已可直接實作 |
| lab C1 | 同上——`apply()` 的合法操作集合與 ObservationRecord 登記規則取決於 R1；其餘（RcaState 欄位、projection 函數、run log 佈局、三種 engineering record、visibility 測試）已可實作 |
| B2–B4、C2–C5 | R1 關閉後依 `implementation-plan.md` 順序，無額外條件 |
