from typing import Any, Dict, List

import numpy as np
from mabwiser.mab import MAB, LearningPolicy

from src.data.reward_generator import RewardGenerator


class MultiArmedBandit:
    """
    Class to fit a multi-armed bandit model using the mabwiser package.
    """

    SEED: int = 42

    def __init__(
        self, reward_generator: RewardGenerator, method: str, method_params: Dict[str, Any] = {}
    ) -> None:
        """
        Initialize the MultiArmedBandit.

        Args:
            reward_generator (RewardGenerator): An instance of RewardGenerator to generate rewards.
            method (str): The name of the bandit method to use (e.g., 'epsilon_greedy', 'softmax', 'ucb', 'thompson_sampling').
            method_params (Dict[str, Any]): Additional parameters specific to the bandit method.
        """
        self.rg = reward_generator
        self.method = method
        self.method_params = method_params
        self.bandit = None  # Initialize bandit object
        self.arm_ids = list(reward_generator.arm_configs.keys())

    def fit(self, num_rounds: int) -> None:
        """
        Fit a multi-armed bandit model using the provided reward generator.

        Args:
            num_rounds (int): The number of rounds to run the bandit algorithm.
        """

        self.rounds_log, self.arms_log, self.rewards_log = self.rg.generate_trials(num_rounds)

        if self.method == "epsilon_greedy":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.EpsilonGreedy(**self.method_params),
                seed=self.SEED,
            )
        elif self.method == "softmax":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.Softmax(**self.method_params),
                seed=self.SEED,
            )
        elif self.method == "ucb":
            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.UCB1(**self.method_params),
                seed=self.SEED,
            )
        elif self.method == "thompson_sampling":

            def binary_func(decision, reward):
                decision_to_threshold = {arm: 0.5 for arm in self.arm_ids}
                return 1 if reward > decision_to_threshold[decision] else 0

            self.bandit = MAB(
                arms=self.arm_ids,
                learning_policy=LearningPolicy.ThompsonSampling(binarizer=binary_func),
                seed=self.SEED,
            )
        else:
            raise ValueError(f"Unsupported bandit method: '{self.method}'")

        self.bandit.fit(self.arms_log, self.rewards_log)

        # Keep history
        # expectations
        self.expectations_log = {
            arm: [np.round(expectation, 2)] * num_rounds
            for arm, expectation in self.bandit.predict_expectations().items()
        }

        # cumultives
        self.arm_cum_log = {arm: [] for arm in self.arm_ids}
        self.reward_cum_log = {arm: [] for arm in self.arm_ids}
        self._update_cumulatives(self.rounds_log, self.arms_log, self.rewards_log, init_mode=True)

    def _update_cumulatives(
        self, rounds: List[int], arms_pulled: List[Any], rewards: List[float], init_mode=False
    ) -> None:
        """
        Update cumulative logs based on historical data.

        This method updates the cumulative logs for each arm based on historical data.

        Args:
            rounds (List[int]): List of round numbers.
            arms_pulled (List[Any]): List of arms pulled in each round.
            rewards (List[float]): List of rewards received in each round.

        """

        for _, arm_pulled, reward in zip(rounds, arms_pulled, rewards):
            for arm in self.arm_ids:
                prev_arm = self.arm_cum_log[arm][-1] if self.arm_cum_log[arm] else 0
                prev_reward = self.reward_cum_log[arm][-1] if self.reward_cum_log[arm] else 0
                if arm == arm_pulled:

                    self.arm_cum_log[arm].append(prev_arm + 1)
                    self.reward_cum_log[arm].append(prev_reward + reward)
                else:
                    self.arm_cum_log[arm].append(prev_arm)
                    self.reward_cum_log[arm].append(prev_reward)

    def next_round(self) -> None:
        """
        Perform the next round of the bandit algorithm.

        Args:
            round_number (int): The number of the current round.
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

        self._update_cumulatives([1], [chosen_arm], [reward])

    def run_n_rounds(self, num_rounds: int) -> None:
        """
        Run the bandit algorithm for a specified number of rounds.

        Args:
            num_rounds (int): The number of rounds to run the bandit algorithm.
        """
        for _ in range(num_rounds):
            self.next_round()
