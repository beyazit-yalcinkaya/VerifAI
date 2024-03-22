
from verifai.scenic_server import ScenicServer
from dotmap import DotMap
from verifai.falsifier import compositional_falsifier
from verifai.features.features import *
from verifai.monitor import specification_monitor, mtl_specification
from time import sleep
import pickle
import random
import math
import sys
import os
from verifai.samplers import CompositionalScenicSampler

class MyMonitor(specification_monitor):
    def __init__(self):
        self.specification = mtl_specification(["G(distance)"])
        super().__init__(self.specification)

    def evaluate(self, simulation):
        traj = simulation.result.trajectory
        safe_values = []
        for positions in traj:
            ego = positions[0]
            dist = min((ego.distanceTo(other) for other in positions[1:]),
                       default=math.inf)
            safe_values.append(dist - 5)
        eval_dictionary = {'safe' : list(enumerate(safe_values)) }

        # Evaluate MTL formula given values for its atomic propositions
        return self.specification.evaluate(eval_dictionary)

path = os.path.join(os.path.dirname(__file__), 'scenario.scenic')

sampler = CompositionalScenicSampler.fromScenario(path, mode2D=True)

falsifier_params = DotMap(
    n_iters=2,
    verbosity=1,
    save_error_table=True,
    save_safe_table=True
)
server_options = DotMap(maxSteps=100, verbosity=0)

falsifier = compositional_falsifier(sampler=sampler,
                                    monitor=MyMonitor(),
                                    falsifier_params=falsifier_params,
                                    server_class=ScenicServer,
                                    server_options=server_options)
falsifier.run_falsifier()






