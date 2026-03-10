from andropy.ui.base import UiComponent


class UiScrollView(UiComponent):
    """Maps to Android ScrollView."""
    _tag = "ScrollView"

    def __init__(self, child, width=None, height=None,
                 padding=None, margin=None,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width or "match_parent",
                         height=height or "match_parent",
                         padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.child = child

    def _component_attrs(self) -> dict:
        return {"android:fillViewport": "true"}

    def to_xml(self, parent_id=None, indent=1) -> str:
        spaces = "    " * indent
        inner = "    " * (indent + 1)
        inner2 = "    " * (indent + 2)

        attrs = self._base_attrs(parent_id=parent_id)
        attrs.update(self._component_attrs())
        attr_lines = "\n".join(f'{inner}{k}="{v}"' for k, v in attrs.items())

        lines = [f"{spaces}<ScrollView\n{attr_lines}>"]
        lines.append(f"{inner}<RelativeLayout")
        lines.append(f'{inner2}android:layout_width="match_parent"')
        lines.append(f'{inner2}android:layout_height="wrap_content">')
        lines.append(self.child.to_xml(parent_id=None, indent=indent + 2))
        lines.append(f"{inner}</RelativeLayout>")
        lines.append(f"{spaces}</ScrollView>")
        return "\n".join(lines)