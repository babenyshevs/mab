from typing import List, Union

import numpy as np
from numpy.random import choice


def bootstrap(
    data: np.ndarray,
    variable: str = None,
    bias: float = 0,
    repeats: int = 1000,
    sample: Union[str, int, None] = None,
) -> List[float]:
    """
    Bootstrap resampling for estimating the distribution of sample statistics.

    Args:
        data (np.ndarray): The dataset.
        variable (str): The variable of interest within the dataset.
        bias (float, optional): A bias term to add to the resampled means. Defaults to 0.
        repeats (int, optional): The number of bootstrap resampling iterations. Defaults to 1000.
        sample (Union[str, int, None], optional): The method or size of sampling.
            If "root", sample size is square root of data size.
            If "log", sample size is logarithm of data size.
            If int, sample size is explicitly specified.
            Defaults to None, where sample size is equal to data size.

    Returns:
        List[float]: List of resampled means.
    """
    if variable:
        data = data[variable].to_list()

    if sample == "root":
        sample_size = int(len(data) ** 0.5)
    elif sample == "log":
        sample_size = int(np.log(len(data)))
    elif isinstance(sample, int):
        sample_size = sample
    else:
        sample_size = len(data)

    means = []
    for _ in range(repeats):
        arr = choice(a=data, size=sample_size, replace=True)
        mean = np.mean(arr) + bias
        means.append(mean)
    return means
