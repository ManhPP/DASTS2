import os


def cal(staff_path_list, drone_path_list, tau, tau_a, num_cus, config, is_use_penalty=True, alpha1=0, alpha2=0,
        print_log=False):
    T = {}
    A = {}
    B = {}

    S = {}

    dz = 0
    cz = 0

    for i, staff in enumerate(staff_path_list):
        if len(staff) == 0:
            continue
        tmp = tau[0, staff[0]]
        S[staff[0]] = tmp
        for j in range(len(staff) - 1):
            tmp += tau[staff[j], staff[j + 1]]
            S[staff[j + 1]] = tmp
        A[i] = tmp + tau[staff[-1], num_cus + 1]

    for i, drone in enumerate(drone_path_list):
        tmp = 0
        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            tmp1 = tau_a[0, trip[0]]
            S[trip[0]] = tmp1
            for k in range(len(trip) - 1):
                tmp1 += tau_a[trip[k], trip[k + 1]]
                S[trip[k + 1]] = tmp1
            T[i, j] = tmp1 + tau_a[trip[-1], num_cus + 1]
            tmp += tmp1

        if tmp > 0:
            B[i] = tmp

    c = max(max(A.values()), max(B.values()))

    if print_log:
        print(f"A: {A}")
        print(f"B: {B}")
        print(f"T: {T}")
        print(f"T: {S}")
        print(f"T: {dz}")
        print(f"T: {cz}")

    return c + alpha1*dz + alpha2*cz if is_use_penalty else c


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
