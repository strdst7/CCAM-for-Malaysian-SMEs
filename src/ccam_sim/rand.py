"""Seeded RNG manager — deterministic random number generation for simulation.

Every simulation run creates an isolated random.Random(seed) instance.
Engines NEVER call random.seed(), random.random() — they always use
the injected instance via SimState.rng.
"""

import random


def create_rng(seed: int) -> random.Random:
    """Create an isolated random.Random instance from a deterministic seed.

    Args:
        seed: Integer seed for deterministic reproducibility.
             Must be hashable by random.Random (int, float, str, bytes, bytearray, None).

    Returns:
        random.Random instance seeded deterministically.

    Raises:
        TypeError: If seed is not a valid random.Random seed type.
    """
    if not isinstance(seed, (int, float, str, bytes, bytearray)):
        raise TypeError(f"seed must be int, float, str, bytes, or bytearray, got {type(seed).__name__}")
    return random.Random(seed)
