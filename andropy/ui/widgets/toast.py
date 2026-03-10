from andropy.ui.widgets.kt_value import KtValue


class Toast:
    """Andropy Toast — compiles to Android Toast KT code."""

    def __init__(self):
        self._kt_lines = []
        self._kt_imports = ["android.widget.Toast"]

    def show(self, message, duration: str = "short"):
        """Register Toast KT code."""
        from andropy.ui.widgets.kt_value import KtValue

        duration_map = {
            "short": "Toast.LENGTH_SHORT",
            "long":  "Toast.LENGTH_LONG",
        }
        kt_duration = duration_map.get(duration, "Toast.LENGTH_SHORT")

        # Handle KtValue in f-string — already resolved via __str__
        self._kt_lines.append(
            f'Toast.makeText(this, "{message}", {kt_duration}).show()'
        )