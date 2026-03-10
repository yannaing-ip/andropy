import re
from pathlib import Path


def activity_to_class_name(activity_name: str) -> str:
    """main_activity → MainActivity"""
    return "".join(word.capitalize() for word in activity_name.split("_"))


def read_package_name(project_root: Path) -> str:
    """Read package name from build.gradle.kts."""
    build_gradle = project_root / "app" / "app" / "build.gradle.kts"
    if build_gradle.exists():
        for line in build_gradle.read_text().splitlines():
            if "applicationId" in line:
                return line.split('"')[1]
    return "com.example.app"


def find_kt_dir(project_root: Path) -> Path | None:
    """Find the java/kotlin source directory."""
    java_base = project_root / "app" / "app" / "src" / "main" / "java"
    if java_base.exists():
        for path in java_base.rglob("*"):
            if path.is_dir() and not any(p.is_dir() for p in path.iterdir()):
                return path
        return java_base
    return None


def update_strings_xml(project_root: Path, config: dict):
    """Update only app_name in strings.xml."""
    strings_xml = project_root / "app" / "app" / "src" / "main" / "res" / "values" / "strings.xml"
    if not strings_xml.exists():
        print("  ⚠ strings.xml not found, skipping.")
        return

    content = strings_xml.read_text(encoding="utf-8")
    new_content = re.sub(
        r'(<string name="app_name">)(.*?)(</string>)',
        rf'\g<1>{config["APP_NAME"]}\3',
        content
    )
    strings_xml.write_text(new_content, encoding="utf-8")
    print(f'  ✅ strings.xml → APP_NAME: "{config["APP_NAME"]}"')


def update_styles_xml(project_root: Path, config: dict):
    """Regenerate styles.xml, colors.xml and drawables from config."""
    styles_xml   = project_root / "app" / "app" / "src" / "main" / "res" / "values" / "styles.xml"
    colors_xml   = project_root / "app" / "app" / "src" / "main" / "res" / "values" / "colors.xml"
    drawable_dir = project_root / "app" / "app" / "src" / "main" / "res" / "drawable"
    drawable_dir.mkdir(parents=True, exist_ok=True)

    theme_map = {
        "light": "Theme.AppCompat.Light.NoActionBar",
        "dark":  "Theme.AppCompat.NoActionBar",
    }
    parent = theme_map.get(config["THEME"], "Theme.AppCompat.Light.NoActionBar")

    # Generate colors.xml
    colors_xml.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">{config["COLOR_PRIMARY"]}</color>
    <color name="colorPrimaryDark">{config["COLOR_PRIMARY_DARK"]}</color>
    <color name="colorAccent">{config["COLOR_ACCENT"]}</color>
    <color name="colorBackground">{config["COLOR_BACKGROUND"]}</color>
    <color name="colorTextPrimary">{config["COLOR_TEXT_PRIMARY"]}</color>
    <color name="colorTextSecondary">{config["COLOR_TEXT_SECONDARY"]}</color>
    <color name="colorTextHint">{config["COLOR_TEXT_HINT"]}</color>
    <color name="colorDivider">{config["COLOR_DIVIDER"]}</color>
    <color name="colorInputBg">{config["COLOR_INPUT_BG"]}</color>
    <color name="colorToolbarTitle">{config["COLOR_TOOLBAR_TITLE"]}</color>
    <color name="colorToolbarSub">{config["COLOR_TOOLBAR_SUB"]}</color>
    <color name="colorButtonText">{config["COLOR_BUTTON_TEXT"]}</color>
</resources>
''', encoding="utf-8")
    print(f'  ✅ colors.xml generated')

    # Generate styles.xml
    styles_xml.write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.App" parent="{parent}">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
        <item name="colorControlActivated">@color/colorAccent</item>
        <item name="colorControlHighlight">@color/colorAccent</item>
        <item name="android:windowBackground">@color/colorBackground</item>
        <item name="android:statusBarColor">@color/colorPrimaryDark</item>
        <item name="android:textColorPrimary">@color/colorTextPrimary</item>
        <item name="android:textColorSecondary">@color/colorTextSecondary</item>
        <item name="android:editTextStyle">@style/InputStyle</item>
        <item name="buttonStyle">@style/ButtonStyle</item>
        <item name="toolbarStyle">@style/ToolbarStyle</item>
    </style>

    <style name="ToolbarStyle" parent="Widget.AppCompat.Toolbar">
        <item name="android:background">@color/colorPrimary</item>
        <item name="android:elevation">4dp</item>
        <item name="titleTextColor">@color/colorToolbarTitle</item>
        <item name="subtitleTextColor">@color/colorToolbarSub</item>
    </style>

    <style name="ButtonStyle" parent="Widget.AppCompat.Button">
        <item name="android:background">@drawable/btn_background</item>
        <item name="android:textColor">@color/colorButtonText</item>
        <item name="android:textSize">14sp</item>
        <item name="android:paddingLeft">16dp</item>
        <item name="android:paddingRight">16dp</item>
        <item name="android:paddingTop">10dp</item>
        <item name="android:paddingBottom">10dp</item>
    </style>

    <style name="InputStyle" parent="Widget.AppCompat.EditText">
        <item name="android:background">@drawable/input_background</item>
        <item name="android:paddingLeft">12dp</item>
        <item name="android:paddingRight">12dp</item>
        <item name="android:paddingTop">12dp</item>
        <item name="android:paddingBottom">12dp</item>
        <item name="android:textSize">14sp</item>
        <item name="android:textColor">@color/colorTextPrimary</item>
        <item name="android:textColorHint">@color/colorTextHint</item>
    </style>
</resources>
''', encoding="utf-8")
    print(f'  ✅ styles.xml → THEME: "{config["THEME"]}" COLOR: {config["COLOR_PRIMARY"]}')

    # Generate btn_background.xml
    (drawable_dir / "btn_background.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="@color/colorPrimary"/>
    <corners android:radius="{config["BUTTON_RADIUS"]}dp"/>
</shape>
''', encoding="utf-8")
    print(f'  ✅ btn_background.xml → RADIUS: {config["BUTTON_RADIUS"]}dp')

    # Generate input_background.xml
    (drawable_dir / "input_background.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@color/colorInputBg"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
    <item android:top="-2dp" android:left="-2dp" android:right="-2dp">
        <shape android:shape="rectangle">
            <stroke android:width="1dp" android:color="@color/colorDivider"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
</layer-list>
''', encoding="utf-8")
    print(f'  ✅ input_background.xml generated')
    
def update_build_gradle(project_root: Path, config: dict):
    """Update versionCode and versionName in build.gradle.kts."""
    build_gradle = project_root / "app" / "app" / "build.gradle.kts"
    if not build_gradle.exists():
        print("  ⚠ build.gradle.kts not found, skipping.")
        return

    content = build_gradle.read_text(encoding="utf-8")
    content = re.sub(
        r'(versionCode\s*=\s*)(\d+)',
        rf'\g<1>{config["VERSION_CODE"]}',
        content
    )
    content = re.sub(
        r'(versionName\s*=\s*")([^"]*?)(")',
        rf'\g<1>{config["VERSION_NAME"]}\3',
        content
    )
    build_gradle.write_text(content, encoding="utf-8")
    print(f'  ✅ build.gradle.kts → VERSION: {config["VERSION_NAME"]} ({config["VERSION_CODE"]})')


def update_manifest(project_root: Path, config: dict):
    """Fully regenerate AndroidManifest.xml from config."""
    manifest = project_root / "app" / "app" / "src" / "main" / "AndroidManifest.xml"
    package_name = read_package_name(project_root)

    launcher_activity = config["LAUNCHER_ACTIVITY"]
    launcher_class = activity_to_class_name(launcher_activity)

    # Only add icon attribute if user set LAUNCHER_ICON
    if config["LAUNCHER_ICON"]:
        icon_attr = f'\n        android:icon="@mipmap/ic_launcher"'
    else:
        icon_attr = ""

    main_dir = project_root / "main"
    activities = []
    for py_file in sorted(main_dir.glob("*.py")):
        class_name = activity_to_class_name(py_file.stem)
        is_launcher = py_file.stem == launcher_activity

        if is_launcher:
            activities.append(f'''        <activity
            android:name=".{class_name}"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>''')
        else:
            activities.append(f'''        <activity
            android:name=".{class_name}"
            android:exported="false"/>''')

    activities_str = "\n".join(activities)
    content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <application
        android:allowBackup="true"{icon_attr}
        android:label="@string/app_name"
        android:theme="@style/Theme.App">
{activities_str}
    </application>
</manifest>
'''
    manifest.write_text(content, encoding="utf-8")
    print(f'  ✅ AndroidManifest.xml → LAUNCHER: {launcher_class}')
    if config["LAUNCHER_ICON"]:
        print(f'  ✅ AndroidManifest.xml → ICON: @mipmap/ic_launcher')
        

def sync_activity_files(project_root: Path):
    """Remove XML and KT files for deleted Python activity files."""
    import re
    main_dir = project_root / "main"
    layout_dir = project_root / "app" / "app" / "src" / "main" / "res" / "layout"
    kt_dir = find_kt_dir(project_root)

    py_files = {f.stem for f in main_dir.glob("*.py")}

    if layout_dir.exists():
        for xml_file in layout_dir.glob("*.xml"):
            if xml_file.stem not in py_files:
                xml_file.unlink()
                print(f"  🗑 Removed {xml_file.name}")

    if kt_dir and kt_dir.exists():
        for kt_file in kt_dir.glob("*.kt"):
            kt_stem = kt_file.stem
            py_stem = re.sub(r'([A-Z])', r'_\1', kt_stem).strip('_').lower()
            if py_stem not in py_files:
                kt_file.unlink()
                print(f"  🗑 Removed {kt_file.name}")

MIPMAP_SIZES = {
    "mipmap-mdpi":     48,
    "mipmap-hdpi":     72,
    "mipmap-xhdpi":    96,
    "mipmap-xxhdpi":   144,
    "mipmap-xxxhdpi":  192,
}


def generate_launcher_icon(project_root: Path, config: dict):
    """Resize and copy launcher icon to all mipmap densities."""
    launcher_icon = config.get("LAUNCHER_ICON")
    if not launcher_icon:
        return

    try:
        from PIL import Image
    except ImportError:
        print("  ⚠ Pillow not installed. Run: pip install Pillow")
        return

    # Find source icon
    src_path = project_root / "main" / "res" / launcher_icon
    if not src_path.exists():
        print(f"  ⚠ Launcher icon not found: {src_path}")
        print(f"  💡 Place your icon at: main/res/{launcher_icon}")
        return

    res_dir = project_root / "app" / "app" / "src" / "main" / "res"

    try:
        img = Image.open(src_path).convert("RGBA")
    except Exception as e:
        print(f"  ⚠ Could not open icon: {e}")
        return

    for folder, size in MIPMAP_SIZES.items():
        mipmap_dir = res_dir / folder
        mipmap_dir.mkdir(parents=True, exist_ok=True)
        resized = img.resize((size, size), Image.LANCZOS)
        out_path = mipmap_dir / "ic_launcher.png"
        resized.save(out_path, "PNG")

    print(f"  ✅ Launcher icon generated → all mipmap densities")
