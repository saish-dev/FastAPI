"""
Queries for user use cases.
Queries represent read operations (CQS pattern).
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetUserByIdQuery:
    """Query to get user by ID."""

    user_id: UUID


@dataclass(frozen=True)
class GetUserByEmailQuery:
    """Query to get user by email."""

    email: str


@dataclass(frozen=True)
class ListUsersQuery:
    """Query to list users."""

    skip: int = 0
    limit: int = 100
