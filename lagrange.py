"""拉格朗日插值：接收采样点，按拉格朗日插值法生成曲线。

基函数法：L(x) = Σ y_i · l_i(x)，其中
l_i(x) = Π_{j≠i} (x - x_j) / (x_i - x_j)

样例：过 (0,0),(1,1),(2,4) 的插值多项式是 x²，
在 x=1.5 处应得 2.25。
"""

import re

import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

import original_function
from nodes import Nodes


def lagrange_eval(xs: list[float], ys: list[float], x: float) -> float:
    """在 x 处计算拉格朗日插值多项式的值。

    >>> lagrange_eval([0.0, 1.0, 2.0], [0.0, 1.0, 4.0], 1.5)
    2.25
    >>> lagrange_eval([0.0, 1.0, 2.0], [0.0, 1.0, 4.0], 1.0)  # 节点上必过
    1.0
    """
    total: float = 0.0
    n: int = len(xs)
    i: int
    for i in range(n):
        li: float = 1.0  # 基函数 l_i(x)
        j: int
        for j in range(n):
            if j != i:
                li *= (x - xs[j]) / (xs[i] - xs[j])
        total += ys[i] * li
    return total


def poly_coefficients(xs: list[float], ys: list[float]) -> np.ndarray:
    """把拉格朗日形式展开成标准多项式系数 [a0, a1, ..., an]（升幂）。

    >>> [float(a) for a in poly_coefficients([0.0, 1.0, 2.0], [0.0, 1.0, 4.0])]
    [0.0, 0.0, 1.0]
    """
    coeff: np.ndarray = np.zeros(len(xs))
    n: int = len(xs)
    i: int
    for i in range(n):
        c: np.ndarray = np.array([1.0])  # 基函数分子 Π(x - x_j)，polymul 返回最高次在前
        denom: float = 1.0
        j: int
        for j in range(n):
            if j != i:
                c = np.polymul(c, [1.0, -xs[j]])
                denom *= (xs[i] - xs[j])
        coeff += ys[i] * c[::-1] / denom  # 反转成升幂再累加
    return coeff


def format_polynomial(coeff: np.ndarray) -> str:
    """系数转数学排版字符串（升幂系数，按降幂输出）。

    >>> format_polynomial(np.array([0.5, -1.0, 2.0]))
    '2x^{2} - x + 0.5'
    """
    parts: list[str] = []
    k: int
    for k in range(len(coeff) - 1, -1, -1):
        a: float = coeff[k]
        if abs(a) < 1e-12:
            continue
        sign: str = "-" if a < 0 else "+"
        mag: float = abs(a)
        num: str = f"{mag:.4g}" if (abs(mag - 1.0) > 1e-12 or k == 0) else ""
        var: str = {0: "", 1: "x"}.get(k, f"x^{{{k}}}")
        parts.append(f"{sign} {num}{var}")
    if not parts:
        return "0"
    expr: str = parts[0][2:] if parts[0].startswith("+ ") else parts[0]
    return expr + "".join(" " + p for p in parts[1:])


def wrap_expression(expr: str, per_line: int = 3) -> list[str]:
    """把多项式表达式按每行 per_line 项拆成多行。

    >>> wrap_expression("a + b - c + d", per_line=2)
    ['a + b', '- c + d']
    """
    tokens: list[str] = re.split(r"( [+-] )", expr)
    terms: list[str] = [tokens[0]]
    k: int
    for k in range(1, len(tokens) - 1, 2):
        terms.append((tokens[k] + tokens[k + 1]).strip())
    return [" ".join(terms[i:i + per_line])
            for i in range(0, len(terms), per_line)]


class LagrangeCurve:
    """拉格朗日插值曲线的绘制对象：点变化后重新 draw 即可。

    只负责画线；图例由 legend_box.LegendBox 统一管理。

    样例：
        curve = LagrangeCurve()
        short_label, full_label = curve.draw(ax, nodes)
    """

    def __init__(self) -> None:
        self._artist: Line2D | None = None

    def draw(self, ax: Axes, nodes: Nodes,
             samples: int = 600) -> tuple[str, str | None]:
        """画插值曲线，返回 (短标签, 完整表达式) 供图例使用。

        :param ax: 画板
        :param nodes: 采样点集合
        :param samples: 曲线采样密度
        :return: (短标签, 完整表达式)；点数 < 2 时完整表达式为 None
        """
        if self._artist is not None:
            self._artist.remove()
            self._artist = None
        xs: list[float]
        ys: list[float]
        xs, ys = nodes.deduplicated()
        if len(xs) < 2:
            return ("拉格朗日插值", None)

        x_min: float = original_function.X_MIN
        x_max: float = original_function.X_MAX
        grid: list[float] = [x_min + (x_max - x_min) * i / samples
                             for i in range(samples + 1)]

        n: int = len(xs) - 1
        short_label: str = f"拉格朗日插值 (n={n})"
        self._artist, = ax.plot(
            grid,
            [lagrange_eval(xs, ys, x) for x in grid],
            color="tab:red", lw=1.6,
            label=short_label,
            zorder=4,
        )

        expr_lines: list[str] = wrap_expression(
            format_polynomial(poly_coefficients(xs, ys)))
        body: str = "\n".join(
            [f"$P(x)={expr_lines[0]}$"] + [f"${line}$" for line in expr_lines[1:]]
        )
        return (short_label, body)
