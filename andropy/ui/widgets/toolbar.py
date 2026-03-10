from andropy.ui.base import UiComponent


class UiToolbar(UiComponent):
    """Maps to androidx.appcompat.widget.Toolbar."""
    _tag = "androidx.appcompat.widget.Toolbar"

    def __init__(self, title="", subtitle="", width=None, height=None,
                 padding=None, margin=None,
                 background="?attr/colorPrimary",
                 elevation=4,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width or "match_parent",
                         height=height or "?attr/actionBarSize",
                         padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.title = title
        self.subtitle = subtitle
        self.background = background
        self.elevation = elevation

    def _component_attrs(self) -> dict:
        attrs = {
            "android:background": self.background,
            "android:elevation": f"{self.elevation}dp",
        }
        if self.title:
            attrs["app:title"] = self.title
        if self.subtitle:
            attrs["app:subtitle"] = self.subtitle
        return attrs