from __future__ import annotations
from displaylib import * # type: ignore
from displaylib.ascii.prototypes.texture_collider import TextCollider
from typing import TYPE_CHECKING
# local imports
from pair_uid import PairUid

if TYPE_CHECKING:
    from main import App


class Voxel(Sprite, TextCollider, PairUid):
    root: App
    texture = [["#"]]

    def queue_free(self) -> None:
        super().queue_free()
        req = networking.Request("DELETE_IF_ALIVE", [self.peer_uid])
        self.root.send(req)


class RandVoxel(Voxel):
    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0) -> None:
        self.color = color.rand_color()
