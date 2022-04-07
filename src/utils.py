import os


def cal(staff_path_list, drone_path_list, tau, tau_a, num_cus, print_log=False):
    T = {}
    A = {}
    B = {}

    for i, staff in enumerate(staff_path_list):
        if len(staff) == 0:
            continue
        tmp = tau[0, staff[0]]
        for i in range(len(staff) - 1):
            tmp += tau[staff[i], staff[i + 1]]
        A[i] = tmp + tau[staff[-1], num_cus + 1]

    for i, drone in enumerate(drone_path_list):
        tmp = 0
        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            tmp1 = tau_a[0, trip[0]]
            for i in range(len(trip) - 1):
                tmp1 += tau_a[trip[i], trip[i + 1]]
            T[i, j] = tmp1 + tau_a[trip[-1], num_cus + 1]
            tmp += tmp1

        if tmp > 0:
            B[i] = tmp
    if print_log:
        print(f"A: {A}")
        print(f"B: {B}")
        print(f"T: {T}")
    return max(max(A.values()), max(B.values()))


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def make_dirs_if_not_present(path):
    """
    creates new directory if not present
    """
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    pass
