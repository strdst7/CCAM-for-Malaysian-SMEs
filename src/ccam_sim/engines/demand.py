"""Demand generator — Poisson process synthetic customer arrivals."""

from ccam_sim.models import SimState, DemandArrival


def demand_generator(state: SimState) -> SimState:
    """Generate synthetic customer demand via Poisson process."""
    rng = state.rng
    scenario = state.scenario

    for block in scenario.demand_pattern:
        rate = float(block.rate)
        if rate <= 0:
            continue

        block_start_us = int(block.start_hour * 3_600_000_000)
        block_end_us = int(block.end_hour * 3_600_000_000)
        sim_end_us = int(scenario.simulation.total_hours * 3_600_000_000)

        actual_end_us = min(block_end_us, sim_end_us)

        t = block_start_us
        while t < actual_end_us:
            mean_seconds = 3600.0 / rate
            if mean_seconds <= 0:
                break
            interarrival_seconds = rng.expovariate(1.0 / mean_seconds)
            interarrival_us = int(interarrival_seconds * 1_000_000)
            if interarrival_us < 1:
                interarrival_us = 1

            t += interarrival_us
            if t < actual_end_us:
                state.events.append(DemandArrival(time_us=t))

    return state
