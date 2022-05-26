from collections import deque
from copy import deepcopy

from src.ap.init_solution import init_random
from src.ap.tabu.tabu import TabuSearch


class Hybrid(TabuSearch):
    def __init__(self, inp, config, initial_state, tabu_size, max_steps, ext=0):

        super().__init__(inp, config, initial_state, tabu_size, max_steps, ext)
        self.actions = ["move10", "move11", "move21", "move20", "move2opt", "move01", "move02"]

    def init_solution_heuristic(self):
        solution = super().init_solution_heuristic()
        score = self._score(solution, True)
        if score[1] == 0 and score[2] == 0:
            return solution

        while True:
            solution = init_random(self.inp, self.config)
            score = self._score(solution, True)
            if score[1] == 0 and score[2] == 0:
                return solution

    def _neighborhood(self):
        result = {}
        act = None
        while len(result) == 0:
            act = self.actions[self.cur_steps]
            print(f"act - {act}")
            result = self.utils.get_all_neighbors(self.current, act)

        return act, result

    def _clear(self):
        super()._clear()
        for act in ["move10", "move11", "move21", "move20", "move2opt", "move01", "move02"]:
            self.tabu_dict[act] = deque(maxlen=self.tabu_size)

    def run_tabu(self, verbose=True):
        self._clear()

        r = {}
        self.cur_steps = 0
        key_log = 0
        while self.cur_steps < len(self.actions):
            key_log += 1

            self.cache["order_neighbor"] = []
            if verbose:
                print(
                    f"Step: {key_log} - Best: {self._score(self.best, True)} "
                    f"- Step Best: {self._score(self.current, True)}")

                print(f"{self.current}")
            act, neighborhood = self._neighborhood()

            print(f"{act} - {len(neighborhood)}")
            ext, neighborhood_best = self._best(neighborhood, True)
            tabu_list = self.tabu_dict[act]

            cur = self.current
            while True:

                if all([self.get_tabu(act, x) in tabu_list for x in neighborhood]):
                    break

                step_best_info = self._score(neighborhood_best, True)
                best_score = self._score(self.best)

                if self.get_tabu(act, ext) in tabu_list and step_best_info[0] >= best_score:
                    ext, neighborhood_best = self._best(neighborhood)
                    if ext is None:
                        self.cur_steps += 1
                        break
                    else:
                        continue

                tabu_list.append(self.get_tabu(act, ext))

                if step_best_info[0] < self._score(cur):
                    self.current = neighborhood_best

                    self.cur_steps = 0
                else:
                    self.cur_steps += 1

                if step_best_info[1] == 0 and step_best_info[2] == 0 and step_best_info[0] < best_score:
                    self.best = deepcopy(neighborhood_best)
                    self.update_penalty_param(step_best_info[1], step_best_info[2])

                r[key_log] = {"best": f"{self._score(self.best)} - {self.best}",
                              "old_current": f"{self._score(cur)} - {cur}",
                              "current": f"{self._score(self.current)} - {self.current}",
                              "action": act,
                              "ext": str(self.get_tabu(act, ext))}
                break

        print("TERMINATING TABU - REACHED MAXIMUM STEPS")
        if verbose:
            print(self)
        print(self.initial_state)

        return {"tabu-sol": str(self.best), "tabu-score": str(self._score(self.best)), "tabu-log": r}
