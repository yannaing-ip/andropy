class AndropyError(Exception):
    """Base Andropy error."""
    pass


class CompileError(AndropyError):
    """Raised during Python → XML/KT compilation."""
    pass


class ConfigError(AndropyError):
    """Raised when config.py has issues."""
    pass


class ProjectError(AndropyError):
    """Raised when project structure is invalid."""
    pass


class BuildError(AndropyError):
    """Raised during Gradle build."""
    pass


class DeviceError(AndropyError):
    """Raised when no device connected."""
    pass