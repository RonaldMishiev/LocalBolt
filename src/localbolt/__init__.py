try:
    from .parsing import process_assembly

    __all__ = ["process_assembly"]
except ImportError:
    # Teammate modules may not be wired up yet; allow partial imports
    __all__ = []
