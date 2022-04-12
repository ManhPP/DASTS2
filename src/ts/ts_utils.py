import copy

from src.utils import cal


class TSUtils:
    def __init__(self, config, inp):
        self.config = config
        self.inp = inp
        self.num_cus = self.inp["num_cus"]
        self.num_staff = self.config.params["num_staff"]
        self.num_drone = self.config.params["num_drone"]

    def get_score(self, solution):
        return cal(solution[self.config.params["num_drone"]:],
                   solution[:self.config.params["num_drone"]], self.inp['tau'],
                   self.inp['tau_a'], self.inp['num_cus'], self.config)

    def get_all_neighbor(self):
        result = []

        # TODO: get all neighbor

        return result

    def find_index(self, solution, val):
        for i in range(self.num_drone):
            drone_trip = solution[i]
            for j, trip in enumerate(drone_trip):
                for k, node in enumerate(trip):
                    if node == val:
                        return i, j, k

        for i in range(self.num_drone, self.num_drone + self.num_staff):
            staff_trip = solution[i]
            for j, node in enumerate(staff_trip):
                if node == val:
                    return i, j

        return None

    def delete_by_ind(self, solution, index):
        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].pop(index[1])

        if len(index) == 3:
            if index[0] < self.num_drone:
                solution[index[0]][index[1]].pop(index[2])

    def delete_by_val(self, solution, val):
        if val <= self.num_cus:
            self.delete_by_ind(solution, self.find_index(solution, val))

    def insert_after(self, solution, val1, val2):
        index = self.find_index(solution, val2)

        if len(index) == 2:
            if index[0] >= self.num_drone:
                solution[index[0]].insert(index[1] + 1, val1)

        else:
            if index[0] < self.num_drone:
                solution[index[0]][index[1]].insert(index[2] + 1, val1)

    def is_in_drone_route(self, solution, val):
        index = self.find_index(solution, val)
        if index[0] >= self.num_drone:
            return False
        return True

    def is_adj(self, solution, val1, val2):
        ind1 = self.find_index(solution, val1)
        ind2 = self.find_index(solution, val2)

        if len(ind1) != len(ind2):
            return False

        if len(ind1) == 2:
            return ind1[0] == ind2[0] and ind2[1] == ind1[1] + 1

        else:
            return ind1[0] == ind2[0] and ind1[1] == ind2[1] and ind2[2] == ind1[2] + 1

    def swap(self, solution, x, y):
        x_ind = self.find_index(solution, x)
        y_ind = self.find_index(solution, y)

        if len(x_ind) == 2:
            solution[x_ind[0]][x_ind[1]] = y
        else:
            solution[x_ind[0]][x_ind[1]][x_ind[2]] = y

        if len(y_ind) == 2:
            solution[y_ind[0]][y_ind[1]] = x
        else:
            solution[y_ind[0]][y_ind[1]][y_ind[2]] = x

    def is_in_same_trip(self, solution, x, y):
        x_ind = self.find_index(solution, x)
        y_ind = self.find_index(solution, y)

        if len(x_ind) != len(y_ind):
            return False
        if len(x_ind) == 2:
            return x_ind[0] == y_ind[0]
        else:
            return x_ind[0] == y_ind[0] and x_ind[1] == y_ind[1]

    def move10(self, solution):
        result = []
        num_cus = self.inp["num_cus"]
        C1 = self.inp["C1"]

        for x in range(1, num_cus + 1):

            for y in range(1, num_cus + 1):
                if x == y:
                    continue

                if x in C1 and self.is_in_drone_route(solution, y):
                    continue

                s = copy.deepcopy(solution)

                self.delete_by_val(s, x)
                self.insert_after(s, x, y)
                result.append(s)

        return result

    def move11(self, solution):
        result = []

        num_cus = self.inp["num_cus"]
        C1 = self.inp["C1"]

        for x in range(1, num_cus + 1):
            for y in range(1, num_cus + 1):
                if x == y:
                    continue

                if x in C1 and self.is_in_drone_route(solution, y):
                    continue

                if y in C1 and self.is_in_drone_route(solution, x):
                    continue

                s = copy.deepcopy(solution)
                self.swap(s, x, y)

                result.append(s)

    def move20(self, solution):
        result = []
        num_cus = self.inp["num_cus"]
        C1 = self.inp["C1"]

        for x1 in range(1, num_cus + 1):
            for x2 in range(1, num_cus + 1):
                if not self.is_adj(solution, x1, x2):
                    continue
                for y in range(1, num_cus + 1):
                    if x1 == y or x2 == y:
                        continue

                    if x1 in C1 and self.is_in_drone_route(solution, y):
                        continue

                    s = copy.deepcopy(solution)

                    self.delete_by_val(s, x1)
                    self.delete_by_val(s, x2)
                    self.insert_after(s, x1, y)
                    self.insert_after(s, x2, 1)

                    result.append(s)

    def move21(self, solution):
        result = []

        num_cus = self.inp["num_cus"]
        C1 = self.inp["C1"]

        for x1 in range(1, num_cus + 1):
            for x2 in range(1, num_cus + 1):
                if not self.is_adj(solution, x1, x2):
                    continue
                for y in range(1, num_cus + 1):
                    if x1 == y or x2 == y:
                        continue

                    if x1 in C1 and self.is_in_drone_route(solution, y):
                        continue

                    if y in C1 and self.is_in_drone_route(solution, x1):
                        continue

                    s = copy.deepcopy(solution)

                    self.swap(s, x1, y)
                    self.delete_by_val(solution, x2)
                    self.insert_after(solution, x2, x1)

                    result.append(s)
        return result

    def move2opt(self, solution):
        result = []

        num_cus = self.inp["num_cus"]
        C1 = self.inp["C1"]

        for x1 in range(1, num_cus + 1):
            for x2 in range(1, num_cus + 1):
                if not self.is_adj(solution, x1, x2):
                    continue
                for y1 in range(1, num_cus + 1):
                    if y1 == x1 or y1 == x2:
                        continue
                    for y2 in range(1, num_cus + 1):
                        if not self.is_adj(solution, y1, y2):
                            continue

                        if x1 in C1 and self.is_in_drone_route(solution, y2):
                            continue

                        if y1 in C1 and self.is_in_drone_route(solution, x2):
                            continue

                        s = copy.deepcopy(solution)

                        x1_ind = self.find_index(s, x1)
                        x2_ind = self.find_index(s, x2)
                        y1_ind = self.find_index(s, y1)
                        y2_ind = self.find_index(s, y2)

                        if self.is_in_same_trip(s, x1, y1):
                            if x1_ind < y1_ind:
                                if len(x1_ind) == 2:
                                    tmp = s[x2_ind[0]][x2_ind[1]:y2_ind[1]]
                                    tmp.reverse()
                                    s[x2_ind[0]][x2_ind[1]:y2_ind[1]] = tmp
                                else:
                                    tmp = s[x2_ind[0]][x2_ind[1]][x2_ind[2]:y2_ind[2]]
                                    tmp.reverse()
                                    s[x2_ind[0]][x2_ind[1]][x2_ind[2]:y2_ind[2]] = tmp
                                result.append(s)
                        else:
                            if len(x2_ind) == 2:
                                tmp1 = s[x2_ind[0]][x2_ind[1]:]
                            else:
                                tmp1 = s[x2_ind[0]][x2_ind[1]][x2_ind[2]:]

                            if len(y2_ind) == 2:
                                tmp2 = s[y2_ind[0]][y2_ind[1]:]
                                s[y2_ind[0]][y2_ind[1]:] = tmp1
                            else:
                                tmp2 = s[y2_ind[0]][y2_ind[1]][y2_ind[2]:]
                                s[y2_ind[0]][y2_ind[1]][y2_ind[2]:] = tmp1

                            if len(x2_ind) == 2:
                                s[x2_ind[0]][x2_ind[1]:] = tmp2
                            else:
                                s[x2_ind[0]][x2_ind[1]][x2_ind[2]:] = tmp2
                            result.append(s)

        return result


if __name__ == '__main__':
    pass
