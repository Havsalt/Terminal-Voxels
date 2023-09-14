from displaylib import * # type: ignore
from displaylib.ascii.prototypes.texture_collider import TextCollider
from displaylib.ascii.prototypes.particles_emitter import Particle
import random
# local imports
from explosive import Explosive


# class ExplosionMaterial(ParticlesMaterial):
#     amount = 20
#     spread = math.radians(45)
#     direction = Vec2(0, -1)
#     colors = (
#         color.YELLOW,
#         color.RED,
#         color.ORANGE
#     )
#     initial_velocity = 80
#     gravity = Vec2(0, -500)
#     lifetime_min = 0.3
#     lifetime_max = 0.4


# class ExplosionParticlesEmitter(ExplosionMaterial, ParticlesEmitter): ...


class ExplosionParticle(Particle):
    direction = Vec2(0, -1)
    acceleration = -57
    speed = direction * 24

    def __init__(self) -> None:
        self.color = color.rand_color()
        self.gravity = self.gravity.copy()
        self.speed = self.speed.copy()


class C4(Sprite, TextCollider, Explosive):
    centered = True
    color = color.CRIMSON
    texture = [[*"[Ӿ]"]]
    fuse_time = 30
    explosion_radius = 8
    frames_elapsed = 0.0
    transformation: Vec2 = Vec2(0.5, 1)
    
    def get_collider(self) -> TextCollider | None:
        here = self.get_global_position()
        if self.centered:
            here -= self.size() // 2
        end = here + self.size()
        for node in Node.nodes.values():
            if node is self or node.name == "Player":
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
            if node is self or node.name == "Player":
                continue
            if isinstance(node, Transform2D) and isinstance(node, TextCollider):
                point = node.get_global_position()
                if here <= point < end:
                    results.append(node)
        return results

    def is_on_floor(self) -> bool:
        self.position.y += 1
        collider = self.get_collider()
        self.position.y -= 1
        return collider is not None

    def _update(self, delta: float) -> None:
        if not self.is_on_floor():
            self.position.y += 1
        self.frames_elapsed += 1
        if self.frames_elapsed >= self.fuse_time:
            self.detonate()
    
    def detonate(self) -> None:
        super().detonate()
        self.queue_free()
        AudioStreamPlayer("./sounds/shotgun_shoot_instant.wav").play()
    
    def _on_node_affected(self, node: Node2D) -> None:
        if node.name == "Player" or node.name == "StaticPlayer" or isinstance(node, Explosive):
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
