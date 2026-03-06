def strategic_override(state):
    """
    Strategic rule layer.

    Used before Monte Carlo / MCTS to enforce
    basic battlefield logic.
    """

    # High battlefield danger → defend
    if state.operational_risk > 0.75:
        return "DEFEND"

    # Poor intelligence → recon first
    if state.communications < 0.40:
        return "RECON"

    # Strong firepower + advantage → attack
    if state.fires > 0.80 and state.force_ratio > 0.65:
        return "ADVANCE"

    # Otherwise allow AI planner
    return None