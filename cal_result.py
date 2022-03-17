def cal(staff_path_list, drone_path_list, tau, tau_a):
    T = {}
    A = {}
    B = {}

    for staff in staff_path_list:
        tmp = 0
        for i in range(len(staff) - 1):
            tmp += tau[staff[i], staff[i + 1]]
        A[staff] = tmp

    for drone in drone_path_list:
        tmp = 0
        for trip in drone:
            tmp1 = 0
            for i in range(len(trip) - 1):
                tmp1 += tau_a[trip[i], trip[i + 1]]
            T[drone, trip] = tmp1
            tmp += tmp1

        B[drone] = tmp
    print(f"A: {A}")
    print(f"B: {B}")
    print(f"T: {T}")
    return max(max(A.values()), max(B.values()))


if __name__ == '__main__':
    pass
