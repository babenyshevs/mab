import random
from typing import Any, Dict, List, Tuple

import numpy as np


class RewardGenerator:
    """
    Class to generate rewards for a multi-armed bandit problem.
    """

    def __init__(self, config: Dict[str, Dict[str, Any]]) -> None:
        """
        Initialize the RewardGenerator.

        Args:
            config (Dict[str, Dict[str, Any]]): A dictionary containing configurations
                for each arm. Each key is the arm identifier, and the value is a dictionary
                containing 'distribution' and 'params' for that arm.
        """
        self.arm_configs = config
        self.distributions = {
            "gauss": random.gauss,
            "uniform": random.uniform,
            # Add more distribution functions here as needed
        }

    def pull_arm(self, arm_id: str) -> float:
        """
        Pull an arm of the bandit and return the reward.

        Args:
            arm_id (str): The identifier of the arm to pull.

        Returns:
            float: The reward generated by pulling the arm.

        Raises:
            ValueError: If the arm ID is not found in the configuration.
            ValueError: If the specified distribution is not supported.
        """
        if arm_id not in self.arm_configs:
            raise ValueError(f"Arm '{arm_id}' not found in configuration")

        arm_config = self.arm_configs[arm_id]
        distribution_name = arm_config["distribution"]
        if distribution_name not in self.distributions:
            raise ValueError(f"Unsupported distribution: '{distribution_name}'")

        distribution_function = self.distributions[distribution_name]
        params = arm_config.get("params", [])
        reward = np.round(distribution_function(*params), 4)

        return reward

    def pull_arm_n_times(self, arm_id: str, n_times: int) -> List[float]:
        """
        Pull a given arm multiple times and return the rewards obtained.

        Args:
            arm_id (str): The identifier of the arm to pull multiple times.
            n_times (int): The number of times to pull the arm.

        Returns:
            List[float]: A list of rewards obtained from pulling the arm.

        Raises:
            ValueError: If the arm ID is not found in the configuration.
        """
        if arm_id not in self.arm_configs:
            raise ValueError(f"Arm '{arm_id}' not found in configuration")

        rewards = []
        for _ in range(n_times):
            reward = self.pull_arm(arm_id)
            rewards.append(reward)

        return rewards

    def generate_trials(self, num_trials: int) -> Tuple[List[str], List[float]]:
        """
        Generate trials during the exploration phase.

        Args:
            num_trials (int): The number of trials to generate.

        Returns:
            Tuple[List[str], List[float]]: Two lists, one containing the arms pulled
                and the other containing the corresponding rewards.
        """
        rounds = []
        arms_pulled = []
        rewards = []

        for trial in range(num_trials):
            arm_id = random.choice(list(self.arm_configs.keys()))
            reward = self.pull_arm(arm_id)
            rounds.append(trial)
            arms_pulled.append(arm_id)
            rewards.append(reward)

        return rounds, arms_pulled, rewards


# # Example usage
# config = {
#     "arm1": {"distribution": "gauss", "params": [10, 2]},  # Mean = 10, Std Dev = 2
#     "arm2": {"distribution": "uniform", "params": [5, 15]},  # Min = 5, Max = 15
#     "arm3": {"distribution": "gauss", "params": [5, 1]},  # Mean = 5, Std Dev = 1
# }

# reward_generator = RewardGenerator(config)

# # Pull arms and get rewards
# arm1_reward = reward_generator.pull_arm("arm1")
# arm2_reward = reward_generator.pull_arm("arm2")
# arm3_reward = reward_generator.pull_arm("arm3")

# print("Reward for arm1:", arm1_reward)
# print("Reward for arm2:", arm2_reward)
# print("Reward for arm3:", arm3_reward)


# # Generate exploration phase trials
# num_trials = 100
# arms_pulled, rewards = reward_generator.generate_trials(num_trials)

# # Print the arms pulled and their corresponding rewards
# print("Exploration Phase Trials:")
# for arm, reward in zip(arms_pulled, rewards):
#     print("Arm Pulled:", arm, "- Reward:", reward)
