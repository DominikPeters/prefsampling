import numpy as np

from prefsampling.decorators import validate_num_voters_candidates


@validate_num_voters_candidates
def urn(
    num_voters: int, num_candidates: int, alpha: float = 0.1, seed: int = None
) -> np.ndarray:
    """
    Generates votes following the Pólya-Eggenberger urn culture. The process is as follows. The urn
    is initially empty and votes are generated one after the other, in turns. When generating a
    vote, the following happens. With a probability of 1/(urn_size + 1), the vote is selected
    uniformly at random (following an impartial culture). With probability `1/urn_size` a vote
    from the urn is selected uniformly at random. In both cases, the vote is put back in the urn
    together with `alpha * m!` copies of the vote (where `m` is the number of candidates).

    Parameters
    ----------
        num_voters: int
            Number of voters
        num_candidates: int
            Number of candidates
        alpha: float
            The dispersion coefficient (`alpha * m!` copies of a vote are put back in the urn after
            a draw). Must be non-negative.
        seed: int
            The seed for the random number generator.

    Returns
    -------
        np.ndarray
            The votes
    """

    if alpha < 0:
        raise ValueError("Alpha needs to be positive for an urn model.")

    rng = np.random.default_rng(seed)
    votes = np.zeros((num_voters, num_candidates), dtype=int)
    urn_size = 1.0
    for i in range(num_voters):
        rho = rng.uniform(0, urn_size)
        if rho <= 1.0:
            votes[i] = rng.permutation(num_candidates)
        else:
            votes[i] = votes[rng.integers(0, i)]
        urn_size += alpha

    return votes
