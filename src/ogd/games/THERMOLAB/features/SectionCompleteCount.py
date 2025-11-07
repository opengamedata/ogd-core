from typing import Any, List, Set
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.Feature import Feature

class SectionCompleteCount(SessionFeature):

    def __init__(self, params: GeneratorParameters):
        self.completed_sections: Set[str] = set()
        super().__init__(params=params)

    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["complete_section"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        if event.EventName == "complete_section":
            section = event.EventData.get("section")
            if section:
                #snake_case conversion
                section = self._convert_keys_to_snake_case(section)
                section_id = f"{section.get('lab_name')}_{section.get('section_number')}"
                self.completed_sections.add(section_id)

    def _updateFromFeature(self, feature:Feature):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [len(self.completed_sections)]

    def _convert_keys_to_snake_case(self, data: dict) -> dict:
        return {self._pascal_to_snake_case(k): v for k, v in data.items()}

    def _pascal_to_snake_case(self, name: str) -> str:
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()

