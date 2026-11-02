"""原始目标函数：Runge 函数 f(x) = 1/(1+x²)，虚线绘制。

课程实验所给函数（第2章 slide 39）：定义域 [-5, 5]。

>>> f(0.0)
1.0
>>> f(2.0)
0.2
"""

from matplotlib.axes import Axes

X_MIN: float = -5.0
X_MAX: float = 5.0

# 原函数的图例条目（短标签, 完整表达式或 None）
LEGEND: tuple[str, str | None] = ("f(x) = 1/(1+x²)", None)


def f(x: float) -> float:
    """Runge 函数。

    >>> f(0.0)
    1.0
    >>> round(f(5.0), 4)
    0.0385
    """
    return 1.0 / (1.0 + x * x)


def draw_original(ax: Axes, x_min: float = X_MIN, x_max: float = X_MAX,
                  samples: int = 400) -> Axes:
    """在画板上用虚线画原始函数曲线。

    样例：draw_original(ax) 在 [-5, 5] 上画 401 个采样点的虚线。

    :param ax: 画板
    :param x_min: 定义域左端
    :param x_max: 定义域右端
    :param samples: 采样点数
    :return: 画板（链式调用用）
    """
    xs: list[float] = [x_min + (x_max - x_min) * i / samples
                       for i in range(samples + 1)]
    ys: list[float] = [f(x) for x in xs]
    ax.plot(xs, ys, linestyle="--", color="tab:blue", lw=1.8,
            label=LEGEND[0], zorder=3)
    return ax
