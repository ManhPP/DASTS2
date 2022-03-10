import argparse
import glob
import os
from datetime import datetime

from omegaconf import OmegaConf

from src.cplex_ip import solve_by_cplex
from src.gurobi_ip import solve_by_gurobi
from src.util import load_input

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DASTS2')

    parser.add_argument('--config', type=str, default="config.yml",
                        help='path of config file')
    args = parser.parse_args()
    config = OmegaConf.load(args.config)
    config.result_folder = os.path.join(config.result_folder, datetime.now().strftime("%m%d%Y%H%M%S"))
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
