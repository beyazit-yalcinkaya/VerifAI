from scenic.simulators.webots.model import WebotsObject

model scenic.simulators.webots.model

import numpy as np

class Lead(WebotsObject):
    webotsName: "LEAD"

class Follower(WebotsObject):
    webotsName: "FOLLOWER"

class Obstacle(WebotsObject):
    webotsName: "OBSTACLE"
    color: Options([[0.0, 0.0, 0.0],
                    [0.5, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 0.5, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.5],
                    [0.0, 0.0, 1.0],
                    [0.5, 0.5, 0.5],
                    [1.0, 1.0, 1.0]])

class OilBarrel1(WebotsObject):
    webotsName: "OIL_BARREL_1"

class OilBarrel2(WebotsObject):
    webotsName: "OIL_BARREL_2"

class OilBarrel3(WebotsObject):
    webotsName: "OIL_BARREL_3"

scenario SubScenario2L():
    setup:
        x_space = list(np.linspace(10.5, 25.5, num=100))
        y_space = list(np.linspace(-54.5, -51.5, num=50)) + list(np.linspace(-38.5, -35.5, num=50))
        obstacle = new Obstacle at Uniform(*x_space) @ Uniform(*y_space)

scenario SubScenario2S():
    setup:
        x_space = list(np.linspace(35.5, 38.5, num=50)) + list(np.linspace(51.5, 54.5, num=50))
        y_space = list(np.linspace(-25.5, -10.5, num=100))
        obstacle = new Obstacle at Uniform(*x_space) @ Uniform(*y_space)

scenario SubScenario2R():
    setup:
        x_space = list(np.linspace(57.0, 67.0, num=100))
        y_space = list(np.linspace(-54.5, -51.5, num=50)) + list(np.linspace(-38.5, -35.5, num=50))
        obstacle = new Obstacle at Uniform(*x_space) @ Uniform(*y_space)

scenario SubScenario1():
    setup:
        oil_barrel_1 = new OilBarrel1 at Range(-30.0, -10.0) @ Range(-115.0, -95.0)
        oil_barrel_2 = new OilBarrel2 at Range(-10.0, 10.0) @ Range(-115.0, -95.0)
        oil_barrel_3 = new OilBarrel3 at Range(10.0, 30.0) @ Range(-115.0, -95.0)

scenario Main():
    setup:
        lead = new Lead at Range(-56.5, -52.5) @ Range(-106, -104), facing Range(-5.0, 5.0) deg
        ego = new Follower at Range(-66.5, -62.5) @ Range(-106, -104), facing Range(-5.0, 5.0) deg
    compose:
        do SubScenario1() until ego.position[1] >= -78.5 or lead.position[1] > -68.5
        do choose SubScenario1(), SubScenario2L(), SubScenario2S(), SubScenario2R()








