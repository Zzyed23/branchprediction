#metrics

class PerformanceMetrics:
    def __init__(self):
        self.total_instructions = 0
        self.total_branches = 0
        self.mispredictions = 0
        self.cycles = 0

    def update_metrics(self, is_branch, mispredicted):
        self.total_instructions += 1
        self.cycles += 1
        if is_branch:
            self.total_branches += 1
            if mispredicted:
                self.mispredictions += 1

    def calculate_metrics(self):
        misprediction_rate = self.mispredictions / self.total_branches if self.total_branches else 0
        ipc = self.total_instructions / self.cycles if self.cycles else 0
        return misprediction_rate, ipc
