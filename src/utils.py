import glob
import json
import os


def cal(staff_path_list, drone_path_list, tau, tau_a, num_cus, config,
        drone_trip_cal=None, staff_trip_cal=None, print_log=False):
    """

    :param staff_trip_cal:
    :param drone_trip_cal:
    :param staff_path_list:
    :param drone_path_list:
    :param tau:
    :param tau_a:
    :param num_cus:
    :param config:
    :param print_log:
    :return:
    """
    T = {}
    A = {}
    B = {}

    S = {}

    dz = 0
    cz = 0

    for i, staff in enumerate(staff_path_list):
        if staff_trip_cal is not None and i not in staff_trip_cal:
            continue

        if len(staff) == 0:
            continue
        tmp = tau[0, staff[0]]
        S[staff[0]] = tmp
        for j in range(len(staff) - 1):
            tmp += tau[staff[j], staff[j + 1]]
            S[staff[j + 1]] = tmp
        A[i] = tmp + tau[staff[-1], num_cus + 1]

    for i, drone in enumerate(drone_path_list):
        if drone_trip_cal is not None and i not in drone_trip_cal:
            continue
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
            tmp += T[i, j]

        if tmp > 0:
            B[i] = tmp

    if len(A) == len(B) == 0:
        c = 0
    elif len(B) == 0:
        c = max(A.values())
    elif len(A) == 0:
        c = max(B.values())
    else:
        c = max(max(A.values()), max(B.values()))

    for i, staff in enumerate(staff_path_list):
        if staff_trip_cal is not None and i not in staff_trip_cal:
            continue

        if len(staff) == 0:
            continue
        for j in staff:
            cz += max(0, A[i] - S[j] - config.params["L_w"])
    for i, drone in enumerate(drone_path_list):
        if drone_trip_cal is not None and i not in drone_trip_cal:
            continue

        for j, trip in enumerate(drone):
            if len(trip) == 0:
                continue
            for k in trip:
                cz += max(0, T[i, j] - S[k] - config.params["L_w"])

            dz += max(0, T[i, j] - config.params["L_d"])

    if print_log:
        print(f"A: {A}")
        print(f"B: {B}")
        print(f"T: {T}")
        print(f"S: {S}")
        print(f"dz: {dz}")
        print(f"cz: {cz}")

    return c, dz, cz


def make_dirs(path):
    """

    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def make_dirs_if_not_present(path):
    """
    creates new directory if not present
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_result(config):
    paths = glob.glob(config.result.path)
    print(paths)
    result = []
    for data_path in paths:
        if 'final_result' in data_path or 'result_all' in data_path:
            continue
        print(data_path)
        data = json.loads(open(data_path).read())
        if config.result.type == 'gurobi':
            optimal = data["Optimal"]
            status = data["status"]
            time = data["Time"]
            result.append(
                {"data_set": os.path.splitext(os.path.basename(data_path))[0].split("_")[1], "obj": optimal,
                 "time": time,
                 "status": status, "num_staff": data['num_staff'], "num_drone": data['num_drone']})

        else:
            result.append(
                {"data_set": os.path.splitext(os.path.basename(data_path))[0].split("_")[1],
                 "run": os.path.splitext(os.path.basename(data_path))[0].split("_")[2],
                 "obj": data["intra"]["intra-score"],
                 "num_drone": data["num_drone"],
                 "num_staff": data["num_staff"],
                 "tabu_time": data["tabu_time"],
                 "tabu_step": len(data["tabu"]["tabu-log"]) if "step" not in data["tabu"] else data["tabu"]["step"],
                 "time": data["time"],
                 "intra-obj": data["intra"]["intra-score"],
                 "inter-obj": data["inter"]["inter-score"],
                 "ejection-obj": data["ejection"]["ejection-score"],
                 "tabu-obj": data["tabu"]["tabu-score"],
                 "po_time": data["po_time"]
                 }
            )
    with open(os.path.join(config.result.result, 'final_result.json'),
              'w') as json_file:
        json.dump(result, json_file, indent=2)


if __name__ == '__main__':
    pass
