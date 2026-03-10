from pathlib import Path
from andropy.compiler.xml_compiler import compile_xml
from andropy.compiler.kt_compiler import compile_kt
from andropy.engine.exceptions import CompileError


def compile_all(main_dir: Path, layout_dir: Path, kt_dir: Path = None, package_name: str = "com.example.app"):
    """Compile all Python activity files in main/ to XML and KT files."""
    py_files = list(main_dir.glob("*.py"))

    if not py_files:
        from andropy.engine.error_handler import show_compile_error
        show_compile_error(
            "main/",
            "No Python activity files found in main/.",
            "Create at least one activity file:\n\n"
            "  main/main_activity.py"
        )
        return

    for py_file in py_files:
        xml_name = py_file.stem + ".xml"
        kt_name = "".join(word.capitalize() for word in py_file.stem.split("_")) + ".kt"
        output_xml = layout_dir / xml_name
        output_kt = (kt_dir / kt_name) if kt_dir else None

        xml_success = False
        try:
            compile_xml(py_file, output_xml)
            xml_success = True
        except CompileError:
            pass
        except Exception as e:
            from andropy.engine.error_handler import show_compile_error
            show_compile_error(py_file.name, str(e))

        # Only compile KT if XML succeeded
        if xml_success and output_kt:
            try:
                compile_kt(py_file, output_kt, package_name)
            except CompileError:
                pass
            except Exception as e:
                from andropy.engine.error_handler import show_compile_error
                show_compile_error(py_file.name, str(e))