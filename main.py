import argparse
import glob
import json
import os
import timeit
from datetime import datetime

import numpy as np
from omegaconf import OmegaConf
from scipy.spatial.distance import cdist

from src.ip.cplex_ip import solve_by_cplex
from src.ip.gurobi_ip import solve_by_gurobi
from src.load_input import load_input
from src.ts.tabu import TabuSearch
from src.utils import cal, get_result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DASTS2')

    parser.add_argument('--config', type=str, default="config.yml",
                        help='path of config file')
    args = parser.parse_args()
    config = OmegaConf.load(args.config)
    config.result_folder = os.path.join(config.result_folder, config.run_type, datetime.now().strftime("%m%d%Y%H%M%S"))

    if config.run_type == "cal":
        inp = load_input(config, config.test.data_path)
        print(
            f"Final result: "
            f"{cal(config.test.staff, config.test.drone, inp['tau'], inp['tau_a'], inp['num_cus'], config)}")
    elif config.run_type == "result":
        get_result(config)
    elif config.run_type == "test":
        m_cus = {}
        m_r = {}
        for data_path in config.data_path.split(","):
            paths = glob.glob(data_path)
            print(paths)
            for data_set in paths:
                print(data_set)
                name_data = os.path.splitext(os.path.basename(data_set))[0]
                cus = name_data.split(".")[0]
                r = name_data.split(".")[1]
                coordinates_matrix = np.loadtxt(data_set, skiprows=2)[:, :2]
                coordinates_matrix = np.insert(coordinates_matrix, 0, np.zeros(2), 0)
                dis_matrix = cdist(coordinates_matrix, coordinates_matrix)
                m = np.max(dis_matrix)
                if m_cus.get(cus, 0) < m:
                    m_cus[cus] = m
                if m_r.get(r, 0) < m:
                    m_r[r] = m

        mt_cus = {"staff": {}, "drone": {}}
        mt_r = {"staff": {}, "drone": {}}
        for i in m_cus:
            mt_cus["drone"][i] = m_cus[i] / config.params.drone_velocity
            mt_cus["staff"][i] = m_cus[i] / config.params.staff_velocity
        for i in m_r:
            mt_r["drone"][i] = m_r[i] / config.params.drone_velocity
            mt_r["staff"][i] = m_r[i] / config.params.staff_velocity
        print("final: ", m_cus)
        print("final: ", m_r)
    else:
        for data_path in config.data_path:
            paths = glob.glob(data_path)
            print(paths)
            result_all = {}

            for data_set in paths:
                if data_set in config.except_path:
                    continue
                print(data_set)

                try:
                    inp = load_input(config, data_set)
                    result_all[inp['data_set']] = {}
                    if config.run_type.startswith("ts") or config.run_type.startswith("tabu"):
                        for run in range(1, config.tabu_params.num_runs + 1):
                            ts = TabuSearch(inp, config, None, config.tabu_params.tabu_size,
                                            config.tabu_params.max_iter, run)
                            start = timeit.default_timer()
                            ts.run()
                            end = timeit.default_timer()

                            result_all[inp['data_set']][run] = {"obj": ts.utils.get_score(ts.best), "sol": str(ts.best),
                                                                "time": end - start}
                        # ts.utils.move02([[[6, 12, 5]], [[10, 7, 11]], [2, 3, 9], [8, 1, 4]])
                        # ts.utils.run_ejection([[[11, 1, 10, 12, 8, 5, 2]], [4, 9, 6, 7, 3]])
                        # print(ts.utils.get_score([[[5, 7, 11]], [[1, 8, 6, 12, 3, 9]], [4], [10, 2]]))
                        # print(ts.utils.get_score([[[5, 7, 11]], [[8, 6, 12, 3, 9]], [1, 4], [10, 2]]))
                        print("done!")

                    elif config.solver.solver == "GUROBI":
                        solve_by_gurobi(config, inp)
                    elif config.solver.solver == "CPLEX":
                        solve_by_cplex(config, inp)
                    else:
                        raise "Unknown solver!"
                except Exception as e:
                    print("Error: ", e)

            with open(os.path.join(config.result_folder, 'result_all.json'),
                      'w') as json_file:
                json.dump(result_all, json_file, indent=2)
