import re
import math
import scenic
import itertools
from verifai.samplers import ScenicSampler

class SubScenario():
    def __init__(self, sampler, id, neighbors=[]):
        self.sampler = sampler
        self.id = id
        self.nexts = list(neighbors)

class CompositionalScenicSampler():
    def __init__(self, init_sub_scenarios):
        self.init_sub_scenarios = init_sub_scenarios

    @classmethod
    def fromScenario(cls, path, maxIterations=None, ignoredProperties=None, is_compositional=False, **kwargs):
        with open(path, "r") as file:
            code = file.read()
        return cls.fromScenicCode(code=code, maxIterations=maxIterations, ignoredProperties=ignoredProperties, is_compositional=True, **kwargs)

    @classmethod
    def fromScenicCode(cls, code, maxIterations=None, ignoredProperties=None, is_compositional=False, **kwargs):
        # Assumption: Compose block only consists of do statements.
        # Assumption: Main scenario is the last one in the file
        init_sub_scenarios = []
        code_lines = list(filter(lambda line: not line.lstrip().startswith("#"), code.split("\n")))
        found_main = False
        found_first_sub_scenarios = False
        compose_line_idx = None
        precondition_line_idx = None
        id_counter = 0
        previous_sub_scenarios = []
        for line_idx in range(len(code_lines)):
            line = code_lines[line_idx]
            if not found_main:
                line_list = line.split()
                if len(line_list) > 1 and line_list[0] == "scenario" and line_list[1] == "Main():":
                    found_main = True
            else:
                if line.lstrip().startswith("compose"):
                    compose_line_idx = line_idx
                if line.lstrip().startswith("precondition"):
                    precondition_line_idx = line_idx
                if line.lstrip().startswith("do"):
                    line_list = line.split()
                    sub_scenario_weight_tuple_list = None
                    if len(line_list) > 1 and line_list[0] == "do" and line_list[1] == "choose":
                        sub_scenario_weight_tuple_list, id_counter = cls._visit_do_choose(line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, id_counter)
                    elif len(line_list) > 1 and line_list[0] == "do" and line_list[1] == "shuffle":
                        sub_scenario_weight_tuple_list, id_counter = cls._visit_do_shuffle(line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, id_counter)
                    else:
                        sub_scenario_weight_tuple_list, id_counter = cls._visit_do(line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, found_first_sub_scenarios, id_counter)
                    if sub_scenario_weight_tuple_list is not None:
                        for sub_scenario, weight in sub_scenario_weight_tuple_list:
                            if not found_first_sub_scenarios:
                                init_sub_scenarios.append((sub_scenario, 1.0))
                            for previous_sub_scenario in previous_sub_scenarios:
                                previous_sub_scenario.nexts.append((sub_scenario, weight))
                        found_first_sub_scenarios = True
                        previous_sub_scenarios = list([sub_scenario_weight_tuple[0] for sub_scenario_weight_tuple in sub_scenario_weight_tuple_list])
        return cls(init_sub_scenarios=init_sub_scenarios)

    @classmethod
    def _visit_do_choose(cls, line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, id_counter):
        line_list = line.split()
        sub_scenario_weight_tuple_list = []
        choose_scenarios_str = " ".join(line_list[2:]).replace("{", "").replace("}", "")
        choose_scenarios_str_list = re.split(r',\s*(?![^()]*\))', choose_scenarios_str)
        for choose_scenario_str in choose_scenarios_str_list:
            weight = 1.0
            if ":" in choose_scenario_str:
                choose_scenario_str, weight = choose_scenario_str.split(":")
                weight = float(weight)
            # TODO: Fix tabs
            partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + ["        do " + choose_scenario_str])
            scenario = scenic.scenarioFromString(partial_code, **kwargs)
            sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
            sub_scenario = SubScenario(id=id_counter, sampler=sampler)
            id_counter += 1
            sub_scenario_weight_tuple_list.append((sub_scenario, weight))
        weight_sum = sum([sub_scenario_weight_tuple[1] for sub_scenario_weight_tuple in sub_scenario_weight_tuple_list])
        return [(sub_scenario, weight/weight_sum) for sub_scenario, weight in sub_scenario_weight_tuple_list], id_counter

    @classmethod
    def _visit_do_shuffle(cls, line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, id_counter):
        line_list = line.split()
        sub_scenario_weight_tuple_list = []
        shuffle_scenarios_str = " ".join(line_list[2:]).replace("{", "").replace("}", "")
        shuffle_scenarios_str_list = re.split(r',\s*(?![^()]*\))', shuffle_scenarios_str)
        shuffle_scenario_str_weight_tuple_list = []
        for shuffle_scenario_str in shuffle_scenarios_str_list:
            weight = 1.0
            if ":" in shuffle_scenario_str:
                shuffle_scenario_str, weight = shuffle_scenario_str.split(":")
                weight = float(weight)
            shuffle_scenario_str_weight_tuple_list.append((shuffle_scenario_str, weight))
        n_perm = math.perm(len(shuffle_scenario_str_weight_tuple_list))
        for shuffle_scenario_str_weight_tuple_permutation in itertools.permutations(shuffle_scenario_str_weight_tuple_list):
            # TODO: Fix tabs
            partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + ["        do " + shuffle_scenario_str for shuffle_scenario_str, weight in shuffle_scenario_str_weight_tuple_permutation])
            scenario = scenic.scenarioFromString(partial_code, **kwargs)
            sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
            sub_scenario = SubScenario(id=id_counter, sampler=sampler)
            id_counter += 1
            # TODO: Compute exact probabilities later
            sub_scenario_weight_tuple_list.append((sub_scenario, 1.0/n_perm))
        return sub_scenario_weight_tuple_list, id_counter

    @classmethod
    def _visit_do(cls, line, code_lines, compose_line_idx, precondition_line_idx, maxIterations, ignoredProperties, kwargs, found_first_sub_scenarios, id_counter):
        if not found_first_sub_scenarios == []:
            partial_code = "\n".join(code_lines[:compose_line_idx + 1] + [line])
        else:
            partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + [line])
        scenario = scenic.scenarioFromString(partial_code, **kwargs)
        sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
        sub_scenario = SubScenario(id=id_counter, sampler=sampler)
        id_counter += 1
        return [(sub_scenario, 1.0)], id_counter







