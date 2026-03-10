from andropy.ui.base import UiComponent


class UiButton(UiComponent):
    """Maps to Android Button."""
    _tag = "Button"

    def __init__(self, text="", width=None, height=None,
                 padding=None, margin=None, on_click=None,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.text = text
        self._on_click_handler = None

    def on_click(self, handler):
        """Register click handler."""
        self._on_click_handler = handler

    def _component_attrs(self) -> dict:
        return {"android:text": self.text}