from andropy.ui.base import UiComponent


class UiInput(UiComponent):
    """Maps to Android EditText."""
    _tag = "EditText"

    def __init__(self, hint="", width=None, height=None,
                 padding=None, margin=None, input_type="text",
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.hint = hint
        self.input_type = input_type
        self._kt_lines = []
        self._kt_imports = []

    def getText(self, var_name: str = "text") -> 'KtValue':
        """Returns KtValue: val {var_name} = findViewById<EditText>(...).getText().toString()"""
        from andropy.ui.widgets.kt_value import KtValue
        kt_line = f'val {var_name} = findViewById<EditText>(R.id.{self.id}).getText().toString()'
        return KtValue(kt_var_name=var_name, kt_line=kt_line, kt_import="android.widget.EditText")

    def setText(self, value):
        """Generates: findViewById<EditText>(...).setText("value")"""
        kt_line = f'findViewById<EditText>(R.id.{self.id}).setText({_kt_value(value)})'
        self._kt_lines.append(kt_line)
        self._kt_imports.append("android.widget.EditText")

    def _component_attrs(self) -> dict:
        input_type_map = {
            "text":     "text",
            "password": "textPassword",
            "email":    "textEmailAddress",
            "number":   "number",
            "phone":    "phone",
        }
        return {
            "android:hint": self.hint,
            "android:inputType": input_type_map.get(self.input_type, "text"),
        }


def _kt_value(value) -> str:
    """Convert Python value to KT string."""
    from andropy.ui.widgets.kt_value import KtValue
    if isinstance(value, KtValue):
        return f'"${{{value.kt_var_name}}}"'
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)
