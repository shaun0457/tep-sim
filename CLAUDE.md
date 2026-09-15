# tep-sim

Tennessee Eastman Process 動態模擬 + LLM agent 即時控制。

## 定案

- 模擬器：`vendor/tep-sim-upstream`（jkitchin/tennessee-eastman-profbraatz，git submodule）。
  不重寫模型、不換 Rust；瓶頸在 LLM 決策延遲，不在積分器（純 Python 已 ~1000 steps/s）。
- 安裝：**不要 `pip install -e vendor/...`**——meson-python 在 Windows 即使 `-Dfortran=disabled`
  也要 C compiler。改用 `.venv` + 把 `vendor/tep-sim-upstream/src` 寫進 site-packages 的
  `tep_upstream.pth`。依賴只有 numpy。
- Agent 控制：必須用 `ControlMode.MANUAL` 或自訂 `BaseController` plugin。
  `CLOSED_LOOP` 下 `set_mv()` 會在下一個 `step()` 被內建 PI 控制器覆寫。
- `data/raw/`（3.2 GB Rieth 資料集）不進 git；本機路徑見 .gitignore 註解。
- `docs/papers/` 是出版社論文 → repo 保持 private。
- Blender / DEXPI 視覺化是展示層，在模擬器 + agent 迴圈跑通之後才做。
  公開的 TEP DEXPI 檔不存在，要自己用 pyDEXPI（AGPL）建。

## 驗證

```
.venv/Scripts/activate && python -c "from tep import TEPSimulator; s=TEPSimulator(); s.initialize(); print(s.step())"
```
