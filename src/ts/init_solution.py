def init_1(inp, config, reverse=False):
    solution = []
    num_drone = config.params.num_drone
    num_staff = config.params.num_staff
    for i in range(num_drone + num_staff):
        solution.append([])

    sorted_neighborhood = {}
    for cus in range(inp['num_cus'] + 1):
        tmp = {}
        for neighbor in range(inp['num_cus'] + 1):
            if cus != neighbor:
                tmp[neighbor] = inp['tau'][cus, neighbor]

        tmp = sorted(tmp.items(), key=lambda e: e[1], reverse=reverse)
        sorted_neighborhood[cus] = [i for i, _ in tmp]

    travel_time = [0] * (num_drone + num_staff)

    i = 0
    C1 = inp['C1']
    visited_cus = []

    while len(visited_cus) < inp['num_cus']:
        time_dict = inp['tau']
        if i < num_drone and len(solution[i]) == 0:
            solution[i].append([])

        if i < num_drone:
            time_dict = inp['tau_a']
            cur_trip = solution[i][-1]
        else:
            cur_trip = solution[i]

        if len(cur_trip) == 0:
            last_cus = 0
            first_cus = 0
        else:
            last_cus = cur_trip[-1]
            first_cus = cur_trip[0]

        next_cus = None
        for nc in sorted_neighborhood[last_cus]:
            if nc == 0:
                continue
            if nc not in visited_cus:
                if i >= num_drone:
                    next_cus = nc
                    break
                if i < num_drone and i not in C1:
                    next_cus = nc
                    break

        if next_cus is None:
            continue

        if i < num_drone:
            if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] > config.params.L_d or \
                    travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] - time_dict[0, first_cus] \
                    > config.params.L_w:
                solution[i].append([next_cus])
                travel_time[i] = time_dict[0, next_cus]
            else:
                cur_trip.append(next_cus)
                travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
            visited_cus.append(next_cus)
        else:
            if travel_time[i] + time_dict[last_cus, next_cus] + time_dict[next_cus, 0] - time_dict[0, first_cus] \
                    <= config.params.L_w:
                cur_trip.append(next_cus)
                travel_time[i] = travel_time[i] + time_dict[last_cus, next_cus]
                visited_cus.append(next_cus)
        i += 1
        i %= num_drone + num_staff

    return solution


def init_2(inp, config):
    solution = []
    num_drone = config.params.num_drone
    num_staff = config.params.num_staff
    for i in range(num_drone + num_staff):
        solution.append([])

    return solution
