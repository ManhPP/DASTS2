import random


class Solution:
    def __init__(self, config, inp):
        self.solution = None
        self.config = config
        self.inp = inp
        self.init_solution()

    def init_solution(self):
        num_staff = self.config.params["num_staff"]
        num_drone = self.config.params["num_drone"]
        L_w = self.config.params["L_w"]
        L_d = self.config.params["L_d"]

        tau_a = self.inp["tau_a"]
        num_cus = self.inp["num_cus"]

        C1 = self.inp["C1"]
        tmp = [i for i in range(1, num_cus + 1) if i not in C1]

        random.shuffle(tmp)
        self.solution = []

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
                self.solution.append(trip)
                trip = []

        self.solution.append(trip)

        for i in range(num_drone):
            if len(self.solution[i]) == 0:
                continue
            t_d = 0
            t_w = -tau_a[0, self.solution[i][0]]
            prev = 0
            new_trip = []
            sub_trip = []
            for ind, cus in enumerate(self.solution[i]):
                if t_d + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_d \
                        or t_w + tau_a[prev, cus] + tau_a[cus, num_cus + 1] > L_w:
                    t_d = 0
                    t_w = -tau_a[0, self.solution[i][ind]]
                    prev = 0
                    new_trip.append(sub_trip)
                    sub_trip = []
                else:
                    t_d += tau_a[prev, cus]
                    t_w += tau_a[prev, cus]
                    prev = cus
                    sub_trip.append(cus)
            new_trip.append(sub_trip)
            self.solution[i] = new_trip

    def move10(self, x_ind, y_ind):
        if x_ind == y_ind:
            return

        x_val = self.solution[x_ind]
        self.solution.remove(x_val)

        if x_ind > y_ind:
            self.solution.insert(y_ind + 1, x_val)
        else:
            self.solution.insert(y_ind, x_val)

    def move11(self, x_ind, y_ind):
        self.solution[x_ind], self.solution[y_ind] = self.solution[y_ind], self.solution[x_ind]

    def move20(self, x_ind, xa_ind, y_ind):
        if x_ind != xa_ind - 1 or x_ind == y_ind or xa_ind == y_ind:
            return

        x_val = self.solution[x_ind]
        xa_val = self.solution[xa_ind]
        self.solution.remove(x_val)
        self.solution.remove(xa_val)
        if x_ind > y_ind:
            self.solution.insert(y_ind + 1, x_val)
            self.solution.insert(y_ind + 2, xa_val)
        else:
            self.solution.insert(y_ind - 1, x_val)
            self.solution.insert(y_ind, xa_val)

    def move21(self, x_ind, xa_ind, y_ind):
        if x_ind != xa_ind - 1 or x_ind == y_ind or xa_ind == y_ind:
            return

        x_val = self.solution[x_ind]
        xa_val = self.solution[xa_ind]
        y_val = self.solution[y_ind]

        self.solution.remove(x_val)
        self.solution.remove(xa_val)
        self.solution.remove(y_val)

        if x_ind > y_ind:
            self.solution.insert(y_ind, x_val)
            self.solution.insert(y_ind + 1, xa_val)
            self.solution.insert(xa_ind, y_val)
        else:
            self.solution.insert(x_ind, y_val)
            self.solution.insert(y_ind - 1, x_val)
            self.solution.insert(y_ind, xa_val)

    def move2opt(self, x_ind, y_ind):
        if abs(x_ind - y_ind) < 2 or x_ind == len(self.solution - 1) or y_ind == len(self.solution - 1):
            return

        self.solution[x_ind + 1], self.solution[y_ind + 1] = self.solution[y_ind + 1], self.solution[x_ind + 1]

    def get_score(self):
        pass

    def get_all_neighbor(self):
        pass

    def find_index(self, val):
        num_staff = self.config.params["num_staff"]
        num_drone = self.config.params["num_drone"]
        for i in range(num_drone):
            drone_trip = self.solution[i]
            for j, trip in enumerate(drone_trip):
                for k, node in enumerate(trip):
                    if node == val:
                        return i, j, k

        for i in range(num_drone, num_drone + num_staff):
            staff_trip = self.solution[i]
            for j, node in enumerate(staff_trip):
                if node == val:
                    return i, j


if __name__ == '__main__':
    pass
