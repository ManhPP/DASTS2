import json
import pandas as pd


def run(path, new_path="result.csv"):
    data = json.load(open(path))
    result = {}

    for data_set in data:
        result[data_set] = {}
        for r in data[data_set]:
            if isinstance(data[data_set][r]['obj'], list):
                result[data_set][r] = float(data[data_set][r]['obj'][0])
            else:
                result[data_set][r] = float(data[data_set][r]['obj'])

    df = pd.DataFrame(result)
    df.to_csv(new_path)


if __name__ == '__main__':
    run('result/tabu_12_1_1/05242022100141/result_all.json', "result_12.csv")
