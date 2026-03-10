from andropy.ui.base import UiComponent


class UiCheckbox(UiComponent):
    """Maps to Android CheckBox."""
    _tag = "CheckBox"

    def __init__(self, text="", width=None, height=None,
                 padding=None, margin=None, checked=False,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.text = text
        self.checked = checked
        self._on_change_handler = None

    def on_change(self, handler):
        """Register change handler."""
        self._on_change_handler = handler

    def isChecked(self) -> 'KtValue':
        """Returns KtValue that generates: val checked = findViewById<CheckBox>(...).isChecked"""
        from andropy.ui.widgets.kt_value import KtValue
        var_name = self.id.lstrip("_") + "_checked"
        kt_line = f'val {var_name} = findViewById<CheckBox>(R.id.{self.id}).isChecked'
        return KtValue(kt_var_name=var_name, kt_line=kt_line, kt_import="android.widget.CheckBox")

    def _component_attrs(self) -> dict:
        return {
            "android:text": self.text,
            "android:checked": "true" if self.checked else "false",
        }


class UiSwitch(UiComponent):
    """Maps to Android Switch."""
    _tag = "Switch"

    def __init__(self, text="", width=None, height=None,
                 padding=None, margin=None, checked=False,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.text = text
        self.checked = checked
        self._on_change_handler = None

    def on_change(self, handler):
        """Register change handler."""
        self._on_change_handler = handler

    def isChecked(self) -> 'KtValue':
        """Returns KtValue that generates: val checked = findViewById<Switch>(...).isChecked"""
        from andropy.ui.widgets.kt_value import KtValue
        var_name = self.id.lstrip("_") + "_checked"
        kt_line = f'val {var_name} = findViewById<Switch>(R.id.{self.id}).isChecked'
        return KtValue(kt_var_name=var_name, kt_line=kt_line, kt_import="android.widget.Switch")

    def _component_attrs(self) -> dict:
        return {
            "android:text": self.text,
            "android:checked": "true" if self.checked else "false",
        }
