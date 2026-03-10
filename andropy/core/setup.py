import os
import shutil
import subprocess
import platform
import zipfile
import urllib.request
from pathlib import Path
from rich.console import Console

console = Console()

CMDLINE_TOOLS_URLS = {
    "linux":   "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip",
    "termux":  "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip",
    "mac":     "https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip",
    "windows": "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip",
}

SDK_PACKAGES = [
    "platform-tools",
    "build-tools;34.0.0",
    "platforms;android-34",
]


def get_platform() -> str:
    if "com.termux" in str(Path.home()):
        return "termux"
    system = platform.system()
    if system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "mac"
    elif system == "Windows":
        return "windows"
    return "unknown"


def get_sdk_dir() -> Path:
    p = get_platform()
    if p in ("termux", "linux"):
        return Path.home() / "android-sdk"
    elif p == "mac":
        return Path.home() / "Library" / "Android" / "sdk"
    elif p == "windows":
        return Path.home() / "AppData" / "Local" / "Android" / "Sdk"
    return Path.home() / "android-sdk"


# ─────────────────────────────────────────────
# Checks
# ─────────────────────────────────────────────

def check_java() -> bool:
    return shutil.which("java") is not None

def get_java_version() -> str:
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        return result.stderr.split("\n")[0]
    except Exception:
        return "unknown"

def check_cmdline_tools(sdk_dir: Path) -> bool:
    return (sdk_dir / "cmdline-tools" / "latest" / "bin" / "sdkmanager").exists()

def check_adb() -> bool:
    return shutil.which("adb") is not None

def check_gradle() -> bool:
    return shutil.which("gradle") is not None

def check_aapt2() -> bool:
    return shutil.which("aapt2") is not None


# ─────────────────────────────────────────────
# Installers
# ─────────────────────────────────────────────

def run_cmd(cmd: list, label: str) -> bool:
    console.print(f"  📦 {label}...")
    try:
        subprocess.run(cmd, check=True)
        console.print(f"  ✅ Done")
        return True
    except Exception as e:
        console.print(f"  ❌ Failed: {e}")
        return False


def install_java(p: str) -> bool:
    console.print("  ❌ Java not found — installing...")
    if p == "termux":
        return run_cmd(["pkg", "install", "-y", "openjdk-21"], "pkg install openjdk-21")
    elif p == "linux":
        console.print("  [yellow]Run: sudo apt install openjdk-21-jdk[/yellow]")
        return False
    elif p == "mac":
        if shutil.which("brew"):
            return run_cmd(["brew", "install", "openjdk@21"], "brew install openjdk@21")
        console.print("  [yellow]Run: brew install openjdk@21[/yellow]")
        return False
    elif p == "windows":
        console.print("  [yellow]Download Java from: https://adoptium.net/[/yellow]")
        return False
    return False


def set_java_home():
    java_path = shutil.which("java")
    if not java_path:
        return
    real_path = Path(java_path).resolve()
    java_home = str(real_path.parent.parent)
    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = f"{java_home}/bin:{os.environ['PATH']}"
    console.print(f"  ✅ JAVA_HOME = {java_home}")


def install_termux_packages() -> bool:
    console.print("\n[bold cyan]📦 Installing Termux packages...[/bold cyan]\n")

    if not run_cmd(["pkg", "install", "-y", "wget", "unzip"], "pkg install wget unzip"):
        return False
    if not run_cmd(["apt", "install", "-y", "gradle", "aapt2"], "apt install gradle aapt2"):
        return False
    if not run_cmd(["pkg", "install", "-y", "android-tools"], "pkg install android-tools"):
        return False

    return True


def install_linux_packages() -> bool:
    console.print("\n[bold cyan]📦 Checking Linux packages...[/bold cyan]\n")
    missing = []
    if not check_gradle():
        missing.append("gradle")
    if not check_aapt2():
        missing.append("aapt2")
    if missing:
        console.print(f"  [yellow]Please install missing packages:[/yellow]")
        console.print(f"    sudo apt install {' '.join(missing)}")
        return False
    return True


def download_cmdline_tools(sdk_dir: Path, p: str) -> bool:
    url = CMDLINE_TOOLS_URLS.get(p, CMDLINE_TOOLS_URLS["linux"])
    zip_path = sdk_dir / "cmdline-tools.zip"

    sdk_dir.mkdir(parents=True, exist_ok=True)

    console.print("  ⬇ Downloading cmdline-tools...")
    try:
        urllib.request.urlretrieve(url, zip_path)
        console.print("  ✅ Downloaded")
    except Exception as e:
        console.print(f"  ❌ Download failed: {e}")
        return False

    console.print("  📦 Extracting...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(sdk_dir)

        # Fix folder structure → cmdline-tools/latest/
        extracted = sdk_dir / "cmdline-tools"
        latest = extracted / "latest"
        if not latest.exists():
            temp = sdk_dir / "cmdline-tools-temp"
            extracted.rename(temp)
            extracted.mkdir()
            temp.rename(latest)

        zip_path.unlink()

        # Fix permissions on sdkmanager
        sdkmanager = sdk_dir / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
        if sdkmanager.exists():
            sdkmanager.chmod(0o755)
        # Fix permissions
        sdkmanager = sdk_dir / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
        if sdkmanager.exists():
            sdkmanager.chmod(0o755)
        console.print("  ✅ cmdline-tools ready")
        return True
    except Exception as e:
        console.print(f"  ❌ Extraction failed: {e}")
        return False


def get_sdkmanager(sdk_dir: Path) -> str | None:
    path = sdk_dir / "cmdline-tools" / "latest" / "bin" / "sdkmanager"
    if path.exists():
        return str(path)
    path_bat = sdk_dir / "cmdline-tools" / "latest" / "bin" / "sdkmanager.bat"
    if path_bat.exists():
        return str(path_bat)
    return None


def accept_licenses(sdk_dir: Path, env: dict) -> bool:
    sdkmanager = get_sdkmanager(sdk_dir)
    if not sdkmanager:
        return False
    console.print("  📜 Accepting licenses...")
    try:
        subprocess.run(
            [sdkmanager, "--licenses"],
            input="y\n" * 20,
            text=True,
            env=env,
            capture_output=True
        )
        console.print("  ✅ Licenses accepted")
        return True
    except Exception as e:
        console.print(f"  ❌ {e}")
        return False


def install_sdk_packages(sdk_dir: Path) -> bool:
    sdkmanager = get_sdkmanager(sdk_dir)
    if not sdkmanager:
        console.print("  ❌ sdkmanager not found!")
        return False

    env = os.environ.copy()
    env["ANDROID_HOME"] = str(sdk_dir)
    env["ANDROID_SDK_ROOT"] = str(sdk_dir)

    accept_licenses(sdk_dir, env)

    for package in SDK_PACKAGES:
        console.print(f"  ⬇ Installing {package}...")
        try:
            result = subprocess.run(
                [sdkmanager, package],
                input="y\n",
                text=True,
                env=env,
                capture_output=True,
                timeout=300
            )
            if result.returncode == 0:
                console.print(f"  ✅ {package} installed")
            else:
                console.print(f"  ❌ Failed: {package}")
                console.print(f"     {result.stderr[:200]}")
                return False
        except subprocess.TimeoutExpired:
            console.print(f"  ❌ Timeout: {package}")
            return False
        except Exception as e:
            console.print(f"  ❌ Error: {e}")
            return False

    return True


def set_android_home(sdk_dir: Path):
    export_lines = (
        f'\n# Android SDK\n'
        f'export ANDROID_HOME="{sdk_dir}"\n'
        f'export ANDROID_SDK_ROOT="{sdk_dir}"\n'
        f'export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"\n'
        f'export PATH="$PATH:$ANDROID_HOME/platform-tools"\n'
    )

    for profile in [Path.home() / ".bashrc", Path.home() / ".bash_profile", Path.home() / ".zshrc"]:
        if profile.exists():
            content = profile.read_text()
            if "ANDROID_HOME" not in content:
                profile.write_text(content + export_lines)
                console.print(f"  ✅ ANDROID_HOME written to {profile.name}")
            else:
                console.print(f"  ✅ ANDROID_HOME already set in {profile.name}")
            break

    os.environ["ANDROID_HOME"] = str(sdk_dir)
    os.environ["ANDROID_SDK_ROOT"] = str(sdk_dir)
    os.environ["PATH"] = f"{sdk_dir}/cmdline-tools/latest/bin:{sdk_dir}/platform-tools:{os.environ['PATH']}"


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def run_setup():
    p = get_platform()
    sdk_dir = get_sdk_dir()

    console.print(f"\n[bold cyan]🔍 Checking environment ({p})...[/bold cyan]\n")

    # ── Step 1: Platform packages ──
    if p == "termux":
        if not install_termux_packages():
            return False
    elif p == "linux":
        if not install_linux_packages():
            return False
    elif p == "mac":
        pass  # handled per-tool below
    elif p == "windows":
        console.print("  [yellow]Windows: Please install manually:[/yellow]")
        console.print("    Java:  https://adoptium.net/")
        console.print("    SDK:   https://developer.android.com/studio#command-tools")
        return False

    # ── Step 2: Java ──
    console.print("\n[bold cyan]☕ Checking Java...[/bold cyan]\n")
    if check_java():
        console.print(f"  ✅ Java found — {get_java_version()}")
    else:
        if not install_java(p):
            return False
    set_java_home()

    # ── Step 3: cmdline-tools ──
    console.print("\n[bold cyan]🔧 Checking Android SDK...[/bold cyan]\n")
    if check_cmdline_tools(sdk_dir):
        console.print(f"  ✅ cmdline-tools found")
    else:
        console.print(f"  ❌ cmdline-tools not found")
        if not download_cmdline_tools(sdk_dir, p):
            return False

    set_android_home(sdk_dir)

    # ── Step 4: SDK packages ──
    console.print("\n[bold cyan]📱 Installing SDK packages...[/bold cyan]\n")
    if not install_sdk_packages(sdk_dir):
        return False

    # ── Step 5: ADB ──
    console.print("\n[bold cyan]🔌 Checking ADB...[/bold cyan]\n")
    if check_adb():
        console.print("  ✅ ADB found")
    else:
        console.print("  ⚠ ADB not found — restart terminal")

    # ── Done ──
    console.print(f"\n[bold green]✅ Environment ready![/bold green]")
    console.print(f"   ANDROID_HOME = {sdk_dir}")
    console.print(f"\n[yellow]⚠ Restart terminal to apply PATH changes[/yellow]")
    console.print("\nNow run:")
    console.print("  andropy create myapp\n")
    return True

