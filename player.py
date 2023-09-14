from __future__ import annotations
from displaylib import * # type: ignore
import keyboard
from typing import TYPE_CHECKING
# ===
from remote_type import RemoteType
from actor import Actor
from voxel import Voxel
from c4 import C4
from mortar import Mortar

if TYPE_CHECKING:
    from main import App


class Player(Actor):
    root: App
    position = Vec2(12, 5)
    color = color.SKY_BLUE
    remote_type: type[Player]

    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0) -> None:
        super().__init__()
        self.can_move = True
        self.tab_pressed = False
        self.build_pressed = False
        self.is_walking = False
        self.animation_player = AnimationPlayer(
            self,
            Idle=Animation("./animations/idle"),
            WalkRight=Animation("./animations/walk"),
            WalkLeft=Animation("./animations/walk", fliph=True),
        )
    
    def size(self) -> Vec2i:
        size = super().size()
        if self.is_walking:
            size.x -= 1
        return size
    
    def _update(self, _delta: float) -> None:
        # for collider in self.get_all_colliders():
        if (collider := self.get_collider()) is not None:
            if isinstance(collider, Voxel):
                collider.queue_free()
                # if hasattr(collider, "peer_uid"):
                #     uid = collider.peer_uid # type: ignore
                #     req = networking.Request("DELETE_IF_ALIVE", data=[uid])
                #     self.root.send(req)
        
        if self.get_collider():
            return

        if self.can_move:
            # apply gravity if not frozen
            self.position.y += 1
            if self.get_collider():
                self.position.y -= 1
            
            velocity = Vec2()
            if keyboard.is_pressed("d"):
                velocity.x += 1
            if keyboard.is_pressed("a"):
                velocity.x -= 1
            if keyboard.is_pressed("w"):
                velocity.y -= 1
            if keyboard.is_pressed("s"):
                velocity.y += 1
            self.position += velocity
            if self.get_collider():
                if not keyboard.is_pressed("space"):
                    self.position -= velocity
                    velocity -= velocity
            
            direction = velocity.sign().x
            if direction == 0:
                self.animation_player.play("Idle")
                self.is_walking = False
            elif direction == 1:
                if self.animation_player.current_animation != "WalkRight" or not self.animation_player.is_playing:
                    self.animation_player.play("WalkRight")
                    self.is_walking = True
            elif direction == -1:
                if self.animation_player.current_animation != "WalkLeft" or not self.animation_player.is_playing:
                    self.animation_player.play("WalkLeft")
                    self.is_walking = True
            if not self.animation_player.is_playing:
                self.is_walking = False
        
        if keyboard.is_pressed("tab") and not self.tab_pressed:
            self.tab_pressed = True
            c4 = C4()
            c4.set_global_position(self.get_global_position())
            c4.position -= Vec2(0, 1)
            req = networking.Request("CREATE", [c4.name, c4.uid, *c4.get_global_position().to_tuple()])
            self.root.send(req)
        elif self.tab_pressed and not keyboard.is_pressed("tab"):
            self.tab_pressed = False
        
        if keyboard.is_pressed("b") and not self.build_pressed:
            self.build_pressed = True
            if self.can_move:
                loc = self.get_global_position()
                building = Mortar(x=loc.x-2, y=loc.y-1)
                req = networking.Request("CREATE", [building.name, building.uid, *building.get_global_position().to_tuple()])
                self.root.send(req)
        elif self.build_pressed and not keyboard.is_pressed("b"):
            self.build_pressed = False


class StaticPlayer(Player, RemoteType):
    position = Vec2(0, 0)
    color = color.SEA_GREEN
    local_type: type[Player]

    def _update(self, _delta: float) -> None:
        return

Player.remote_type = StaticPlayer
StaticPlayer.local_type = Player
