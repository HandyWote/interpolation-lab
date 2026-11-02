"""拉格朗日插值：接收采样点，按拉格朗日插值法生成曲线。

基函数法：L(x) = Σ y_i · l_i(x)，其中
l_i(x) = Π_{j≠i} (x - x_j) / (x_i - x_j)
"""

import re

import numpy as np

import original_function


def lagrange_eval(xs: list[float], ys: list[float], x: float) -> float:
    """在 x 处计算拉格朗日插值多项式的值。"""
    total = 0.0
    n = len(xs)
    for i in range(n):
        li = 1.0
        for j in range(n):
            if j != i:
                li *= (x - xs[j]) / (xs[i] - xs[j])
        total += ys[i] * li
    return total


def poly_coefficients(xs: list[float], ys: list[float]) -> np.ndarray:
    """把拉格朗日形式展开成标准多项式系数 [a0, a1, ..., an]（升幂）。"""
    coeff = np.zeros(len(xs))
    n = len(xs)
    for i in range(n):
        c = np.array([1.0])            # 基函数分子 Π(x - x_j)，polymul 返回最高次在前
        denom = 1.0
        for j in range(n):
            if j != i:
                c = np.polymul(c, [1.0, -xs[j]])
                denom *= (xs[i] - xs[j])
        coeff += ys[i] * c[::-1] / denom  # 反转成升幂再累加
    return coeff


def format_polynomial(coeff: np.ndarray) -> str:
    """系数转数学排版字符串，如 0.031x^{2} - 1.2x + 0.5。"""
    parts = []
    for k in range(len(coeff) - 1, -1, -1):
        a = coeff[k]
        if abs(a) < 1e-12:
            continue
        sign = "-" if a < 0 else "+"
        mag = abs(a)
        num = f"{mag:.4g}" if (abs(mag - 1.0) > 1e-12 or k == 0) else ""
        var = {0: "", 1: "x"}.get(k, f"x^{{{k}}}")
        parts.append(f"{sign} {num}{var}")
    if not parts:
        return "0"
    expr = parts[0][2:] if parts[0].startswith("+ ") else parts[0]
    return expr + "".join(" " + p for p in parts[1:])


def wrap_expression(expr: str, per_line: int = 3) -> list[str]:
    """把多项式表达式按每行 per_line 项拆成多行。"""
    tokens = re.split(r"( [+-] )", expr)
    terms = [tokens[0]]
    for k in range(1, len(tokens) - 1, 2):
        terms.append((tokens[k] + tokens[k + 1]).strip())
    return [" ".join(terms[i:i + per_line])
            for i in range(0, len(terms), per_line)]


class LagrangeCurve:
    """只负责画线；图例由 legend_box 统一管理。"""

    def __init__(self) -> None:
        self._artist = None

    def draw(self, ax, nodes, samples: int = 600):
        """画插值曲线，返回 (short_label, full_label)。"""
        if self._artist is not None:
            self._artist.remove()
            self._artist = None
        if len(nodes.xs) < 2:
            return ("拉格朗日插值", None)

        # 去掉重复 x（防止除零）
        uniq: dict[float, float] = {}
        for x, y in zip(nodes.xs, nodes.ys):
            uniq[round(x, 12)] = y
        xs = sorted(uniq)
        ys = [uniq[x] for x in xs]

        x_min, x_max = original_function.X_MIN, original_function.X_MAX
        grid = [x_min + (x_max - x_min) * i / samples for i in range(samples + 1)]

        n = len(xs) - 1
        self._artist, = ax.plot(
            grid,
            [lagrange_eval(xs, ys, x) for x in grid],
            color="tab:red", lw=1.6,
            label=f"拉格朗日插值 (n={n})",
            zorder=4,
        )

        lines = wrap_expression(format_polynomial(poly_coefficients(xs, ys)))
        body = "\n".join(
            [f"$P(x)={lines[0]}$"] + [f"${line}$" for line in lines[1:]]
        )
        return (self._artist.get_label(), body)
