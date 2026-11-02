"""原始目标函数：Runge 函数 f(x) = 1/(1+x²)，虚线绘制。

课程实验所给函数（第2章 slide 39）：定义域 [-5, 5]。
"""

X_MIN, X_MAX = -5.0, 5.0
LEGEND = ("f(x) = 1/(1+x²)", None)  # 原函数图例条目（无展开内容）


def f(x: float) -> float:
    return 1.0 / (1.0 + x * x)


def draw_original(ax, x_min: float = X_MIN, x_max: float = X_MAX,
                  samples: int = 400):
    xs = [x_min + (x_max - x_min) * i / samples for i in range(samples + 1)]
    ys = [f(x) for x in xs]
    ax.plot(xs, ys, linestyle="--", color="tab:blue", lw=1.8,
            label=LEGEND[0], zorder=3)
    return ax
