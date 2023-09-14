from displaylib.ascii import * # type: ignore
# ===
from actor import Actor


class Enemy(Actor):
    position = Vec2(3, 5)
    color = color.DARK_VIOLET
