from pathlib import Path


KOTLIN_TEMPLATE = '''package {package_name}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
{imports}

class {class_name} : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContentView(R.layout.{layout_name})
{setup_code}
    }}
}}
'''


def generate_kotlin(
    package_name: str,
    imports: list,
    setup_code: list,
    output_kt: Path
):
    """Generate Activity KT file."""
    # Derive class name and layout name from file name
    # MainActivity.kt → MainActivity, main_activity
    kt_stem = output_kt.stem
    layout_name = "_".join(
        word.lower() for word in
        __import__('re').sub(r'([A-Z])', r'_\1', kt_stem).strip('_').split('_')
    )

    imports_str = "\n".join(f"import {i}" for i in imports) if imports else ""
    setup_str = "\n".join(f"        {line}" for line in setup_code) if setup_code else ""

    content = KOTLIN_TEMPLATE.format(
        package_name=package_name,
        class_name=kt_stem,
        layout_name=layout_name,
        imports=imports_str,
        setup_code=setup_str,
    )

    output_kt.parent.mkdir(parents=True, exist_ok=True)
    output_kt.write_text(content, encoding="utf-8")
    print(f"  ✅ Generated {output_kt.name}")