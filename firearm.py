from __future__ import annotations

from displaylib import * # type: ignore
import pygame.mixer as mixer
import keyboard
import copy
from typing import TYPE_CHECKING
# local imports
from item import Item

if TYPE_CHECKING:
    from main import App


class Projectile(Sprite):
    texture = [["."]]
    direction: int = 1
    speed: int = 5

    def _update(self, delta: float) -> None:
        self.position.x += self.direction * self.speed


class Firearm(Item):
    root: App
    # color = color.LIGHT_GRAY
    default_z_index = 1
    texture = [[*" -- -"]]
    original_texture: list[list[str]] = copy.deepcopy(texture)

    def __init__(self, parent: AnyNode | None = None, *, x: float = 0, y: float = 0) -> None:
        self._sound_shoot = mixer.Sound("./sounds/shotgun_shoot_instant.wav")
    
    def _update(self, delta: float) -> None:
        if keyboard.is_pressed("SHIFT"):
            self.shoot()
    
    def shoot(self) -> None:
        loc = self.get_global_position()
        loc += Vec2(5, 0)
        projectile = Projectile(x=loc.x, y=loc.y)
        # projectile.set_global_position(self.get_global_position())
        projectile.direction = self.root.player.direction.x
