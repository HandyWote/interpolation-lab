"""编排：提供画板，装坐标轴，画原始函数；按钮添加随机采样点，
同时触发拉格朗日与牛顿插值曲线重绘；图例统一管理。

运行：uv run main.py
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import axes
import original_function
from legend_box import LegendBox
from lagrange import LagrangeCurve
from newton import NewtonCurve
from nodes import Nodes

matplotlib.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]  # 中文
matplotlib.rcParams["axes.unicode_minus"] = False


def main() -> None:
    fig, ax = plt.subplots(figsize=(8, 8))  # 画板
    axes.draw_axes(ax)                      # 坐标系
    original_function.draw_original(ax)     # 原始函数（虚线）

    sample_points: Nodes = Nodes()
    lag_curve: LagrangeCurve = LagrangeCurve()
    newton_curve: NewtonCurve = NewtonCurve()
    legend_panel: LegendBox = LegendBox(ax)

    def redraw() -> None:
        """加点/重绘的统一入口：点 → 两条插值曲线 → 图例。"""
        sample_points.draw(ax)
        lagrange_entry: tuple[str, str | None] = lag_curve.draw(ax, sample_points)
        newton_entry: tuple[str, str | None] = newton_curve.draw(ax, sample_points)
        entries: list[tuple[str, str | None]] = [
            original_function.LEGEND, lagrange_entry, newton_entry]
        legend_panel.update(entries)
        fig.canvas.draw_idle()

    redraw()

    fig.tight_layout()

    # ---- 按钮：新增随机生成的函数上的点 ----
    ax_button = fig.add_axes([0.015, 0.015, 0.13, 0.055])  # 画板内左下角
    button: Button = Button(ax_button, "随机加点")

    def on_click(event) -> None:
        sample_points.add_random()
        redraw()

    button.on_clicked(on_click)

    plt.show()


if __name__ == "__main__":
    main()
