from __future__ import annotations

import uuid


class MissionID:
    """Immutable wrapper around a UUID4 string.

    ``MissionID`` centralises identifier generation and validation so
    that raw ``uuid`` module usage is not scattered throughout the
    project.

    Attributes:
        _value: The underlying UUID4 string.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    @classmethod
    def generate(cls) -> MissionID:
        """Create a new random MissionID."""
        return cls(str(uuid.uuid4()))

    @classmethod
    def validate(cls, value: str) -> bool:
        """Return ``True`` if *value* is a valid UUID4 string."""
        if not isinstance(value, str):
            return False
        try:
            parsed = uuid.UUID(value)
            return parsed.version == 4
        except ValueError:
            return False

    @property
    def value(self) -> str:
        """Return the raw UUID string."""
        return self._value

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"MissionID({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MissionID):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value)
