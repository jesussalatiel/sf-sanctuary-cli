from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


class UserRole(Enum):
    """User roles mapping to Salesforce profiles."""

    STANDARD = "Standard User"
    ADMIN = "System Administrator"
    READ_ONLY = "Read Only"


@dataclass
class UserBase:
    """Base data model for a Salesforce user."""

    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.STANDARD
    is_active: bool = True


@dataclass
class User(UserBase):
    """Complete data model for a Salesforce user."""

    id: Optional[str] = None
    created_date: Optional[datetime] = None


@dataclass
class CreateUserParams:
    """Parameters for creating a new user."""

    email: str
    last_name: str
    first_name: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    company: Optional[str] = None
    role: str = "standard"
    username: Optional[str] = None
