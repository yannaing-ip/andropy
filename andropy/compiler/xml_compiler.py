import ast
from pathlib import Path
from andropy.ui.activity import ActivityUI
from andropy.ui.base import UiComponent
from andropy.compiler.class_parser import parse_activity_file
from andropy.engine.exceptions import CompileError
from andropy.engine.error_handler import show_compile_error


XML_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

'''

XML_FOOTER = '\n</RelativeLayout>'


def extract_self_variable_names(python_file: Path) -> dict:
    """Extract self.var_name assignments inside build() method."""
    source = python_file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    var_names = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "build":
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute):
                            if isinstance(target.value, ast.Name):
                                if target.value.id == "self":
                                    var_names[target.attr] = target.attr

    return var_names


def compile_xml(python_file: Path, output_xml: Path):
    """Compile ActivityUI.build() to XML layout file."""

    # Reset ID counter
    UiComponent._id_counter = 0

    try:
        result = parse_activity_file(python_file)
    except SyntaxError as e:
        show_compile_error(
            python_file.name,
            f"Syntax error on line {e.lineno}: {e.msg}",
            "Check your Python syntax — missing brackets, colons or indentation."
        )
        raise CompileError(str(e))

    ui_class = result["ui"]

    if ui_class is None:
        show_compile_error(
            python_file.name,
            "No ActivityUI subclass found.",
            f"Create a class that extends ui.ActivityUI in {python_file.name}\n\n"
            "  class MainUI(ui.ActivityUI):\n"
            "      def build(self):\n"
            "          return ui.UiColumn(...)"
        )
        raise CompileError(f"No ActivityUI in {python_file.name}")

    # Extract self.var_names from build() via ast
    var_names = extract_self_variable_names(python_file)

    # Instantiate and call build()
    try:
        ui_instance = ui_class()
        root = ui_instance.build()
    except NotImplementedError:
        show_compile_error(
            python_file.name,
            "ActivityUI.build() not implemented.",
            "Override build() and return a UI component:\n\n"
            "  def build(self):\n"
            "      return ui.UiColumn(\n"
            "          ui.UiText('Hello!')\n"
            "      )"
        )
        raise CompileError(f"build() not implemented in {python_file.name}")
    except Exception as e:
        show_compile_error(
            python_file.name,
            f"Error inside build(): {e}",
            "Check your build() method for mistakes."
        )
        raise CompileError(str(e))

    # Check return type
    if root is None:
        show_compile_error(
            python_file.name,
            "build() returned None.",
            "Make sure build() returns a UI component:\n\n"
            "  def build(self):\n"
            "      return ui.UiColumn(...)  ← don't forget return!"
        )
        raise CompileError(f"build() returned None in {python_file.name}")

    if not hasattr(root, 'to_xml'):
        show_compile_error(
            python_file.name,
            f"build() must return a UI component, not {type(root).__name__}.",
            "Return a UI component from build():\n\n"
            "  def build(self):\n"
            "      return ui.UiColumn(...)  ← must return a widget"
        )
        raise CompileError(f"build() returned wrong type in {python_file.name}")

    # Map self.var_names to component IDs
    for var_name in var_names:
        obj = getattr(ui_instance, var_name, None)
        if obj is not None and isinstance(obj, UiComponent):
            obj.id = f"_{var_name}"

    # Generate XML
    xml_body = root.to_xml(parent_id=None, indent=1)
    xml_content = XML_HEADER + xml_body + XML_FOOTER

    output_xml.parent.mkdir(parents=True, exist_ok=True)
    output_xml.write_text(xml_content, encoding="utf-8")
    print(f"  ✅ {python_file.name} → {output_xml.name}")