from copy import deepcopy
from typing import Union
import numpy as np

from .game_state import GameState
from .probability import compute_success_probability


def _clamp_value(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def apply_action(state: GameState, action: str) -> GameState:
    """
    Apply a player action and return updated GameState.
    """

    s = deepcopy(state)

    if action == "RECON":
        s.communications = _clamp_value(s.communications + 0.06)
        s.operational_risk = _clamp_value(s.operational_risk - 0.04)

    elif action == "ARTILLERY_STRIKE":
        s.fires = _clamp_value(s.fires + 0.12)
        s.supply = _clamp_value(s.supply - 0.05)
        s.operational_risk = _clamp_value(s.operational_risk + 0.04)

    elif action == "ADVANCE":
        s.force_ratio = _clamp_value(s.force_ratio + 0.06)
        s.morale = _clamp_value(s.morale + 0.04)
        s.operational_risk = _clamp_value(s.operational_risk + 0.03)

    elif action == "DEFEND":
        s.operational_risk = _clamp_value(s.operational_risk - 0.10)
        s.morale = _clamp_value(s.morale + 0.02)
        s.mobility = _clamp_value(s.mobility - 0.02)

    s.success_probability = compute_success_probability(s)

    return s.clamp()


def apply_enemy_action(state: Union[GameState, dict], enemy_action: str) -> GameState:

    if not isinstance(state, GameState):
        state = GameState(**state)

    s = deepcopy(state)

    if enemy_action == "hold":
        s.supply = _clamp_value(s.supply - 0.01)

    elif enemy_action == "counterattack":
        s.operational_risk = _clamp_value(s.operational_risk + 0.06)
        s.morale = _clamp_value(s.morale - 0.05)
        s.supply = _clamp_value(s.supply - 0.04)

    elif enemy_action == "artillery":
        s.supply = _clamp_value(s.supply - 0.06)
        s.morale = _clamp_value(s.morale - 0.04)
        s.operational_risk = _clamp_value(s.operational_risk + 0.04)

    elif enemy_action == "retreat":
        s.force_ratio = _clamp_value(s.force_ratio + 0.05)
        s.morale = _clamp_value(s.morale + 0.03)

    s.success_probability = compute_success_probability(s)

    return s.clamp()


def state_to_array(state: GameState) -> np.ndarray:

    return np.array(
        [
            state.morale,
            state.supply,
            state.operational_risk,
            state.success_probability,
            state.mobility,
            state.communications,
            state.fires,
            state.force_ratio,
        ],
        dtype=float,
    )


def array_to_state(arr: np.ndarray) -> GameState:

    return GameState(
        morale=float(arr[0]),
        supply=float(arr[1]),
        operational_risk=float(arr[2]),
        success_probability=float(arr[3]),
        mobility=float(arr[4]),
        communications=float(arr[5]),
        fires=float(arr[6]),
        force_ratio=float(arr[7]),
    )