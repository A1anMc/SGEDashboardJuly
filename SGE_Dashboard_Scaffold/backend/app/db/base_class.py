from typing import Any

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from the class name."""
        # Remove 'Model' suffix if present and convert to lowercase
        name = cls.__name__
        if name.endswith('Model'):
            name = name[:-5]
        return name.lower() + 's' 