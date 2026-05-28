# PackVision 分阶段开发执行与自动化

> 日期：2026-05-28  
> 当前主开发分支：`codex/astra-pro-depth-camera`  
> 自动化任务：`packvision`，已设置为继续在本会话中按阶段推进。

## 1. 开发总原则

PackVision 后续按“可交付小步”推进，不追求一次性把所有想法塞完。

每一步必须满足：

- 有明确目标。
- 有 API、UI、脚本或文档中的至少一个可验证增量。
- 有测试或人工验证命令。
- 文档同步更新。
- 可以提交到 GitHub。

如果某个方向存在明显取舍，例如模型太大、UI 两种方案难选、多相机外参方案不确定，就新建 `codex/` 前缀分支探索，不直接污染主开发分支。

## 2. 自动化任务怎么运行

我已经把 Codex 自动化 `packvision` 改成分阶段落地模式，并重新启用。

它每次醒来要做的事：

1. 检查 `git status`。
2. 阅读当前路线图和最近文档。
3. 选择一个小而完整的阶段任务。
4. 修改代码/文档/脚本。
5. 运行测试。
6. 必要时打包 EXE 和海外仓交付包。
7. 提交并推送 GitHub。
8. 如果遇到路线分歧，创建 `codex/` 前缀分支并记录取舍。

## 3. 本地开发循环脚本

新增脚本：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\dev_cycle.ps1
```

默认执行：

- `git status --short --branch`
- `pytest -q`
- `scripts\check_astra_depth_status.ps1`
- 再次输出 git 状态

如果本轮需要重新打包：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\dev_cycle.ps1 -BuildPackage
```

会额外执行：

- `scripts\build_exe.ps1`
- `scripts\build_handoff_package.ps1`

交付包仍然受 `100 MB` 限制，超过会失败。

## 4. 阶段执行队列

### A. 开箱即用与相机到货验收

状态：已完成第一版，还要继续打磨。

已完成：

- `/api/deployment/readiness`
- `scripts\check_astra_depth_status.ps1`
- `scripts\build_handoff_package.ps1`
- 海外仓开箱即用交付文档
- 最新交付包位于 `D:\Documents\包装尺寸检测\release\PackVision_Field_Kit_*.zip`，当前包大小约 `73.55 MB`

下一步：

- 让 readiness 输出更适合现场人员阅读。
- 增加日志打包和远程排错包。
- 相机到货后补真实硬件验证结果。

验收：

- `pytest -q`
- `scripts\dev_cycle.ps1`
- `scripts\dev_cycle.ps1 -BuildPackage`
- 现场包启动 EXE 后 `/api/deployment/readiness` 返回正常。

### B. 工业现场 UI 自动化

目标：仓库员工不需要选择复杂模式。

要做：

- 首页默认流程变成：扫码/单号 -> 放件 -> 自动测量 -> 结果 -> 复核。
- 包装类型、材质风险、采集模式默认自动判断。
- 高级参数折叠给工程师。
- 结果统一显示：`可入库`、`需复核`、`重拍/失败`。

建议分支：

```text
codex/packvision-ui-auto-workstation
```

验收：

- 桌面和移动截图无重叠。
- 仓库员工不需要理解 ROI、内参、焦距、材质参数。
- `tests/test_static_ui.py` 通过。

### C. 真值模板与复核样本池

目标：把失败和人工修正样本变成后续训练资产。

要做：

- 增加复核样本状态：失败、低置信、人工改框、异常材质、深度质量差。
- 历史记录支持按复核状态筛选。
- WPS/Excel CSV 模板增加人工真值字段和复核结论。
- 支持导出误差报告和复核样本清单。

建议分支：

```text
codex/packvision-review-sample-pool
```

验收：

- 测量失败或低置信后，能进入复核池。
- CSV 能被 WPS/Excel 打开。
- 每条复核样本能追溯单号、原图、标注图和接口日志。

### D. AI 插件接口

目标：先搭插件架构，不把大模型塞进基础包。

要做：

- 设计 `models/` 插件目录约定。
- 定义模型元数据：名称、版本、输入尺寸、推理后端、是否 CPU 可用。
- API 返回当前安装的模型插件和启用状态。
- YOLO/分割/Depth Anything 都作为可选插件。

建议分支：

```text
codex/packvision-ai-plugin-spike
```

验收：

- 不安装模型时基础 EXE 正常运行。
- 模型插件缺失时 UI 给出明确提示。
- 模型插件不会让基础交付包超过 100 MB。

### E. 多相机三视图与外参

目标：支持未来两台、三台深度相机。

要做：

- 固定相机角色：`top`、`front`、`side`。
- 支持序列号绑定。
- 定义外参验证流程。
- 多视角结果冲突时自动进入复核。
- 保守融合，不短报尺寸。

建议分支：

```text
codex/packvision-multiview-extrinsics
```

验收：

- 没有三台相机时，单相机模式不受影响。
- 多视图结果差异超过阈值时标记复核。
- 新相机只新增 backend/provider，不改业务主流程。

## 5. 分支规则

| 情况 | 分支策略 |
| --- | --- |
| 小修小补、文档、测试、明确 bugfix | 直接在 `codex/astra-pro-depth-camera` 做 |
| UI 方向存在两种明显方案 | 新建 `codex/packvision-ui-auto-workstation` |
| AI 模型或依赖可能变重 | 新建 `codex/packvision-ai-plugin-spike` |
| 多相机外参/支架方案不确定 | 新建 `codex/packvision-multiview-extrinsics` |
| 需要真实相机验证但硬件未到 | 先写模拟/接口/文档，真实结果到货后补 |

分支开好后必须：

- 推送到 GitHub。
- 在本文件记录目的和取舍。
- 不把实验性重依赖合入基础包，除非验证通过。

## 6. 每轮完成标准

每轮我都按这个标准收尾：

1. `git status` 清楚。
2. 测试通过。
3. 文档同步。
4. 如果影响交付包，重新打包并确认小于 `100 MB`。
5. commit message 说明这一步做了什么。
6. push 到 GitHub。

## 7. 当前下一步

按照优先级，下一批应该从 **工业现场 UI 自动化** 和 **真值/复核样本池** 二选一。

我的判断：

1. 先做 UI 自动化，因为这直接影响仓库员工能不能用。
2. 然后做复核样本池，因为它决定后续能不能持续变准。
3. AI 插件和多相机外参先保持架构预留，等真实样本和相机验证后再做重投入。
