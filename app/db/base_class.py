from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Add common model attributes here
    id: Any
    __name__: str
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically, converting CamelCase to snake_case."""
        return cls.__name__.lower()