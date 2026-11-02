"""牛顿插值：差商表 + 嵌套乘法（秦九韶式）求值。

N(x) = f[x0] + f[x0,x1](x-x0) + f[x0,x1,x2](x-x0)(x-x1) + ...
系数取差商表第一行（从首节点出发的各阶差商）。
加点只需在表末尾追加一列，旧系数不变。
"""

import numpy as np

import original_function


def divided_diffs(xs: list[float], ys: list[float]) -> list[float]:
    """计算牛顿系数 [f[x0], f[x0,x1], ..., f[x0..xn]]（差商表逐列递推）。"""
    n = len(xs)
    coeffs = [ys[0]]
    table = list(ys)
    for col in range(1, n):
        table = [(table[i + 1] - table[i]) / (xs[i + col] - xs[i])
                 for i in range(n - col)]
        coeffs.append(table[0])
    return coeffs


def newton_eval(xs: list[float], coeffs: list[float], x: float) -> float:
    """嵌套乘法（秦九韶）：从最高阶项往里套。"""
    result = coeffs[-1]
    for k in range(len(coeffs) - 2, -1, -1):
        result = result * (x - xs[k]) + coeffs[k]
    return result


def newton_expression(xs: list[float], coeffs: list[float]) -> str:
    """把牛顿嵌套形式展开为标准多项式表达式字符串。"""
    from lagrange import format_polynomial
    n = len(xs)
    coeff_std = np.zeros(n)
    for k in range(n):
        c = np.array([1.0])
        for i in range(k):
            c = np.polymul(c, [1.0, -xs[i]])
        coeff_std[:k + 1] += coeffs[k] * c[::-1]  # 反转成升幂，长度为 k+1
    return format_polynomial(coeff_std)


class NewtonCurve:
    """只负责画线；图例由 legend_box 统一管理。"""

    def __init__(self) -> None:
        self._artist = None

    def draw(self, ax, nodes, samples: int = 600):
        """画插值曲线，返回 (short_label, full_label)。"""
        if self._artist is not None:
            self._artist.remove()
            self._artist = None
        if len(nodes.xs) < 2:
            return ("牛顿插值", None)

        uniq: dict[float, float] = {}
        for x, y in zip(nodes.xs, nodes.ys):
            uniq[round(x, 12)] = y
        xs = sorted(uniq)
        ys = [uniq[x] for x in xs]

        coeffs = divided_diffs(xs, ys)
        n = len(xs) - 1
        self._artist, = ax.plot(
            [original_function.X_MIN + (original_function.X_MAX - original_function.X_MIN) * i / samples
             for i in range(samples + 1)],
            [newton_eval(xs, coeffs,
                         original_function.X_MIN + (original_function.X_MAX - original_function.X_MIN) * i / samples)
             for i in range(samples + 1)],
            color="tab:green", lw=1.6, linestyle="-.",
            label=f"牛顿插值 (n={n})",
            zorder=4,
        )

        from lagrange import wrap_expression
        lines = wrap_expression(newton_expression(xs, coeffs))
        body = "\n".join(
            [f"$N(x)={lines[0]}$"] + [f"${line}$" for line in lines[1:]]
        )
        return (self._artist.get_label(), body)
