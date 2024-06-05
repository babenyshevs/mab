from typing import Any, Dict, List

import numpy as np
from mabwiser.mab import MAB, LearningPolicy

from src.data.reward_generator import RewardGenerator


class MultiArmedBandit:
    """
    Class to fit a multi-armed bandit model using the mabwiser package.
    """

    def __init__(
        self, reward_generator: RewardGenerator, config: Dict[str, Any], seed: int = 42
    ) -> None:
        """
        Initialize the MultiArmedBandit.

        Args:
            reward_generator (RewardGenerator): An instance of RewardGenerator to generate rewards.
            config (Dict[str, Any]): Configuration parameters for the bandit method.
            seed (int): Seed for random number generation (default is 42).
        """
        self.rg = reward_generator
        self.arm_ids = list(reward_generator.arm_configs.keys())
        self.config = config
        self.seed = seed
        self.bandit = None

    def fit(self, num_rounds: int) -> None:
        """
        Fit a multi-armed bandit model using the provided reward generator.

        Args:
            num_rounds (int): The number of rounds to run the bandit algorithm.
        """
        self.rounds_log, self.arms_log, self.rewards_log = self.rg.generate_trials(num_rounds)

        if self.config["method"] == "epsilon_greedy":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.EpsilonGreedy(**self.config["method_params"]),
                seed=self.seed,
            )
        elif self.config["method"] == "softmax":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.Softmax(**self.config["method_params"]),
                seed=self.seed,
            )
        elif self.config["method"] == "ucb":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.UCB1(**self.config["method_params"]),
                seed=self.seed,
            )
        elif self.config["method"] == "thompson_sampling":

            def binary_func(decision, reward):
                """
                Binarizing function as Thompson algorithm expects Bernoulli distribution.

                Args:
                    decision (Any): The decision made by the algorithm.
                    reward (float): The reward received for the decision.

                Returns:
                    int: Binarized reward (1 for success, 0 for failure).
                """
                decision_to_threshold = {arm: 0.5 for arm in self.arm_ids}
                return 1 if reward > decision_to_threshold[decision] else 0

            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.ThompsonSampling(binarizer=binary_func),
                seed=self.seed,
            )
        else:
            raise ValueError(f"Unsupported bandit method: '{self.method}'")

        self.bandit.fit(self.arms_log, self.rewards_log)

        # Keep logs
        self.expectations_log = {
            arm: [np.round(expectation, 2)] * num_rounds
            for arm, expectation in self.bandit.predict_expectations().items()
        }
        self.arm_pull_cum_log = {arm: [] for arm in self.arm_ids}  # how many times arms was pulled
        self.arm_reward_cum_log = {
            arm: [] for arm in self.arm_ids
        }  # cumulative reward it generated
        self.arm_reward_log = {arm: [] for arm in self.arm_ids}  # reward it generated

        self._update_logs(self.arms_log, self.rewards_log)

    def _update_logs(self, arms_pulled: List[Any], rewards: List[float]) -> None:
        """
        Update cumulative logs based on historical data.

        This method updates the cumulative logs for each arm based on historical data.

        Args:
            arms_pulled (List[Any]): List of arms pulled in each round.
            rewards (List[float]): List of rewards received in each round.

        """
        for arm_pulled, reward in zip(arms_pulled, rewards):
            for arm in self.arm_ids:

                # take last value from history or 0 if there is no history (empty list)
                prev_arm = self.arm_pull_cum_log[arm][-1] if self.arm_pull_cum_log[arm] else 0
                prev_reward = (
                    self.arm_reward_cum_log[arm][-1] if self.arm_reward_cum_log[arm] else 0
                )

                # increment value of pulled arm, for others use value of previous step;
                # this is because at each step only 1 arm was pulled, but
                # we need to keep timeline equal for all arms (to plot it on 1 graph),
                # hence is usage of last value of unpulled arms
                if arm == arm_pulled:
                    self.arm_pull_cum_log[arm].append(prev_arm + 1)
                    self.arm_reward_cum_log[arm].append(prev_reward + reward)
                    self.arm_reward_log[arm].append(reward)
                else:
                    self.arm_pull_cum_log[arm].append(prev_arm)
                    self.arm_reward_cum_log[arm].append(prev_reward)
                    self.arm_reward_log[arm].append(0)

    def next_round(self) -> None:
        """
        Perform the next round of the bandit algorithm.
        """
        if self.bandit is None:
            raise ValueError(
                "Bandit model has not been trained yet. Please call fit() method first."
            )

        chosen_arm = self.bandit.predict()
        reward = self.rg.pull_arm(chosen_arm)
        self.bandit.partial_fit([chosen_arm], [reward])
        self.arms_log.append(chosen_arm)
        self.rewards_log.append(reward)

        for arm, expectation in self.bandit.predict_expectations().items():
            self.expectations_log[arm].append(np.round(expectation, 4))

        self._update_logs([chosen_arm], [reward])

    def run_n_rounds(self, num_rounds: int) -> None:
        """
        Run the bandit algorithm for a specified number of rounds.

        Args:
            num_rounds (int): The number of rounds to run the bandit algorithm.
        """
        for _ in range(num_rounds):
            self.next_round()


# Example usage:
if __name__ == "__main__":
    # Assuming you have a configured RewardGenerator and a configuration dictionary
    reward_generator = RewardGenerator()  # Initialize with appropriate parameters
    config = {"method": "epsilon_greedy", "method_params": {"epsilon": 0.1}}
    bandit = MultiArmedBandit(reward_generator, config)

    # Fit the model
    bandit.fit(num_rounds=100)

    # Run additional rounds
    bandit.run_n_rounds(num_rounds=50)

    # Access logs or other relevant information
    print("Arms log:", bandit.arms_log)
    print("Rewards log:", bandit.rewards_log)
    print("Expectations log:", bandit.expectations_log)
    print("Arm cumulative log:", bandit.arm_pull_cum_log)
    print("Reward cumulative log:", bandit.arm_reward_cum_log)
