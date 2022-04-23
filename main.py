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
    config.result_folder = os.path.join(config.result_folder, datetime.now().strftime("%m%d%Y%H%M%S"))
    if config.run_type == "ts":
        inp = load_input(config, config.data_path)
        ts = TabuSearch(inp, config, None, config.tabu_params.tabu_size, config.tabu_params.max_iter)
        ts.run()
        print("done!")

    elif config.run_type == "cal":
        inp = load_input(config, config.test.data_path)
        print(
            f"Final result: "
            f"{cal(config.test.staff, config.test.drone, inp['tau'], inp['tau_a'], inp['num_cus'], config, {}, True)}")

    else:
        for data_path in config.data_path.split(","):
            paths = glob.glob(data_path)
            print(paths)
            for data_set in paths:
                print(data_set)
                try:
                    inp = load_input(config, data_set)
                    if config.solver.solver == "GUROBI":
                        solve_by_gurobi(config, inp)
                    elif config.solver.solver == "CPLEX":
                        solve_by_cplex(config, inp)
                    else:
                        raise "Unknown solver!"
                except Exception as e:
                    print("Error: ", e)
