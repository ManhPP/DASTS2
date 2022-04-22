import json
import random
from collections import deque
from copy import deepcopy

from src.ts.ts_utils import TSUtils


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

    def __init__(self, inp, config, initial_state, tabu_size, max_steps):
        """

        :param initial_state:
        :param tabu_size:
        :param max_steps:
        """
        self.config = config
        self.inp = inp
        self.penalty_params = self.config.tabu_params

        self.utils = TSUtils(config, inp)
        self.actions = list(self.utils.action.keys())

        if initial_state is None:
            initial_state = self.init_solution()
        self.initial_state = initial_state

        if isinstance(tabu_size, int) and tabu_size > 0:
            self.tabu_size = tabu_size
        else:
            raise TypeError('Tabu size must be a positive integer')

        if isinstance(max_steps, int) and max_steps > 0:
            self.max_steps = max_steps
        else:
            raise TypeError('Maximum steps must be a positive integer')

    def init_solution(self):
        num_cus = self.inp["num_cus"]
        num_staff = self.config.params["num_staff"]
        num_drone = self.config.params["num_drone"]
        L_w = self.config.params["L_w"]
        L_d = self.config.params["L_d"]

        tau_a = self.inp["tau_a"]

        C1 = self.inp["C1"]
        tmp = [i for i in range(1, num_cus + 1) if i not in C1]

        random.shuffle(tmp)
        solution = []

        for i in range(num_drone + num_staff - 1):
            tmp.insert(random.randint(0, len(tmp) + 1), 0)

        indices = [i for i, x in enumerate(tmp) if x == 0]

        for i in C1:
            tmp.insert(random.randint(indices[num_drone - 1] + 1, len(tmp) + 1), i)

        trip = []
        for i in tmp:
            if i != 0:
                trip.append(i)
            else:
                solution.append(trip)
                trip = []

        solution.append(trip)
        for i in range(num_drone):
            if len(solution[i]) == 0:
                continue
            t_d = 0
            t_w = -tau_a[0, solution[i][0]]
            prev = 0
            new_trip = []
            sub_trip = []
            for ind, cus in enumerate(solution[i]):
                if t_d + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_d \
                        or t_w + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_w:
                    t_d = 0
                    t_w = -tau_a[0, solution[i][ind]]
                    prev = 0
                    new_trip.append(sub_trip)
                    sub_trip = [cus]
                else:
                    t_d += tau_a[prev, cus]
                    t_w += tau_a[prev, cus]
                    prev = cus
                    sub_trip.append(cus)
            new_trip.append(sub_trip)
            solution[i] = new_trip

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
        act = random.choice(self.actions)

        return act, self.utils.get_all_neighbors(self.current, act)

    def _best(self, neighborhood):
        """
        Finds the best member of a neighborhood

        :param neighborhood:
        :return:
        """

        return min(neighborhood.items(), key=lambda x: self._score(x[1]))

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

    def run(self, verbose=True):
        """
        Conducts tabu search

        :param verbose:
        :return:
        """

        r = {}
        self._clear()
        for _ in range(self.max_steps):
            self.cur_steps += 1
            if verbose:
                print(
                    f"Step: {self.cur_steps} - Best: {self._score(self.best)} - Step Best: {self._score(self.current)}")
            act, neighborhood = self._neighborhood()
            ext, neighborhood_best = self._best(neighborhood)
            tabu_list = self.tabu_dict[act]

            cur = self.current

            while True:

                if all([x in tabu_list for x in neighborhood]):
                    print("TERMINATING - NO SUITABLE NEIGHBORS")
                    return self.best, self._score(self.best)

                step_best_info = self._score(neighborhood_best, True)
                best_score = self._score(self.best)

                if ext in tabu_list:
                    if step_best_info[0] < best_score:
                        self.current = neighborhood_best
                        self.update_penalty_param(step_best_info[1], step_best_info[2])
                        self.best = deepcopy(neighborhood_best)
                        tabu_list.append(ext)
                        r[self.cur_steps] = {"best": f"{self._score(self.best)} - {self.best}",
                                             "old_current": f"{self._score(cur)} - {cur}",
                                             "current": f"{self._score(self.current)} - {self.current}",
                                             "action": act,
                                             "ext": str(ext),
                                             "tb:": str(self.tabu_dict),
                                             "t": 1}
                        break
                    else:
                        neighborhood.pop(ext)
                        ext, neighborhood_best = self._best(neighborhood)
                else:
                    self.current = neighborhood_best
                    current_info = self._score(self.current, True)
                    tabu_list.append(ext)
                    if current_info[0] < best_score:
                        self.best = deepcopy(self.current)
                        self.update_penalty_param(current_info[1], current_info[2])
                    r[self.cur_steps] = {"best": f"{self._score(self.best)} - {self.best}",
                                         "old_current": f"{self._score(cur)} - {cur}",
                                         "current": f"{self._score(self.current)} - {self.current}",
                                         "action": act,
                                         "ext": str(ext),
                                         "tb:": str(self.tabu_dict),
                                         "t": 2}
                    break
        print("TERMINATING - REACHED MAXIMUM STEPS")
        if verbose:
            print(self)
        print(self.initial_state)

        with open('result.json', 'w') as json_file:
            json.dump(r, json_file, indent=2)
        return self.best, self._score(self.best)
