class UiComponent:
    """Base class for all Andropy UI components."""

    _id_counter = 0

    def __init__(self, width=None, height=None, padding=None, margin=None,
                 center=False, center_horizontal=False, center_vertical=False):
        UiComponent._id_counter += 1
        self.id = f"_view_{UiComponent._id_counter}"
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.center = center
        self.center_horizontal = center_horizontal
        self.center_vertical = center_vertical
        self._kt_lines = []
        self._kt_imports = []

    def _base_attrs(self, parent_id=None) -> dict:
        attrs = {
            "android:id": f"@+id/{self.id}",
            "android:layout_width": self._resolve_size(self.width),
            "android:layout_height": self._resolve_size(self.height),
        }
        if parent_id:
            attrs["android:layout_below"] = f"@+id/{parent_id}"

        # Centering
        if self.center:
            attrs["android:layout_centerInParent"] = "true"
        else:
            if self.center_horizontal:
                attrs["android:layout_centerHorizontal"] = "true"
            if self.center_vertical:
                attrs["android:layout_centerVertical"] = "true"

        padding = self._resolve_spacing(self.padding)
        if padding:
            attrs["android:padding"] = padding

        margin = self._resolve_spacing(self.margin)
        if margin:
            attrs["android:layout_margin"] = margin

        return attrs

    def setVisible(self, visible: bool = True):
        value = "View.VISIBLE" if visible else "View.GONE"
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).visibility = {value}')
        self._kt_imports.append("android.view.View")

    def setEnabled(self, enabled: bool = True):
        value = "true" if enabled else "false"
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).isEnabled = {value}')
        self._kt_imports.append("android.view.View")

    def to_xml(self, parent_id=None, indent=1) -> str:
        raise NotImplementedError("Each component must implement to_xml()")

    def _component_attrs(self) -> dict:
        return {}

    def _resolve_size(self, value) -> str:
        from andropy.ui.layout import W0, W1, H0, H1
        size_map = {
            W0: "wrap_content",
            W1: "match_parent",
            H0: "wrap_content",
            H1: "match_parent",
        }
        if value is None:
            return "wrap_content"
        if value in size_map:
            return size_map[value]
        if isinstance(value, int):
            return f"{value}dp"
        return str(value)

    def _resolve_spacing(self, value) -> str | None:
        from andropy.ui.layout import (
            P0, P1, P2, P3, P4, P5, P6,
            M0, M1, M2, M3, M4, M5, M6
        )
        spacing_map = {
            P0: "0dp",  P1: "4dp",  P2: "8dp",
            P3: "12dp", P4: "16dp", P5: "24dp", P6: "32dp",
            M0: "0dp",  M1: "4dp",  M2: "8dp",
            M3: "12dp", M4: "16dp", M5: "24dp", M6: "32dp",
        }
        if value is None:
            return None
        if value in spacing_map:
            return spacing_map[value]
        if isinstance(value, int):
            return f"{value}dp"
        return str(value)

    def _base_attrs(self, parent_id=None) -> dict:
        attrs = {
            "android:id": f"@+id/{self.id}",
            "android:layout_width": self._resolve_size(self.width),
            "android:layout_height": self._resolve_size(self.height),
        }
        if parent_id:
            attrs["android:layout_below"] = f"@+id/{parent_id}"

        padding = self._resolve_spacing(self.padding)
        if padding:
            attrs["android:padding"] = padding

        margin = self._resolve_spacing(self.margin)
        if margin:
            attrs["android:layout_margin"] = margin

        return attrs

    def _build_xml(self, tag: str, attrs: dict, indent: int) -> str:
        spaces = "    " * indent
        inner = "    " * (indent + 1)
        attr_lines = "\n".join(f'{inner}{k}="{v}"' for k, v in attrs.items())
        return f"{spaces}<{tag}\n{attr_lines}/>"

    def to_xml(self, parent_id=None, indent=1) -> str:
        attrs = self._base_attrs(parent_id=parent_id)
        attrs.update(self._component_attrs())
        return self._build_xml(self._tag, attrs, indent)
    def setVisible(self):
        """Generates: findViewById<View>(...).visibility = View.VISIBLE"""
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).visibility = View.VISIBLE')
        self._kt_imports.append("android.view.View")

    def setGone(self):
        """Generates: findViewById<View>(...).visibility = View.GONE"""
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).visibility = View.GONE')
        self._kt_imports.append("android.view.View")

    def setInvisible(self):
        """Generates: findViewById<View>(...).visibility = View.INVISIBLE"""
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).visibility = View.INVISIBLE')
        self._kt_imports.append("android.view.View")

    def setEnabled(self):
        """Generates: findViewById<View>(...).isEnabled = true"""
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).isEnabled = true')
        self._kt_imports.append("android.view.View")

    def setDisabled(self):
        """Generates: findViewById<View>(...).isEnabled = false"""
        self._kt_lines.append(f'findViewById<View>(R.id.{self.id}).isEnabled = false')
        self._kt_imports.append("android.view.View")
