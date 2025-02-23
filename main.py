from displaylib import * # type: ignore
from displaylib.ascii.prototypes.particles_emitter import Particle
import itertools
import random
from typing import Any
import keyboard
# audio imports
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame.mixer as mixer
mixer.init(channels=16)
# local imports
from actor import Actor
from player import Player, StaticPlayer
from voxel import Voxel, RandVoxel
from ore import Ore
from tree import Tree
from explosive import Explosive
from mortar import Mortar, Shell
from c4 import C4


class App(Engine, networking.Peer):
    request_batch = 64
    response_batch = 64
    LOAD_TYPES: tuple[type[Any], ...] = (
        Voxel, # any voxel
        Tree,
        Mortar
    )
    EXCLUDED_LOAD_TYPES: tuple[type[Any], ...] = (
        Debug, # those who has this component
    )
    f_pressed: bool = False

    def _on_start(self) -> None:
        debug("[Info] DevPeer started", lifetime=5)
        Camera.current.mode = Camera.CENTERED
        self.player = Player(x=25, y=-3)
        self.player.color = color.SKY_BLUE
        self.other_player = StaticPlayer()
        self.other_player.hide()
        # self.other_player.hide()
        if not self.is_peer_responsive():
            debug("[Net] Is network master")
            trees = (
                Vec2(35, 4),
                Vec2(45, 4)
            )
            for loc in trees:
                tree = Tree(x=loc.x, y=loc.y)
            ore_spawn_info = (
                (Ore, Vec2(78, 13), 5, Vec2(0.5, 1)),
                (Ore, Vec2(35, 17), 8, Vec2(0.5, 1)),
            )
            for x, y in itertools.product(range(100), range(20)):
                for ore_kind, loc, radius, transformation in ore_spawn_info:
                    there = Vec2(x, y)
                    rel = there - loc
                    transformed = rel * transformation
                    if transformed.length() <= radius:
                        voxel = ore_kind(x=x, y=y)
                        continue
                voxel = RandVoxel(x=x+18, y=y+5)
            for x, y in itertools.product(range(20), range(5)):
                voxel = RandVoxel(x=x, y=y+10)
        else:
            debug("[Net] Loading world")
            req = networking.Request("LOAD_WORLD")
            self.send(req)
            # freeze until world is loaded
            self.world_loaded = False
            while not self.world_loaded:
                self._update_socket()
                self.screen.clear()
                self.screen.render(Texture._instances)
                self.screen.show()
            req = networking.Request("PLAYER_JOIN", ["SEND", *self.player.get_global_position().to_tuple()])
            self.send(req)
    
    def _on_response(self, response: networking.Response) -> None:
        match response:
            case networking.Response(kind="LOAD_WORLD"):
                for uid, node in Node.nodes.items():
                    if isinstance(node, self.LOAD_TYPES) and isinstance(node, Transform2D) and not isinstance(node, self.EXCLUDED_LOAD_TYPES):
                        req = networking.Request("CREATE", [node.name, uid, *node.get_global_position().to_tuple()])
                        self.send(req)
                req = networking.Request("LOAD_WORLD_FINISHED")
                self.send(req)
            
            case networking.Response(kind="LOAD_WORLD_FINISHED"):
                self.world_loaded = True
            
            case networking.Response(kind="CREATE", data=[node_type, peer_uid, x, y]):
                debug("Remote Create:", node_type)
                node_class = globals()[node_type]
                instance = node_class(x=float(x), y=float(y)) # type: Node2D  # type: ignore
                instance.peer_uid = peer_uid # type: ignore
                req = networking.Request("SET_PEER_UID", [peer_uid, instance.uid])
                self.send(req)
                # DEBUG
                if isinstance(instance, Actor):
                    instance.uid_bar.text = f"({(instance.uid).center(3)})"
            
            case networking.Response(kind="DELETE", data=[uid]):
                debug("RUID destroy:", Node.nodes[uid])
                Node.nodes[uid].queue_free()
            
            case networking.Response(kind="DELETE_IF_ALIVE", data=[uid]):
                if uid in Node.nodes:
                    # debug("Remote destroy:", Node.nodes[uid])
                    Node.nodes[uid].queue_free()
            
            case networking.Response(kind="SET_PEER_UID", data=[this_uid, extern_uid]):
                node = Node.nodes[this_uid]
                node.peer_uid = extern_uid # type: ignore
            
            case networking.Response(kind="MOVE", data=[uid, x, y]):
                new_position = Vec2(float(x), float(y))
                instance = Node.nodes[uid] # type: Node2D  # type: ignore
                instance.set_global_position(new_position)
                ...
            
            case networking.Response(kind="CREATE_SHELL", data=[shell_type, peer_uid, x, y, tx, ty, sx, sy, c1, c2, c3, c4, c5, c6]):
                x, y, tx, ty, sx, sy = map(float, (x, y, tx, ty, sx, sy))
                # debug("Remote Create Shell:", shell_type)
                shell_class = globals()[shell_type]
                instance = shell_class(x=x, y=y) # type: Shell
                instance.peer_uid = peer_uid # type: ignore
                instance.target = Vec2(tx, ty)
                instance.speed = Vec2(sx, sy)
                instance.texture = [
                    [c1, c2, c3],
                    [c4, c5, c6]
                ]
                req = networking.Request("SET_PEER_UID", [peer_uid, instance.uid])
                self.send(req)
            
            case networking.Response(kind="PLAYER_JOIN", data=[status, x, y]):
                loc = Vec2(int(x), int(y))
                self.other_player.set_global_position(loc)
                self.other_player.show()
                if status == "SEND":
                    req = networking.Request("PLAYER_JOIN", data=["RETURN", *self.player.get_global_position().to_tuple()])
                    self.send(req)

            # case networking.Response(kind="SPAWN", data=[thing, x, y]):
            #     x, y = map(int, (x, y))
            #     debug(f"[Spawn] {thing} at {x},{y}")
            #     class_object = globals()[thing]
            #     new_thing = class_object(x=x, y=y, texture=["!"], color=color.CORAL) # spawn
            #     new_thing.position += Vec2(2, 0)

            # case networking.Response(kind="TAKE_DAMAGE", data=[source, target, amount]):
            #     debug(f"[Take Damage] {source} dealt {amount} damage to {target}")
            #     actor = Node.nodes[target]
            #     assert isinstance(actor, Actor)
            #     actor.health -= int(amount)
    
    def _update(self, _delta: float) -> None:
        # Camera.current.set_global_position(Camera.current.get_global_position().lerp(self.player.get_global_position(), 0.20))
        Camera.current.set_global_position(self.player.get_global_position())
        debug("Req", len(self._queued_requests))
        debug("Ans", len(self._queued_responses))

        # if keyboard.is_pressed("shift"):
        #     self.player.position = Vec2(
        #         random.randint(5, 12),
        #         random.randint(4, 6),
        #     )
        if hasattr(self.player, "peer_uid"): # FIXME: bind peer uid for original too!
            uid = self.player.peer_uid # type: ignore
            req = networking.Request("MOVE", [uid, *self.player.get_global_position().to_tuple()])
            self.send(req)
        
        if keyboard.is_pressed("r"):
            self.reload_world()
    
    def reload_world(self):
        self.player.set_global_position(Vec2(25, -5))
        self.player.can_move = True
        for node in Node.nodes.values():
            if any(isinstance(node, kind) for kind in (Voxel, Tree, Explosive, Mortar, Particle)):
                node.queue_free()
        # ===
        trees = (
            # Vec2(35, 4),
            # Vec2(45, 4)
            Vec2(random.randint(35, 100), 4) for _ in range(random.randint(5, 8))
        )
        for loc in trees:
            tree = Tree(x=loc.x, y=loc.y)
        ore_spawn_info = (
            (Ore, Vec2(78, 13), 5, Vec2(0.5, 1)),
            (Ore, Vec2(35, 17), 8, Vec2(0.5, 1)),
        )
        for x, y in itertools.product(range(100), range(20)):
            for ore_kind, loc, radius, transformation in ore_spawn_info:
                there = Vec2(x, y)
                rel = there - loc
                transformed = rel * transformation
                if transformed.length() <= radius:
                    voxel = ore_kind(x=x, y=y)
                    continue
            voxel = RandVoxel(x=x+18, y=y+5)
        for x, y in itertools.product(range(20), range(5)):
            voxel = RandVoxel(x=x, y=y+10)
        

if __name__ == "__main__":
    echo_peer = App(port=8080, peer_port=7979, auto_resize_screen=True)
