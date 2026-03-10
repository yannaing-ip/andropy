from andropy.ui.base import UiComponent


class UiDivider(UiComponent):
    """A horizontal line divider."""
    _tag = "View"

    def __init__(self, width=None, height=1,
                 padding=None, margin=None, color="#E0E0E0",
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.color = color

    def _component_attrs(self) -> dict:
        return {"android:background": self.color}


class UiSpace(UiComponent):
    """Empty space."""
    _tag = "Space"

    def __init__(self, width=None, height=16):
        super().__init__(width=width, height=height)

    def _component_attrs(self) -> dict:
        return {}