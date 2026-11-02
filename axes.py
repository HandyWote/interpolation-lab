"""坐标数轴：完整 x/y 轴，原点在中心，带箭头、刻度、轴名。

只负责在给定的 Axes 上画坐标系，不创建画板。
"""

LIMIT = 5.5  # 坐标范围 [-LIMIT, LIMIT]


def draw_axes(ax, limit: float = LIMIT):
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal")
    ax.axis("off")  # 关掉默认边框，手工画数轴

    # ---- x 轴 / y 轴（穿过原点）----
    ax.plot([-limit, limit], [0, 0], color="black", lw=1.2, zorder=1)
    ax.plot([0, 0], [-limit, limit], color="black", lw=1.2, zorder=1)

    # 轴末端箭头
    arrow_kw = dict(color="black", lw=0)
    ax.annotate("", xy=(limit, 0), xytext=(limit - 0.3, 0),
                arrowprops={**arrow_kw, "arrowstyle": "-|>", "mutation_scale": 14})
    ax.annotate("", xy=(0, limit), xytext=(0, limit - 0.3),
                arrowprops={**arrow_kw, "arrowstyle": "-|>", "mutation_scale": 14})

    # ---- 刻度与数字 ----
    tick_half = 0.09   # 刻度线半长
    label_off = 0.32   # 数字离轴的距离
    for t in range(-5, 6):
        if t == 0:
            continue  # 原点单独标
        # x 轴刻度
        ax.plot([t, t], [-tick_half, tick_half], color="black", lw=1, zorder=2)
        ax.text(t, -label_off, str(t), ha="center", va="top", fontsize=10)
        # y 轴刻度
        ax.plot([-tick_half, tick_half], [t, t], color="black", lw=1, zorder=2)
        ax.text(-label_off, t, str(t), ha="right", va="center", fontsize=10)

    # 原点与轴名
    ax.text(-label_off, -label_off, "0", ha="right", va="top", fontsize=10)
    ax.text(limit + 0.15, 0, "x", ha="left", va="center", fontsize=12, style="italic")
    ax.text(0, limit + 0.15, "y", ha="center", va="bottom", fontsize=12, style="italic")

    return ax
