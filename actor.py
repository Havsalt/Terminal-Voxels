from __future__ import annotations
from displaylib import * # type: ignore
from displaylib.ascii.prototypes.texture_collider import TextCollider
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import App
# local imports
from c4 import C4


class Actor(Sprite, TextCollider):
    root: App
    centered = True
    texture = [
        [*"  O"],
        [*"/ | \\"],
        [*" / \\"]
    ]
    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0) -> None:
        self.uid_bar = Label(self, y=-2, text=f"({(self.uid).center(3)})", color=color.CORAL, centered=True)
    #     self._health = 100
    #     self._health_bar = Label(self, y=3, text=f"[{str(self._health).center(3)}]", color=color.CRIMSON)
    
    # @property
    # def health(self) -> int:
    #     return self._health

    # @health.setter
    # def health(self, value: int) -> None:
    #     self._health = value
    #     self._health_bar.text = f"[{str(self._health).center(3)}]"

    def get_collider(self) -> TextCollider | None:
        here = self.get_global_position()
        if self.centered:
            here -= self.size() // 2
        end = here + self.size()
        for node in Node.nodes.values():
            if node is self:
                continue
            if isinstance(node, Transform2D) and isinstance(node, TextCollider) and not isinstance(node, C4):
                point = node.get_global_position()
                if here <= point < end:
                    return node
        return None

    def get_all_colliders(self) -> list[TextCollider]:
        results = []
        here = self.get_global_position()
        if self.centered:
            here -= self.size() // 2
        end = here + self.size()
        for node in Node.nodes.values():
            if node is self:
                continue
            if isinstance(node, Transform2D) and isinstance(node, TextCollider) and not isinstance(node, C4):
                point = node.get_global_position()
                if here <= point < end:
                    results.append(node)
        return results

    def is_on_floor(self) -> bool:
        self.position.y += 1
        cond = self.get_collider() is None
        self.position.y -= 1
        return cond
