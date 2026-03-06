from fastapi import APIRouter

from engine.game_state import GameState, get_state, update_state
from engine.transition import apply_action
from engine.monte_carlo import run_monte_carlo
from engine.mcts import run_mcts
from engine.strategy import strategic_override

router = APIRouter()


class SimulationRequest(GameState):
    action: str


@router.post("/simulate_turn")
def simulate_turn(payload: dict):

    action = payload.get("action")

    if not action:
        return {"error": "No action provided"}

    # Get current battlefield state
    state = get_state()

    # Apply player action
    state = apply_action(state, action)

    # Run Monte Carlo simulation
    sim = run_monte_carlo(state)

    # Strategic rule layer
    override = strategic_override(state)

    if override:
        best_action = override
    else:
        best_action = run_mcts(state)

    # Update state with simulation results
    state.success_probability = sim["expected_success"]
    state.operational_risk = sim["expected_risk"]

    # Save updated state
    update_state(state)

    return {
        "state": state.dict(),
        "simulation": sim,
        "recommended_next_action": best_action
    }