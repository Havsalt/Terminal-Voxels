from displaylib import * # type: ignore
from typing import cast
# local imports
from building import Building


class Explosive:
    fuse_time: float = 50 # frames
    explosion_radius: float = 5.0
    transformation: Vec2 = Vec2(1, 1)
    destructable_types: tuple[type, ...] = (
        Building,
    )
    
    def detonate(self) -> None:
        self = cast(Node2D, self)
        here = self.get_global_position()
        self = cast(Explosive, self)
        for node in tuple(Node.nodes.values()):
            if not isinstance(node, self.destructable_types):
                continue
            assert isinstance(node, Node2D)
            there = node.get_global_position()
            diff = (there - here) * self.transformation
            dist = diff.length()
            if dist <= self.explosion_radius:
                self._on_node_affected(node)
    
    def _on_node_affected(self, node: Node2D) -> None:
        node.queue_free()
