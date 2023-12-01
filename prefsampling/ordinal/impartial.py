import math

import numpy as np

from prefsampling.decorators import validate_num_voters_candidates
from prefsampling.ordinal.urn import urn


@validate_num_voters_candidates
def impartial(num_voters: int, num_candidates: int, seed: int = None) -> np.ndarray:
    """
    Generates ordinal votes from impartial culture.

    In an impartial culture, all votes are equally likely to occur. In this function, each vote is
    generated by getting a random permutation of the candidates from the random number generator.

    Parameters
    ----------
    num_voters : int
        Number of Voters.
    num_candidates : int
        Number of Candidates.
    seed : int
        Seed for numpy random number generator.

    Returns
    -------
    np.ndarray
        Ordinal votes.
    """
    rng = np.random.default_rng(seed)
    votes = np.zeros([num_voters, num_candidates], dtype=int)
    for i in range(num_voters):
        votes[i] = rng.permutation(num_candidates)
    return votes


@validate_num_voters_candidates
def impartial_anonymous(
    num_voters: int, num_candidates: int, seed: int = None
) -> np.ndarray:
    """
    Generates ordinal votes from impartial anonymous culture.

    In an impartial anonymous culture, every multi-set of votes is equally likely to occur. For
    instance with 3 voters and 2 candidates, the probability of observing `a > b, a > b, a > b`
    is 1/4. This probability was 1/8 according to the impartial (but not-anonymous) culture.

    Votes are generated by sampling from an urn model (using :py:func:`~prefsampling.ordinal.urn`)
    with parameter `alpha = 1` (see Lepelley, Valognes 2003).

    Parameters
    ----------
    num_voters : int
        Number of Voters.
    num_candidates : int
        Number of Candidates.
    seed : int
        Seed for numpy random number generator.

    Returns
    -------
    np.ndarray
        Ordinal votes.
    """
    return urn(
        num_voters, num_candidates, alpha=1 / math.factorial(num_candidates), seed=seed
    )


@validate_num_voters_candidates
def stratification(
    num_voters: int, num_candidates: int, weight: float = 0.5, seed: int = None
) -> np.ndarray:
    """
    Generates ordinal votes from stratification model.

    Parameters
    ----------
    num_voters : int
        Number of Voters.
    num_candidates : int
        Number of Candidates.
    weight : float
        Size of the upper class.
    seed : int
        Seed for numpy random number generator.

    Returns
    -------
    np.ndarray
        Ordinal votes.
    """
    rng = np.random.default_rng(seed)
    votes = np.zeros((num_voters, num_candidates), dtype=int)
    upper_class_size = int(weight * num_candidates)
    upper_class_candidates = range(upper_class_size, num_candidates)
    for i in range(num_voters):
        votes[i][:upper_class_size] = rng.permutation(upper_class_size)
        votes[i][upper_class_size:] = rng.permutation(upper_class_candidates)
    return votes
