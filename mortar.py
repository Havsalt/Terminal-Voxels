from __future__ import annotations
from displaylib import * # type: ignore
from displaylib.ascii.prototypes.texture_collider import TextCollider
import keyboard
import random
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from typing import TYPE_CHECKING
import pygame.mixer as mixer
mixer.init(channels=16)
# local imports
from explosive import Explosive
from c4 import ExplosionParticle

if TYPE_CHECKING:
    from main import App


class Marker(Sprite):
    position = Vec2(3, 2)
    centered = True
    color = color.RED
    texture = [[*".-."]]


class Mortar(Sprite):
    root: App
    rotation_margin: int = 12
    color = color.GRAY
    texture = [
        [*"     "],
        [*" <  >"],
        [*"/-::-\\"]
    ]
    _interaction_radius: float = 7
    _cooldown_frames: int = 50 // 10
    _elapsed_frames: int = _cooldown_frames

    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0) -> None:
        self._use_pressed = False
        self._activate_pressed = False
        self._player_mounted = False
        self._player_in_reach = False
        self._aim_direction = Vec2(1, -1)
        self._sound_shoot = mixer.Sound("./sounds/shotgun_shoot_instant.wav")
        self._sound_reload = mixer.Sound("./sounds/shotgun_reload.wav")
        self._barrel = Sprite(
            self,
            x=1,
            color=color.SLATE_GRAY,
            texture=[
                [*"  //"],
                [*" //"]
            ])
        self._button = Label(
            self,
            x=-1,
            y=-1,
            centered=True,
            z_index=1,
            text="[E]"
            )
        self._marker = Marker(self)
        self._marker.hide()
    
    @property
    def _can_shoot(self) -> bool:
        return self._elapsed_frames >= self._cooldown_frames
    
    def _update(self, _delta: float) -> None:
        self._elapsed_frames += 1
        if self._barrel.get_global_position().distance_to(self.root.player.get_global_position()) <= self._interaction_radius:
            self._player_in_reach = True
            self._button.color = color.rgb_color(255, 255, 255, reverse=True)
        else:
            self._player_in_reach = False
            self._button.color = color.WHITE
        
        if self._player_in_reach:
            if self._player_mounted:
                if self._can_shoot and not self._activate_pressed and keyboard.is_pressed("Space"):
                    self._elapsed_frames = 0
                    self._activate_pressed = True
                    self._activate()
                elif self._activate_pressed and not keyboard.is_pressed("Space"):
                    self._activate_pressed = False
            
            if not self._use_pressed and keyboard.is_pressed("E"):
                self._use_pressed = True
                if not self._player_mounted:
                    self._player_mounted = True
                    self.root.player.can_move = False
                    loc = self.get_global_position() + Vec2(0, 1)
                    self.root.player.set_global_position(loc)
                    self._button.hide()
                    self._marker.show()
                else:
                    self._player_mounted = False
                    self._marker.hide()
                    self._marker.position = Vec2(3, 2)
                    self.root.player.can_move = True
                    self._button.show()
            elif self._use_pressed and not keyboard.is_pressed("E"):
                self._use_pressed = False
        
        if self._player_mounted:
            if keyboard.is_pressed("D"):
                self._marker.position.x += 2
            if keyboard.is_pressed("A"):
                self._marker.position.x -= 2
            value = self._marker.position.x
            if abs(value) <= self.rotation_margin:
                self._barrel.texture = [
                    [*" ||"],
                    [*" ||"]
                ]
            elif value > self.rotation_margin:
                self._barrel.texture = [
                    [*"  //"],
                    [*" //"]
                ]
            else:
                self._barrel.texture = [
                    [*"\\\\"],
                    [*" \\\\"]
                ]
    
    def _activate(self) -> None:
        loc = self.get_global_position()
        shell = Shell(x=loc.x+1, y=loc.y, target=self._marker.get_global_position()).as_unique()
        value = self._marker.position.x
        if abs(value) <= self.rotation_margin:
            shell.texture = [
                [*" ::"],
                [*" ||"]
            ]
        elif value > self.rotation_margin:
            shell.speed = Vec2(1, -1)
            shell.texture = [
                [*"  .:"],
                [*" // "]
            ]
        else:
            shell.speed = Vec2(-1, -1)
            shell.texture = [
                [*":. "],
                [*" \\\\"]
            ]
        data = [
            shell.name,
            shell.uid,
            *self.get_global_position().to_tuple(),
            *shell.target.to_tuple(),
            *shell.speed.to_tuple(),
            *shell.texture[0],
            *shell.texture[1]
        ]
        req = networking.Request("CREATE_SHELL", data)
        self.root.send(req)
        self._sound_shoot.play()
        self._sound_reload.play()
        # AudioStreamPlayer("./sounds/shotgun_shoot_instant.wav").play()
        # AudioStreamPlayer("./sounds/shotgun_reload.wav").play()
        
    def queue_free(self) -> None:
        super().queue_free()
        self._barrel.queue_free()
        self._button.queue_free()
        self._marker.queue_free()
        if self._player_mounted:
            self.root.player.can_move = True


class Shell(Sprite, TextCollider, Explosive):
    right_mount_pos: Vec2 = Vec2(0, 1)
    left_mount_pos: Vec2 = Vec2(5, 1)
    is_falling: bool = False
    should_fall: bool = False
    fall_height: int = 4
    target_margin: float = 3
    fall_speed: float = 3
    min_frames: int = 10
    frames_elapsed: int = 0
    explosion_radius = 2
    transformation = Vec2(1, 0.5)
    default_z_index = -1
    color = color.SLATE_BLUE
    texture = [
        [*"[!!]"],
        [*"[!!]"]
    ]
    def __init__(self, parent: AnyNode | None = None, x: float = 0, y: float = 0, target: Vec2 = Vec2(0, 0), speed: Vec2 = Vec2(0, -1)) -> None:
        self.target = target
        self.speed = speed
        self._sound_detonate = mixer.Sound("./sounds/shotgun_shoot_instant.wav")

    def _update(self, _delta: float) -> None:
        self.frames_elapsed += 1
        self.position += self.speed
        if not self.is_falling and self.speed == Vec2(0, -1) and self.frames_elapsed >= self.min_frames:
            self.should_fall = True
        if not self.is_falling and abs(self.target.x - self.get_global_position().x) < self.target_margin:
            self.should_fall = True
        if not self.is_falling and self.should_fall and self.frames_elapsed >= self.min_frames:
            self.is_falling = True
            self.set_global_position(self.target)
            self.position.y -= self.fall_height
            self.speed = Vec2(0, self.fall_speed)
            self.texture = [
                [*"||"],
                [*"':"]
            ]
            if random.randint(0, 1):
                self.texture[1] = [*":'"]
        
        if self.should_fall and self.get_collider():
            # AudioStreamPlayer("./sounds/shotgun_shoot_instant.wav").play()
            self._sound_detonate.play()
            self.detonate()
    
    def get_collider(self) -> TextCollider | None:
        here = self.get_global_position()
        end = here + self.size()
        for node in Node.nodes.values():
            if node is self:
                continue
            if isinstance(node, Transform2D) and isinstance(node, TextCollider):
                point = node.get_global_position()
                if here <= point < end:
                    return node
        return None

    def get_all_colliders(self) -> list[TextCollider]:
        results = []
        here = self.get_global_position()
        end = here + self.size()
        for node in Node.nodes.values():
            if node is self:
                continue
            if isinstance(node, Transform2D) and isinstance(node, TextCollider):
                point = node.get_global_position()
                if here <= point < end:
                    results.append(node)
        return results

    def is_on_floor(self) -> bool:
        self.position.y += 1
        cond = self.get_collider() is not None
        self.position.y -= 1
        return cond

    def _on_node_affected(self, node: Node2D) -> None:
        self.queue_free()
        if isinstance(node, (Explosive, Marker)) or node.name == "Player":
            return
        node.queue_free()
        if not random.randint(0, 2):
            return
        particle = ExplosionParticle().as_unique()
        particle.set_global_position(node.get_global_position())
        particle.lifetime = 0.25 + 0.25 * random.random()
        particle.texture[0][0] = (
            "+",
            "*",
            "."
        )[random.randint(0, 2)]
        if isinstance(node, Color):
            particle.color = node.color
