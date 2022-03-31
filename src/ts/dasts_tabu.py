from src.ts.Solution import Solution
from src.ts.tabu import TabuSearch


class DTabu(TabuSearch):
    def _score(self, state: Solution):
        return state.get_score()

    def _neighborhood(self):
        return self.current.get_all_neighbor()


if __name__ == '__main__':
    pass
