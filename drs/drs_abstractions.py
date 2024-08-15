from pydantic import BaseModel, Field
from typing import List
from morpher import Abstraction

class EnglishNarrative(BaseModel):
    text: str = Field(..., description="The input English narrative text")

    class Config:
        extra = "forbid"

class Clause(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")

    class Config:
        extra = "forbid"

class ClauseSegmentation(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    clauses: List[Clause] = Field(..., description="List of clauses from the narrative")

    class Config:
        extra = "forbid"

class LambdaExpression(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    expression: str = Field(..., description="Lambda calculus expression for a clause")

    class Config:
        extra = "forbid"

class LambdaExpressions(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    expressions: List[LambdaExpression] = Field(..., description="List of lambda expressions for clauses")

    class Config:
        extra = "forbid"

class DRSUpdate(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    operation: str = Field(..., description="DRS update operation")
    arguments: List[str] = Field(..., description="Arguments for the DRS update operation")

    class Config:
        extra = "forbid"

class DRSUpdates(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    updates: List[DRSUpdate] = Field(..., description="List of DRS update operations")

    class Config:
        extra = "forbid"

class DRSEntity(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    name: str = Field(..., description="Name of the entity in the DRS")
    type: str = Field(..., description="Type of the entity")

    class Config:
        extra = "forbid"

class DRSCondition(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    predicate: str = Field(..., description="Predicate in the DRS condition")
    arguments: List[str] = Field(..., description="Arguments of the predicate")

    class Config:
        extra = "forbid"

class FinalDRS(BaseModel):
    goal_oriented_learning: str = Field(..., description="Notepad to use for goal-oriented learning and in context improvement of the agent behavior - not accessible by user")
    text: str = Field(..., description="A single clause from the narrative")
    entities: List[DRSEntity] = Field(..., description="List of entities in the DRS")
    conditions: List[DRSCondition] = Field(..., description="List of conditions in the DRS")

    class Config:
        extra = "forbid"

# Create Abstraction instances
english_narrative_abstraction = Abstraction(
    id="english_narrative",
    name="English Narrative",
    description="Represents an English narrative text",
    model=EnglishNarrative
)

clause_segmentation_abstraction = Abstraction(
    id="clause_segmentation",
    name="Clause Segmentation",
    description="Represents a narrative broken down into clauses",
    model=ClauseSegmentation
)

lambda_expressions_abstraction = Abstraction(
    id="lambda_expressions",
    name="Lambda Expressions",
    description="Represents a list of lambda expressions for clauses",
    model=LambdaExpressions
)

drs_updates_abstraction = Abstraction(
    id="drs_updates",
    name="DRS Updates",
    description="Represents a list of DRS update operations",
    model=DRSUpdates
)

final_drs_abstraction = Abstraction(
    id="final_drs",
    name="Final DRS",
    description="Represents the complete Discourse Representation Structure",
    model=FinalDRS
)