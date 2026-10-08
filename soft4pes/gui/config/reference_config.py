"""Reference configuration for Soft4PES GUI."""

from dataclasses import dataclass
from typing import List


@dataclass
class SequenceConfig:
    """Container for a time series used in the reference configuration."""

    times: List[float]
    values: List[float]


@dataclass
class ReferenceConfig:
    """Container for the reference profiles of active/reactive power and voltage."""

    P: SequenceConfig
    Q: SequenceConfig
    V: SequenceConfig
