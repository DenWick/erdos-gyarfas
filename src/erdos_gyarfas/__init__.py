"""Tools for testing the Erdős–Gyárfás conjecture on concrete graphs."""

from .cycles import (
    cycle_spectrum,
    find_cycle_of_length,
    is_power_of_two,
    power_of_two_cycles,
    powers_of_two_up_to,
)
from .graph import Graph
from .named_graphs import NAMED, markstrom, petersen

__all__ = [
    "Graph",
    "NAMED",
    "cycle_spectrum",
    "find_cycle_of_length",
    "is_power_of_two",
    "markstrom",
    "petersen",
    "power_of_two_cycles",
    "powers_of_two_up_to",
]
__version__ = "1.0.0"
