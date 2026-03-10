from andropy.ui.base import UiComponent


class UiProgress(UiComponent):
    """Maps to Android ProgressBar."""
    _tag = "ProgressBar"

    def __init__(self, width=None, height=None,
                 padding=None, margin=None, style="circular",
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.style = style

    def _component_attrs(self) -> dict:
        attrs = {}
        if self.style == "horizontal":
            attrs["style"] = "@android:style/Widget.ProgressBar.Horizontal"
            attrs["android:max"] = "100"
            attrs["android:progress"] = "0"
        return attrs


class UiImage(UiComponent):
    """Maps to Android ImageView."""
    _tag = "ImageView"

    def __init__(self, src="", width=None, height=None,
                 padding=None, margin=None, scale="centerCrop",
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.src = src
        self.scale = scale

    def _component_attrs(self) -> dict:
        return {
            "android:src": f"@drawable/{self.src}" if self.src else "@android:drawable/ic_menu_gallery",
            "android:scaleType": self.scale,
        }


class UiSlider(UiComponent):
    """Maps to Android SeekBar."""
    _tag = "SeekBar"

    def __init__(self, width=None, height=None,
                 padding=None, margin=None,
                 max=100, progress=0,
                 center=False, center_horizontal=False, center_vertical=False):
        super().__init__(width=width, height=height, padding=padding, margin=margin,
                         center=center, center_horizontal=center_horizontal,
                         center_vertical=center_vertical)
        self.max = max
        self.progress = progress
        self._on_change_handler = None

    def on_change(self, handler):
        """Register change handler."""
        self._on_change_handler = handler

    def getValue(self) -> 'KtValue':
        """Returns KtValue that generates: val value = findViewById<SeekBar>(...).progress"""
        from andropy.ui.widgets.kt_value import KtValue
        var_name = self.id.lstrip("_") + "_value"
        kt_line = f'val {var_name} = findViewById<SeekBar>(R.id.{self.id}).progress'
        return KtValue(kt_var_name=var_name, kt_line=kt_line, kt_import="android.widget.SeekBar")

    def _component_attrs(self) -> dict:
        return {
            "android:max": str(self.max),
            "android:progress": str(self.progress),
        }
