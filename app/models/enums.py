"""
Shared enums used across multiple models.
Single source of truth prevents divergent duplicates.
"""
import enum


class ExperienceLevel(str, enum.Enum):
    """Unified experience level enum used by both UserProfile and Job models."""

    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        """Support case-insensitive lookup so rows normalized to uppercase
        (e.g. by the startup UPPER() reconciliation query) still deserialize."""
        if isinstance(value, str):
            return cls._value2member_map_.get(value.lower())
        return None
