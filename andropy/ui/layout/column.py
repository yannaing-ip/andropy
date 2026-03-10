from andropy.ui.base import UiComponent
from andropy.ui.layout.constants import W1, H0


class UiColumn(UiComponent):
    """Places components vertically top to bottom."""

    _tag = "View"

    def __init__(self, *children, width=None, height=None, padding=None, margin=None):
        super().__init__(width=width or W1, height=height or H0, padding=padding, margin=margin)
        self.children = list(children)

    def _component_attrs(self):
        return {}

    def to_xml(self, parent_id=None, indent=1) -> str:
        from andropy.ui.layout.row import UiRow
        lines = []
        prev_id = parent_id

        for child in self.children:
            if isinstance(child, UiRow):
                xml = child.to_xml(parent_id=prev_id, indent=indent)
                lines.append(xml)
                prev_id = child.last_id()
            else:
                attrs = child._base_attrs(parent_id=prev_id)
                attrs.update(child._component_attrs())
                xml = child._build_xml(child._tag, attrs, indent)
                lines.append(xml)
                prev_id = child.id

        return "\n".join(lines)