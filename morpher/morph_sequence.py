from typing import List, Any
from pydantic import Field
from .morph import Morph
from .abstraction import Abstraction

class MorphSequence(Morph):
    steps: List[Morph] = Field(..., description="List of morphs to apply in sequence")

    def __init__(self, steps: List[Morph], **data):
        super().__init__(
            id=f"morph_sequence_{id(self)}",
            name="Morph Sequence",
            description="A sequence of morphs applied in order",
            source=steps[0].source,
            target=steps[-1].target,
            steps=steps,
            **data
        )

    def forward(self, input_data: Any) -> Any:
        for step in self.steps:
            input_data = step.forward(input_data)
        return input_data

    def backward(self, evaluation: dict) -> None:
        for step in reversed(self.steps):
            step.backward(evaluation)

    def system_message(self) -> str:
        return f"You are a sequence of {len(self.steps)} morphs: {', '.join(step.name for step in self.steps)}"

    def user_message(self, input_data: Any) -> str:
        return f"Apply the sequence of morphs to the following input: {input_data}"

    def __getitem__(self, idx):
        return self.steps[idx]

    def __len__(self):
        return len(self.steps)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value