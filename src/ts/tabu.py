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

        :param initial_state: initial state, should implement __eq__ or __cmp__
        :param tabu_size: number of states to keep in tabu list
        :param max_steps: maximum number of steps to run algorithm for
        """
        self.config = config
        self.inp = inp

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

        :return: None
        """
        self.cur_steps = 0
        self.tabu_dict = {}
        for act in self.actions:
            self.tabu_dict[act] = deque(maxlen=self.tabu_size)
        self.current = self.initial_state
        self.best = self.initial_state

    def _score(self, state):
        """
        Returns objective function value of a state

        :param state: a state
        :return: objective function value of state
        """
        return self.utils.get_score(state)

    def _neighborhood(self):
        """
        Returns list of all members of neighborhood of current state, given self.current

        :return: list of members of neighborhood
        """
        act = random.choice(self.actions)

        return act, self.utils.get_all_neighbors(self.current, act)

    def _best(self, neighborhood):
        """
        Finds the best member of a neighborhood

        :param neighborhood: a neighborhood
        :return: best member of neighborhood
        """

        return min(neighborhood.items(), key=lambda x: self._score(x[1]))

    def run(self, verbose=True):
        """
        Conducts tabu search

        :param verbose: indicates whether or not to print progress regularly
        :return: best state and objective function value of best state
        """
        self._clear()
        for _ in range(self.max_steps):
            self.cur_steps += 1

            act, neighborhood = self._neighborhood()
            ext, neighborhood_best = self._best(neighborhood)

            tabu_list = self.tabu_dict[act]
            while True:
                if all([x in tabu_list for x in neighborhood.keys()]):
                    print("TERMINATING - NO SUITABLE NEIGHBORS")
                    return self.best, self._score(self.best)
                if ext in tabu_list and self._score(neighborhood_best) < self._score(self.best):
                    tabu_list.append(ext)
                    self.current = neighborhood_best
                    self.best = deepcopy(neighborhood_best)
                    break
                else:
                    tabu_list.append(ext)
                    self.current = neighborhood_best
                    if self._score(self.current) < self._score(self.best):
                        self.best = deepcopy(self.current)
                    break
            if verbose:
                print(f"Step: {self.cur_steps} - Best: {self._score(self.best)} - Step Best: {self._score(self.current)}")
        print("TERMINATING - REACHED MAXIMUM STEPS")
        if verbose:
            print(self)

        return self.best, self._score(self.best)
