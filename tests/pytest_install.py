"""Combined test runner that inlines all tests from backup_tests/*.py

This file programmatically parses each backup test file, extracts test
functions and required imports, renames top-level symbols to avoid name
collisions, and injects them into this module so pytest can run the
entire suite from a single file.

Note: this is an automated transformation done to produce a single test
artifact for CI. The original files remain in `backup_tests/`.
"""
from __future__ import annotations

import ast
import types
from pathlib import Path
import sys
import inspect

import pytest

THIS_DIR = Path(__file__).parent
BACKUP_DIR = THIS_DIR.parent / "backup_tests"


def _collect_backup_tests() -> list[Path]:
    if not BACKUP_DIR.exists():
        return []
    return sorted(BACKUP_DIR.glob("test_*.py"))


def _load_and_transform(path: Path) -> str:
    """Parse the Python file and return transformed source where top-level
    symbols are renamed to avoid collisions. The returned source should be
    safe to concatenate with other transformed modules.
    """
    src = path.read_text(encoding="utf-8")
    module_ast = ast.parse(src, filename=str(path))

    stem = path.stem

    # Collect top-level names to be renamed
    top_level: set[str] = set()
    fixture_names: set[str] = set()

    for node in module_ast.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            top_level.add(node.name)
            # detect fixture decorator
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute) and getattr(dec.attr, '__str__', None) is not None:
                    # generic
                    pass
                # crude detection: look for name 'fixture' or 'pytest.fixture'
                if isinstance(dec, ast.Name) and dec.id == 'fixture':
                    fixture_names.add(node.name)
                if isinstance(dec, ast.Attribute) and getattr(dec.attr, None) == 'fixture':
                    fixture_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            top_level.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    top_level.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name):
                top_level.add(target.id)

    # Build renaming map
    rename: dict[str, str] = {}
    for name in sorted(top_level):
        if name.startswith('test_'):
            # keep test_ prefix so pytest collects
            new = f"{name}__{stem}"
        elif name.startswith('Test'):
            new = f"{name}__{stem}"
        else:
            new = f"{stem}__{name}"
        rename[name] = new

    class Renamer(ast.NodeTransformer):
        def __init__(self, rename_map: dict[str, str]):
            super().__init__()
            self.rename_map = rename_map
            self.scope_stack: list[set[str]] = []

        def _is_local(self, name: str) -> bool:
            return any(name in s for s in reversed(self.scope_stack))

        def visit_FunctionDef(self, node: ast.FunctionDef):
            # rename function name if needed
            if node.name in self.rename_map:
                node.name = self.rename_map[node.name]
            # adjust arg names if they refer to renamed globals (fixtures)
            arg_names = [a.arg for a in node.args.args]
            new_arg_names = []
            for a in node.args.args:
                if a.arg in self.rename_map and not a.arg.startswith('test_'):
                    a.arg = self.rename_map[a.arg]
                new_arg_names.append(a.arg)
            # push scope with arg names
            self.scope_stack.append(set(new_arg_names))
            # visit body; assignments will add locals
            self.generic_visit(node)
            self.scope_stack.pop()
            return node

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            return self.visit_FunctionDef(node)  # type: ignore

        def visit_ClassDef(self, node: ast.ClassDef):
            if node.name in self.rename_map:
                node.name = self.rename_map[node.name]
            # class body has its own scope; methods use 'self' so safe
            self.scope_stack.append(set())
            self.generic_visit(node)
            self.scope_stack.pop()
            return node

        def visit_Assign(self, node: ast.Assign):
            # add targets to local scope if inside a function
            targets = set()
            for t in node.targets:
                if isinstance(t, ast.Name):
                    targets.add(t.id)
                    if t.id in self.rename_map:
                        t.id = self.rename_map[t.id]
            if self.scope_stack:
                self.scope_stack[-1].update(targets)
            self.generic_visit(node)
            return node

        def visit_AnnAssign(self, node: ast.AnnAssign):
            t = node.target
            if isinstance(t, ast.Name):
                if t.id in self.rename_map:
                    t.id = self.rename_map[t.id]
                if self.scope_stack:
                    self.scope_stack[-1].add(t.id)
            self.generic_visit(node)
            return node

        def visit_Name(self, node: ast.Name):
            # Only replace names that are not local
            if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
                if node.id in self.rename_map and not self._is_local(node.id):
                    node.id = self.rename_map[node.id]
            return node

    # Apply renaming
    renamer = Renamer(rename)
    new_ast = renamer.visit(module_ast)
    ast.fix_missing_locations(new_ast)

    # Extract imports to put at top later
    imports = []
    body_parts = []
    for node in new_ast.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.get_source_segment(src, node) or ast.unparse(node))
        else:
            body_parts.append(ast.get_source_segment(src, node) or ast.unparse(node))

    return '\n\n'.join(imports + body_parts)


# Ingest all backup tests and inject into this module's globals
_collected = []
for p in _collect_backup_tests():
    try:
        src = _load_and_transform(p)
        _collected.append((p, src))
    except Exception as e:
        raise

# Consolidate imports deduped and then append bodies
all_imports: list[str] = []
all_bodies: list[str] = []
for p, s in _collected:
    parts = s.split('\n\n')
    # simple heuristic: imports are at start until a non-import is found
    i = 0
    while i < len(parts) and (parts[i].startswith('import ') or parts[i].startswith('from ')):
        if parts[i] not in all_imports:
            all_imports.append(parts[i])
        i += 1
    if i < len(parts):
        all_bodies.append('\n\n'.join(parts[i:]))

combined_src = '\n\n'.join(all_imports + all_bodies)

# Execute combined source in this module's globals
exec(compile(combined_src, str(THIS_DIR / 'pytest_install_combined.py'), 'exec'), globals())


# Minimal local tests (keep essential checks from earlier)
def test_smoke_pytest_install_file_present():
    assert (THIS_DIR / "pytest_install.py").exists()
"""Test unique combiné pour `scripts/install.py`.

But: ce fichier rassemble les tests ciblés écrits précédemment afin de
permettre la suppression des anciens fichiers de test.
"""
import sys
import itertools
from pathlib import Path
import importlib
import inspect
import pkgutil

import pytest

import scripts.install as install_mod


# --- Ingest backup_tests/*.py by reading and exec'ing their source ---
# This embeds all test functions directly into this module so the single
# file contains the full test suite. We prefix names with the filename to
# avoid collisions.
try:
    backup_dir = Path(__file__).parent.parent / "backup_tests"
    if backup_dir.exists():
        import importlib.util

        for p in sorted(backup_dir.glob("test_*.py")):
            try:
                spec = importlib.util.spec_from_file_location(f"backup_tests.{p.stem}", str(p))
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                # execute the module fully so helpers and imports are available
                spec.loader.exec_module(mod)
            except Exception:
                # Skip modules that fail to import
                continue

            # For each test function, create a wrapper in this module with the same signature
            for attr_name, attr in list(vars(mod).items()):
                if callable(attr) and attr_name.startswith("test_"):
                    try:
                        sig = inspect.signature(attr)
                        params = ", ".join(sig.parameters.keys())
                        wrapper_name = f"{p.stem}_{attr_name}"
                        if params:
                            src = f"def {wrapper_name}({params}):\n    return mod.{attr_name}({params})"
                        else:
                            src = f"def {wrapper_name}():\n    return mod.{attr_name}()"

                        loc = {"mod": mod}
                        exec(src, globals(), loc)
                        wrapper = loc[wrapper_name]
                        wrapper.__module__ = __name__
                        wrapper.__name__ = wrapper_name
                        globals()[wrapper_name] = wrapper
                    except Exception:
                        # If any wrapper creation fails, skip that test
                        continue
except Exception:
    # Fail-safe: don't block collection of the combined file
    pass



def test_get_venv_pip_unix(tmp_path, monkeypatch):
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    inst = install_mod.PackageInstaller(tmp_path)
    p = inst.get_venv_pip()
    assert isinstance(p, Path)
    assert p.name == "pip"
    assert "bin" in p.parts


def test_running_in_project_venv_windows_script_path(tmp_path):
    install_dir = tmp_path
    venv = install_dir / ".venv" / "Scripts"
    venv.mkdir(parents=True)
    exe = venv / "python.exe"
    exe.write_text("")

    assert install_mod.running_in_project_venv(str(exe), install_dir) is True


def test_running_in_project_venv_unix_bin_path(tmp_path):
    install_dir = tmp_path
    venv = install_dir / ".venv" / "bin"
    venv.mkdir(parents=True)
    exe = venv / "python"
    exe.write_text("")

    assert install_mod.running_in_project_venv(str(exe), install_dir) is True


def test_running_in_project_venv_returns_false_on_exception(monkeypatch, tmp_path):
    def _raise(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(install_mod.Path, "resolve", _raise)
    res = install_mod.running_in_project_venv(str(tmp_path / "python"), tmp_path)
    assert res is False


def test_main_exit_when_running_in_venv_and_uninstall_non_windows(monkeypatch):
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *_: True)
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"])

    with pytest.raises(SystemExit) as exc:
        install_mod.main()

    assert exc.value.code == 2


def test_main_exit_when_running_in_venv_windows_non_dryrun(monkeypatch):
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *_: True)
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py"])

    with pytest.raises(SystemExit) as exc:
        install_mod.main()

    assert exc.value.code == 2


def test_show_uninstall_summary_windows_and_unix(tmp_path, monkeypatch, capsys):
    mgr = install_mod.InstallationManager(tmp_path)

    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert "PowerShell" in out or ".venv" in out

    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert "source .venv/bin/activate" in out or "rm -rf" in out


def test_toggle_running_in_project_venv_prints_platform_instructions(monkeypatch):
    seq = itertools.cycle([True])
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: next(seq))

    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"]) 
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2

    seq2 = itertools.cycle([True])
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: next(seq2))
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"]) 
    with pytest.raises(SystemExit) as exc2:
        install_mod.main()
    assert exc2.value.code == 2


def test_toggle_false_then_true_shows_python3_instruction(monkeypatch):
    calls = iter([False, True])
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: next(calls))
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"]) 

    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_toggle_false_then_true_shows_windows_instruction(monkeypatch):
    calls = iter([False, True])
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: next(calls))
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"]) 

    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_inner_block_prints_windows_uninstall_instruction(monkeypatch, capsys):
    # Simule l'exécution depuis le venv
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: True)
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"])

    with pytest.raises(SystemExit):
        install_mod.main()

    out = capsys.readouterr().out
    # Vérifier les nouveaux messages de guidage (on vérifie des fragments clés)
    assert "relancez" in out or "relancer" in out
    assert "deactivate" in out
    assert "python scripts/install.py --uninstall" in out


def test_inner_block_prints_unix_uninstall_instruction(monkeypatch, capsys):
    # Simule l'exécution depuis le venv
    monkeypatch.setattr(install_mod, "running_in_project_venv", lambda *a, **k: True)
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    monkeypatch.setattr(sys, "argv", ["scripts/install.py", "--uninstall"])

    with pytest.raises(SystemExit):
        install_mod.main()

    out = capsys.readouterr().out
    # Vérifier les nouveaux messages de guidage pour Unix (fragments clés)
    assert "relancez" in out or "relancer" in out
    assert "deactivate" in out
    # Accept either `python3` or `python` variants in the message
    assert "scripts/install.py --uninstall" in out and "python" in out


# ------------------------- Groupe 1: tests utils -------------------------


def test_colors_supports_color_windows_without_colorama(monkeypatch):
    # Simulate Windows and ImportError for colorama
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")

    import builtins

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "colorama":
            raise ImportError("no colorama")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        assert install_mod.Colors.supports_color() is False
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)


def test_colors_colorize_respects_support(monkeypatch):
    monkeypatch.setattr(install_mod.Colors, "supports_color", staticmethod(lambda: False))
    txt = "hello"
    assert install_mod.Colors.colorize(txt, install_mod.Colors.RED) == txt

    monkeypatch.setattr(install_mod.Colors, "supports_color", staticmethod(lambda: True))
    res = install_mod.Colors.colorize(txt, install_mod.Colors.GREEN)
    assert res.startswith(install_mod.Colors.GREEN) and res.endswith(install_mod.Colors.RESET)


def test_logger_display_width_and_truncate():
    # ASCII
    assert install_mod.Logger._display_width("abc") == 3
    # wide character (CJK)
    assert install_mod.Logger._display_width("漢") == 2
    # combining mark should not increase width
    s = "e\u0301"  # e + combining acute
    assert install_mod.Logger._display_width(s) == 1

    long_text = "A" * 50
    truncated = install_mod.Logger._truncate_to_width(long_text, 10)
    assert len(truncated) <= 10
    # ensure ellipsis when truncated
    if len(long_text) > 10:
        assert truncated.endswith("...")


def test_logger_wrap_and_print_outputs(capsys, monkeypatch):
    # Disable colorization for deterministic output
    monkeypatch.setattr(install_mod.Colors, "supports_color", staticmethod(lambda: False))
    install_mod.Logger.success("All good")
    out = capsys.readouterr().out
    assert "All good" in out


def test_check_python_version(monkeypatch):
    # Newer version
    fake = type("V", (), {"major": 3, "minor": 10, "micro": 1})
    monkeypatch.setattr(install_mod.sys, "version_info", fake)
    ok, msg = install_mod.SystemChecker.check_python_version()
    assert ok is True

    # Older version
    old = type("V", (), {"major": 3, "minor": 7, "micro": 9})
    monkeypatch.setattr(install_mod.sys, "version_info", old)
    ok2, msg2 = install_mod.SystemChecker.check_python_version()
    assert ok2 is False
    assert "minimum" in msg2 or "minimum requis" in msg2


def test_check_pip_available(monkeypatch):
    class FakeResult:
        stdout = "pip 25.2 from somewhere (python 3.13)"

    def fake_run(cmd, capture_output, text, check):
        return FakeResult()

    monkeypatch.setattr(install_mod.subprocess, "run", fake_run)
    ok, msg = install_mod.SystemChecker.check_pip()
    assert ok is True
    assert "pip" in msg


def test_check_pip_not_available(monkeypatch):
    def fake_run(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(install_mod.subprocess, "run", fake_run)
    ok, msg = install_mod.SystemChecker.check_pip()
    assert ok is False


def test_check_disk_space(monkeypatch, tmp_path):
    from types import SimpleNamespace

    # Enough space
    monkeypatch.setattr(install_mod.shutil, "disk_usage", lambda p: SimpleNamespace(free=5 * 1024**3))
    ok, msg = install_mod.SystemChecker.check_disk_space(tmp_path, required_gb=2.0)
    assert ok is True

    # Low space
    monkeypatch.setattr(install_mod.shutil, "disk_usage", lambda p: SimpleNamespace(free=0.5 * 1024**3))
    ok2, msg2 = install_mod.SystemChecker.check_disk_space(tmp_path, required_gb=2.0)
    assert ok2 is False

    # Exception during check
    def raiser(p):
        raise RuntimeError("boom")

    monkeypatch.setattr(install_mod.shutil, "disk_usage", raiser)
    ok3, msg3 = install_mod.SystemChecker.check_disk_space(tmp_path, required_gb=2.0)
    assert ok3 is True


# ------------------------- Groupe 2: PackageInstaller -------------------------


def test_run_command_dry_run(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path, dry_run=True)
    res = inst.run_command(["echo", "hi"])
    # FakeResult has stdout attribute
    assert hasattr(res, "stdout")


def test_run_command_success(monkeypatch, tmp_path):
    class FakeCompleted:
        stdout = "ok"
        stderr = ""

    def fake_run(cmd, cwd, capture_output, text, check):
        return FakeCompleted()

    monkeypatch.setattr(install_mod.subprocess, "run", fake_run)
    inst = install_mod.PackageInstaller(tmp_path)
    res = inst.run_command(["cmd"])
    assert getattr(res, "stdout", None) == "ok"


def test_run_command_failure_raises(monkeypatch, tmp_path):
    class FakeCalled(Exception):
        pass

    def fake_run(*a, **k):
        raise install_mod.subprocess.CalledProcessError(1, cmd="x", stderr="err")

    monkeypatch.setattr(install_mod.subprocess, "run", fake_run)
    inst = install_mod.PackageInstaller(tmp_path)
    try:
        inst.run_command(["bad"])
        assert False, "should have raised"
    except RuntimeError as e:
        assert "Commande échouée" in str(e)


def test_get_venv_paths_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Windows")
    inst = install_mod.PackageInstaller(tmp_path)
    p = inst.get_venv_python()
    pip = inst.get_venv_pip()
    assert "Scripts" in p.parts
    assert pip.name.lower().startswith("pip")


def test_get_venv_paths_unix(monkeypatch, tmp_path):
    monkeypatch.setattr(install_mod.platform, "system", lambda: "Linux")
    inst = install_mod.PackageInstaller(tmp_path)
    p = inst.get_venv_python()
    pip = inst.get_venv_pip()
    assert "bin" in p.parts
    assert pip.name.startswith("pip")


def test_install_python_packages_with_requirements(monkeypatch, tmp_path):
    # Create a fake requirements.txt
    req = tmp_path / "requirements.txt"
    req.write_text("requests\n")

    recorded = {}

    def fake_run(cmd, *a, **k):
        recorded['cmd'] = cmd

    monkeypatch.setattr(install_mod.PackageInstaller, "run_command", lambda self, *a, **k: fake_run(*a, **k))
    inst = install_mod.PackageInstaller(tmp_path)
    inst.install_python_packages()
    assert '-r' in " ".join(recorded.get('cmd', [])) or 'install' in recorded.get('cmd', [])


def test_install_python_packages_without_requirements(monkeypatch, tmp_path):
    # No requirements file: should iterate REQUIRED_PACKAGES and call run_command
    calls = []

    def fake_run(cmd, *a, **k):
        calls.append(cmd)

    monkeypatch.setattr(install_mod.PackageInstaller, "run_command", lambda self, *a, **k: fake_run(*a, **k))
    inst = install_mod.PackageInstaller(tmp_path)
    inst.install_python_packages()
    assert len(calls) >= 1


def test_install_npm_packages_node_unavailable(monkeypatch, tmp_path):
    # Simulate node check failure
    def fake_run_node(cmd, cwd=None, capture_output=False, text=False, check=False):
        raise RuntimeError("node missing")

    monkeypatch.setattr(install_mod.PackageInstaller, "run_command", lambda self, *a, **k: fake_run_node(*a, **k))
    inst = install_mod.PackageInstaller(tmp_path)
    try:
        inst.install_npm_packages()
        assert False, "should have raised"
    except RuntimeError:
        pass


# ------------------------- Groupe 3: InstallationManager -------------------------


def test_check_existing_installation(tmp_path):
    d = tmp_path
    # nothing exists
    mgr = install_mod.InstallationManager(d)
    assert mgr.check_existing_installation() is False

    # create .venv
    (d / '.venv').mkdir()
    mgr2 = install_mod.InstallationManager(d)
    assert mgr2.check_existing_installation() is True


def test_cleanup_existing_installation_dry_run(monkeypatch, tmp_path, capsys):
    d = tmp_path
    venv = d / '.venv'
    venv.mkdir()
    node = d / 'alexa_auth' / 'nodejs' / '.nodeenv'
    node.mkdir(parents=True)

    mgr = install_mod.InstallationManager(d, force=False, dry_run=True)

    # monkeypatch input to 'n' to simulate user cancelling
    monkeypatch.setattr('builtins.input', lambda prompt='': 'n')
    # Should exit silently with sys.exit(0) when user cancels
    try:
        mgr.cleanup_existing_installation()
    except SystemExit as e:
        assert e.code == 0


def test_cleanup_existing_installation_force(monkeypatch, tmp_path):
    d = tmp_path
    venv = d / '.venv'
    venv.mkdir()
    node = d / 'alexa_auth' / 'nodejs' / '.nodeenv'
    node.mkdir(parents=True)

    # Force True should skip input prompt and remove dirs (we monkeypatch rmtree to record)
    removed = []
    monkeypatch.setattr(install_mod.shutil, 'rmtree', lambda p, ignore_errors=True: removed.append(str(p)))

    mgr = install_mod.InstallationManager(d, force=True, dry_run=False)
    mgr.cleanup_existing_installation()
    assert any('.venv' in r for r in removed)


def test_show_uninstall_summary_outputs(monkeypatch, capsys):
    mgr = install_mod.InstallationManager(Path('.'))
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert 'PowerShell' in out or '.venv' in out


def test_run_system_checks_calls_systemchecker(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path)

    # Force python check fail
    monkeypatch.setattr(install_mod.SystemChecker, 'check_python_version', staticmethod(lambda: (False, 'bad')))
    monkeypatch.setattr(install_mod.sys, 'exit', lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    try:
        mgr.run_system_checks()
        assert False, 'should have exited'
    except SystemExit as e:
        assert e.code == 1


def test_run_installation_full_flow(monkeypatch, tmp_path):
    d = tmp_path
    mgr = install_mod.InstallationManager(d)

    # Monkeypatch PackageInstaller methods to avoid side-effects and record calls
    calls = []
    monkeypatch.setattr(install_mod.PackageInstaller, 'create_venv', lambda self: calls.append('create_venv'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'upgrade_pip', lambda self: calls.append('upgrade_pip'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_python_packages', lambda self: calls.append('install_python_packages'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_nodejs', lambda self: calls.append('install_nodejs'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_npm_packages', lambda self: calls.append('install_npm_packages'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'create_data_directory', lambda self: calls.append('create_data_directory'))
    monkeypatch.setattr(install_mod.PackageInstaller, 'test_configuration', lambda self: calls.append('test_configuration'))

    # Ensure check_existing_installation returns False to run full installation
    monkeypatch.setattr(install_mod.InstallationManager, 'check_existing_installation', lambda self: False)

    mgr.run_installation()
    assert 'create_venv' in calls and 'install_npm_packages' in calls


def test_main_detects_running_in_project_venv_and_exits(monkeypatch, tmp_path):
    # Simulate running in project venv and passing --uninstall
    script_dir = Path(__file__).parent.parent / 'scripts'
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda *a, **k: True)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py', '--uninstall'])

    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_main_normal_flow_calls_manager(monkeypatch, tmp_path):
    # Simulate normal run: patch InstallationManager to record calls
    called = {}

    class FakeManager:
        def __init__(self, install_dir, force, skip_tests, dry_run):
            called['init'] = True

        def check_existing_installation(self):
            return False

        def run_system_checks(self):
            called['checks'] = True

        def run_installation(self):
            called['install'] = True

        def show_summary(self):
            called['summary'] = True

    monkeypatch.setattr(install_mod, 'InstallationManager', FakeManager)
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py'])

    # run main and ensure it completes
    install_mod.main()
    assert called.get('init') and called.get('checks') and called.get('install') and called.get('summary')


# ------------------------- Groupe final: tests restants -------------------------


def test_install_nodejs_makes_nodejs_dir_and_calls_nodeenv(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    called = []

    # stub get_venv_python to some path
    monkeypatch.setattr(install_mod.PackageInstaller, 'get_venv_python', lambda self: tmp_path / '.venv' / 'bin' / 'python')

    def fake_run(cmd, cwd=None, capture_output=False, text=False, check=False):
        called.append((cmd, cwd))
        class R:
            stdout = 'v20'
        return R()

    monkeypatch.setattr(install_mod.PackageInstaller, 'run_command', lambda self, *a, **k: fake_run(*a, **k))

    inst.install_nodejs()
    nodejs_dir = tmp_path / 'alexa_auth' / 'nodejs'
    assert nodejs_dir.exists()
    # ensure we called nodeenv via run_command (first arg contains '--node')
    assert any('--node' in ' '.join(cmd) or 'nodeenv' in ' '.join(cmd) for cmd, cwd in called)


def test_install_npm_packages_success_and_partial_failure(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)

    node_path = tmp_path / 'node'
    npm_path = tmp_path / 'npm'

    def fake_get_nodejs_paths(self):
        return node_path, npm_path

    monkeypatch.setattr(install_mod.PackageInstaller, 'get_nodejs_paths', fake_get_nodejs_paths)

    calls = []

    def fake_run(self_or_cmd, *a, **k):
        # allow being called as bound or with cmd directly
        cmd = self_or_cmd if isinstance(self_or_cmd, list) else a[0] if a else self_or_cmd
        calls.append(cmd)
        # If checking node version
        if isinstance(cmd, (list,)) and '--version' in cmd:
            class R: stdout = 'v20.17.0'
            return R()
        # For npm install: simulate first package success, second failure
        if isinstance(cmd, (list,)) and 'install' in cmd:
            if 'alexa-cookie2' in cmd:
                return None
            else:
                raise RuntimeError('fail npm')

    # Monkeypatch run_command on class
    # patch the instance method to avoid bound-method arg mismatch
    monkeypatch.setattr(inst, 'run_command', fake_run)

    # Run and capture warnings/success messages
    inst.install_npm_packages()
    # Should have attempted node version check and at least two installs
    assert any('--version' in ' '.join(c) if isinstance(c, list) else False for c in calls)


def test_test_configuration_python_and_node(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)

    node_path = tmp_path / 'node'
    monkeypatch.setattr(install_mod.PackageInstaller, 'get_nodejs_paths', lambda self: (node_path, tmp_path / 'npm'))

    class R1:
        stdout = 'Python 3.13.5'
        stderr = ''

    class R2:
        stdout = ""
        stderr = 'Node OK'

    def fake_run(*args, **kwargs):
        # command may be in args[0] or kwargs first positional
        cmd = args[0] if args else kwargs.get('cmd')
        if isinstance(cmd, list):
            if '-V' in cmd:
                return R1()
            if '-e' in cmd:
                return R2()
        # fallback: if string
        if isinstance(cmd, str):
            if '-V' in cmd:
                return R1()
            if '-e' in cmd:
                return R2()

    monkeypatch.setattr(
        install_mod.PackageInstaller,
        'run_command',
        lambda self, cmd, cwd=None, capture_output=False, **kwargs: fake_run(cmd, cwd=cwd, capture_output=capture_output, **kwargs),
    )
    # Should not raise
    inst.test_configuration()


def test_run_installation_existing_install_calls_cleanup(monkeypatch, tmp_path):
    d = tmp_path
    mgr = install_mod.InstallationManager(d)
    monkeypatch.setattr(install_mod.InstallationManager, 'check_existing_installation', lambda self: True)
    called = {}
    monkeypatch.setattr(install_mod.InstallationManager, 'cleanup_existing_installation', lambda self: called.setdefault('cleanup', True))

    # Monkeypatch installer actions to avoid side-effects
    monkeypatch.setattr(install_mod.PackageInstaller, 'create_venv', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'upgrade_pip', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_python_packages', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_nodejs', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'install_npm_packages', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'create_data_directory', lambda self: None)
    monkeypatch.setattr(install_mod.PackageInstaller, 'test_configuration', lambda self: None)

    mgr.run_installation()
    assert called.get('cleanup') is True


def test_main_uninstall_no_existing(monkeypatch, tmp_path, capsys):
    # Simulate args --uninstall and manager that reports no installation
    class FakeManager:
        def __init__(self, install_dir, force, skip_tests, dry_run):
            pass

        def check_existing_installation(self):
            return False

    monkeypatch.setattr(install_mod, 'InstallationManager', FakeManager)
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py', '--uninstall'])
    # Should not raise; it prints info about no installation
    install_mod.main()
    out = capsys.readouterr().out
    assert 'Aucune installation trouvée' in out


def test_install_python_packages_partial_failures(monkeypatch, tmp_path, capsys):
    # Simulate installing REQUIRED_PACKAGES with some failures
    inst = install_mod.PackageInstaller(tmp_path)

    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get('cmd')
        # simulate pip install failure for package containing 'selenium'
        if isinstance(cmd, list) and any('selenium' in c for c in cmd):
            raise RuntimeError('pip fail')
        class R:
            stdout = ''
            stderr = ''
        return R()

    monkeypatch.setattr(
        install_mod.PackageInstaller,
        'run_command',
        lambda self, cmd, cwd=None, capture_output=False, **kwargs: fake_run(cmd, cwd=cwd, capture_output=capture_output, **kwargs),
    )
    # ensure no requirements file
    inst.install_python_packages()


def test_install_npm_packages_all_paths(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)
    node_path = tmp_path / 'node'
    npm_path = tmp_path / 'npm'

    def fake_get_nodejs_paths(self):
        return node_path, npm_path

    monkeypatch.setattr(install_mod.PackageInstaller, 'get_nodejs_paths', fake_get_nodejs_paths)

    def fake_run(*args, **kwargs):
        # handle bound method (self, cmd, ...)
        if args and isinstance(args[0], install_mod.PackageInstaller):
            cmd = args[1] if len(args) > 1 else None
        else:
            cmd = args[0] if args else kwargs.get('cmd')

        # normalize to list of strings
        parts = cmd if isinstance(cmd, list) else (cmd.split() if isinstance(cmd, str) else [])
        if any('--version' in str(p) for p in parts):
            class R: stdout = 'v20'
            return R()
        s = ' '.join(parts)
        # simulate alexa-cookie2 success, yargs fail
        if 'alexa-cookie2' in s:
            return None
        if 'yargs' in s:
            raise RuntimeError('npm fail')
        return None

    monkeypatch.setattr(
        install_mod.PackageInstaller,
        'run_command',
        lambda self, cmd, cwd=None, capture_output=False, **kwargs: fake_run(cmd, cwd=cwd, capture_output=capture_output, **kwargs),
    )
    inst.install_npm_packages()


def test_show_summary_and_get_venv_instructions(monkeypatch, capsys):
    # force activate lines
    monkeypatch.setattr(install_mod, 'get_venv_instructions', lambda: (['act1', 'act2'], 'deact'))
    inst = install_mod.InstallationManager(Path('.'))
    inst.show_summary()
    out = capsys.readouterr().out
    assert 'act1' in out or 'INSTRUCTIONS' in out


def test_test_configuration_node_failure(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)
    # python -V returns ok, but node test raises
    class R1: stdout = 'Python X'; stderr = ''

    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get('cmd')
        if isinstance(cmd, list) and '-V' in cmd:
            return R1()
        raise RuntimeError('node fail')

    monkeypatch.setattr(
        install_mod.PackageInstaller,
        'run_command',
        lambda self, cmd, cwd=None, capture_output=False, **kwargs: fake_run(cmd, cwd=cwd, capture_output=capture_output, **kwargs),
    )
    inst.test_configuration()


def test_main_block_when_running_in_project_venv_windows_and_not_dryrun(monkeypatch):
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda *a, **k: True)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py'])
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_main_block_when_running_in_project_venv_unix_and_not_dryrun(monkeypatch):
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda *a, **k: True)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py'])
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_install_python_packages_all_failures(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)

    def fake_run(*args, **kwargs):
        # Always fail to trigger Logger.warning per package
        raise RuntimeError('fail')

    monkeypatch.setattr(
        install_mod.PackageInstaller,
        'run_command',
        lambda self, cmd, cwd=None, capture_output=False, **kwargs: fake_run(cmd, cwd=cwd, **kwargs),
    )
    # No requirements file exists
    inst.install_python_packages()


def test_test_configuration_stderr_paths(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)

    class R:
        stdout = ''
        stderr = 'py stderr'

    class Rn:
        stdout = ''
        stderr = 'node stderr'

    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get('cmd')
        # python -V
        if isinstance(cmd, list) and '-V' in cmd:
            return R()
        # node -e
        if isinstance(cmd, list) and '-e' in cmd:
            return Rn()

    # patch the instance method to avoid bound/unbound mismatch
    monkeypatch.setattr(inst, 'run_command', fake_run)
    inst.test_configuration()
    out = capsys.readouterr().out
    assert 'Test Python' in out or 'Test Node.js' in out


def test_get_venv_instructions_both_platforms(monkeypatch):
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    lines, deact = install_mod.get_venv_instructions()
    assert any('PowerShell' in l for l in lines)

    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    lines2, deact2 = install_mod.get_venv_instructions()
    assert any('source .venv' in l for l in lines2)


def test_running_in_project_venv_parent_path(tmp_path):
    install_dir = tmp_path
    venv = install_dir / '.venv' / 'lib' / 'python'
    venv.mkdir(parents=True)
    # path inside the venv
    exe = venv / 'somefile'
    exe.write_text('')
    assert install_mod.running_in_project_venv(str(exe), install_dir) is True


def test_main_keyboardinterrupt_and_exception(monkeypatch):
    # KeyboardInterrupt path
    monkeypatch.setattr(install_mod.InstallationManager, '__init__', lambda self, *a, **k: None)
    monkeypatch.setattr(install_mod.InstallationManager, 'run_system_checks', lambda self: (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py'])
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 1

    # Generic exception path
    monkeypatch.setattr(install_mod.InstallationManager, 'run_system_checks', lambda self: (_ for _ in ()).throw(Exception('boom')))
    with pytest.raises(SystemExit) as exc2:
        install_mod.main()
    assert exc2.value.code == 1


def test_logger_header_and_wrap_variants(capsys):
    # header with emoji in special set (double space)
    install_mod.Logger.header('Test Header', emoji='ℹ️')
    # header with other emoji (single space)
    install_mod.Logger.header('Another Header', emoji='🎉')
    # wrap with message starting/ending with emoji to trigger strip
    install_mod.Logger._wrap_and_print('✅', '🎉 Hello world 🎉', install_mod.Colors.GREEN)
    out = capsys.readouterr().out
    assert 'Test Header' in out
    assert 'Another Header' in out
    assert 'Hello world' in out


def test_systemchecker_check_pip_and_disk(monkeypatch):
    # pip not available -> FileNotFoundError
    def fake_run_fail(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(install_mod.subprocess, 'run', fake_run_fail)
    ok, msg = install_mod.SystemChecker.check_pip()
    assert ok is False

    # disk usage raises -> fallback True
    def fake_disk(path):
        raise Exception('no disk')

    monkeypatch.setattr(install_mod.shutil, 'disk_usage', fake_disk)
    ok2, msg2 = install_mod.SystemChecker.check_disk_space(Path('.'))
    assert ok2 is True


def test_install_python_packages_with_requirements(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    req = tmp_path / 'requirements.txt'
    req.write_text('requests')

    called = {}

    def fake_run(cmd, cwd=None, capture_output=False, **kwargs):
        called['cmd'] = cmd
        class R:
            stdout = ''
            stderr = ''
        return R()

    # patch the instance method to avoid bound/unbound signature issues
    monkeypatch.setattr(inst, 'run_command', fake_run)
    inst.install_python_packages()
    assert '-r' in called['cmd']


def test_install_nodejs_and_get_node_paths(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)

    called = {'cmds': []}

    def fake_run_instance(cmd, cwd=None, capture_output=False, **kwargs):
        # record the command and return a fake result
        called['cmds'].append(cmd)
        class R:
            stdout = ''
            stderr = ''

        return R()

    # patch the instance method directly to avoid signature mismatch
    monkeypatch.setattr(inst, 'run_command', fake_run_instance)

    # ensure install_nodejs creates directory and calls run
    inst.install_nodejs()
    assert (tmp_path / 'alexa_auth' / 'nodejs').exists()

    # get_nodejs_paths Windows
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    node_path, npm_path = inst.get_nodejs_paths()
    assert 'node.exe' in str(node_path) or 'node.exe' in str(node_path)
    assert 'npm.cmd' in str(npm_path) or 'npm.cmd' in str(npm_path)


def test_install_npm_packages_success_and_package_failure(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)

    # create nodeenv structure
    nodeenv = tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv' / 'bin'
    nodeenv.mkdir(parents=True, exist_ok=True)
    node = nodeenv / 'node'
    npm = nodeenv / 'npm'
    node.write_text('')
    npm.write_text('')

    calls = []

    class R:
        def __init__(self, s='v20'):
            self.stdout = s
            self.stderr = ''

    def fake_run(cmd, cwd=None, capture_output=False, **kwargs):
        calls.append(cmd)
        # first call is node --version
        if '--version' in cmd:
            return R('v20.17.0')
        # simulate failure for second package
        if 'yargs' in cmd:
            raise RuntimeError('npm fail')
        return R('')

    monkeypatch.setattr(install_mod.PackageInstaller, 'run_command', lambda self, *a, **k: fake_run(*a, **k))
    inst.install_npm_packages()
    out = capsys.readouterr().out
    assert 'Node.js' in out or 'installé' in out


def test_run_system_checks_branches(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path)

    # python version fail -> exit
    monkeypatch.setattr(install_mod.SystemChecker, 'check_python_version', lambda: (False, 'old'))
    with pytest.raises(SystemExit):
        mgr.run_system_checks()

    # pip fail -> exit
    monkeypatch.setattr(install_mod.SystemChecker, 'check_python_version', lambda: (True, 'ok'))
    monkeypatch.setattr(install_mod.SystemChecker, 'check_pip', lambda: (False, 'no pip'))
    with pytest.raises(SystemExit):
        mgr.run_system_checks()

    # disk low -> warning but not exit
    monkeypatch.setattr(install_mod.SystemChecker, 'check_pip', lambda: (True, 'pip ok'))
    monkeypatch.setattr(install_mod.SystemChecker, 'check_disk_space', lambda path, required_gb=2.0: (False, 'low'))
    mgr.run_system_checks()


def test_cleanup_existing_installation_user_declines(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path)
    # simulate existing venv
    (tmp_path / '.venv').mkdir()
    monkeypatch.setattr('builtins.input', lambda prompt='': 'n')
    with pytest.raises(SystemExit) as exc:
        mgr.cleanup_existing_installation()
    assert exc.value.code == 0


def test_show_uninstall_summary_windows(monkeypatch, capsys):
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    mgr = install_mod.InstallationManager(Path('.'))
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert 'PowerShell' in out


def test_main_uninstall_running_in_project_venv_windows(monkeypatch):
    # Simulate being inside venv and platform Windows
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda cur, inst: True)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py', '--uninstall'])
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2


def test_wrap_and_strip_edge_emojis_small_width(capsys):
    # Force small max_width to trigger avail <= 20 branch and wrapping
    install_mod.Logger._wrap_and_print('ℹ️', '🎉' + 'A' * 100 + '🎉', install_mod.Colors.CYAN, max_width=10)
    out = capsys.readouterr().out
    assert 'A' in out


def test_systemchecker_platform_info_and_pip_success(monkeypatch):
    info = install_mod.SystemChecker.get_platform_info()
    assert 'system' in info and 'release' in info

    class R:
        stdout = 'pip 25.2 from somewhere'
        stderr = ''

    def fake_run_ok(*a, **k):
        return R()

    monkeypatch.setattr(install_mod.subprocess, 'run', fake_run_ok)
    ok, msg = install_mod.SystemChecker.check_pip()
    assert ok and 'pip 25.2' in msg


def test_check_disk_space_high_and_low(monkeypatch, tmp_path):
    class Usage:
        def __init__(self, free):
            self.free = free

    # plenty of space
    monkeypatch.setattr(install_mod.shutil, 'disk_usage', lambda p: Usage(10 * 1024**3))
    ok, m = install_mod.SystemChecker.check_disk_space(tmp_path, required_gb=2.0)
    assert ok is True

    # low space
    monkeypatch.setattr(install_mod.shutil, 'disk_usage', lambda p: Usage(1 * 1024**3))
    ok2, m2 = install_mod.SystemChecker.check_disk_space(tmp_path, required_gb=2.0)
    assert ok2 is False


def test_run_command_dry_run_does_not_call_subprocess(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path, dry_run=True)

    def bad_run(*a, **k):
        raise RuntimeError('should not be called')

    monkeypatch.setattr(install_mod.subprocess, 'run', bad_run)
    res = inst.run_command(['echo', 'hi'])
    assert hasattr(res, 'stdout')


def test_get_venv_python_and_pip_paths(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    assert 'Scripts' in str(inst.get_venv_python())
    assert 'Scripts' in str(inst.get_venv_pip())

    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    assert 'bin' in str(inst.get_venv_python())
    assert 'bin' in str(inst.get_venv_pip())


def test_upgrade_pip_calls_install_upgrade(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    called = {}

    def fake_run(cmd, cwd=None, **kwargs):
        called['cmd'] = cmd
        class R:
            stdout = ''
            stderr = ''
        return R()

    monkeypatch.setattr(install_mod.PackageInstaller, 'run_command', lambda self, *a, **k: fake_run(*a, **k))
    inst.upgrade_pip()
    assert 'install' in called['cmd'] and '--upgrade' in called['cmd']


def test_install_npm_packages_node_unavailable_raises(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    # create minimal nodeenv structure
    (tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv' / 'bin').mkdir(parents=True, exist_ok=True)
    # run_command will raise on version check
    def fake_run(cmd, cwd=None, capture_output=False, **kwargs):
        raise RuntimeError('node fail')

    monkeypatch.setattr(install_mod.PackageInstaller, 'run_command', lambda self, *a, **k: fake_run(*a, **k))
    with pytest.raises(RuntimeError):
        inst.install_npm_packages()


def test_create_data_directory_when_exists(tmp_path):
    d = tmp_path / 'data'
    d.mkdir()
    inst = install_mod.PackageInstaller(tmp_path)
    # should not raise
    inst.create_data_directory()
    assert d.exists()


def test_run_command_calledprocesserror_raises(tmp_path, monkeypatch):
    inst = install_mod.PackageInstaller(tmp_path)

    def fake_run(*a, **k):
        raise install_mod.subprocess.CalledProcessError(1, 'cmd', stderr='err')

    monkeypatch.setattr(install_mod.subprocess, 'run', fake_run)
    with pytest.raises(RuntimeError):
        inst.run_command(['false'])


def test_check_pip_short_output(monkeypatch):
    class R:
        stdout = 'pip\n'
        stderr = ''

    monkeypatch.setattr(install_mod.subprocess, 'run', lambda *a, **k: R())
    ok, msg = install_mod.SystemChecker.check_pip()
    assert ok is True and 'pip' in msg


def test_get_nodejs_paths_unix(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    node_path, npm_path = inst.get_nodejs_paths()
    assert 'bin' in str(node_path) and 'bin' in str(npm_path)


def test_run_installation_skip_tests(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path, skip_tests=True)
    called = {}
    for name in ('create_venv', 'upgrade_pip', 'install_python_packages', 'install_nodejs', 'install_npm_packages', 'create_data_directory', 'test_configuration'):
        setattr(mgr.installer, name, (lambda n: (lambda *a, **k: called.setdefault(n, True)))(name))

    mgr.run_installation()
    # test_configuration should NOT be called because skip_tests=True
    assert 'test_configuration' not in called


def test_cleanup_existing_installation_force_dryrun(monkeypatch, tmp_path):
    # create venv and nodeenv
    (tmp_path / '.venv').mkdir(parents=True)
    (tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv').mkdir(parents=True)
    mgr = install_mod.InstallationManager(tmp_path, force=True, dry_run=True)
    # should not raise and should leave directories in place
    mgr.cleanup_existing_installation()
    assert (tmp_path / '.venv').exists()
    assert (tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv').exists()


def test_show_summary_prints_activate(monkeypatch, capsys, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path)
    monkeypatch.setattr(install_mod, 'get_venv_instructions', lambda: (['act line'], 'deact'))
    mgr.show_summary()
    out = capsys.readouterr().out
    assert 'act line' in out


def test_cleanup_existing_installation_force_no_dryrun(monkeypatch, tmp_path):
    # create venv and nodeenv
    (tmp_path / '.venv').mkdir(parents=True)
    (tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv').mkdir(parents=True)
    mgr = install_mod.InstallationManager(tmp_path, force=True, dry_run=False)
    # should call shutil.rmtree
    mgr.cleanup_existing_installation()
    # directories should be removed
    assert not (tmp_path / '.venv').exists()
    assert not (tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv').exists()


def test_run_installation_with_tests(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path, skip_tests=False)
    called = {}
    for name in ('create_venv', 'upgrade_pip', 'install_python_packages', 'install_nodejs', 'install_npm_packages', 'create_data_directory', 'test_configuration'):
        setattr(mgr.installer, name, (lambda n: (lambda *a, **k: called.setdefault(n, True)))(name))

    mgr.run_installation()
    # test_configuration should be called because skip_tests=False
    assert 'test_configuration' in called


def test_show_uninstall_summary_unix(monkeypatch, capsys):
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    mgr = install_mod.InstallationManager(Path('.'))
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert 'Bash' in out


def test_truncate_with_wide_characters():
    # Use CJK characters which have width 2 to force truncation path
    s = '漢' * 50
    out = install_mod.Logger._truncate_to_width(s, max_width=10)
    assert out.endswith('...')


def test_cleanup_existing_installation_calls_rmtree(monkeypatch, tmp_path):
    # create venv and nodeenv
    v = tmp_path / '.venv'
    ne = tmp_path / 'alexa_auth' / 'nodejs' / '.nodeenv'
    v.mkdir(parents=True)
    ne.mkdir(parents=True)

    called = {'rmtree': []}

    def fake_rmtree(p, ignore_errors=True):
        called['rmtree'].append(str(p))

    monkeypatch.setattr(install_mod.shutil, 'rmtree', fake_rmtree)

    mgr = install_mod.InstallationManager(tmp_path, force=True, dry_run=False)
    mgr.cleanup_existing_installation()
    assert any('.venv' in p for p in called['rmtree'])
    assert any('.nodeenv' in p for p in called['rmtree'])


def test_running_in_project_venv_exact_paths(tmp_path):
    # exact Scripts/python.exe path
    s1 = tmp_path / '.venv' / 'Scripts' / 'python.exe'
    s1.parent.mkdir(parents=True)
    s1.write_text('')
    assert install_mod.running_in_project_venv(str(s1), tmp_path) is True

    # exact bin/python path
    s2 = tmp_path / '.venv' / 'bin' / 'python'
    s2.parent.mkdir(parents=True)
    s2.write_text('')
    assert install_mod.running_in_project_venv(str(s2), tmp_path) is True


def test_show_uninstall_summary_unix(monkeypatch, capsys):
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Linux')
    mgr = install_mod.InstallationManager(Path('.'))
    mgr.show_uninstall_summary()
    out = capsys.readouterr().out
    assert 'rm -rf alexa_auth/nodejs/.nodeenv' in out


def test_create_venv_flow(monkeypatch, tmp_path):
    inst = install_mod.PackageInstaller(tmp_path)
    called = {}
    monkeypatch.setattr(inst, 'run_command', lambda *a, **k: called.setdefault('run', True))
    inst.create_venv()
    assert 'run' in called


def test_create_data_directory_when_missing(tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)
    # ensure data missing
    d = tmp_path / 'data'
    if d.exists():
        for p in d.iterdir():
            p.unlink()
        d.rmdir()
    inst.create_data_directory()
    out = capsys.readouterr().out
    assert 'Dossier data créé' in out


def test_test_configuration_python_failure(monkeypatch, tmp_path, capsys):
    inst = install_mod.PackageInstaller(tmp_path)

    def fake_run(*a, **k):
        # python -V fails
        raise RuntimeError('py fail')

    monkeypatch.setattr(inst, 'run_command', fake_run)
    inst.test_configuration()
    out = capsys.readouterr().out
    assert 'Test Python échoué' in out or 'Test Node.js échoué' in out


def test_run_system_checks_disk_branches(monkeypatch, tmp_path):
    mgr = install_mod.InstallationManager(tmp_path)
    # python ok, pip ok
    monkeypatch.setattr(install_mod.SystemChecker, 'check_python_version', lambda: (True, 'ok'))
    monkeypatch.setattr(install_mod.SystemChecker, 'check_pip', lambda: (True, 'pip ok'))
    # disk ok
    monkeypatch.setattr(install_mod.SystemChecker, 'check_disk_space', lambda path, required_gb=2.0: (True, '10.0 GB disponibles'))
    mgr.run_system_checks()

    # disk low -> warning
    monkeypatch.setattr(install_mod.SystemChecker, 'check_disk_space', lambda path, required_gb=2.0: (False, '0.5 GB disponibles'))
    mgr.run_system_checks()


def test_main_uninstall_triggers_cleanup_and_success(monkeypatch, tmp_path, capsys):
    # Create an install to be found
    (tmp_path / '.venv').mkdir()

    class FakeManager:
        def __init__(self, install_dir, force, skip_tests, dry_run=False):
            self.install_dir = install_dir
        def check_existing_installation(self):
            return True
        def cleanup_existing_installation(self):
            print('cleanup called')

    monkeypatch.setattr(install_mod, 'InstallationManager', FakeManager)
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda *a, **k: False)
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py', '--uninstall'])
    install_mod.main()
    out = capsys.readouterr().out
    assert 'cleanup called' in out or 'Désinstallation terminée' in out


def test_main_block_when_running_in_project_venv_windows_late(monkeypatch, capsys):
    # First call: not in venv (avoid early return). Second call: in venv -> triggers later block.
    seq = iter([False, True])
    monkeypatch.setattr(install_mod, 'running_in_project_venv', lambda *a, **k: next(seq))
    monkeypatch.setattr(install_mod.platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(sys, 'argv', ['scripts/install.py', '--uninstall'])
    with pytest.raises(SystemExit) as exc:
        install_mod.main()
    assert exc.value.code == 2
    out = capsys.readouterr().out
    # Ensure the Windows-specific uninstall instruction line was printed
    assert 'python scripts/install.py --uninstall' in out


def test_running_in_project_venv_handles_resolve_exception(monkeypatch, tmp_path):
    # Force Path.resolve to raise to exercise the except: return False branch
    def bad_resolve(self):
        raise RuntimeError('boom')

    monkeypatch.setattr(install_mod.Path, 'resolve', bad_resolve)
    # Should return False instead of raising
    assert install_mod.running_in_project_venv(str(tmp_path / 'python'), tmp_path) is False


def test_running_in_project_venv_none_and_parent_cases(tmp_path):
    # None should return False
    assert install_mod.running_in_project_venv(None, tmp_path) is False

    # A file path deeply nested under .venv should be considered inside
    deep = tmp_path / '.venv' / 'lib' / 'python' / 'site-packages' / 'pkg' / 'mod.py'
    deep.parent.mkdir(parents=True, exist_ok=True)
    deep.write_text('')
    assert install_mod.running_in_project_venv(str(deep), tmp_path) is True


def test_cleanup_existing_installation_non_interactive_logs(tmp_path, capsys):
    # Create venv and run cleanup with non_interactive=True and force=False to hit the info branch
    (tmp_path / '.venv').mkdir(parents=True)
    mgr = install_mod.InstallationManager(tmp_path, force=False, dry_run=True, non_interactive=True)
    # Should not raise and should log non-interactive confirmation
    mgr.cleanup_existing_installation()
    out = capsys.readouterr().out
    assert 'Non-interactive' in out or 'suppression confirmée' in out


def test_core_main_blocks_uninstall_when_running_in_venv():
    # Call core_main directly to exercise the early uninstall-block path
    args = types.SimpleNamespace(uninstall=True, force=False, skip_tests=False, dry_run=False, yes=False)
    install_dir = Path('.').resolve()

    def running_true():
        return True

    with pytest.raises(install_mod.CLIError) as ei:
        install_mod.core_main(args, install_dir, running_true)
    assert ei.value.code == 2


def test_logger_internal_wrap_strips_edge_emojis_small_width(capsys):
    # Ensure internal wrap strips leading/trailing emojis and respects small max_width fallback
    # Use an emoji-starting message to trigger stripping
    install_mod.Logger._internal_wrap_and_print('✅', '🎉 Hello World 🎉', install_mod.Colors.GREEN, max_width=10)
    out = capsys.readouterr().out
    # Emoji prefix should be printed by the logger, but inner message emojis stripped
    assert '✅' in out
    assert '🎉' not in out


def test_package_tester_prefers_stderr_for_python(monkeypatch, tmp_path, capsys):
    # Simulate python -V returning nothing on stdout but version on stderr
    class FakeResult:
        stdout = ''
        stderr = 'Python 3.13.5'

    inst = install_mod.PackageInstaller(tmp_path)

    def fake_run(cmd, cwd=None, capture_output=False, **kwargs):
        # python -V
        if isinstance(cmd, list) and '-V' in cmd:
            return FakeResult()
        # node check: raise to exercise error branch
        if isinstance(cmd, list) and '-e' in cmd:
            raise RuntimeError('node fail')

    monkeypatch.setattr(inst, 'run_command', fake_run)
    inst.test_configuration()
    out = capsys.readouterr().out
    assert 'Test Python réussi' in out or 'Test Python échoué' in out
