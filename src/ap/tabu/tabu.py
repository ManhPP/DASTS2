import json
import os
import random
import timeit
from collections import deque
from copy import deepcopy

from src.ap.ap_utils import APUtils
from src.ap.init_solution import init_by_distance, init_by_angle, init_random
from src.utils import make_dirs_if_not_present


class TabuSearch:
    """
    Conducts tabu search
    """
    cur_steps = None

    tabu_size = None
    tabu_dict = None

    initial_state = None
    current = None
    best = None

    max_steps = None

    cache = {}

    def __init__(self, inp, config, initial_state, tabu_size, max_steps, ext=0):
        """

        :param initial_state:
        :param tabu_size:
        :param max_steps:
        """
        self.init_info = "random"
        self.config = config
        self.inp = inp
        self.penalty_params = self.config.tabu_params
        self.ext = ext
        self.utils = APUtils(config, inp)
        self.actions = list(self.utils.action.keys())
        self.action_weights = None
        if self.config.tabu_params.use_weights:
            self.action_weights = []
            for a in self.actions:
                self.action_weights.append(self.config.tabu_params.action_weights[a])
        self.action_order = self.config.tabu_params.action_order[:]
        if initial_state is None:
            initial_state = self.init_solution_heuristic()
        self.initial_state = initial_state

        if isinstance(tabu_size, int) and tabu_size > 0:
            self.tabu_size = tabu_size
        else:
            raise TypeError('Tabu size must be a positive integer')

        if isinstance(max_steps, int) and max_steps > 0:
            self.max_steps = max_steps
        else:
            raise TypeError('Maximum steps must be a positive integer')

    def init_solution_heuristic(self):
        solution = init_random(self.inp, self.config)
        for reverse in [True, False]:
            s = init_by_distance(self.inp, self.config, reverse=reverse)
            print(s)
            print(self._score(s))
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"distance-reversed: {reverse}"

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=1)
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"angle-reversed: {reverse}-direction: 1"

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=-1)
            if s is not None and self._score(s) < self._score(solution):
                solution = s
                self.init_info = f"angle-reversed: {reverse}-direction: -1"

        return solution

    def __str__(self):
        return ('TABU SEARCH: \n' +
                'CURRENT STEPS: %d \n' +
                'BEST SCORE: %f \n' +
                'BEST MEMBER: %s \n\n') % \
               (self.cur_steps, self._score(self.best), str(self.best))

    def __repr__(self):
        return self.__str__()

    def _clear(self):
        """
        Resets the variables that are altered on a per-run basis of the algorithm

        :return:
        """
        self.cur_steps = 0
        self.tabu_dict = {}
        for act in self.actions:
            self.tabu_dict[act] = deque(maxlen=self.tabu_size)
        self.current = self.initial_state
        self.best = self.initial_state
        self.cache["order_neighbor"] = []
        self.cache["temp_sol"] = []

    def _score(self, state, return_all=False):
        """
        Returns objective function value of a state

        :param state:
        :return:
        """
        if return_all:
            return self.utils.get_score(state, self.penalty_params)
        return self.utils.get_score(state, self.penalty_params)[0]

    def _neighborhood(self):
        """
        Returns list of all members of neighborhood of current state, given self.current

        :return:
        """
        result = None
        act = None
        while result is None:
            act = random.choices(self.actions, weights=self.action_weights)[0]
            if not self.config.tabu_params.use_weights:
                act = self.action_order.pop(0)

                if len(self.action_order) == 0:
                    self.action_order = self.config.tabu_params.action_order[:]

            print(f"act - {act}")
            result = self.utils.get_all_neighbors(self.current, act,
                                                  self._score(self.best),
                                                  self.penalty_params,
                                                  self.tabu_dict[act])

        return act, result

    def _best(self, neighborhood, reset=False):
        """
        Finds the best member of a neighborhood

        :param neighborhood:
        :return:
        """

        if reset:
            self.cache["order_neighbor"] = sorted(neighborhood.items(), key=lambda x: self._score(x[1]))

        if len(self.cache["order_neighbor"]) > 0:
            return self.cache["order_neighbor"].pop(0)
        return None, None

    def update_penalty_param(self, dz, cz):
        alpha1 = self.penalty_params.get("alpha1", 0)
        alpha2 = self.penalty_params.get("alpha2", 0)
        beta = self.penalty_params.get("beta", 0)

        if dz > 0:
            self.penalty_params["alpha1"] = alpha1 * (1 + beta)
        else:
            self.penalty_params["alpha1"] = alpha1 / (1 + beta)

        if cz > 0:
            self.penalty_params["alpha2"] = alpha2 * (1 + beta)
        else:
            self.penalty_params["alpha2"] = alpha2 / (1 + beta)

    def run_tabu(self, verbose=False):
        """
        Conducts tabu search

        :param verbose:
        :return:
        """

        r = {}
        self._clear()
        not_improve_iter = 0

        for _ in range(self.max_steps):
            previous_best = self.best
            self.cache["order_neighbor"] = []
            self.cur_steps += 1
            if verbose:
                print(
                    f"Step: {self.cur_steps} - Best: {self._score(self.best, True)} "
                    f"- Step Best: {self._score(self.current, True)}")

                print(f"{self.current}")
            act, neighborhood = self._neighborhood()

            ext, neighborhood_best = neighborhood
            tabu_list = self.tabu_dict[act]

            cur = self.current

            best_score = self._score(self.best)

            self.current = neighborhood_best

            current_info = self._score(self.current, True)
            tabu_list.append(self.utils.get_tabu(act, ext))
            if current_info[0] < best_score:
                self.best = deepcopy(self.current)
                self.cache['temp_sol'].append(self.best)
                self.update_penalty_param(current_info[1], current_info[2])
            r[self.cur_steps] = {"best": f"{self._score(self.best)} - {self.best}",
                                 "old_current": f"{self._score(cur)} - {cur}",
                                 "current": f"{self._score(self.current)} - {self.current}",
                                 "action": act,
                                 "ext": str(self.utils.get_tabu(act, ext))}

            if self.best == previous_best:
                not_improve_iter += 1
            if not_improve_iter > self.config.tabu_params.terminate_iter:
                print("TERMINATING TABU - REACHED MAXIMUM NOT IMPROVE STEPS")
                break

        print("TERMINATING TABU - REACHED MAXIMUM STEPS")
        if verbose:
            print(self)
        print(self.initial_state)

        # with open('result.json', 'w') as json_file:
        #     json.dump(r, json_file, indent=2)

        return {"tabu-sol": str(self.best), "tabu-score": str(self._score(self.best)), "tabu-log": r,
                "step": self.cur_steps}

    def run_post_optimization(self, verbose=True):
        r = {}
        if (self.best is None):
            self.best = self.initial_state
        if self.config.params.use_ejection:
            ejection_log = self.utils.run_ejection(_solution=self.best, return_sol=False)
            r["ejection"] = {"ejection-sol": str(self.best), "ejection-score": str(self._score(self.best)),
                             "ejection-log": ejection_log}
        if self.config.params.use_inter:
            self.utils.run_inter_route(solution=self.best)
            r["inter"] = {"inter-sol": str(self.best), "inter-score": str(self._score(self.best)), "inter-log": {}}

        if self.config.params.use_inter:
            self.utils.run_intra_route(solution=self.best)
            r["intra"] = {"intra-sol": str(self.best), "intra-score": str(self._score(self.best)), "intra-log": {}}

        return r

    def run(self, verbose=True):
        r = {"num_drone": self.config.params.num_drone,
             "num_staff": self.config.params.num_staff,
             "init_info": {"method": self.init_info, "init": str(self.initial_state)}}

        start = timeit.default_timer()

        tabu_info = self.run_tabu(verbose)
        tabu_time = timeit.default_timer() - start
        post_optimization_info = self.run_post_optimization(verbose)
        po_time = timeit.default_timer() - start - tabu_time

        r["time"] = timeit.default_timer() - start
        r["tabu_time"] = tabu_time
        r["po_time"] = po_time
        r["tabu"] = tabu_info
        r.update(post_optimization_info)

        make_dirs_if_not_present(self.config.result_folder)

        with open(os.path.join(self.config.result_folder,
                               'result_' + self.inp['data_set'] + '_' + str(self.ext) + '.json'), 'w') as json_file:
            json.dump(r, json_file, indent=2)
