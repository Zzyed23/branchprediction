# predictors

import numpy as np

class GsharePredictor:
    def __init__(self, history_bits, table_size=1024):
        self.history_bits = history_bits
        self.GHR = 0  # Global History Register
        self.PHT = [1] * table_size  # Pattern History Table with 2-bit counters

    def predict(self, pc):
        index = (pc ^ self.GHR) % len(self.PHT)
        return self.PHT[index] >= 2  # Predict taken if counter is 2 or more

    def update(self, pc, taken):
        index = (pc ^ self.GHR) % len(self.PHT)
        if taken:
            self.PHT[index] = min(self.PHT[index] + 1, 3)  # Increase counter
        else:
            self.PHT[index] = max(self.PHT[index] - 1, 0)  # Decrease counter
        # Update the Global History Register
        self.GHR = ((self.GHR << 1) | taken) & ((1 << self.history_bits) - 1)


class PerceptronPredictor:
    def __init__(self, num_weights, history_length):
        self.history_length = history_length
        self.history = [0] * history_length  # Initialize global history
        self.weights = np.zeros((num_weights, history_length))  # Initialize perceptron weights

    def predict(self, pc):
        index = pc % len(self.weights)
        prediction = np.dot(self.weights[index], self.history)
        return prediction >= 0  # Predict taken if the sum is non-negative

    def update(self, pc, taken):
        index = pc % len(self.weights)
        prediction = np.dot(self.weights[index], self.history) >= 0
        if prediction != taken:
            adjustment = [1 if taken else -1]
            self.weights[index] += np.array(adjustment) * np.array(self.history)
        # Update the global history
        self.history.pop(0)
        self.history.append(1 if taken else -1)


class LocalHistoryPredictor:
    def __init__(self, history_bits=4, table_size=1024):
        self.history_bits = history_bits
        self.local_history_table = [0] * table_size  # Local history registers
        self.pattern_history_table = [1] * table_size  # Pattern History Table (2-bit counters)

    def predict(self, pc):
        local_history = self.local_history_table[pc % len(self.local_history_table)]
        index = (local_history << self.history_bits) % len(self.pattern_history_table)
        return self.pattern_history_table[index] >= 2  # Predict taken if counter is 2 or more

    def update(self, pc, taken):
        local_history_index = pc % len(self.local_history_table)
        local_history = self.local_history_table[local_history_index]
        pht_index = (local_history << self.history_bits) % len(self.pattern_history_table)

        # Update pattern history table
        if taken:
            self.pattern_history_table[pht_index] = min(self.pattern_history_table[pht_index] + 1, 3)
        else:
            self.pattern_history_table[pht_index] = max(self.pattern_history_table[pht_index] - 1, 0)

        # Update local history
        self.local_history_table[local_history_index] = ((local_history << 1) | taken) & ((1 << self.history_bits) - 1)

class TAGEPredictor:
    def __init__(self, num_components=4, table_size=1024, history_lengths=None):
        """
        A simplified TAGE (Tagged Geometric History Length) branch predictor.
        - num_components: Number of predictor tables (components).
        - table_size: Number of entries in each table.
        - history_lengths: List of history lengths for each component table.
        """
        self.num_components = num_components
        self.table_size = table_size
        self.history_lengths = history_lengths or [4, 8, 16, 32]
        self.components = [{} for _ in range(num_components)]  # Simulate tagged tables

    def predict(self, pc):
        """
        Predicts branch outcome based on PC and history tables.
        - pc: Program counter (address).
        """
        for i, table in enumerate(self.components):
            tag = (pc >> self.history_lengths[i]) % self.table_size
            if tag in table:
                return table[tag] >= 0  # Predict taken if counter >= 0
        return True  # Default prediction is taken

    def update(self, pc, taken):
        """
        Updates the predictor tables based on actual outcome.
        - pc: Program counter (address).
        - taken: True if branch was taken, False otherwise.
        """
        for i, table in enumerate(self.components):
            tag = (pc >> self.history_lengths[i]) % self.table_size
            if tag in table:
                table[tag] += 1 if taken else -1  # Increment or decrement counter
                table[tag] = max(-3, min(3, table[tag]))  # Saturate to [-3, 3]
                return
        # Insert a new entry in the first available table
        tag = (pc >> self.history_lengths[0]) % self.table_size
        self.components[0][tag] = 1 if taken else -1
