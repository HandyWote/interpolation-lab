# 消融实验报告

基线：重构前工作区（438 行 / 7 文件）。
判定标准：删除或合并后，数值回归、doctest、渲染回归三者必须全部通过且结果与基线一致。

## 一、删除/合并项

| # | 对象 | 动作 | 理由 | 验证结果 |
|---|---|---|---|---|
| 1 | `newton.py::newton_expression` 及辅助函数 `_ys_of`（约 25 行） | 删除 | 牛顿形式与拉格朗日形式是同一个多项式（唯一性定理），展开为标准式时复用 `lagrange.poly_coefficients(xs, ys)` 即可，无需第二套展开累加逻辑 | 展开表达式与基线逐字符一致（悬浮窗中 P(x) 与 N(x) 相同）；doctest 通过 |
| 2 | `newton.py` 的 `import numpy as np` | 删除 | 删除项 1 落地后，newton.py 内无 numpy 使用点（`divided_diffs`/`newton_eval` 为纯 Python） | 模块导入与全部测试通过 |
| 3 | `lagrange.py::draw` 与 `newton.py::draw` 中重复的去重段（两处各 8 行） | 合并为 `nodes.py::Nodes.deduplicated()` | 去重是节点状态自身的职责（随机采样可能重复），不应在两个插值文件各抄一份 | doctest 覆盖去重语义（重复 x 保留后者 y、升序输出） |

## 二、审查后保留项（确认非冗余）

| 对象 | 结论 |
|---|---|
| `legend_box.py` 全部方法 | 每个方法均有调用方（update/redraw/motion 链路完整） |
| `main.py::redraw` 内联条目拼装 | 编排逻辑本体，非冗余 |
| `lagrange.py::poly_coefficients` | 删除项 1 后成为两法共用的展开实现，是收敛点而非冗余 |

## 三、死代码扫描

对全部公开符号做引用检查（grep + doctest 运行时验证）：未发现无引用符号。

## 四、行数变化（基线 → 现状）

| 文件 | 基线 | 现状 | 变化 | 说明 |
|---|---|---|---|---|
| main.py | 58 | 60 | +2 | 类型标注 + 命名改善 |
| axes.py | 44 | 61 | +17 | docstring + 标注 |
| original_function.py | 20 | 48 | +28 | docstring/doctest + 标注 |
| nodes.py | 29 | 62 | +33 | 新增 deduplicated（净增 1 个职责）+ 标注 |
| lagrange.py | 107 | 151 | +44 | docstring/doctest + 标注（无逻辑变化） |
| newton.py | 84 | 109 | +25 | **删 25 行展开逻辑**，+50 行文档/标注 |
| legend_box.py | 96 | 124 | +28 | 标注 + docstring |
| **合计** | **438** | **615** | **+177** | 全部增量来自文档与标注；逻辑代码净减少约 33 行 |

结论：消融在"只减逻辑、只增文档"的方向上达成；三处删除/合并均有回归验证背书。

## 五、回归记录

- doctest：5 个模块全部通过（`python -m doctest <各模块>`）
- 数值：过点误差 ≤1e-12；两法一致 ≤1e-9；加点旧系数逐位不变；差商表与手算对照一致
- 渲染：3 次随机加点 + hover 悬浮窗，hover 态图例位移 0.0px
