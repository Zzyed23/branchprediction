class PipelineStage:
    def __init__(self, name):
        self.name = name
        self.instruction = None

    def process(self, instruction=None):
        if instruction:
            self.instruction = instruction
        return self.instruction


class Pipeline:
    def __init__(self, branch_predictor):
        self.stages = [
            PipelineStage("IF"),
            PipelineStage("ID"),
            PipelineStage("EX"),
            PipelineStage("MEM"),
            PipelineStage("WB"),
        ]
        self.branch_predictor = branch_predictor
        self.flush_needed = False
        self.mispredictions = 0
        self.stall_cycles = 0  # Stall counter

    def process_cycle(self, instruction):
        # Check for stall cycles
        if self.stall_cycles > 0:
            self.stall_cycles -= 1
            return None  # Indicates a stall cycle

        mispredicted = False
        if instruction["type"] == "branch":
            prediction = self.branch_predictor.predict(instruction["pc"])
            mispredicted = prediction != instruction["taken"]
            if mispredicted:
                self.mispredictions += 1
                self.flush_needed = True
                self.stall_cycles = 2  # Stall for 2 cycles on misprediction
            self.branch_predictor.update(instruction["pc"], instruction["taken"])

        # Flush if needed
        if self.flush_needed:
            self.flush_pipeline()
            self.flush_needed = False

        return mispredicted  # Returns True for mispredicted branches, False otherwise

    def flush_pipeline(self):
        for stage in self.stages:
            stage.instruction = None
