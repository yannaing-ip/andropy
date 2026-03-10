import ast
import textwrap
import inspect
from pathlib import Path
from andropy.compiler.class_parser import parse_activity_file
from andropy.engine.exceptions import CompileError
from andropy.engine.error_handler import show_compile_error


def snake_to_camel(name: str) -> str:
    """handle_login → handleLogin"""
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def collect_click_listeners(ui_instance, kt_setup: list, kt_imports: list):
    """Scan all UI components for _on_click_handler."""
    from andropy.ui.widgets.button import UiButton

    kt_imports.append("android.widget.Button")

    for attr, val in vars(ui_instance).items():
        if isinstance(val, UiButton) and val._on_click_handler is not None:
            handler = val._on_click_handler
            handler_name = handler.__name__
            kt_handler = snake_to_camel(handler_name)
            kt_setup.append(f'val {val.id} = findViewById<Button>(R.id.{val.id})')
            kt_setup.append(f'{val.id}.setOnClickListener {{')
            kt_setup.append(f'    {kt_handler}()')
            kt_setup.append(f'}}')


def collect_method_kt(logic_instance, method_name: str) -> tuple:
    import textwrap
    import inspect
    from andropy.ui.widgets.toast import Toast
    from andropy.ui.widgets.kt_value import KtValue
    from andropy.ui.widgets.input import UiInput
    from andropy.ui.widgets.text import UiText

    kt_lines = []
    kt_imports = []

    # Reset per-method KT lines
    logic_instance._kt_lines = []
    logic_instance._kt_imports_method = []

    # Parse method body via ast
    source = inspect.getsource(getattr(type(logic_instance), method_name))
    source = textwrap.dedent(source)
    tree = ast.parse(source)

    # Detect getText() assignments
    get_text_vars = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if isinstance(node.value, ast.Call):
                        func = node.value.func
                        if isinstance(func, ast.Attribute) and func.attr == "getText":
                            if isinstance(func.value, ast.Attribute):
                                attr_name = func.value.attr
                                get_text_vars[attr_name] = var_name

    # Patch isChecked() on UiCheckbox
    from andropy.ui.widgets.selection import UiCheckbox, UiSwitch
    from andropy.ui.widgets.media import UiSlider

    original_is_checked_cb = UiCheckbox.isChecked
    def patched_is_checked_cb(self_cb):
        result = original_is_checked_cb(self_cb)
        if result.kt_line not in kt_lines:
            kt_lines.insert(0, result.kt_line)
        if result.kt_import and result.kt_import not in kt_imports:
            kt_imports.append(result.kt_import)
        return result
    UiCheckbox.isChecked = patched_is_checked_cb

    # Patch isChecked() on UiSwitch
    original_is_checked_sw = UiSwitch.isChecked
    def patched_is_checked_sw(self_sw):
        result = original_is_checked_sw(self_sw)
        if result.kt_line not in kt_lines:
            kt_lines.insert(0, result.kt_line)
        if result.kt_import and result.kt_import not in kt_imports:
            kt_imports.append(result.kt_import)
        return result
    UiSwitch.isChecked = patched_is_checked_sw

    # Patch getValue() on UiSlider
    original_get_value = UiSlider.getValue
    def patched_get_value(self_slider):
        result = original_get_value(self_slider)
        if result.kt_line not in kt_lines:
            kt_lines.insert(0, result.kt_line)
        if result.kt_import and result.kt_import not in kt_imports:
            kt_imports.append(result.kt_import)
        return result
    UiSlider.getValue = patched_get_value

    # Patch getText()
    original_get_text = UiInput.getText

    def patched_get_text(self_input, var_name="text"):
        for attr, detected_var in get_text_vars.items():
            if self_input.id == f"_{attr}" or self_input.id == attr:
                var_name = detected_var
                break
        result = original_get_text(self_input, var_name)
        if result.kt_line not in kt_lines:
            kt_lines.insert(0, result.kt_line)
        if result.kt_import and result.kt_import not in kt_imports:
            kt_imports.append(result.kt_import)
        return result

    UiInput.getText = patched_get_text

    # Patch setText() — collect KT lines from UiText
    original_set_text = UiText.setText

    def patched_set_text(self_text, value):
        original_set_text(self_text, value)
        for line in self_text._kt_lines:
            if line not in kt_lines:
                kt_lines.append(line)
        for imp in self_text._kt_imports:
            if imp not in kt_imports:
                kt_imports.append(imp)
        # Reset after collecting
        self_text._kt_lines = []
        self_text._kt_imports = []

    UiText.setText = patched_set_text

    # Patch Toast
    created_toasts = []
    original_init = Toast.__init__

    def patched_init(self_toast):
        original_init(self_toast)
        created_toasts.append(self_toast)

    Toast.__init__ = patched_init

    try:
        method = getattr(logic_instance, method_name)
        method()
    except Exception:
        pass
    finally:
        UiInput.getText = original_get_text
        UiText.setText = original_set_text
        Toast.__init__ = original_init
        UiCheckbox.isChecked = original_is_checked_cb
        UiSwitch.isChecked = original_is_checked_sw
        UiSlider.getValue = original_get_value

    # Collect from navigate()
    kt_lines.extend(logic_instance._kt_lines)
    kt_imports.extend(getattr(logic_instance, "_kt_imports_method", []))

    # Collect from Toast
    for toast in created_toasts:
        kt_imports.extend(toast._kt_imports)
        kt_lines.extend(toast._kt_lines)

    # Collect _kt_lines from all UI widgets (setVisible, setGone, setEnabled, etc.)
    from andropy.ui.base import UiComponent
    for attr in dir(logic_instance):
        val = getattr(logic_instance, attr, None)
        if isinstance(val, UiComponent):
            for line in getattr(val, "_kt_lines", []):
                if line not in kt_lines:
                    kt_lines.append(line)
            for imp in getattr(val, "_kt_imports", []):
                if imp not in kt_imports:
                    kt_imports.append(imp)
            val._kt_lines = []
            val._kt_imports = []

    if not kt_lines:
        kt_lines.append("// TODO")

    return kt_lines, kt_imports


def extract_methods(logic_class) -> list:
    """Extract all user defined methods from ActivityLogic subclass."""
    from andropy.ui.activity import ActivityLogic
    base_methods = set(dir(ActivityLogic))
    methods = []

    for name, obj in inspect.getmembers(logic_class, predicate=inspect.isfunction):
        if name.startswith("__"):
            continue
        if name in base_methods:
            continue
        if name == "on_create":
            continue
        methods.append(name)

    return methods


def extract_normal_classes(result: dict) -> list:
    """Extract normal classes from parsed result."""
    normal = []

    for cls in result["normal"]:
        methods = []
        for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("__"):
                continue
            methods.append(name)
        normal.append({
            "name": cls.__name__,
            "methods": methods
        })

    return normal


def generate_kt_content(
    package_name: str,
    class_name: str,
    layout_name: str,
    kt_imports: list,
    kt_setup: list,
    kt_methods: list,
    normal_classes: list,
) -> str:
    """Generate full KT file content."""
    base_imports = [
        "android.os.Bundle",
        "androidx.appcompat.app.AppCompatActivity",
    ]
    # Deduplicate imports
    seen = set(base_imports)
    all_imports = list(base_imports)
    for i in kt_imports:
        if i not in seen:
            seen.add(i)
            all_imports.append(i)

    imports_str = "\n".join(f"import {i}" for i in all_imports)

    # onCreate body
    setup_lines = []
    for line in kt_setup:
        setup_lines.append(f"        {line}")
    setup_str = "\n".join(setup_lines)

    # User defined methods
    methods_str = ""
    for method in kt_methods:
        kt_name = snake_to_camel(method["name"])
        body = "\n        ".join(method["body"])
        methods_str += f"\n    private fun {kt_name}() {{\n        {body}\n    }}\n"

    # Normal classes
    normal_str = ""
    for cls in normal_classes:
        normal_str += f"\nclass {cls['name']} {{\n"
        for method in cls["methods"]:
            kt_name = snake_to_camel(method)
            normal_str += f"\n    fun {kt_name}() {{\n        // TODO\n    }}\n"
        normal_str += "}\n"

    return f'''package {package_name}

{imports_str}

class {class_name} : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.{layout_name})
{setup_str}
    }}
{methods_str}}}
{normal_str}'''

def compile_kt(python_file: Path, output_kt: Path, package_name: str):
    """Compile ActivityLogic to KT file."""
    from andropy.ui.base import UiComponent
    from andropy.compiler.xml_compiler import extract_self_variable_names

    result = parse_activity_file(python_file)
    logic_class = result["logic"]
    ui_class = result["ui"]

    if logic_class is None:
        show_compile_error(
            python_file.name,
            "No ActivityLogic subclass found.",
            f"Create a class that extends ui.ActivityLogic in {python_file.name}\n\n"
            "  class MainLogic(ui.ActivityLogic):\n"
            "      def on_create(self):\n"
            "          pass"
        )
        raise CompileError(f"No ActivityLogic in {python_file.name}")

    logic_instance = logic_class()
    ui_instance = None

    if ui_class is not None:
        UiComponent._id_counter = 0
        var_names = extract_self_variable_names(python_file)

        try:
            ui_instance = ui_class()
            ui_instance.build()
        except Exception as e:
            show_compile_error(
                python_file.name,
                f"Error inside build(): {e}",
                "Check your build() method for mistakes."
            )
            raise CompileError(str(e))

        for var_name in var_names:
            obj = getattr(ui_instance, var_name, None)
            if obj is not None and isinstance(obj, UiComponent):
                obj.id = f"_{var_name}"

        for attr, val in vars(ui_instance).items():
            setattr(logic_instance, attr, val)

    try:
        logic_instance.on_create()
    except NotImplementedError:
        show_compile_error(
            python_file.name,
            "ActivityLogic.on_create() not implemented.",
            "Override on_create() in your Logic class:\n\n"
            "  def on_create(self):\n"
            "      pass"
        )
        raise CompileError(f"on_create() not implemented in {python_file.name}")
    except AttributeError as e:
        attr_name = str(e).split("'")[-2] if "'" in str(e) else str(e)
    
        # Guess widget type from attribute name
        widget_hints = {
            "toolbar": "ui.UiToolbar(title='My App')",
            "btn":     "ui.UiButton('Click me')",
            "input":   "ui.UiInput(hint='Enter text')",
            "text":    "ui.UiText('Hello!')",
            "image":   "ui.UiImage(src='image_name')",
            "switch":  "ui.UiSwitch(text='Toggle')",
            "checkbox":"ui.UiCheckbox(text='Check me')",
            "slider":  "ui.UiSlider()",
            "progress":"ui.UiProgress()",
        }
    
        # Match by prefix
        widget_hint = "ui.UiText(...)"
        for key, hint in widget_hints.items():
            if attr_name.startswith(key) or key in attr_name:
                widget_hint = hint
                break
    
        show_compile_error(
            python_file.name,
            f"'{attr_name}' used in Logic but not defined in UI.",
            f"Add self.{attr_name} to your build() method:\n\n"
            f"  def build(self):\n"
            f"      self.{attr_name} = {widget_hint}  ← add this"
        )
        raise CompileError(str(e))
    except Exception as e:
        show_compile_error(
            python_file.name,
            f"Error inside on_create(): {e}",
            "Check your on_create() method for mistakes."
        )
        raise CompileError(str(e))

    kt_imports = logic_instance._kt_imports
    kt_setup = logic_instance._kt_setup

    if ui_instance is not None:
        collect_click_listeners(ui_instance, kt_setup, kt_imports)

    raw_methods = extract_methods(logic_class)
    kt_methods = []
    for method_name in raw_methods:
        body_lines, method_imports = collect_method_kt(logic_instance, method_name)
        kt_methods.append({
            "name": method_name,
            "body": body_lines,
        })
        for imp in method_imports:
            if imp not in kt_imports:
                kt_imports.append(imp)

    normal_classes = extract_normal_classes(result)
    kt_stem = output_kt.stem
    layout_name = python_file.stem

    content = generate_kt_content(
        package_name=package_name,
        class_name=kt_stem,
        layout_name=layout_name,
        kt_imports=kt_imports,
        kt_setup=kt_setup,
        kt_methods=kt_methods,
        normal_classes=normal_classes,
    )

    output_kt.parent.mkdir(parents=True, exist_ok=True)
    output_kt.write_text(content, encoding="utf-8")
    print(f"  ✅ {python_file.name} → {output_kt.name}")