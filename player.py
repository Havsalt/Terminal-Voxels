from __future__ import annotations
from displaylib import * # type: ignore
import keyboard
from typing import TYPE_CHECKING
# local imports
from remote_type import RemoteType
from actor import Actor
from voxel import Voxel
from c4 import C4
from mortar import Mortar
from firearm import Firearm

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
        self.direction = Vec2i(0, 0)
        self.animation_player = AnimationPlayer(
            self,
            Idle=Animation("./animations/idle"),
            WalkRight=Animation("./animations/walk"),
            WalkLeft=Animation("./animations/walk", fliph=True),
            Hold=Animation("./animations/hold"),
            WalkHoldRight=Animation("./animations/walk_hold"),
            WalkHoldLeft=Animation("./animations/walk_hold", fliph=True, fill=True)
        )
        # self.firearm = Firearm(self, x=-1)
    
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
            
            velocity = Vec2i()
            if keyboard.is_pressed("D"):
                velocity.x += 1
            if keyboard.is_pressed("A"):
                velocity.x -= 1
            if keyboard.is_pressed("W"):
                velocity.y -= 1
            if keyboard.is_pressed("S"):
                velocity.y += 1
            self.position += velocity
            if self.get_collider():
                if not keyboard.is_pressed("SPACE"):
                    self.position -= velocity
                    velocity -= velocity
            else:
                self.direction = velocity.copy()
            
            direction = velocity.sign().x
            if direction == 0:
                anim_name = "Idle" if not hasattr(self, "firearm") else "Hold"
                self.animation_player.play(anim_name)
                self.is_walking = False
            elif direction == 1:
                anim_name = "WalkRight" if not hasattr(self, "firearm") else "WalkHoldRight"
                if hasattr(self, "firearm"):
                    self.firearm.position.x = -1 # type: ignore
                    self.firearm.texture = self.firearm.original_texture # type: ignore
                if self.animation_player.current_animation != anim_name or not self.animation_player.is_playing:
                    self.animation_player.play(anim_name)
                    self.is_walking = True
            elif direction == -1:
                anim_name = "WalkLeft" if not hasattr(self, "firearm") else "WalkHoldLeft"
                if hasattr(self, "firearm"):
                    self.firearm.position.x = -4 # type: ignore
                    self.firearm.texture = text.mapfliph(self.firearm.original_texture) # type: ignore
                if self.animation_player.current_animation != anim_name or not self.animation_player.is_playing:
                    self.animation_player.play(anim_name)
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
