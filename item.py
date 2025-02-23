from displaylib import * # type: ignore


class Item(Sprite):
    color = color.SKY_BLUE
    texture = [[*"[?]"]]

    def __init__(self, parent: AnyNode | None = None, *, x: float = 0, y: float = 0) -> None:
        ...