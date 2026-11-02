"""牛顿插值：差商表 + 嵌套乘法（秦九韶式）求值。

N(x) = f[x0] + f[x0,x1](x-x0) + f[x0,x1,x2](x-x0)(x-x1) + ...
系数取差商表第一行（从首节点出发的各阶差商）。
加点只需在表末尾追加一列，旧系数不变。

样例：过 (1,3),(2,7),(4,19),(7,55) 的插值多项式，
系数为 [3, 4, 2/3, 4/45]，在 x=7 处应得 55。

注：牛顿形式与拉格朗日形式是同一个多项式（唯一性定理），
展开为标准式时直接复用 lagrange.poly_coefficients。
"""

from matplotlib.axes import Axes
from matplotlib.lines import Line2D

import original_function
from lagrange import format_polynomial, poly_coefficients, wrap_expression
from nodes import Nodes


def divided_diffs(xs: list[float], ys: list[float]) -> list[float]:
    """计算牛顿系数 [f[x0], f[x0,x1], ..., f[x0..xn]]（差商表逐列递推）。

    >>> [round(c, 6) for c in
    ...  divided_diffs([1.0, 2.0, 4.0, 7.0], [3.0, 7.0, 19.0, 55.0])]
    [3.0, 4.0, 0.666667, 0.088889]
    """
    n: int = len(xs)
    coeffs: list[float] = [ys[0]]
    current_col: list[float] = list(ys)  # 差商表当前列
    col: int
    for col in range(1, n):
        current_col = [(current_col[i + 1] - current_col[i])
                       / (xs[i + col] - xs[i])
                       for i in range(n - col)]
        coeffs.append(current_col[0])
    return coeffs


def newton_eval(xs: list[float], coeffs: list[float], x: float) -> float:
    """嵌套乘法（秦九韶）：从最高阶项往里套。

    >>> coeffs = divided_diffs([1.0, 2.0, 4.0, 7.0], [3.0, 7.0, 19.0, 55.0])
    >>> round(newton_eval([1.0, 2.0, 4.0, 7.0], coeffs, 7.0), 10)
    55.0
    >>> round(newton_eval([1.0, 2.0, 4.0, 7.0], coeffs, 1.0), 10)
    3.0
    """
    result: float = coeffs[-1]
    k: int
    for k in range(len(coeffs) - 2, -1, -1):
        result = result * (x - xs[k]) + coeffs[k]
    return result


class NewtonCurve:
    """牛顿插值曲线的绘制对象：点变化后重新 draw 即可。

    只负责画线；图例由 legend_box.LegendBox 统一管理。

    样例：
        curve = NewtonCurve()
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
            return ("牛顿插值", None)

        coeffs: list[float] = divided_diffs(xs, ys)
        n: int = len(xs) - 1
        short_label: str = f"牛顿插值 (n={n})"

        x_min: float = original_function.X_MIN
        x_max: float = original_function.X_MAX
        grid: list[float] = [x_min + (x_max - x_min) * i / samples
                             for i in range(samples + 1)]
        self._artist, = ax.plot(
            grid,
            [newton_eval(xs, coeffs, x) for x in grid],
            color="tab:green", lw=1.6, linestyle="-.",
            label=short_label,
            zorder=4,
        )

        expr_lines: list[str] = wrap_expression(
            format_polynomial(poly_coefficients(xs, ys)))
        body: str = "\n".join(
            [f"$N(x)={expr_lines[0]}$"] + [f"${line}$" for line in expr_lines[1:]]
        )
        return (short_label, body)
