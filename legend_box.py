"""图例盒子：表格样式边框 + 行分隔线 + hover 悬浮窗展示完整表达式。

图例大小恒定；完整表达式在悬浮窗中展示，避免图例重绘导致布局变动。
"""


class LegendBox:
    def __init__(self, ax) -> None:
        self.ax = ax
        self._legend = None
        self._separators = []   # 行分隔线（表格样式）
        self._tooltip = None    # hover 悬浮窗
        self._entries = []      # [(短标签, 完整表达式或 None), ...]
        self._cid = None

    def update(self, entries) -> None:
        """entries: [(short_label, full_text_or_None), ...]。重建图例与分隔线。"""
        self._entries = entries
        self._hide_tooltip()
        for line in self._separators:
            line.remove()
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
        texts = self._legend.texts
        inv = self.ax.transAxes.inverted()
        lb = self._legend.get_window_extent()
        (lb_x0, lb_y0), (lb_x1, _) = inv.transform(
            [[lb.x0, lb.y0], [lb.x1, lb.y1]])
        for i in range(len(texts) - 1):
            top = inv.transform((0, texts[i].get_window_extent().y0))[1]
            bot = inv.transform((0, texts[i + 1].get_window_extent().y1))[1]
            ymid = (top + bot) / 2
            line, = self.ax.plot(
                [lb_x0 + 0.004, lb_x1 - 0.004], [ymid, ymid],
                transform=self.ax.transAxes,
                color="gray", lw=0.8, zorder=7,
            )
            self._separators.append(line)

        if self._cid is None:
            self._cid = fig.canvas.mpl_connect(
                "motion_notify_event", self._on_motion)
        fig.canvas.draw_idle()

    # ---- hover：悬浮窗，不改变图例本身 ----

    def _on_motion(self, event) -> None:
        if self._legend is None:
            return
        inside = self._legend.get_window_extent().contains(event.x, event.y)
        if inside:
            self._show_tooltip()
        else:
            self._hide_tooltip()

    def _show_tooltip(self) -> None:
        blocks = [full for _, full in self._entries if full]
        if not blocks:
            return
        text = "\n".join(blocks)
        if self._tooltip is None:
            lb = self._legend.get_window_extent()
            inv = self.ax.transAxes.inverted()
            x1, y0 = inv.transform((lb.x1, lb.y0))
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
        if self._tooltip is not None:
            self._tooltip.remove()
            self._tooltip = None
            self.ax.figure.canvas.draw_idle()
