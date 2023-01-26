import sys
import pathlib

mod_dir = pathlib.Path(__file__).parent.parent
if not str(mod_dir) in sys.path:
    sys.path.append(str(mod_dir))

pdocs_dir = pathlib.Path(__file__).parent.parent.parent / "pdocs"
if pdocs_dir.is_dir() and not str(pdocs_dir) in sys.path:
    sys.path.append(str(pdocs_dir))

try:
    from portray.cli import __hug__  # type: ignore
    __hug__.cli()
except (AttributeError, ImportError, ModuleNotFoundError) as exc:
    import traceback
    tb = traceback.format_tb(exc.__traceback__)
    print("".join(tb), file=sys.stderr)
    print("\n".join(sys.path), file=sys.stderr)

