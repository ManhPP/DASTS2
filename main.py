import argparse
import glob
import os
from datetime import datetime

from omegaconf import OmegaConf

from src.ip.cplex_ip import solve_by_cplex
from src.ip.gurobi_ip import solve_by_gurobi
from src.load_input import load_input
from src.ts.tabu import TabuSearch
from src.utils import cal

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
            f"{cal(config.test.staff, config.test.drone, inp['tau'], inp['tau_a'], inp['num_cus'], config, {})}")
    else:
        for data_path in config.data_path.split(","):
            paths = glob.glob(data_path)
            print(paths)
            for data_set in paths:
                print(data_set)
                try:
                    inp = load_input(config, data_set)
                    if config.run_type.startswith("ts") or config.run_type.startswith("tabu"):
                        ts = TabuSearch(inp, config, None, config.tabu_params.tabu_size, config.tabu_params.max_iter)
                        ts.run()
                        # ts.utils.move02([[[6, 12, 5]], [[10, 7, 11]], [2, 3, 9], [8, 1, 4]])
                        # ts.utils.run_ejection([[[5, 10]], [[11, 2, 9, 8, 4, 1], [12, 3, 6, 7]], [], []])
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
