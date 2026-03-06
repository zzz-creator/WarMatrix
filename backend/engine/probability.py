from .game_state import GameState


def compute_success_probability(state: GameState, environment_factor: float = 0.0) -> float:
    """
    Weighted battlefield success model.

    Offensive capability slightly outweighs moderate risk.
    """

    fr = float(state.force_ratio)
    morale = float(state.morale)
    supply = float(state.supply)
    fires = float(state.fires)
    comms = float(state.communications)
    mobility = float(state.mobility)
    risk = float(state.operational_risk)

    val = (
        0.30 * fr
        + 0.20 * morale
        + 0.15 * supply
        + 0.18 * fires
        + 0.08 * comms
        + 0.09 * mobility
        - 0.10 * risk
        + 0.05 * float(environment_factor)
    )

    return max(0.0, min(1.0, val))