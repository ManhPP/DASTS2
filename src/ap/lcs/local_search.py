import random

from src.ap.ap_utils import APUtils
from src.ap.init_solution import init_by_distance, init_by_angle, init_random


class LocalSearch:
    def __init__(self, inp, config):
        self.max_iter = config.local_search_params.max_iter
        self.max_stable = config.local_search_params.max_stable
        self.inp = inp
        self.config = config
        self.utils = APUtils(config, inp)
        self.neighborhoods = self.utils.lcs_neighborhoods[:]

        self.z_best = None
        self.f_opt = float('inf')
        self.heuristic_init_sol = self.get_heuristic_init_solution()

    def get_heuristic_init_solution(self):
        sol_list = []
        for reverse in [True, False]:
            s = init_by_distance(self.inp, self.config, reverse=reverse)
            if s is not None:
                sol_list.append(s)

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=1)
            if s is not None:
                sol_list.append(s)

            s = init_by_angle(self.inp, self.config, reverse=reverse, direction=-1)
            if s is not None:
                sol_list.append(s)

        random.shuffle(sol_list)

        return sol_list

    def gen_init_solution(self):
        if len(self.heuristic_init_sol) == 0:
            # print("random")
            while True:
                s = init_random(self.inp, self.config)
                s_score = self.utils.get_score(s)
                if s_score[1] == 0 and s_score[2] == 0:
                    return s
        else:
            return self.heuristic_init_sol.pop()

    def clear(self):
        self.z_best = None
        self.f_opt = float('inf')
        self.heuristic_init_sol = self.get_heuristic_init_solution()

    def run(self):
        self.clear()
        log_ = {}
        z = self.gen_init_solution()

        f_z = self.utils.get_score(z)

        if f_z[1] == 0 and f_z[2] == 0:
            self.z_best = z
            self.f_opt = f_z[0]

        it = 0
        nic = 1

        while it < self.max_iter:
            it += 1
            # print(it)
            f_e = float('inf')
            e = None

            random.shuffle(self.neighborhoods)

            neighbor_improved = None
            for neighbor in self.neighborhoods:
                za = self.utils.get_best_sol_by_neighbor(z, neighbor)
                if za is None:
                    # print(f"{neighbor} - {z} - {za}")
                    continue
                f_za = self.utils.get_score(za)

                if f_e > f_za[0]:
                    f_e = f_za[0]
                    e = za
                    # print(f"{neighbor} - {z} - {za}")
                    neighbor_improved = neighbor
                    break

            z = e
            init_again = False
            if f_e < self.f_opt:
                self.z_best = e
                self.f_opt = self.utils.get_score(self.z_best)[0]
                nic = 1
            else:
                nic += 1
                if nic > self.max_stable:
                    z = self.gen_init_solution()
                    nic = 1
                    init_again = True

            log_[it] = {"nic": nic, "init_again": init_again, "e": str(e), "f_e": f_e, "z_best": str(self.z_best),
                        "f_opt": self.f_opt,
                        "neighbor_improved": neighbor_improved}
            # it, nic,  init_again, fe, f_opt
            # print(self.z_best)
            # print(self.f_opt)

        return self.f_opt, self.z_best, log_
