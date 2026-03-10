class KtValue:
    """Represents a KT variable reference."""

    def __init__(self, kt_var_name: str, kt_line: str, kt_import: str = None):
        self.kt_var_name = kt_var_name
        self.kt_line = kt_line
        self.kt_import = kt_import

    def __str__(self):
        """Used in f-strings — returns $varName for KT string interpolation."""
        return f"${self.kt_var_name}"