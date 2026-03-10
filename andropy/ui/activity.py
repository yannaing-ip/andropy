class ActivityUI:
    """Base class for UI definition — compiles to XML."""

    def build(self):
        """Override this to define your UI layout."""
        raise NotImplementedError("ActivityUI must implement build()")


class ActivityLogic:
    """Base class for activity logic — compiles to KT."""

    def __init__(self):
        self._kt_imports = []
        self._kt_setup = []
        self._kt_lines = []
        self._kt_imports_method = []

    def set_toolbar(self, toolbar):
        """Register toolbar KT code."""
        self._kt_imports.append("androidx.appcompat.widget.Toolbar")
        self._kt_setup.append(f'val {toolbar.id} = findViewById<Toolbar>(R.id.{toolbar.id})')
        self._kt_setup.append(f'setSupportActionBar({toolbar.id})')
        if toolbar.title:
            self._kt_setup.append(f'supportActionBar?.title = "{toolbar.title}"')

    def navigate(self, activity_name: str):
        """Register navigation KT code."""
        self._kt_imports_method.append("android.content.Intent")
        self._kt_lines.append(f'val intent = Intent(this, {activity_name}::class.java)')
        self._kt_lines.append(f'startActivity(intent)')

    def on_create(self):
        """Override this to define onCreate() logic."""
        raise NotImplementedError("ActivityLogic must implement.")