# Independent Spec Review — Industrial Agent Playground

Status: review record (not a spec)
Date: 2026-09-15
Reviewed ref: `architecture/hybrid-agent-runtime` @ `9a1316d`
Reviewer: independent architecture/spec review (Claude Opus 5), per the review contract in `review.txt`
Scope: all 41 program / runtime / lab / environment documents listed in the contract were read in full.

路徑縮寫：`RT/` = `docs/ecosystem/blueprints/industrial-agent-runtime/`，`LAB/` = `docs/ecosystem/blueprints/tep-agent-lab/`。

---

## 執行判定

### NOT READY FOR DESIGN FREEZE（但距離不遠，且可部分放行）

`implementation-plan.md` 自訂的 freeze 出口條件是「implementation agents can work from specs without inventing product architecture」。目前至少有四處，工程師必須自行發明架構才能寫出第一行 code：

1. Verifier 到底在 Executor 之前還是之後（三份文件三種說法）；
2. generic runtime 的 Coordinator 如何對它「不認識」的 domain `InvestigationState` 執行 status/revision transition；
3. Dynamic DAG 的 `ANALYSIS` / `MERGE` node 由誰執行、model call 如何計費、失敗如何傳播；
4. Tool Bridge 複合工具（sensitivity / optimizer）內部跑 rollout 時，budget 與 side-effect gate 如何計算。

這些是架構缺口，不是實證問題。另一方面，`tep-sim` 的四份 spec（A1–A4）是自足、可測、與上述問題無關的——可以立刻放行。

```text
                 ┌────────────────────────────────────┐
                 │ tep-sim  (A1–A4)                    │  ✅ 契約完整、可測、無外部依賴
                 │ env API / snapshot / DEXPI / safety │     → 可立即開工
                 └────────────────┬───────────────────┘
                                  │ pinned
   ┌──────────────────────────────┴──────────────────────────────┐
   │ industrial-agent-runtime                                     │
   │  Task/Budget/ToolSpec/Gate/Trace   ✅ 良好                    │
   │  Coordinator/Executor/Verifier     ⚠ Verifier 位置矛盾        │
   │  Dynamic DAG                       ❌ node 語意未定義           │
   │  Subagents                         ✅ 足夠                     │
   │  LangGraph adapter                 ⚠ 無實驗需要、與 OQ-6 矛盾   │
   └──────────────────────────────┬──────────────────────────────┘
                                  │ "coordinated through" ← 這條線沒有契約
   ┌──────────────────────────────┴──────────────────────────────┐
   │ tep-agent-lab                                                │
   │  InvestigationState   ⚠ 寫入路徑跨 repo 未定義                 │
   │  Hypothesis/Experiment ⚠ expected_outcomes 為 free text        │
   │  Rule Registry K0–K4   ⚠ 三軸混在一軸；「reviewed policy」無名分 │
   │  Tool Bridge           ⚠ 複合工具繞過 rollout budget           │
   │  Benchmark/Eval        ⚠ 候選集經 topology 洩漏；C0 未定義      │
   │  RCA/HAZOP/Recovery/AutoResearch  ✅ 方向正確、已正確排後        │
   └─────────────────────────────────────────────────────────────┘
```

---

## A. Top 10 findings

| # | Severity | Area | Finding | Why it matters | Recommended action |
|---|---|---|---|---|---|
| 1 | **BLOCKER** | Runtime / Verifier | Verifier 位置三份文件矛盾：`RT/README.md`「Conceptual runtime」與 `RT/docs/architecture.md`「Hybrid runtime model」把 Verifier 畫在 Executor 之前（Main Agent → Verifier → gates → Executor）；`RT/docs/specs/hybrid-orchestration-v0.md`「Macro orchestration」把它放在 EXECUTE_READY_WORK → INGEST_RESULTS → VERIFY（之後）。Verifier 的職責清單（evidence/artifact ref 存在、DAG dependency completion、provenance）只有執行後才能檢查；schema/authority 檢查則是 gate 的事 | 實作者必須自己決定 Verifier 是 pre-execution request validator 還是 post-execution result validator；兩種選擇會造成不同的 trace 事件序、不同的 acceptance test 語意（runtime-v0 test 8 vs hybrid test 6） | 定案：gates = pre-execution（request）；Verifier = post-execution（result/state）。修 README 與 architecture.md 的圖。同時合併「consumer validator」的三個名字（見 B-9） |
| 2 | **BLOCKER** | Repo boundary / State | `InvestigationState` 由 lab 擁有（`LAB/docs/specs/investigation-state-v0.md`），但「Transitions are Coordinator-controlled」「Coordinator, not model prose, owns status/budget/revision transitions」，而 Coordinator 屬 runtime，且 `RT/README.md`「Repository does not own: application-specific Investigation State fields」。`information-plane.md` 寫「Owner: tep-agent-lab, coordinated through industrial-agent-runtime」——這條「coordinated through」沒有任何契約：runtime 不知道 `StateDelta` 的 `target_ref/field` 是什麼，也沒有 generic 的 status enum（`WAITING_FOR_WORK`、`READY_TO_CONCLUDE` 都是 lab enum） | 這是 runtime ↔ lab 的唯一雙向資料流，卻沒有 interface。實作者會發明：要嘛 runtime import lab（違反 D-001/D-002 依賴方向），要嘛 lab 重寫 Coordinator（違反 lab AGENTS.md「do not fork its executor」） | 在 runtime 新增一個最小 generic 契約，例如 `TaskStateStore` protocol：`apply(delta, expected_revision) -> revision`、`project(policy) -> ContextProjection`、`status() -> GenericStatus`。lab 實作它。generic status 只保留 RUNNING/WAITING/READY/DONE/FAILED/EXHAUSTED；lab 的細狀態放 `metadata` |
| 3 | **BLOCKER** | Dynamic DAG | `hybrid-orchestration-v0.md`「PlanNode」定義 `type: TOOL \| ANALYSIS \| SIMULATION \| SUBTASK \| MERGE`，但：(a) `ANALYSIS` 與 `TOOL` 差別未定義；(b) `MERGE` 由誰執行——若需 LLM，它是 Main Agent turn 還是 subagent？算不算 `max_model_calls`？(c) `SUBTASK` node 是否計入 `max_subagents`／depth？(d) node 失敗後 dependents 是 skip / cancel / block？(e) 無 cancellation、retry、parallel-width 語意（`max_parallel_width?` 是 optional 欄位）；(f) `plan_budget` 與 task `Budget` 的關係未定義。最關鍵：spec 從未回答「DAG 比一組帶 `depends_on` 的 Subtask 多了什麼」 | 沒有這些語意，acceptance test 2「三 node 平行 DAG」和 test 5「failed node → bounded replan」無法寫出唯一正確的期望結果；不同實作者會得到不同 trace，D2 orchestration ablation 就量不到「Dynamic DAG」本身 | 兩條路擇一：(A) 補齊語意（建議：`MERGE` 一律 = 下一個 Main Agent turn，不是 node type；`ANALYSIS` 刪除，併入 `TOOL`；SUBTASK node 計入 subagent 配額；失敗 → dependents 標 `SKIPPED`，回到 Main Agent replan）；(B) v0 把 DAG 降為「`Subtask[]` + `depends_on`」的 batch 契約（見 J），DAG 一詞留給 O4 ablation。建議 B |
| 4 | **MAJOR** | Tool / Budget / Safety | `LAB/docs/specs/tool-bridge-v0.md`「Sensitivity / design of experiments」`run_sensitivity_analysis(simulation_callable_ref, budget)` 與 `optimize_parameters(objective_ref, trial_budget)` 會在 adapter 內部跑 N 次 isolated rollout。但 (a) 這兩個工具的 `side_effect_class` 未指定（COMPUTE？SIMULATE？）；(b) generic G2 budget gate（`deterministic-gates-v0.md`）只看 `max_tool_calls`，而 `max_simulation_rollouts`/`max_simulated_horizon_total` 是 lab 專屬（`rca-v0.md`「Budgets」明說「application-specific and must be enforced outside model prose」），卻沒有任何契約說 lab 的 budget 維度如何接進 G2；(c) 一次 tool call = 500 rollouts，`max_tool_calls=20` 形同虛設 | 這是唯一能讓 Agent 以一個 READ/COMPUTE 等級的請求消耗大量模擬預算、且不經 SIMULATE gate 的路徑。同時破壞 E4 效率指標（rollout 數被藏在一個 tool call 裡） | (1) `Budget` 加 generic 的 `extra_dimensions: dict[str, int]`，G2 對其一視同仁扣減；(2) `ToolSpec` 加 `declared_budget_draw`（例如 `{rollouts: trial_budget}`），複合工具呼叫前必須預扣；(3) 複合工具 side-effect class 明定為 SIMULATE，並要求 adapter 宣告 isolation |
| 5 | **MAJOR** | Evaluation | `hypothesis-experiment-v0.md`：`ExperimentProposal.expected_outcomes[]` 與 `Hypothesis.falsification_conditions[]` 是 free text。但 `evaluation-v0.md` E3 的「experiment discrimination score」「information-value proxy」「belief/rank change」都需要機器可比對的預測。範例寫「H1 predicts … signature A」——A 是什麼、誰判定「符合 A」？ | 沒有 typed prediction，discrimination 只能由人或另一個 LLM 判，違反 rule 12（deterministic validation 優先），且 E3 是本計畫最核心的「科學行為」指標 | 新增 `Prediction` 契約：`{hypothesis_ref, variable_id, feature: DIRECTION\|PEAK\|LAG\|SETTLING\|…, expected_range, tolerance}`。`ExperimentProposal.expected_outcomes` 改為 `Prediction[]`。discrimination score 定義為：跨 hypothesis 的預測在 metric 空間的可分離度 × 實際結果落點 |
| 6 | **MAJOR** | Benchmark validity | `tool-surface-v0.md` 的 `get_related_disturbances(node_id)` 與 `dexpi-binding-v0.md` 的 binding registry 會把 reactor 綁到 IDV(4)/(11)/(14)（`dexpi-tep-integration.md`「Build the TEP binding registry」）。一個不需 LLM 的策略——「查 trigger node 綁定的所有 IDV → 每個 fork 一次 → 用 `compare_trajectories` 選最像的」——很可能直接解掉第一個 scenario family。`evaluation-v0.md` 的 C0「deterministic/no-agent baseline」存在但未定義做什麼 | 若 C0 = 上述枚舉比對即可拿到 top-1，整個 capability/orchestration ablation 量到的是 LLM 的 overhead，不是 investigation 能力。這正是「benchmark whose answer is encoded」的變體：答案編碼在 binding registry 裡 | (1) 明定 C0 = 「enumerate bound IDVs + fork + trajectory match」，並列為每份報告的必報基準；(2) identifiability pilot（`benchmark-design-v0.md`）加一條：若 C0 解得掉，該 case 不得標為 MEDIUM 以上；(3) HARD tier 必須包含 cause 不綁在 trigger node 上的案例（例如 feed composition 導致反應器溫升）；(4)「semantic case IDs」從 optionally 改為 MUST |
| 7 | **MAJOR** | Knowledge / Authority | K0–K4（`knowledge-rule-registry-v0.md`）把三個正交軸疊成一軸：K0 是權威（runtime 說了算）、K1 是審查狀態、K2 是驗證成熟度、K3 是來源、K4 是作者。後果：(a) 「Precedence for execution truth」鏈中出現 `reviewed policy` 這個 K0–K4 之外的第六級，而 lab policy gate 的規則（allowed actuators、max delta，`recovery-v0.md`「v0 policy constraints」）沒有任何 knowledge level；(b) K1 owner 三份文件三種說法（見 B-3）；(c) Agent 由實驗發現的關係要走 K4→K2，跳過 K3，說明 K3 不是一個「級」而是一個「來源標籤」 | 實作 Rule 契約時 `knowledge_level` 一欄無法同時表達「paper 來源 + 已模擬驗證 + 只准 WARN」；promotion 語意（K3→K2 是改 level 還是改 validation_status？）會被實作者各自決定 | 拆成三個獨立欄位：`origin: SIMULATOR\|FORMAL_DERIVATION\|LITERATURE\|EXPERIMENT\|AGENT`、`validation: NONE\|SIMULATED(envelope)\|REVIEWED`、`authority: BLOCK\|ALLOW\|WARN\|SCORE\|ANNOTATE\|PRIOR`。K0–K4 可保留為這三欄的命名預設組合（方便溝通），但 promotion 只改 `validation`，`authority` 只能由獨立 policy 依 `(origin, validation)` 查表決定。lab policy rules 明定為 `origin=POLICY, validation=REVIEWED` |
| 8 | **MAJOR** | Evaluation design | Ablation 兩軸互相污染：subagents 同時出現在 capability 軸（C6）與 orchestration 軸（O5）；`program-charter.md`「Success criteria for v1」把「Hybrid + counterfactual simulation」列為 orchestration 變體（它是 capability C5）；`rca-v0.md`「Baselines / ablations」是第三份不一致清單；O2「fixed deterministic DAG/workflow」與 O3「Hybrid: deterministic macro + local ReAct」差別未定義——兩者都是「確定性流程包 LLM」。且 `hybrid-orchestration-v0.md`「Tool exposure」允許依「current macro stage」暴露工具子集，但 macro stage 從未在任何文件定義；O1 ReAct 看全部工具、O3 看子集 → tool exposure 是隱藏 confound | D2 ablation 無法「isolate one factor」；報告會把「工具暴露策略」的效應算成「Hybrid」的效應 | (1) subagents 只留在 O 軸，C6 刪除；(2) 定義 O2 = 固定順序（observe→hypothesize→experiment→conclude）每步一個 LLM call、無 replan；O3 = 同樣的 macro loop 但每步內是 ReAct 可多輪；(3) 所有 O-mode 固定同一 tool exposure policy，exposure 策略另開一個 ablation；(4) 以 `evaluation-v0.md` 為唯一 canonical，charter/rca-v0 只連結 |
| 9 | **MAJOR** | Reproducibility | `runtime-v0.md`「TraceEvent」只存 `input summary / output summary`；但 `evaluation-v0.md`「Reproducibility bundle」「Ground-truth leakage checks」要求檢查「prompts/context snapshots」，且「Why did the Agent believe this?」需要該 turn 實際看到的 projection 全文。`prompt/template version` 出現在 evaluation 的 run identity，卻不在 runtime TraceEvent | 用 summary 做 leakage audit 等於沒審；事後無法重建某個 hypothesis 的證據基礎 | TraceEvent 對 `MODEL_TURN` 類型 MUST 附 `context_projection_ref`（artifact，全文）與 `prompt_template_version`、sampling 參數。summary 僅供顯示 |
| 10 | **MAJOR** + OPEN_RESEARCH | Semantic stopping | `investigation-state-v0.md`「Stop readiness」條件含「expected information gain from further allowed work is below configured policy」——沒有任何 estimator 定義，`Hypothesis` 只有 `current_score_or_rank?`（無機率模型）。同段又說「the Main Agent supplies the substantive judgment that evidence is sufficient」。實際上 v0 的 stopping = Agent 自報 + 結構檢查，這與計畫「semantic stopping 是被研究的能力」一致，但 spec 把它寫得像系統會算 information gain | 實作者要嘛發明一個 estimator，要嘛留空；兩者都讓 E3「stop efficiency」的解讀不同 | 明寫：v0 停止 = Agent 提出 `READY_TO_CONCLUDE` + Verifier 結構檢查（最小 schema、無未解 critical open question、每個 ACTIVE hypothesis 至少一個 evidence link）；information-gain 型停止列為 OPEN_RESEARCH，並且若要實作，必須先在 `Hypothesis` 定義 `belief` 的數值語意與更新規則 |

---

## B. Contradiction matrix

### B-1 Verifier 位置
- Document A: `RT/README.md`「Conceptual runtime」、`RT/docs/architecture.md`「Hybrid runtime model」— Main Agent → Verifier → gates → Executor
- Document B: `RT/docs/specs/hybrid-orchestration-v0.md`「Macro orchestration」— GATE/VALIDATE → EXECUTE_READY_WORK → INGEST_RESULTS → VERIFY
- Conflict: Verifier 在執行前或執行後
- Recommended source of truth: hybrid-orchestration-v0.md（後）；修兩張圖

### B-2 InvestigationState 誰擁有 transition
- Document A: `LAB/docs/specs/investigation-state-v0.md`「Status」「Invariants」— Coordinator 擁有 status/budget/revision
- Document B: `RT/README.md`「Repository does not own」— application-specific Investigation State fields；`information-plane.md`「Read/write authority」— InvestigationState write authority = "Coordinator + validated updates"
- Conflict: runtime 元件擁有 lab 物件的 transition，但 runtime 不得認識該物件
- Recommended source of truth: 新增 generic `TaskStateStore` 契約於 runtime-v0.md；investigation-state-v0.md 改為「lab 實作該契約」

### B-3 K1 owner
- Document A: `program-charter.md`「tep-sim」— "K0 runtime truth and reviewed K1 environment constraints" 由 tep-sim 擁有
- Document B: `docs/ecosystem/README.md`「Knowledge authority」— "K1 → tep-sim / reviewed policy"
- Document C: `LAB/docs/specs/knowledge-rule-registry-v0.md`「K1」— "Owner depends on scope"
- Conflict: 唯一能 BLOCK 的非 simulator 規則，owner 不明
- Recommended source of truth: knowledge-rule-registry-v0.md，但改為明確規則：K1 若引用 simulator 量 → tep-sim；否則 → lab `policies/`，並標 `origin=POLICY`

### B-4 Subagent 配額語意
- Document A: `RT/docs/specs/subagents-v0.md`「v0 defaults」— `max_subagents_per_parent = 3`
- Document B: `RT/docs/specs/runtime-v0.md`「Budget」/ `RT/README.md` 範例 — `max_subagents=3`（per task）
- Conflict: depth=1 時相同，但 DAG 的 SUBTASK node、以及 plan revision 後重新 spawn，是 per-parent 累計還是 per-task 累計？
- Recommended source of truth: runtime-v0.md 的 Budget（per task 累計，含 DAG node）；subagents-v0 改引用

### B-5 Ablation 清單四版
- Document A: `program-charter.md`「Success criteria for v1」（7 項，混 capability 與 orchestration）
- Document B: `implementation-plan.md` D2（6 項 orchestration）
- Document C: `LAB/docs/specs/rca-v0.md`「Baselines / ablations」（6 項 capability，含 subagents）
- Document D: `LAB/docs/specs/evaluation-v0.md` C0–C8 / O0–O6
- Conflict: subagents 在兩軸；「counterfactual simulation」被當 orchestration
- Recommended source of truth: evaluation-v0.md；其餘改為連結

### B-6 Spec 狀態詞彙
- Document A: `documentation-standard.md`「Spec status」— 只允許 `proposal | accepted | deprecated`
- Document B: 實際 12 份文件使用「accepted direction / v0 contract proposal」「accepted base contracts / implemented later under Design Freeze」「accepted working policy」「v0 contract proposal」
- Conflict: freeze 出口條件「every accepted decision has an owner/spec」無法機械判定——哪些算 accepted？
- Recommended source of truth: documentation-standard.md；把「accepted direction」拆為 ADR status（accepted）+ spec status（proposal）

### B-7 ADR-001（lab）狀態 vs 決策登記
- Document A: `LAB/docs/decisions/ADR-001-simulate-before-reference-mutation.md`— Status: proposed
- Document B: `decision-register.md` D-012 — accepted direction
- Conflict: 同一決策兩種狀態
- Recommended source of truth: decision-register.md；升 ADR 為 accepted

### B-8 LangGraph adapter 的必要性
- Document A: `RT/docs/open-questions.md` OQ-6 —「Do not select infrastructure before state-size/concurrency requirements exist」
- Document B: `implementation-plan.md` B5、`RT/docs/roadmap.md` Phase 5、`ADR-002`「allowed/recommended」— adapter 是排定的交付項
- Conflict: 一邊說沒需求前不選基礎設施，一邊已排入交付
- Recommended source of truth: OQ-6；B5 改為「僅當 D1/D2 顯示需要 checkpoint/resume 才啟動」

### B-9 Consumer validator 的三個名字／兩個掛點
- Document A: `deterministic-gates-v0.md`「Consumer/domain validator contract」— 執行前，在 G3 之後
- Document B: `hybrid-orchestration-v0.md`「Verifier」—「rule/policy compliance」「exact constraint checks supplied by the consumer」— 執行後
- Document C: `tool-surface-v0.md`「Domain gate layering」—「lab experiment-policy gate」+「tep-sim capability validation」
- Conflict: consumer 提供的是一個 hook 還是兩個？若兩個，各自的簽名？
- Recommended source of truth: gates spec 定義 pre-execution `validate_request`；hybrid spec 定義 post-execution `verify_result`；tool-surface 只引用

### B-10 Duplicate experiment 偵測 owner
- Document A: `hypothesis-experiment-v0.md`「Duplicate / low-value experiment control」—「the Coordinator/lab policy SHOULD compare a proposal with the Experiment Ledger」
- Document B: `RT/README.md`— runtime 不認識 Experiment Ledger；`subagents-v0.md`「Duplicate-work control」— runtime 偵測重複 subtask goal
- Conflict: generic Coordinator 無法讀 lab ledger
- Recommended source of truth: lab 的 pre-execution consumer validator 負責；runtime 只做 subtask goal 字串去重

### B-11 SIMULATE 是否可變更 reference
- Document A: `deterministic-gates-v0.md`「Tool side-effect classes」— SIMULATE = "no reference-world side effect"
- Document B: `tool-surface-v0.md`「Simulation tools」—「MUST NOT mutate the reference branch unless the operation is explicitly a recovery application step」
- Conflict: B 的 unless 讓 SIMULATE 類工具在某條件下 MUTATE；但 recovery application 已有獨立的 `apply_validated_intervention`（MUTATE）
- Recommended source of truth: gates spec；刪除 tool-surface 的 unless 子句

### B-12 AGENTS.md 與 canonical spec 清單漂移
- Document A: `RT/AGENTS.md`「Canonical specs」— 列出已 superseded 的 ADR-001，漏列 `hybrid-orchestration-v0.md`
- Document B: `LAB/AGENTS.md`「Canonical specs」— 漏列 investigation-state / knowledge-rule-registry / hypothesis-experiment / tool-bridge / autoresearch / benchmark-design 六份；「v0 experiment order」沒有 Dynamic DAG ablation
- Conflict: coding agent 讀 AGENTS.md 會得到舊架構
- Recommended source of truth: 各 `docs/specs/README.md`；AGENTS.md 只連結

### B-13 Branch 命名
- Document A: `development-workflow.md`「Suggested initial branch sequence」— `feat/contracts-executor-v0`
- Document B: `implementation-plan.md` B1 / `RT/docs/roadmap.md` — `feat/contracts-runtime-v0`
- Recommended source of truth: implementation-plan.md（NIT）

### B-14 LangGraph 的語氣
- `RT/docs/specs/runtime-v0.md`「optional」；`ADR-002`「allowed/recommended」；`decision-register.md` D-009「may implement」；`LAB/docs/architecture.md`「may be implemented through」
- Conflict: optional vs recommended 影響 B5 是否進 critical path
- Recommended source of truth: D-009（may）；ADR-002 刪「recommended」

---

## C. Missing contracts

實作必需、目前不存在或不足以據以寫 code 的契約：

1. **`TaskStateStore`（runtime ↔ consumer state 介面）** — 見 A-2。目前 `StateDelta` 有 `operation/target_ref/field` 但 runtime 無法驗證 field 合法性。
2. **Evidence 產生路徑** — `information-plane.md` 說 EvidenceStore write authority = "tool/runtime adapters"。是每個 `ToolResult` 自動變成 `Evidence`，還是 Agent 需明確請求「attach as evidence」？兩者對 E3「evidence efficiency」「irrelevant query rate」的定義完全不同。另外 `EvidenceBundle.evidence_id`（runtime）與 `EvidenceStore.evidence_id`（lab）同名不同義。
3. **`Prediction`（typed expected outcome）** — 見 A-5。
4. **`CauseCatalog` / 答案詞彙與比對規則** — `rca-v0.md` 的 `selected_root_cause` 是什麼型別？若 IDV 標籤對 Agent 隱藏（semantic case IDs），scorer 如何把 Agent 輸出對到 hidden truth？需要 `ScenarioFamily.candidate_causes[]` 的 ID 對 Agent 可見（等於多選題，需明寫），或定義 free-text→cause 的 deterministic 映射。healthy case 也需要 `NO_ABNORMAL_CAUSE` 選項（目前 schema 沒有）。
5. **Consumer budget 維度 + 複合工具預扣** — 見 A-4。
6. **DAG node 執行語意** — 見 A-3。
7. **Macro workflow stage 定義** — `hybrid-orchestration-v0.md`「Tool exposure」依「current macro stage」；`LAB/docs/architecture.md` 有「Deterministic Macro Workflow」方塊；沒有任何地方列出 RCA 的 stage 是哪些。若 stage 不存在，刪掉該句；若存在，需 `MacroStage` enum 與 transition 規則（且這就是 O2/O3 的差異所在）。
8. **`ContextProjection` schema** — `investigation-state-v0.md`「Model-facing projection」列了內容類別，沒有 schema；`ContextBroker` 在 runtime 是 interface、在 lab 是 adapter，`visibility` 由誰強制執行（runtime 說「apply visibility policy」，lab 說「lab adapter selects」）——兩邊都可能假設對方做了。
9. **Knowledge promotion 的五個物件** — `KnowledgePromotionProposal`、`ValidationPlan`（誰設計？若由提出的 Agent 設計 scenarios/seeds，即 self-validation）、`ValidationResult`、`PromotionDecision`、`AuthorityLevel`。目前只有 `ValidationCampaign` 一個結構，且「semantic/unit/scope review」的執行者未定義。
10. **Lab policy rule 契約** — `recovery-v0.md`「v0 policy constraints」（allowed_actuators、max_delta、cooldown）說「Do not encode these limits only in prompts」，但沒有說 encode 在哪個型別；它們不是 K0–K4 任何一級。
11. **`RecoveryStrategy` 表示法** — `autoresearch-v0.md`「Mutable surface: selected recovery strategy structure; approved actuator targets/sequence」。「strategy structure」若是 code/DSL，需要 DSL 契約；若是參數向量，需要 schema。這決定 AutoResearch 的整個 change_set 型別。
12. **Engineering records** — 計畫意圖列「record engineering knowledge」，v1 成功條件含「report saved」，但 `InvestigationReport`、`RecoveryRecord`、`LessonLearned`、`RunbookCandidate` 一個都沒有。v0 至少需要 `InvestigationReport`（= 最終 state revision + evidence refs + 結論 + 未解問題）的 schema，否則「report」會變成 LLM 自由文本。同時需明寫：records 是 write-only archive，不進入未來 prompt（與 D-016 一致）。
13. **Experiment identity / dedup key** — `ExperimentRunSpec` 含 `branch/snapshot_ref` 與 `seeds`；每次 fork 產生新 snapshot id，所以「identical run spec」幾乎永不成立。需定義 canonical key = hash(parent_snapshot_content_checksum, resolved_interventions, horizon, seed_policy, scorer_version)。
14. **C0 deterministic baseline 定義** — 見 A-6。
15. **`InformationRef` owner** — 定義在 program-level `information-plane.md`；runtime roadmap Phase 4 說「generic InformationRef/ContextBroker interfaces」。依 `documentation-standard.md`「Public contracts must be owned by exactly one repository」，它需要一個 owner（建議 runtime）。
16. **Approval state machine**（OQ-7）— 可留 open，但 `apply_validated_intervention(validation_token)` 的 token 綁定 reference state revision 目前在 gates spec 是 MAY；只要 MUTATE 啟用就應為 MUST。

---

## D. Over-engineering candidates

| component | why it may be premature | simpler alternative | evidence that would justify adding it later |
|---|---|---|---|
| LangGraph adapter (B5) | 沒有任何 D1–D4 實驗需要 checkpoint/resume/interrupt；OQ-6 自己承認需求未知；ADR-002 列出「additional integration layer」為成本；reference executor 本來就是 baseline | 完全刪出 v0 路線；runtime 只保證「state 可序列化」 | D1 跑出 run 長度 > 單一 process 可容忍、或需要 human interrupt 的具體案例 |
| Dynamic DAG（作為獨立元件） | A-3 所列語意缺口；「DAG vs N 個 subtasks」差異未論證；D-015 已要求先量 baseline | `Subtask[]` + `depends_on` 的 batch 請求（Coordinator 拓樸排序、平行執行 ready 者）；MERGE = 下一個 Main Agent turn。這已足以支撐 O4 ablation | O3 vs O4 ablation 顯示 DAG 有正向效果且 replan 是效果來源 |
| 五個 store（Evidence / Ledger / Artifact / Trace / State） | 每個都要 owner、versioning、ref 解析；v0 只有一個 consumer | 一個 append-only run log（JSONL）+ 多個 typed view；EvidenceStore、ExperimentLedger 是 view 不是 store；ArtifactStore 只是檔案系統 + checksum | 多 domain lab 或跨 run 查詢需求出現（information-plane.md 自己的 revisit 條件） |
| Generic `ContextBroker` interface | runtime 不知道什麼相關，實際工作全在 lab adapter；generic 層只剩「量 token、檢查 visibility」 | lab 的一個純函數 `project(state, refs, policy) -> ContextProjection`；runtime 對結果做 size/visibility assert | 第二個 domain lab 出現且 projection 邏輯可共用 |
| K3→K2 promotion pipeline | Phase F 才用；v0 沒有 K3 rule 來源（KG 未接） | v0 Rule = YAML 檔 + 三欄 metadata（origin/validation/authority）；promotion workflow 留 spec 不實作 | Phase F 接 manufacturing-kg-agent 後有第一批 K3 候選 |
| `InvestigationState.mode` 四合一 | RCA / HAZOP / RECOVERY / AUTORESEARCH 的 state 內容差異大（AutoResearch 有 best_candidate、backlog；HAZOP 有 node/param/guide word）；共用 schema 會產生大量 optional 欄位 | v0 只做 `RcaState`；其他 mode 各自 spec 時再定義 | Phase 7–9 實作時看是否真有共通欄位 |
| MCP | 文件完全未提（grep 零命中）——這是正確的 | 明寫一句：v0 tools 是 in-process typed Python callables；MCP 只可能作為未來的 optional tool provider，永不成為 core dependency | 需要接外部服務且該服務只有 MCP 介面 |
| Coordinator / Executor 二分 | Executor 職責 = 「用 timeout 呼叫 adapter、綁 request/result id」——一個函數 | 保留為 module 命名，不當「架構元件」寫 spec；Coordinator = loop，Executor = dispatch fn，Verifier = post-check fn | 無需——這不是研究問題，只是不要為它寫三份 spec |
| AutoResearch | 已正確放在 Phase E 且獨立 mode——保留現狀，不算 over-engineering | — | — |
| Ephemeral subagents | 契約小、O5 ablation 需要——保留 | — | — |

---

## E. Research questions masquerading as architecture decisions

1. **D-007「Hybrid orchestration accepted」** — 「O3 優於 O1」是 D2 要量的問題；register 有 revisit trigger，但 status 寫 accepted 會讓 coding agent 把 Hybrid 當前提硬編（例如 tool exposure by stage 只在 Hybrid 存在 → confound）。建議：契約 accepted，優越性 proposal。
2. **D-006「One Main Agent by default」** — 固定角色 vs 單 agent 也是可 ablation 的（README 的 not-to-build 清單直接排除了 Supervisor/MachineExpert 組織）。作為範圍決策可以，但不要宣稱它是研究結論。
3. **Dynamic DAG 的價值** — 正確地列為 O4 ablation，但 `program-charter.md`「Agent abilities under study」把「Dynamic DAG planning/replanning」列為被研究的能力，這預設 DAG 存在。
4. **Simulate-before-apply 是否值得** — recovery baselines 3 vs 4 會量到；ADR 寫成 policy 是對的，但要在報告裡當結果呈現。
5. **Semantic stop 閾值、K2 promotion 閾值、subagent 上限** — 正確地留在 open questions。
6. **LLM critic 是否有用**（RT OQ-8）— 正確地 open。
7. **Tool Bridge 分析工具的價值**（C4）— 正確地 ablation。
8. **「Coordinator/Executor/Verifier 應為 deterministic」（D-008）** — 這不是研究問題，是安全原則；保留為 accepted，且是本設計最好的部分之一。

---

## F. Architecture decisions that are still accidentally open

| 決策 | 看似定案於 | 實際 open 於 |
|---|---|---|
| Verifier 前/後 | README、architecture.md | hybrid-orchestration-v0 macro flow |
| K1 owner | charter | rule registry spec「depends on scope」 |
| Macro workflow 住在哪（lab LangGraph graph vs runtime Coordinator loop） | LAB/architecture.md 畫「Deterministic Macro Workflow」 | runtime 說 Coordinator 擁有 routing；兩層 macro？ |
| Rollout 是否算 tool call | rca-v0「application-specific」 | G2 只認 generic budget |
| InvestigationState 是 generic `TaskState` 的特化還是 lab 專屬 | information-plane「coordinated through」 | runtime 無對應型別 |
| Hidden IDV 標籤是否對 Agent 可見 | benchmark-design「optionally semantic IDs」 | rca-v0 first case 直接寫 XMEAS(9)/(21)/XMV(10) |
| 子 agent 可否拿 PROPOSE 類工具 | subagents-v0 open question | 依 gates spec 的 class 定義，PROPOSE ≠ MUTATE，本來就允許——此 OQ 其實已被 class 模型回答，應關閉 |
| SIMULATE 是否可碰 reference | gates spec（否） | tool-surface「unless」 |
| LangGraph optional / recommended / may | runtime-v0 / ADR-002 / D-009 | 三種語氣 |
| Spec status 語意 | documentation-standard | 12 份文件用非標準詞 |

---

## G. Safety / authority findings

「model proposes, system authorizes」在主路徑上是成立的，且 `GateDecision`「A model-authored rationale is not a gate decision」寫得很好。以下是旁路：

1. **MAJOR — 複合 Tool Bridge 工具的預算旁路**（A-4）：一個 COMPUTE 級請求觸發 N 次 rollout，不經 SIMULATE gate、不扣 rollout budget。
2. **MAJOR — `RT/docs/architecture.md`「Tool permissions」**：「Authority can only narrow through delegation unless host policy explicitly grants otherwise」。這句 unless 是一個 escalation 後門；`deterministic-gates-v0.md` invariant「Child authority never exceeds explicitly delegated parent/task authority」沒有這個例外。刪除 unless，或要求任何例外必須是 ADR。
3. **MAJOR — DAG SUBTASK node 的 depth/count 計算**：`subagents-v0.md` `child_can_spawn_subagents=false`，但 subtask 內若 Main Agent 邏輯提出含 SUBTASK node 的 plan，是否等於 depth 2？未定義。明寫：plan 內 SUBTASK node 計入提出者的 subagent 配額，且 child 不得提出含 SUBTASK 的 plan。
4. **MINOR — SIMULATE「unless recovery application step」**（B-11）。
5. **MINOR — AutoResearch 未明寫 MUTATE 停用**：`autoresearch-v0.md`「Explicit non-goals」列了不能改 physics/evaluator，但沒說 `apply_validated_intervention` 在 AUTORESEARCH mode 必須不在 allowlist。加一句。
6. **MAJOR — Knowledge promotion 的 self-validation**：`knowledge-rule-registry-v0.md`「Validation campaign」沒有說 `ValidationCampaign.scenarios[]/seeds[]` 由誰選。若由提出 K3/K4 的同一 Agent 選，它可以挑對自己有利的 operating points。建議：campaign 的 scenario/seed 由 deterministic generator 依 `ScenarioFamily` 抽樣，提出者只能指定 `expected_relation` 與 `operating_envelope`；並要求 held-out envelope 驗證。這比人工審查更能解決「owner 不是化工 SME」的問題——人只審 provenance 與流程合規，不審化工正確性。
7. **OK — 生成的 runbook/recommendation**：目前只是 free text 欄位（`hazop-v0.md` `recommendations[]`、`recovery-v0.md` proposal），沒有任何工具讀它們——安全，但需在 engineering records 契約（C-12）出現時保持「record 不自動變 tool input」。
8. **MINOR — validation token 綁 revision 為 MAY**（C-16）：MUTATE 啟用時應為 MUST。
9. **MINOR — visibility 執行者未指定**（C-8）：runtime 與 lab 都可能以為對方擋了 EVALUATOR ref。

---

## H. Evaluation threats

1. **候選集洩漏（最嚴重）** — 見 A-6。binding registry 把「trigger node → 3 個 IDV」直接交給 Agent；C0 若未定義成枚舉比對，ablation 全部失去解釋力。
2. **記憶效應** — 「reactor temperature rising」→ IDV(4) 是每篇 TEP 論文的第一個例子。`benchmark-design-v0.md` 的緩解措施合理，但「semantic case IDs」是 optional、且 `rca-v0.md` 明寫 XMEAS(9)/(21)/XMV(10)。至少要有一個 HARD case 的 cause 不在 reactor node 的 binding 內。
3. **可 gaming 的 E3 指標**：
   - `hypotheses eliminated per experiment` — 多提垃圾 hypothesis 再淘汰即可灌分；需以「evaluator 標記為 plausible 的 hypothesis」為分母。
   - `open-question resolution rate` — 製造瑣碎問題再關閉；同上。
   - `experiments linked to explicit hypothesis` — 永遠掛一個 ref 即可；需配合 typed Prediction 才有意義。
   - `relevant evidence query rate` — 「relevant」需要 per-case 標註（scoring_config），目前未定義由誰標。
4. **Confound：tool exposure policy 隨 orchestration mode 變**（A-8）。
5. **Confound：subagents 在兩軸**（A-8）。
6. **Circular scoring 風險** — `compare_trajectories` 的 similarity metric 同時是 Agent 的工具與 identifiability pilot 的可分性判準；若 scorer 也用同一 metric，則「Agent 是否正確」= 「Agent 是否呼叫了 scorer」。需明寫 scorer 的 metric 版本獨立於 Agent 可用工具，或至少在報告中揭露。
7. **Partition 污染** — AutoResearch「Experimental design research」mode 在 RESEARCH partition 上最佳化 experiment policy；orchestration ablation 也在 RESEARCH 上報告。HIDDEN_EVAL 每次「final check」都消耗一次；沒有說 hidden set 是否 per-campaign 換版。
8. **弱 baseline** — O0 static one-shot 用 compact context 是稻草人；`recovery-v0.md` baseline 2「deterministic recovery policy」需要 SME 設計，owner 沒有 SME——這是 recovery benchmark 的實際風險，需在 open-questions 承認。
9. **LLM 隨機性** — provider 不保證可重現；`benchmark-design-v0.md` 已要求 repeats，但 evaluation 沒定義最小 repeat 數與 paired test；「Early MVP reports may be descriptive」給了逃生口。
10. **Calibration** — `rca-v0.md` 要求 confidence calibration，但 `Hypothesis.current_score_or_rank?` 沒有機率語意；若 Agent 輸出 rank，calibration 無法計算。

---

## I. Design Freeze checklist

### Must resolve before implementation（runtime / lab）
- [ ] A-1 Verifier 定位為 post-execution；修兩張圖；合併 consumer hook 為 `validate_request`（pre）+ `verify_result`（post）
- [ ] A-2 新增 `TaskStateStore` generic 契約；lab 實作
- [ ] A-3 Dynamic DAG：選 (A) 補語意 或 (B) 降為 `Subtask[]+depends_on`
- [ ] A-4 `Budget.extra_dimensions` + `ToolSpec.declared_budget_draw`；複合工具 class = SIMULATE
- [ ] A-5 `Prediction` 契約；`expected_outcomes` 改型別
- [ ] C-4 `CauseCatalog` + 比對規則 + `NO_ABNORMAL_CAUSE`
- [ ] C-2 Evidence 產生路徑（自動 vs 請求）；`EvidenceBundle` 改名（例如 `SubtaskResult`）
- [ ] A-9 `MODEL_TURN` trace 附全文 projection ref + template version
- [ ] G-2 刪除「unless host policy explicitly grants otherwise」
- [ ] B-11 刪除 SIMULATE 的 unless 子句
- [ ] G-3 DAG SUBTASK node 配額規則
- [ ] B-6 統一 spec status 詞彙；B-12 修兩份 AGENTS.md
- [ ] A-6 定義 C0 = enumerate-and-match，並加入 identifiability pilot 判準

### Can resolve during first pilot（D1 之前或之中）
- [ ] A-7 Rule 三欄拆分（v0 只有幾條 rule，改 schema 成本低，但 C2 開工前要定）
- [ ] C-7 Macro stage：定義或刪除「by current macro stage」
- [ ] C-8 `ContextProjection` schema + visibility 執行者
- [ ] C-13 experiment dedup key
- [ ] A-8 ablation 清單統一到 evaluation-v0；O2/O3 差異定義；tool exposure 固定
- [ ] H-3 E3 指標分母改為 evaluator-plausible 集合
- [ ] C-12 `InvestigationReport` 最小 schema
- [ ] A-10 明寫 v0 stopping = Agent 提議 + 結構檢查
- [ ] C-16 validation token 綁 revision 改 MUST（MUTATE 啟用時）

### Can defer until later research
- [ ] C-9 promotion 五物件（Phase F）
- [ ] C-11 `RecoveryStrategy` DSL（Phase E）
- [ ] LangGraph adapter（等需求）
- [ ] information-gain 型 stopping（OPEN_RESEARCH）
- [ ] HAZOP worksheet 結構深度（LAB OQ-11）
- [ ] 跨 run 記憶（D-016）
- [ ] MCP provider

---

## J. Simplified architecture proposal

只改動能提升 testability / attribution / safety / implementation cost 的地方；`tep-sim` 不動。

```text
┌─────────────────────────────────────────────────────────────────────┐
│ industrial-agent-runtime  v0                                          │
│                                                                       │
│   Task / Budget(+extra_dimensions) / ToolSpec(+budget_draw)           │
│   TraceEvent(+projection_ref)                                         │
│                                                                       │
│   loop:  project ──► model_turn ──► route                             │
│             ▲                        │                                │
│             │            ┌───────────┼───────────┐                    │
│             │            ▼           ▼           ▼                    │
│             │        ToolCall   SubtaskBatch   Finish                 │
│             │            │      [Subtask + depends_on]   │            │
│             │            ▼           ▼                   │            │
│             │      gates G0–G3 + consumer.validate_request           │
│             │            │           │                   │            │
│             │            ▼           ▼                   │            │
│             │        dispatch    topo-sort + parallel    │            │
│             │            │           │                   │            │
│             │            ▼           ▼                   ▼            │
│             │      consumer.verify_result  (post-exec, deterministic) │
│             │            │                                            │
│             └── TaskStateStore.apply(delta) ◄─────────────────────────┘
│                                                                       │
│   ✂ 刪除：ANALYSIS/MERGE node、generic ContextBroker、LangGraph B5    │
└─────────────────────────────────────────────────────────────────────┘
                              │ implements TaskStateStore / registers tools
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ tep-agent-lab  v0                                                     │
│                                                                       │
│   RcaState (只做 RCA)                                                 │
│   RunLog  ── 一個 append-only JSONL ──┬─ view: Evidence               │
│                                       ├─ view: ExperimentLedger       │
│                                       └─ view: StateDeltas            │
│   Hypothesis + Prediction[]  (typed)                                  │
│   CauseCatalog  (scorer 與 Agent 共用的答案詞彙)                        │
│   Rule = YAML {origin, validation, authority}   (幾條即可)             │
│   project(state, policy) -> ContextProjection   (純函數)               │
│   tools: env tools + 2–3 個 bridge (corr/lag, compare_trajectories)    │
│   C0 baseline: enumerate bound IDVs → fork → match                    │
│                                                                       │
│   ✂ 延後：HAZOP/Recovery/AutoResearch 實作、promotion pipeline、       │
│           五個 store、mode 四合一 state                                │
└─────────────────────────────────────────────────────────────────────┘
```

這個簡化保留了什麼：所有安全不變量、gates 管線、fake provider、subagents（O5 需要）、平行 batch（O4 需要）、Hypothesis/Experiment 分離、hidden partition、append-only ledger、識別性 pilot。刪掉的只有：三個未定義語意的 node type、一個沒有需求的 framework adapter、四個可以是 view 的 store、以及一個 generic 層裡實際上沒有 generic 工作的 broker。

明確應維持不變的好設計：`tep-sim` 的全部邊界與 capability honesty（`safety-capability-v0.md`「Supported vs unsupported statements」是全案最清楚的一段）；G0–G3 + `GateDecision`；`ExperimentResult` vs `ExperimentInterpretation` 分離；「不以 fault-name recall 計分」；identifiability pilot 先於 benchmark freeze；AutoResearch 獨立 mode 且排在 recovery 之後；D-015「先量 baseline 再量 DAG/subagent」；development-agent-orchestration 的 `SPEC_CONFLICT` 流程。

---

## 獨立建議：coding agents 可否開工？

| 範圍 | 建議 | 理由 |
|---|---|---|
| `tep-sim` A1–A4（`feat/environment-api-v0` → `feat/snapshot-fork-v0` → `feat/dexpi-binding-v0` → `feat/capability-safety-v0`） | 立即放行 | 四份 spec 有 scope / 契約 / 錯誤行為 / 不變量 / acceptance tests，完全不依賴本報告任何 blocker；且 OQ-1 snapshot fidelity 是唯一能靠寫 code 才回答的問題，越早越好 |
| runtime B1（contracts） | 修完 A-1、A-4 後放行（估計是幾小時的 spec 編輯） | 這兩項直接改 `Budget` / `ToolSpec` / `TraceEvent` 的欄位 |
| runtime B2–B4、lab C1–C5 | 暫停，直到 Must-resolve 清單完成 | 否則 B2 的 Verifier、C1 的 state 寫入路徑會被實作者各自發明，之後對不起來 |
| D1 以後 | 依 implementation-plan 順序 | 無額外意見 |
