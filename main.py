"""编排：提供画板，装坐标轴，画原始函数；按钮添加随机采样点，
同时触发拉格朗日与牛顿插值曲线重绘；图例统一管理。

运行：uv run main.py
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import axes
import lagrange as lagrange_mod
import legend_box
import newton as newton_mod
import nodes as nodes_mod
import original_function

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]  # 中文
matplotlib.rcParams["axes.unicode_minus"] = False


def main() -> None:
    fig, ax = plt.subplots(figsize=(8, 8))  # 画板
    axes.draw_axes(ax)                      # 坐标系
    original_function.draw_original(ax)     # 原始函数（虚线）

    nodes = nodes_mod.Nodes()
    lag_curve = lagrange_mod.LagrangeCurve()
    newton_curve = newton_mod.NewtonCurve()
    box = legend_box.LegendBox(ax)

    def redraw() -> None:
        nodes.draw(ax)
        e1 = lag_curve.draw(ax, nodes)
        e2 = newton_curve.draw(ax, nodes)
        entries = [original_function.LEGEND, e1, e2]
        box.update(entries)
        fig.canvas.draw_idle()

    redraw()

    fig.tight_layout()

    # ---- 按钮：新增随机生成的函数上的点 ----
    ax_button = fig.add_axes([0.015, 0.015, 0.13, 0.055])  # 画板内左下角
    button = Button(ax_button, "随机加点")

    def on_click(event) -> None:
        nodes.add_random()
        redraw()

    button.on_clicked(on_click)

    plt.show()


if __name__ == "__main__":
    main()
