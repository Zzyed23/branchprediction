import os
from predictors import GsharePredictor, PerceptronPredictor, LocalHistoryPredictor, TAGEPredictor
from pipeline import Pipeline
from metrics import PerformanceMetrics
from traces import realistic_trace_generator, load_traces_with_defined_paths

# Initialize branch predictors
predictors = [
    GsharePredictor(history_bits=4),  # Gshare Predictor
    PerceptronPredictor(num_weights=128, history_length=8),  # Perceptron Predictor
    LocalHistoryPredictor(history_bits=4),  # Local History Predictor
    TAGEPredictor()  # TAGE Predictor
]

# Simulate and evaluate predictors on synthetic traces
print("Evaluating predictors on synthetic traces...")
trace_length = 10000  # Length of the synthetic trace
synthetic_trace = list(realistic_trace_generator(trace_length))  # Convert generator to list for reuse

for branch_predictor in predictors:
    print(f"\nTesting {branch_predictor.__class__.__name__} on synthetic traces...")

    # Initialize pipeline and metrics
    pipeline = Pipeline(branch_predictor)
    metrics = PerformanceMetrics()

    # Run the simulation for the synthetic trace
    for instruction in synthetic_trace:
        mispredicted = pipeline.process_cycle(instruction)
        if mispredicted is None:
            metrics.cycles += 1  # Increment cycle count for stall cycles
        else:
            is_branch = instruction["type"] == "branch"
            metrics.update_metrics(is_branch=is_branch, mispredicted=mispredicted)

    # Output performance metrics
    misprediction_rate, ipc = metrics.calculate_metrics()
    print(f"Results for {branch_predictor.__class__.__name__}:")
    print(f"  Misprediction Rate: {misprediction_rate:.2f}")
    print(f"  IPC: {ipc:.2f}")

# Simulate and evaluate predictors on real-world traces using explicit paths
print("\nEvaluating predictors on real-world traces (explicit paths)...")
explicit_traces = load_traces_with_defined_paths()

for branch_predictor in predictors:
    print(f"\nTesting {branch_predictor.__class__.__name__} on real-world traces (explicit paths)...")

    for trace_name, instructions in explicit_traces.items():
        print(f"  Processing {trace_name}...")

        # Initialize pipeline and metrics
        pipeline = Pipeline(branch_predictor)
        metrics = PerformanceMetrics()

        # Run the simulation for the real-world trace
        for instruction in instructions:
            mispredicted = pipeline.process_cycle(instruction)
            if mispredicted is None:
                metrics.cycles += 1  # Increment cycle count for stall cycles
            else:
                is_branch = instruction["type"] == "branch"
                metrics.update_metrics(is_branch=is_branch, mispredicted=mispredicted)

        # Output performance metrics
        misprediction_rate, ipc = metrics.calculate_metrics()
        print(f"    Results for {trace_name}:")
        print(f"      Misprediction Rate: {misprediction_rate:.2f}")
        print(f"      IPC: {ipc:.2f}")

print("\nSimulation completed!")
