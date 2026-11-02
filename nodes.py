"""插值节点：管理画在函数上的采样点（状态 + 绘制）。

点从原始函数 f(x) 上随机采样得到，后续将作为插值节点使用。
"""

import random

import original_function


class Nodes:
    def __init__(self) -> None:
        self.xs: list[float] = []
        self.ys: list[float] = []
        self._artist = None  # 当前散点图对象，重绘前先移除

    def add_random(self, x_min: float = original_function.X_MIN,
                   x_max: float = original_function.X_MAX) -> None:
        """在函数上随机取一个点。"""
        x = random.uniform(x_min, x_max)
        self.xs.append(x)
        self.ys.append(original_function.f(x))

    def draw(self, ax):
        if self._artist is not None:
            self._artist.remove()
        self._artist = ax.scatter(self.xs, self.ys, s=30, color="crimson",
                                  zorder=5)
        return self._artist
