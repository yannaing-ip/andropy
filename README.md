# Andropy 🐍📱

Build native Android apps with pure Python.

Andropy compiles Python code to Kotlin and XML — no Android Studio, no Java, no Kotlin required.

---

## Installation

```bash
pip install andropy
```

---

## Requirements

- Python 3.10+
- Android SDK
- Java 17+
- ADB (for running on device)

---

## Quick Start

**1. Create a new project:**

```bash
andropy create myapp
cd myapp
```

**2. Write your UI in Python:**

```python
# main/main_activity.py
from andropy import ui
from andropy.ui import layout as L

class MainUI(ui.ActivityUI):
    def build(self):
        self.toolbar = ui.UiToolbar(title="My App")
        self.input_name = ui.UiInput(hint="Enter your name", width=L.W1, margin=L.M4)
        self.btn_greet = ui.UiButton("Greet", width=L.W1, margin=L.M4)
        self.text_result = ui.UiText("Result appears here", width=L.W1, padding=L.P4)

        return ui.UiScrollView(
            ui.UiColumn(
                self.toolbar,
                self.input_name,
                self.btn_greet,
                self.text_result,
            )
        )

class MainLogic(ui.ActivityLogic):
    def on_create(self):
        self.set_toolbar(self.toolbar)
        self.btn_greet.on_click(self.handle_greet)

    def handle_greet(self):
        name = self.input_name.getText()
        self.text_result.setText(f"Hello, {name}!")
```

**3. Compile, build and run:**

```bash
andropy compile
andropy build
andropy run
```

---

## Project Structure

```
myapp/
├── config.py          ← App configuration
├── main/              ← Python activity files
│   └── main_activity.py
└── app/               ← Generated Android project
```

---

## Configuration

```python
# config.py
from main import main_activity

# ─────────────────────────────────────────────
# App Info
# ─────────────────────────────────────────────
APP_NAME = "My App"
VERSION_CODE = 1
VERSION_NAME = "1.0"

# ─────────────────────────────────────────────
# Theme
# ─────────────────────────────────────────────
THEME = "light"  # light, dark

# ─────────────────────────────────────────────
# Launcher
# ─────────────────────────────────────────────
LAUNCHER_ICON = None
LAUNCHER_ACTIVITY = main_activity

# ─────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────
COLOR_PRIMARY        = "#1565C0"
COLOR_PRIMARY_DARK   = "#0D47A1"
COLOR_ACCENT         = "#1565C0"
COLOR_BACKGROUND     = "#FFFFFF"
COLOR_TEXT_PRIMARY   = "#212121"
COLOR_TEXT_SECONDARY = "#757575"
COLOR_TEXT_HINT      = "#9E9E9E"
COLOR_DIVIDER        = "#E0E0E0"
COLOR_INPUT_BG       = "#F5F5F5"
COLOR_TOOLBAR_TITLE  = "#FFFFFF"
COLOR_TOOLBAR_SUB    = "#BBDEFB"
COLOR_BUTTON_TEXT    = "#FFFFFF"

# ─────────────────────────────────────────────
# Shape
# ─────────────────────────────────────────────
BUTTON_RADIUS = 4  # dp
```

---

## UI Widgets

| Widget | Android View |
|--------|-------------|
| `UiText` | TextView |
| `UiButton` | Button |
| `UiInput` | EditText |
| `UiImage` | ImageView |
| `UiCheckbox` | CheckBox |
| `UiSwitch` | Switch |
| `UiSlider` | SeekBar |
| `UiProgress` | ProgressBar |
| `UiToolbar` | Toolbar |
| `UiDivider` | Divider line |
| `UiSpace` | Empty space |
| `UiScrollView` | ScrollView |

---

## Layouts

| Layout | Description |
|--------|-------------|
| `UiColumn` | Vertical layout |
| `UiRow` | Horizontal layout |

---

## Layout Constants

```python
from andropy.ui import layout as L

L.W0  # wrap_content    L.W1  # match_parent
L.H0  # wrap_content    L.H1  # match_parent

L.P0  # 0dp    L.P1  # 4dp    L.P2  # 8dp
L.P3  # 12dp   L.P4  # 16dp   L.P5  # 24dp   L.P6  # 32dp

L.M0  # 0dp    L.M1  # 4dp    L.M2  # 8dp
L.M3  # 12dp   L.M4  # 16dp   L.M5  # 24dp   L.M6  # 32dp
```

---

## Events

```python
# Button click
def on_create(self):
    self.btn.on_click(self.handle_click)

def handle_click(self):
    toast = ui.Toast()
    toast.show("Clicked!")

# Read input
def handle_submit(self):
    text = self.input_name.getText()
    self.text_result.setText(f"Hello, {text}!")

# Navigate to another screen
def handle_login(self):
    self.navigate("DashboardActivity")
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `andropy create <name>` | Create new project |
| `andropy compile` | Compile Python → XML + KT |
| `andropy build` | Build debug APK |
| `andropy run` | Install and run on device |
| `andropy clean` | Clean build artifacts |
| `andropy sync` | Sync assets and drawables |

---

## Multi-Screen Apps

```python
# main/dashboard_activity.py
from andropy import ui
from andropy.ui import layout as L

class DashboardUI(ui.ActivityUI):
    def build(self):
        self.toolbar = ui.UiToolbar(title="Dashboard")
        return ui.UiScrollView(
            ui.UiColumn(
                self.toolbar,
            )
        )

class DashboardLogic(ui.ActivityLogic):
    def on_create(self):
        self.set_toolbar(self.toolbar)
```

Navigate from `MainLogic`:

```python
def handle_login(self):
    self.navigate("DashboardActivity")
```

Andropy automatically registers `DashboardActivity` in `AndroidManifest.xml`.

