import re
import math
import scenic
import itertools
from verifai.samplers import ScenicSampler

class SubScenario():
    def __init__(self, sampler, id, previous_sub_scenarios=[], next_sub_scenarios=[]):
        self.sampler = sampler
        self.id = id
        self.previous_sub_scenarios = list(previous_sub_scenarios)
        self.next_sub_scenarios = list(next_sub_scenarios)
        self.falsifier = None
        self.last_states = []

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
        # Assumption: `ego` is declared in the setup block of main scenario.
        code_lines = list(filter(lambda line: not line.lstrip().startswith("#"), code.split("\n")))
        main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx = cls._find_indices(code_lines)
        init_sub_scenarios = []
        id_counter = 0
        previous_sub_scenarios = []
        for line_idx in range(main_start_line_idx, main_end_line_idx):
            line = code_lines[line_idx]
            if line.lstrip().startswith("do"):
                sub_scenario_weight_tuple_list, id_counter = cls._visit_do_statements(code_lines, line_idx, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, init_sub_scenarios != [], id_counter, maxIterations, ignoredProperties, kwargs)
                if sub_scenario_weight_tuple_list is not None:
                    if init_sub_scenarios == []:
                        init_sub_scenarios.extend([(sub_scenario, 1.0) for sub_scenario, _ in sub_scenario_weight_tuple_list])
                    else:
                        for previous_sub_scenario in previous_sub_scenarios:
                            previous_sub_scenario.next_sub_scenarios.extend(sub_scenario_weight_tuple_list)
                        for sub_scenario, _ in sub_scenario_weight_tuple_list:
                            sub_scenario.previous_sub_scenarios.extend(previous_sub_scenarios)
                    previous_sub_scenarios = list([sub_scenario for sub_scenario, _ in sub_scenario_weight_tuple_list])
        return cls(init_sub_scenarios=init_sub_scenarios)

    @classmethod
    def _visit_do_statements(cls, code_lines, line_idx, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs):
        line = code_lines[line_idx]
        line_list = line.split()
        sub_scenario_weight_tuple_list = None
        if len(line_list) > 1 and line_list[0] == "do" and line_list[1] == "choose":
            sub_scenario_weight_tuple_list, id_counter = cls._visit_do_choose(line_list, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs)
        elif len(line_list) > 1 and line_list[0] == "do" and line_list[1] == "shuffle":
            sub_scenario_weight_tuple_list, id_counter = cls._visit_do_shuffle(line_list, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs)
        else:
            sub_scenario_weight_tuple_list, id_counter = cls._visit_do(line, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs)
        return sub_scenario_weight_tuple_list, id_counter

    @classmethod
    def _find_indices(cls, code_lines):
        main_start_line_idx = None
        precondition_line_idx = None
        invariant_line_idx = None
        setup_line_idx = None
        compose_line_idx = None
        main_end_line_idx = None
        for line_idx in range(len(code_lines)):
            line = code_lines[line_idx]
            if not main_start_line_idx:
                line_list = line.split()
                if len(line_list) > 1 and line_list[0] == "scenario" and line_list[1] == "Main():":
                    main_start_line_idx = line_idx
            else:
                if line.lstrip().startswith("precondition"):
                    precondition_line_idx = line_idx
                elif line.lstrip().startswith("invariant"):
                    invariant_line_idx = line_idx
                elif line.lstrip().startswith("setup"):
                    setup_line_idx = line_idx
                elif line.lstrip().startswith("compose"):
                    compose_line_idx = line_idx
                elif compose_line_idx and not line.lstrip().startswith("do"):
                    main_end_line_idx = line_idx
                    break
        assert main_start_line_idx is not None
        assert main_end_line_idx is not None
        assert (precondition_line_idx is None) or (main_start_line_idx < precondition_line_idx)
        assert (invariant_line_idx is None) or (main_start_line_idx < invariant_line_idx)
        assert (precondition_line_idx is None or setup_line_idx is None) or (precondition_line_idx < setup_line_idx)
        assert (invariant_line_idx is None or setup_line_idx is None) or (invariant_line_idx < setup_line_idx)
        assert (setup_line_idx is None or compose_line_idx is None) or (setup_line_idx < compose_line_idx)
        assert (compose_line_idx is None) or (compose_line_idx < main_end_line_idx)
        return main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx

    @classmethod
    def _visit_do_choose(cls, line_list, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs):
        sub_scenario_weight_tuple_list = []
        choose_scenarios_str = " ".join(line_list[2:]).replace("{", "").replace("}", "")
        choose_scenarios_str_list = re.split(r',\s*(?![^()]*\))', choose_scenarios_str)
        for choose_scenario_str in choose_scenarios_str_list:
            weight = 1.0
            if ":" in choose_scenario_str:
                choose_scenario_str, weight = choose_scenario_str.split(":")
                weight = float(weight)
            # TODO: Fix tabs
            if found_first_sub_scenarios and precondition_line_idx:
                # Do not include precondition line and setup lines
                # partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + ["        do " + choose_scenario_str] + code_lines[main_end_line_idx:])
                partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:setup_line_idx + 1] + ["        ego = new Object"] + code_lines[compose_line_idx: compose_line_idx + 1] + ["        do " + choose_scenario_str] + code_lines[main_end_line_idx:])
            else:
                # Include precondition line and setup lines
                partial_code = "\n".join(code_lines[:compose_line_idx + 1] + ["        do " + choose_scenario_str] + code_lines[main_end_line_idx:])
            scenario = scenic.scenarioFromString(partial_code, **kwargs)
            sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
            sub_scenario = SubScenario(id=choose_scenario_str, sampler=sampler)
            id_counter += 1
            sub_scenario_weight_tuple_list.append((sub_scenario, weight))
        weight_sum = sum([sub_scenario_weight_tuple[1] for sub_scenario_weight_tuple in sub_scenario_weight_tuple_list])
        return [(sub_scenario, weight/weight_sum) for sub_scenario, weight in sub_scenario_weight_tuple_list], id_counter

    @classmethod
    def _visit_do_shuffle(cls, line_list, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs):
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
            if found_first_sub_scenarios and precondition_line_idx:
                # Do not include precondition line and setup lines
                # partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + ["        do " + shuffle_scenario_str for shuffle_scenario_str, weight in shuffle_scenario_str_weight_tuple_permutation] + code_lines[main_end_line_idx:])
                partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:setup_line_idx + 1] + ["        ego = new Object"] + code_lines[compose_line_idx:compose_line_idx + 1] + ["        do " + shuffle_scenario_str for shuffle_scenario_str, weight in shuffle_scenario_str_weight_tuple_permutation] + code_lines[main_end_line_idx:])
            else:
                # Include precondition line and setup lines
                partial_code = "\n".join(code_lines[:compose_line_idx + 1] + ["        do " + shuffle_scenario_str for shuffle_scenario_str, weight in shuffle_scenario_str_weight_tuple_permutation] + code_lines[main_end_line_idx:])
            scenario = scenic.scenarioFromString(partial_code, **kwargs)
            sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
            sub_scenario = SubScenario(id=shuffle_scenario_str, sampler=sampler)
            id_counter += 1
            # TODO: Compute exact probabilities later
            sub_scenario_weight_tuple_list.append((sub_scenario, 1.0/n_perm))
        return sub_scenario_weight_tuple_list, id_counter

    @classmethod
    def _visit_do(cls, line, code_lines, main_start_line_idx, precondition_line_idx, setup_line_idx, compose_line_idx, main_end_line_idx, found_first_sub_scenarios, id_counter, maxIterations, ignoredProperties, kwargs):
        if found_first_sub_scenarios and precondition_line_idx:
            # Do not include precondition line and setup lines
            # partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:compose_line_idx + 1] + [line] + code_lines[main_end_line_idx:])
            partial_code = "\n".join(code_lines[:precondition_line_idx] + code_lines[precondition_line_idx + 1:setup_line_idx + 1] + ["        ego = new Object"] + code_lines[compose_line_idx:compose_line_idx + 1] + [line] + code_lines[main_end_line_idx:])
        else:
            # Include precondition line and setup lines
            partial_code = "\n".join(code_lines[:compose_line_idx + 1] + [line] + code_lines[main_end_line_idx:])
        scenario = scenic.scenarioFromString(partial_code, **kwargs)
        sampler = ScenicSampler(scenario, maxIterations=maxIterations, ignoredProperties=ignoredProperties)
        sub_scenario = SubScenario(id=line.split()[1], sampler=sampler)
        id_counter += 1
        return [(sub_scenario, 1.0)], id_counter

