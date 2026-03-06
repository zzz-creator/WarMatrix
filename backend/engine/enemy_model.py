import numpy as np

# Stochastic enemy behavior. We provide both a single-sample function
# `enemy_action()` (used by MCTS and other single-step callers) and a
# vectorized `sample_enemy_actions()` helper used by Monte Carlo rollouts.

_ENEMY_ACTIONS = ["hold", "counterattack", "artillery", "retreat"]

# Probabilities as requested: hold 0.35, counterattack 0.30, artillery 0.20, retreat 0.15
_PROBS = np.array([0.35, 0.30, 0.20, 0.15], dtype=float)
_PROBS = _PROBS / _PROBS.sum()


def enemy_action(rng: np.random.Generator = None) -> str:
    """Return a single sampled enemy action string using weighted probabilities."""
    if rng is None:
        # use global numpy RNG
        return np.random.choice(_ENEMY_ACTIONS, p=_PROBS)
    else:
        return rng.choice(_ENEMY_ACTIONS, p=_PROBS)


def sample_enemy_actions(n: int, rng: np.random.Generator = None) -> np.ndarray:
    """Vectorized sampling: returns an array of length `n` of enemy action strings."""
    if rng is None:
        rng = np.random.default_rng()
    return rng.choice(_ENEMY_ACTIONS, size=n, p=_PROBS)
