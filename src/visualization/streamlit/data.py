import numpy as np

from src.data.reward_generator import RewardGenerator
from src.models.mab import MultiArmedBandit


def generate_data(
    trials: int,
    exploration_share: float,
    algorithms: list[str],
    arm_ids: list[str],
    reward_generator: RewardGenerator,
    bandit: MultiArmedBandit,
) -> dict[str, dict[str, dict[int, np.ndarray]]]:
    """
    Generate data for A/B testing and Multi-Armed Bandit (MAB) algorithms.

    This function simulates the performance of two different algorithms
    (A/B testing and a Multi-Armed Bandit) over a specified period and
    returns their respective reward data.

    Args:
        trials (int): The number of trials to generate for the A/B test.
        exploration_share (float): The fraction of trials dedicated to exploration in the MAB algorithm.
        algorithms (list[str]): A list containing the names of the algorithms.
        arm_ids (list[str]): A list of arm IDs to be used in the simulation.
        reward_generator (RewardGenerator): An instance of the RewardGenerator class.
        bandit (MultiArmedBandit): An instance of the MultiArmedBandit class.

    Returns:
        dict[str, dict[str, dict[int, np.ndarray]]]: A dictionary containing the reward data for both algorithms.

    Example:
        >>> reward_gen = RewardGenerator()
        >>> mab = MultiArmedBandit()
        >>> data = generate_data(
        ...     trials=1000,
        ...     exploration_share=0.1,
        ...     algorithms=['AB', 'MAB'],
        ...     arm_ids=["1", "2", "3"],
        ...     reward_generator=reward_gen,
        ...     bandit=mab
        ... )
        >>> print(data['AB']['y'])
    """
    data = {
        algorithm: {"y": {}, "y_cumulative": {}, "trials_count_cumulative": {}}
        for algorithm in algorithms
    }

    # A/B data (algos[0])
    for arm_id in arm_ids:
        arm_data = reward_generator.pull_arm_n_times(arm_id, trials)
        data[algorithms[0]]["y"][arm_id] = arm_data
        data[algorithms[0]]["y_cumulative"][arm_id] = np.cumsum(arm_data)
        data[algorithms[0]]["trials_count_cumulative"][arm_id] = np.arange(0, trials, 1)

    # Bandit data (algos[1])
    mab_trials = trials * len(arm_ids)  # because in MAB only 1 arm is pulled per trial
    explore_rounds = int(mab_trials * exploration_share)
    bandit.fit(explore_rounds)
    bandit.run_n_rounds(mab_trials - explore_rounds)
    data[algorithms[1]]["y"] = bandit.arm_reward_log
    data[algorithms[1]]["y_cumulative"] = bandit.arm_reward_cum_log
    data[algorithms[1]]["trials_count_cumulative"] = bandit.arm_pull_cum_log

    return data
