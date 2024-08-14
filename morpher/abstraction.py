from pydantic import BaseModel, Field
from typing import Type

class Abstraction(BaseModel):
    id: str = Field(..., description="Unique identifier for the abstraction")
    name: str = Field(..., description="Human-readable name of the abstraction")
    description: str = Field(..., description="Detailed description of what this abstraction represents")
    model: Type[BaseModel] = Field(..., description="Pydantic model defining the structure of this abstraction")

    def __repr__(self) -> str:
        return f"Abstraction(id='{self.id}', name='{self.name}', model={self.model.__name__})"
