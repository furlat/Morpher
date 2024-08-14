from typing import Dict, Optional
from .morph import Morph
from .abstraction import Abstraction

class MorphRegistry:
    def __init__(self):
        self.morphs: Dict[str, Morph] = {}
        self.abstractions: Dict[str, Abstraction] = {}

    def register_morph(self, morph: Morph):
        self.morphs[morph.id] = morph

    def get_morph(self, morph_id: str) -> Optional[Morph]:
        return self.morphs.get(morph_id)

    def register_abstraction(self, abstraction: Abstraction):
        self.abstractions[abstraction.id] = abstraction

    def get_abstraction(self, abstraction_id: str) -> Optional[Abstraction]:
        return self.abstractions.get(abstraction_id)

    def list_morphs(self):
        return list(self.morphs.values())

    def list_abstractions(self):
        return list(self.abstractions.values())
