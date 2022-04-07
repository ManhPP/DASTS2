import random

from src.ts.ts_utils import TSUtils
from src.ts.tabu import TabuSearch


class DTabu(TabuSearch):
    def __init__(self, inp, config, tabu_size, max_steps, max_score=None):
        self.config = config
        self.inp = inp

        self.utils = TSUtils(config, inp)

        super().__init__(self.init_solution(), tabu_size, max_steps, max_score)

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
                    sub_trip = []
                else:
                    t_d += tau_a[prev, cus]
                    t_w += tau_a[prev, cus]
                    prev = cus
                    sub_trip.append(cus)
            new_trip.append(sub_trip)
            solution[i] = new_trip

        return solution

    def _score(self, state):
        return self.utils.get_score(state)

    def _neighborhood(self):
        return self.utils.get_all_neighbor()


if __name__ == '__main__':
    pass
