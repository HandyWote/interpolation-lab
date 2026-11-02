"""图例盒子：表格样式边框 + 行分隔线 + hover 悬浮窗展示完整表达式。

图例大小恒定；完整表达式在悬浮窗中展示，避免图例重绘导致布局变动。

样例：
    box = LegendBox(ax)
    box.update([("f(x) = 1/(1+x²)", None),
                ("拉格朗日插值 (n=5)", "$P(x)=...$"),
                ("牛顿插值 (n=5)", "$N(x)=...$")])
"""

from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Text


class LegendBox:
    """表格样式图例与 hover 悬浮窗的统一管理者。"""

    def __init__(self, ax: Axes) -> None:
        self.ax: Axes = ax
        self._legend: Legend | None = None
        self._separators: list[Line2D] = []   # 行分隔线（表格样式）
        self._tooltip: Text | None = None     # hover 悬浮窗
        self._entries: list[tuple[str, str | None]] = []
        self._cid: int | None = None          # 事件监听 ID

    def update(self, entries: list[tuple[str, str | None]]) -> None:
        """重建图例与分隔线。

        :param entries: [(短标签, 完整表达式或 None), ...]，顺序即条目顺序
        """
        self._entries = entries
        self._hide_tooltip()
        old_separator: Line2D
        for old_separator in self._separators:
            old_separator.remove()
        self._separators = []

        self._legend = self.ax.legend(
            loc="upper right", fontsize=8,
            framealpha=1.0,       # 不透明底，分割更清晰
            fancybox=False,       # 直角，表格风格
            edgecolor="black",
            labelspacing=1.2,     # 行距加大
            borderpad=0.8,
            handlelength=2.2,
        )
        self._legend.get_frame().set_linewidth(1.0)
        self._legend.set_zorder(6)

        fig = self.ax.figure
        fig.canvas.draw()  # 需要渲染一次才能拿到窗口坐标

        # ---- 行分隔线：相邻两行文字之间的灰线 ----
        texts: list[Text] = list(self._legend.texts)
        inv = self.ax.transAxes.inverted()
        legend_bbox = self._legend.get_window_extent()
        (lb_x0, lb_y0), (lb_x1, _) = inv.transform(
            [[legend_bbox.x0, legend_bbox.y0], [legend_bbox.x1, legend_bbox.y1]])
        i: int
        for i in range(len(texts) - 1):
            top: float = inv.transform(
                (0.0, texts[i].get_window_extent().y0))[1]
            bottom: float = inv.transform(
                (0.0, texts[i + 1].get_window_extent().y1))[1]
            y_mid: float = (top + bottom) / 2
            separator: Line2D
            separator, = self.ax.plot(
                [lb_x0 + 0.004, lb_x1 - 0.004], [y_mid, y_mid],
                transform=self.ax.transAxes,
                color="gray", lw=0.8, zorder=7,
            )
            self._separators.append(separator)

        if self._cid is None:
            self._cid = fig.canvas.mpl_connect(
                "motion_notify_event", self._on_motion)
        fig.canvas.draw_idle()

    # ---- hover：悬浮窗，不改变图例本身 ----

    def _on_motion(self, event: Event) -> None:
        """鼠标悬停在图例上 ↔ 离开：显示/隐藏悬浮窗。"""
        if self._legend is None:
            return
        inside: bool = self._legend.get_window_extent().contains(
            event.x, event.y)
        if inside:
            self._show_tooltip()
        else:
            self._hide_tooltip()

    def _show_tooltip(self) -> None:
        """在图例下方显示所有完整表达式的悬浮窗。"""
        blocks: list[str] = [full for _, full in self._entries if full]
        if not blocks:
            return
        text: str = "\n".join(blocks)
        if self._tooltip is None:
            legend_bbox = self._legend.get_window_extent()
            inv = self.ax.transAxes.inverted()
            x1: float
            y0: float
            x1, y0 = inv.transform((legend_bbox.x1, legend_bbox.y0))
            self._tooltip = self.ax.text(
                x1 - 0.01, y0 - 0.015, text,
                transform=self.ax.transAxes,
                ha="right", va="top", fontsize=8, zorder=20,
                bbox=dict(boxstyle="square,pad=0.4",
                          fc="white", ec="black", lw=1.0),
            )
        else:
            self._tooltip.set_text(text)
        self.ax.figure.canvas.draw_idle()

    def _hide_tooltip(self) -> None:
        """隐藏悬浮窗。"""
        if self._tooltip is not None:
            self._tooltip.remove()
            self._tooltip = None
            self.ax.figure.canvas.draw_idle()
