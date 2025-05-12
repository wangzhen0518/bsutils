"""
Author       : wangzhen0518 wangzhen0518@126.com
Date         : 2025-05-09 19:40 +0800
LastEditors  : wangzhen0518 wangzhen0518@126.com
LastEditTime : 2025-05-12 11:11 +0800
FilePath     : random.py
Description  :

"""

# Supported set of random number generation libraries:
# "random" (Python built-in random module), "torch" (PyTorch), "numpy" (NumPy)
ALL_SET = {"random", "torch", "numpy"}


def set_seed(seed: int, include: set[str] | None = None, exclude: set[str] | None = None):
    """Set random seeds to ensure reproducible experiments.

    Args:
        seed (int): Random seed value. Accepts all integers, but values in 0-2^32-1 range are recommended
                   as some libraries may have this limitation.
        include (set[str] | None): Specify which libraries to set seeds for. Optional, defaults to None.
                                   When None, uses all libraries in ALL_SET.
                                   Supported library names: "random", "torch", "numpy".
                                   Example: {"random", "numpy"} will only set seeds for random and numpy.
        exclude (set[str] | None): Specify which libraries to exclude. Optional, defaults to None.
                                   When include is None, excludes specified libraries from ALL_SET;
                                   When include is not None, excludes from the include set.
                                   Supported library names same as include parameter.
                                   Example: {"torch"} will skip setting torch seeds.
        Examples:
        >>> # Basic usage - set seeds for all supported libraries
        >>> set_seed(42)

        >>> # Set seeds only for random and numpy
        >>> set_seed(42, include={"random", "numpy"})

        >>> # Set seeds for all except torch
        >>> set_seed(42, exclude={"torch"})
    """
    # Determine final set of libraries to seed
    final_set = include if include else ALL_SET
    if exclude:
        final_set -= exclude

    # Set random module seed
    if "random" in final_set:
        import random

        random.seed(seed)

    # Set torch seeds (including CUDA)
    if "torch" in final_set:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    # Set numpy seed
    if "numpy" in final_set:
        import numpy as np

        np.random.seed(seed)
