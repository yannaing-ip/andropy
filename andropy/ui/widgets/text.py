from andropy.ui.base import UiComponent


class UiText(UiComponent):
    """Maps to Android TextView."""
    _tag = "TextView"

    def __init__(self, text="", width=None, height=None,
                 padding=None, margin=None,
                 text_size=14, bold=False, italic=False,
                 color=None, text_align="left",
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.text = text
        self.text_size = text_size
        self.bold = bold
        self.italic = italic
        self.color = color
        self.text_align = text_align
        self._kt_lines = []
        self._kt_imports = []

    def setText(self, value) -> None:
        """Register setText KT code."""
        self._kt_imports.append("android.widget.TextView")
        self._kt_lines.append(
            f'findViewById<TextView>(R.id.{self.id}).setText("{value}")'
        )

    def _component_attrs(self) -> dict:
        attrs = {
            "android:text": self.text,
            "android:textSize": f"{self.text_size}sp",
        }
        styles = []
        if self.bold:
            styles.append("bold")
        if self.italic:
            styles.append("italic")
        if styles:
            attrs["android:textStyle"] = "|".join(styles)
        if self.color:
            attrs["android:textColor"] = self.color

        align_map = {"left": "start", "center": "center", "right": "end"}
        if self.text_align != "left":
            attrs["android:gravity"] = align_map.get(self.text_align, "start")

        return attrs