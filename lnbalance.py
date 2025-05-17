
import numpy as np

def random_bimodal(c, s=None, size=1, random_state=None):
    """
    Draw samples from the PDF P(x) = (exp(-x/s) + exp((x-c)/s)) / [2 s (1 - exp(-c/s))],
    for x in [0, c].

    Parameters
    ----------
    c : float
        Upper bound of support (c > 0).
    s : float
        Scale parameter (0 < s < c).
    size : int
        Number of samples to draw.
    random_state : None, int, or np.random.Generator
        Seed, Generator, or None for default RNG.

    Returns
    -------
    samples : ndarray
        Array of shape (size,) of draws from the target distribution.
    """
    # Set up RNG
    if isinstance(random_state, np.random.Generator):
        rng = random_state
    else:
        rng = np.random.default_rng(random_state)

    if s is None:
        s = c / 10
        
    # Precompute truncation constant
    u_max = 1.0 - np.exp(-c / s)

    # Decide mixture components
    coin = rng.random(size) < 0.5

    # Uniforms for inversion
    u = rng.random(size)

    # Inverse CDF of truncated Exp(1/s): 
    #  x = -s * ln(1 - u * (1 - e^{-c/s}))
    t = -s * np.log1p(-u * u_max)

    # Allocate result
    x = np.empty(size)
    # Heads: direct
    x[coin] = t[coin]
    # Tails: mirror
    x[~coin] = c - t[~coin]

    return x



def random_quadratic(c, size=1, random_state=None):
    """
    Sample from PDF P(x) ∝ (x - c/2)^2 on [0, c] via inverse‐transform.

    Parameters
    ----------
    c : float
        Upper bound of support (c > 0).
    size : int
        Number of samples.
    random_state : None, int, or np.random.Generator
        RNG or seed.

    Returns
    -------
    samples : ndarray of shape (size,)
    """
    # RNG setup
    if isinstance(random_state, np.random.Generator):
        rng = random_state
    else:
        rng = np.random.default_rng(random_state)

    # Uniform variates
    u = rng.random(size)

    # Inverse CDF: handle cube root of negative values correctly
    v = (c**3 / 4) * (u - 0.5)
    # cube‐root preserving sign
    t = np.sign(v) * np.abs(v)**(1/3)

    return c/2 + t
