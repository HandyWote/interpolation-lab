"""插值节点：管理画在函数上的采样点（状态 + 绘制）。

点从原始函数 f(x) 上随机采样得到，后续将作为插值节点使用。

样例：
    nodes = Nodes()
    nodes.xs = [1.0, 2.0]
    nodes.ys = [3.0, 7.0]
"""

import random

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection

import original_function


class Nodes:
    """采样点集合：xs/ys 平行列表，与插值模块共享。"""

    def __init__(self) -> None:
        self.xs: list[float] = []
        self.ys: list[float] = []
        self._artist: PathCollection | None = None  # 当前散点，重绘前先移除

    def add_random(self, x_min: float = original_function.X_MIN,
                   x_max: float = original_function.X_MAX) -> None:
        """在函数上随机取一个点（x 均匀分布，y = f(x)）。"""
        x: float = random.uniform(x_min, x_max)
        self.xs.append(x)
        self.ys.append(original_function.f(x))

    def deduplicated(self) -> tuple[list[float], list[float]]:
        """返回去重后的 (xs, ys)，按 x 升序。

        随机采样极小概率产生重复 x，重复时保留后者的 y，
        防止插值公式中除零。

        >>> nodes = Nodes()
        >>> nodes.xs = [2.0, 1.0, 2.0]
        >>> nodes.ys = [7.0, 3.0, 9.0]
        >>> nodes.deduplicated()
        ([1.0, 2.0], [3.0, 9.0])
        """
        unique_points: dict[float, float] = {}
        i: int
        for i in range(len(self.xs)):
            unique_points[round(self.xs[i], 12)] = self.ys[i]
        xs: list[float] = sorted(unique_points)
        ys: list[float] = [unique_points[x] for x in xs]
        return (xs, ys)

    def draw(self, ax: Axes) -> PathCollection | None:
        """把当前所有点画成红色散点（覆盖旧散点）。"""
        if self._artist is not None:
            self._artist.remove()
            self._artist = None
        if self.xs:
            self._artist = ax.scatter(self.xs, self.ys, s=30,
                                      color="crimson", zorder=5)
        return self._artist
