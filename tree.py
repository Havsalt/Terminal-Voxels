from displaylib import * # type: ignore


class Tree(Sprite):
    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0) -> None:
        self._leaves = Sprite(
            self,
            x=-2,
            y=-5,
            color=color.SEA_GREEN,
            texture=[
                [*"  &"],
                [*" &?&"],
                [*"&?&?&"],
            ]
        )
        self._stem = Sprite(
            self,
            y=-2,
            color = color.BROWN,
            texture = [
                ["|"],
                ["|"],
                ["|"]
            ]
        )
        self._rock = Sprite(
            self,
            x=-1,
            z_index=-1,
            color=color.GRAY,
            texture=[[*", ."]]
        )
    
    def queue_free(self) -> None:
        super().queue_free()
        self._leaves.queue_free()
        self._stem.queue_free()
        self._rock.queue_free()
