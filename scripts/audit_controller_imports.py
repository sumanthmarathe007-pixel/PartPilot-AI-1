"""Basic import audit for the controller/helper source tree (stdlib only)."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = [ROOT / "solution.py", ROOT / "partpilot"]
ALLOWED_TOP_LEVEL = set()  # all controller imports should be stdlib or local partpilot


def iter_python_files():
    for item in SCAN:
        if item.is_file():
            yield item
        else:
            yield from item.rglob("*.py")


def main():
    offenders = []
    for path in iter_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.level:
                    continue  # package-relative import is local helper code
                names = [node.module.split(".")[0]]
            else:
                continue
            for name in names:
                if name == "partpilot" or name in ALLOWED_TOP_LEVEL:
                    continue
                # Local/stdlib detection uses Python's module registry and known stdlib paths.
                import sysconfig
                stdlib = Path(sysconfig.get_paths()["stdlib"]).resolve()
                candidates = [stdlib / (name + ".py"), stdlib / name]
                if not any(candidate.exists() for candidate in candidates):
                    offenders.append((str(path.relative_to(ROOT)), name))
    if offenders:
        for path, module in offenders:
            print(f"NON-STDLIB IMPORT: {path}: {module}")
        return 1
    print("Controller import audit: no third-party imports found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
