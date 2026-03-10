import ast
import importlib.util
from pathlib import Path


XML_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

'''

XML_FOOTER = '\n</RelativeLayout>'


def extract_variable_names(python_file: Path) -> dict:
    """Use ast to extract variable names assigned to UI components."""
    source = python_file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    var_names = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Call):
                        var_names[target.id] = target.id

    return var_names


def detect_set_toolbar(python_file: Path) -> str | None:
    """Detect if user called ui.set_toolbar(variable_name)."""
    source = python_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            if isinstance(node.value, ast.Call):
                call = node.value
                is_set_toolbar = False

                if isinstance(call.func, ast.Attribute):
                    if call.func.attr == "set_toolbar":
                        is_set_toolbar = True
                elif isinstance(call.func, ast.Name):
                    if call.func.id == "set_toolbar":
                        is_set_toolbar = True

                if is_set_toolbar and call.args:
                    arg = call.args[0]
                    if isinstance(arg, ast.Name):
                        return arg.id

    return None


def compile_ui(python_file: Path, output_xml: Path, output_kt: Path = None, package_name: str = "com.example.app"):
    """Execute a Python UI file, find root layout, compile to XML and KT."""
    from andropy.ui.base import UiComponent
    from andropy.ui.layout import UiColumn, UiRow
    from andropy.ui.widgets import UiScrollView
    from andropy.ui.kotlin_generator import generate_kotlin

    # Reset component ID counter
    UiComponent._id_counter = 0

    # Extract variable names via ast BEFORE executing
    var_names = extract_variable_names(python_file)
    toolbar_var = detect_set_toolbar(python_file)

    # Execute the Python UI file
    spec = importlib.util.spec_from_file_location("ui_module", python_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Find root layout
    root = getattr(module, "root", None)
    if root is None:
        raise ValueError(f"No 'root' variable found in {python_file.name}")
    
    if not isinstance(root, (UiColumn, UiRow, UiScrollView)):
        raise ValueError(f"'root' must be UiColumn, UiRow or UiScrollView in {python_file.name}")
    # Map variable names to component IDs
    for var_name in var_names:
        obj = getattr(module, var_name, None)
        if obj is not None and isinstance(obj, UiComponent):
            obj.id = var_name

    # Generate XML
    # Generate XML
    if isinstance(root, UiScrollView):
        xml_body = root.to_xml(parent_id=None, indent=1)
        xml_content = XML_HEADER + xml_body + XML_FOOTER
    else:
        xml_body = root.to_xml(parent_id=None, indent=1)
        xml_content = XML_HEADER + xml_body + XML_FOOTER
    output_xml.parent.mkdir(parents=True, exist_ok=True)
    output_xml.write_text(xml_content, encoding="utf-8")
    print(f"  ✅ {python_file.name} → {output_xml.name}")

    # Generate KT only if output_kt is provided
    if output_kt:
        kt_imports = []
        kt_setup = []

        if toolbar_var:
            toolbar_obj = getattr(module, toolbar_var, None)
            if toolbar_obj:
                kt_imports.append("androidx.appcompat.widget.Toolbar")
                kt_setup.append("// Toolbar setup")
                kt_setup.append(f'val {toolbar_var} = findViewById<Toolbar>(R.id.{toolbar_var})')
                kt_setup.append(f'setSupportActionBar({toolbar_var})')
                if hasattr(toolbar_obj, "title") and toolbar_obj.title:
                    kt_setup.append(f'supportActionBar?.title = "{toolbar_obj.title}"')

        generate_kotlin(
            package_name=package_name,
            imports=kt_imports,
            setup_code=kt_setup,
            output_kt=output_kt
        )


import ast
import importlib.util
from pathlib import Path


def compile_all(main_dir: Path, layout_dir: Path, kt_dir: Path = None, package_name: str = "com.example.app"):
    """Compile all Python activity files in main/ to XML and KT files."""
    from andropy.compiler.xml_compiler import compile_xml

    py_files = list(main_dir.glob("*.py"))

    if not py_files:
        print("⚠ No Python activity files found in main/")
        return

    for py_file in py_files:
        xml_name = py_file.stem + ".xml"
        kt_name = "".join(word.capitalize() for word in py_file.stem.split("_")) + ".kt"
        output_xml = layout_dir / xml_name
        output_kt = (kt_dir / kt_name) if kt_dir else None
        try:
            compile_xml(py_file, output_xml)
            print(f"  ✅ {py_file.name} → {xml_name}")
        except Exception as e:
            print(f"  ❌ Failed to compile {py_file.name}: {e}")