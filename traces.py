import os
import random

def realistic_trace_generator(length=3000000):
    """
    Generates a synthetic instruction trace including branches, loops, and other instructions.
    - length: Number of instructions to generate
    """
    pc = 0  # Program Counter
    generated_count = 0

    while generated_count < length:
        # Simulate a loop with a fixed number of iterations
        loop_iterations = 5
        for i in range(loop_iterations):
            yield {"pc": pc, "type": "branch", "taken": True}  # Loop branches are taken
            pc += 4
            generated_count += 1
            if generated_count >= length:
                return

        yield {"pc": pc, "type": "branch", "taken": False}  # Exit loop branch is not taken
        pc += 4
        generated_count += 1
        if generated_count >= length:
            return

        # Simulate conditional branches with a certain probability
        for _ in range(3):  # Add a few conditional branches
            yield {
                "pc": pc,
                "type": "branch",
                "taken": random.choices([True, False], weights=[0.7, 0.3])[0]
            }
            pc += 4
            generated_count += 1
            if generated_count >= length:
                return

        # Add some non-branch instructions (ALU, LOAD, STORE)
        for _ in range(10):  # Non-branch instructions
            inst_type = random.choice(["alu", "load", "store"])
            yield {"pc": pc, "type": inst_type, "taken": None}  # Non-branches have no 'taken' status
            pc += 4
            generated_count += 1
            if generated_count >= length:
                return


def load_trace_file(file_path):
    """
    Parses a single trace file with format:
    <address> <outcome>
    Example:
    0x40fc96 1
    100 0

    - address: Program Counter (PC), in decimal or hexadecimal
    - outcome: 1 (branch taken), 0 (not taken)
    """
    trace_data = []
    with open(file_path, "r") as f:
        for line in f:
            pc, outcome = line.strip().split()
            trace_data.append({
                "pc": int(pc, 16) if pc.startswith("0x") else int(pc),  # Handle hex or decimal
                "type": "branch",  # Assume all instructions in these traces are branch instructions
                "taken": outcome == "1",  # Convert "1" to True and "0" to False
            })
    return trace_data


def load_traces_with_defined_paths():
    """
    Manually load 16 trace files with relative paths.
    """
    trace_files = [
        "trace_01", "trace_02", "trace_03", "trace_04",
        "trace_05", "trace_06", "trace_07", "trace_08",
        "trace_09", "trace_10", "trace_11", "trace_12",
        "trace_13", "trace_14", "trace_15", "trace_16"
    ]

    traces = {}
    for trace_name in trace_files:
        if os.path.exists(trace_name):
            traces[trace_name] = load_trace_file(trace_name)
        else:
            print(f"Warning: Trace file {trace_name} not found.")

    return traces
