import numpy as np
import random

from .probability import compute_success_probability
from .enemy_model import enemy_action
from .actions import ACTIONS
from .transition import apply_action, apply_enemy_action


def run_monte_carlo(state, rollouts=400, steps=6):

    successes = []

    for _ in range(rollouts):

        sim_state = state.copy()

        player_turn = True

        for _ in range(steps):

            if player_turn:

                # Strategic bias toward offensive moves
                action = random.choices(
                    ACTIONS,
                    weights=[0.25, 0.25, 0.35, 0.15]  # RECON, ARTILLERY, ADVANCE, DEFEND
                )[0]

                sim_state = apply_action(sim_state, action)

            else:

                enemy = enemy_action()
                sim_state = apply_enemy_action(sim_state, enemy)

            sim_state.success_probability = compute_success_probability(sim_state)

            player_turn = not player_turn

        successes.append(sim_state.success_probability)

    successes = np.array(successes)

    expected_success = float(successes.mean())
    expected_risk = float(1 - expected_success)
    uncertainty = float(successes.std())

    return {
        "expected_success": expected_success,
        "expected_risk": expected_risk,
        "uncertainty": uncertainty,
    }