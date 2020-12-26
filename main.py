from phoenyx import Engine
from population import Population

WIDTH, HEIGHT = 1100, 650
GETINFO = True
FPS = 60
N = 50
renderer = Engine(WIDTH, HEIGHT)

pop: Population
speed, radius, max_force = 0, 0, 0


def setup() -> None:
    global pop
    global speed, radius, max_force
    renderer.fps = FPS

    pop = Population(renderer, (WIDTH, HEIGHT), N)

    renderer.create_slider(WIDTH - 150, HEIGHT - 150, "alignment", 0, 2, 1, 1)
    renderer.create_slider(WIDTH - 150, HEIGHT - 110, "cohesion", 0, 2, 1, 1)
    renderer.create_slider(WIDTH - 150, HEIGHT - 70, "separation", 0, 2, 1.2, 1)

    renderer.text_size = 15

    speed = pop.pop.sprites()[0].SPEED
    radius = pop.pop.sprites()[0].RADIUS
    max_force = pop.pop.sprites()[0].MAXFORCE


def draw() -> None:
    global pop
    global speed, radius, max_force

    fps = renderer.fps
    a = renderer.get_slider_value("alignment")
    b = renderer.get_slider_value("cohesion")
    c = renderer.get_slider_value("separation")
    mates, vel, brute, modified = pop.update(a, b, c)

    renderer.background((60, 70, 80))
    pop.qt.show()
    pop.show()

    if GETINFO:
        renderer.text(10, 10, f"fps : {round(fps)}")
        renderer.text(10, 20, f"total boids : {N}")
        renderer.text(10, 30, f"average local flockmates : {round(mates / N, 1)}")
        renderer.text(10, 40, f"perception radius : {radius}")
        renderer.text(10, 50, f"max velocity : {speed}")
        renderer.text(10, 60, f"average velocity : {round(vel/N, 2)}")
        renderer.text(10, 70, f"max brute force : {round(3 * max_force, 3)}")
        renderer.text(10, 80, f"average brute force : {round(brute / N, 3)}")
        renderer.text(10, 90, f"modified/brute ratio : {round(modified / brute, 3)}")


if __name__ == "__main__":
    renderer.run(draw, setup=setup)
