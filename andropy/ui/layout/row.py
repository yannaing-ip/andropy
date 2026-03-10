from andropy.ui.base import UiComponent
from andropy.ui.layout.constants import W1, H0


class UiRow(UiComponent):
    """Places components horizontally left to right inside RelativeLayout."""

    _tag = "View"

    def __init__(self, *children, width=None, height=None, padding=None, margin=None):
        super().__init__(width=width or W1, height=height or H0, padding=padding, margin=margin)
        self.children = list(children)

    def _component_attrs(self):
        return {}

    def to_xml(self, parent_id=None, indent=1) -> str:
        lines = []
        prev_id = None
    
        for i, child in enumerate(self.children):
            attrs = child._base_attrs(parent_id=None)
    
            # ALL children in row get layout_below from parent
            if parent_id:
                attrs["android:layout_below"] = f"@id/{parent_id}"
    
            # Subsequent children — place to right of previous
            if prev_id:
                attrs["android:layout_toRightOf"] = f"@id/{prev_id}"
    
            attrs.update(child._component_attrs())
            xml = child._build_xml(child._tag, attrs, indent)
            lines.append(xml)
            prev_id = child.id
    
        return "\n".join(lines)

    def last_id(self):
        if self.children:
            return self.children[0].id
        return self.id