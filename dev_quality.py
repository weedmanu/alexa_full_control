#!/usr/bin/env python3
"""
Complete Development Quality Tools - Test Runner and Code Quality Checker

Comprehensive testing suite with all available quality checks:
- mypy: Static type checking (strict mode)
- ruff: Fast Python linter
- black: Code formatter
- isort: Import sorting
- flake8: Style guide enforcement
- pytest: Unit tests with coverage
- bandit: Security vulnerability scanner
- safety: Dependency vulnerability checker
- vulture: Dead code detection

Usage:
    python dev_quality.py --all              # Run all checks
    python dev_quality.py --mypy             # Run mypy type checking
    python dev_quality.py --all --fix        # Auto-fix issues
    python dev_quality.py --pytest --coverage  # Tests with coverage report
    python dev_quality.py --bandit --safety  # Security checks
    python dev_quality.py --help             # Show this help

Examples:
    python dev_quality.py --all                    # All checks
    python dev_quality.py --mypy core/device_manager.py  # Check specific file
    python dev_quality.py --ruff core/timers --fix       # Fix issues in directory
    python dev_quality.py --pytest Dev/pytests -k TestDevice  # Run specific tests
    python dev_quality.py --all --verbose --fix          # Full quality assurance
"""

import argparse
import io
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Force UTF-8 output for cross-platform compatibility
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


class QualityTools:
    """Wrapper for all quality checking tools."""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent
        self.failed = False
        self.results: Dict[str, bool] = {}
        # Use simple indicators for compatibility
        self.ok = "[OK]"
        self.err = "[FAIL]"
        self.run = "[RUN]"
        self.info = "[INFO]"
        # Use the current Python interpreter (ensures venv usage)
        self.python_exe = sys.executable

    def print_banner(self, title: str) -> None:
        """Print a beautiful banner."""
        width = 80
        print(f"\n{chr(9608) * width}")
        print(f"  {title}")
        print(f"{chr(9608) * width}\n")

    def print_check_header(self, check_name: str) -> None:
        """Print header for a check."""
        print(f"\n{'=' * 80}")
        print(f"[{check_name}]".rjust(80))
        print(f"{'=' * 80}\n")

    def print_check_result(self, check_name: str, passed: bool) -> None:
        """Print result for a single check."""
        status = self.ok if passed else self.err
        result_text = "PASSED" if passed else "FAILED"
        print(f"\n{status} {check_name}: {result_text}\n")

    def run_command(self, cmd: List[str]) -> bool:
        """Run a command and return success status."""
        try:
            print(f"{self.run} Running: {' '.join(cmd)}\n")

            result = subprocess.run(cmd, cwd=self.project_root)

            if result.returncode == 0:
                return True
            else:
                print(f"\n{self.err} Command failed with exit code {result.returncode}")
                self.failed = True
                return False
        except FileNotFoundError:
            print(f"\n{self.err} Error: {cmd[0]} not found. Make sure it's installed.")
            self.failed = True
            return False
        except Exception as e:
            print(f"\n{self.err} Error: {e}")
            self.failed = True
            return False

    def run_mypy(self, path: Optional[str] = None) -> bool:
        """Run mypy static type checking."""
        self.print_check_header("MYPY - Static Type Checking")

        target = path or "core"
        cmd = [self.python_exe, "-m", "mypy", target, "--strict"]
        passed = self.run_command(cmd)
        self.results["mypy"] = passed
        self.print_check_result("mypy", passed)
        return passed

    def run_ruff(self, path: Optional[str] = None, fix: bool = False) -> bool:
        """Run ruff linter."""
        mode = "AUTO-FIX" if fix else "CHECK"
        self.print_check_header(f"RUFF - Linting ({mode})")

        target = path or "core"
        cmd = [self.python_exe, "-m", "ruff", "check"]
        if fix:
            cmd.append("--fix")
        cmd.extend([target, "--select", "E,W,F"])
        passed = self.run_command(cmd)
        self.results["ruff"] = passed
        self.print_check_result("ruff", passed)
        return passed

    def run_black(self, path: Optional[str] = None, fix: bool = False) -> bool:
        """Run black code formatter."""
        mode = "AUTO-FIX" if fix else "CHECK"
        self.print_check_header(f"BLACK - Code Formatting ({mode})")

        target = path or "core"
        cmd = [self.python_exe, "-m", "black", target]
        if not fix:
            cmd.append("--check")
        passed = self.run_command(cmd)
        self.results["black"] = passed
        self.print_check_result("black", passed)
        return passed

    def run_isort(self, path: Optional[str] = None, fix: bool = False) -> bool:
        """Run isort import sorting."""
        mode = "AUTO-FIX" if fix else "CHECK"
        self.print_check_header(f"ISORT - Import Sorting ({mode})")

        target = path or "core"
        cmd = [self.python_exe, "-m", "isort", target]
        if not fix:
            cmd.append("--check-only")
        passed = self.run_command(cmd)
        self.results["isort"] = passed
        self.print_check_result("isort", passed)
        return passed

    def run_flake8(self, path: Optional[str] = None) -> bool:
        """Run flake8 style guide enforcement."""
        self.print_check_header("FLAKE8 - Style Guide Enforcement")

        target = path or "core"
        cmd = [self.python_exe, "-m", "flake8", target, "--max-line-length=120"]
        passed = self.run_command(cmd)
        self.results["flake8"] = passed
        self.print_check_result("flake8", passed)
        return passed

    def run_pytest(
        self,
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        verbose: bool = False,
    ) -> bool:
        """Run pytest unit tests."""
        self.print_check_header("PYTEST - Unit Tests")

        os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        target = path or "Dev/pytests"
        cmd = [self.python_exe, "-m", "pytest", target]

        if pattern:
            cmd.extend(["-k", pattern])

        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")

        cmd.append("--tb=short")
        passed = self.run_command(cmd)
        self.results["pytest"] = passed
        self.print_check_result("pytest", passed)

        if "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in os.environ:
            del os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"]

        return passed

    def run_coverage(
        self,
        path: Optional[str] = None,
        verbose: bool = False,
    ) -> bool:
        """Run pytest with coverage report."""
        self.print_check_header("COVERAGE - Code Coverage Report")

        os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

        target = path or "Dev/pytests"
        cmd = [
            self.python_exe,
            "-m",
            "pytest",
            target,
            "--cov=core",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--tb=short",
        ]

        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")

        passed = self.run_command(cmd)
        self.results["coverage"] = passed

        if passed:
            print(f"\n{self.info} Coverage report generated in htmlcov/index.html")

        self.print_check_result("coverage", passed)

        if "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in os.environ:
            del os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"]

        return passed

    def run_bandit(self, path: Optional[str] = None) -> bool:
        """Run bandit security vulnerability scanner."""
        self.print_check_header("BANDIT - Security Vulnerability Scanner")

        target = path or "core"
    cmd = [self.python_exe, "-m", "bandit", "-r", target, "-f", "json"]
        passed = self.run_command(cmd)
        self.results["bandit"] = passed
        self.print_check_result("bandit", passed)
        return passed

    def run_safety(self) -> bool:
        """Run safety dependency vulnerability checker."""
        self.print_check_header("SAFETY - Dependency Security Checker")

    cmd = [self.python_exe, "-m", "safety", "check", "--json"]
        passed = self.run_command(cmd)
        self.results["safety"] = passed
        self.print_check_result("safety", passed)
        return passed

    def run_pedostyle(self, path: Optional[str] = None, fix: bool = False) -> bool:
        """Run pedostyle code quality checker."""
        mode = "AUTO-FIX" if fix else "CHECK"
        self.print_check_header(f"PEDOSTYLE - Code Quality ({mode})")

        target = path or "core"
    cmd = [self.python_exe, "-m", "pedostyle"]
        if fix:
            cmd.append("--fix")
        cmd.append(target)
        passed = self.run_command(cmd)
        self.results["pedostyle"] = passed
        self.print_check_result("pedostyle", passed)
        return passed

    def run_all(
        self,
        path: Optional[str] = None,
        pattern: Optional[str] = None,
        fix: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Run all quality checks."""
        self.print_banner("QUALITY ASSURANCE - RUNNING ALL CHECKS")

        all_passed = True

        # Run all type and code quality checks
        if not self.run_mypy(path):
            all_passed = False

        if not self.run_ruff(path, fix):
            all_passed = False

        if not self.run_black(path, fix):
            all_passed = False

        if not self.run_isort(path, fix):
            all_passed = False

        if not self.run_flake8(path):
            all_passed = False

        # Run tests with coverage
        if not self.run_coverage(path, verbose):
            all_passed = False

        # Run security checks
        if not self.run_bandit(path):
            all_passed = False

        if not self.run_safety():
            all_passed = False

        # Run dead code detection
        if not self.run_vulture(path):
            all_passed = False

        # Run pedostyle code quality
        if not self.run_pedostyle(path, fix):
            all_passed = False

        return all_passed

    def print_summary(self) -> None:
        """Print final summary."""
        self.print_banner("QUALITY ASSURANCE SUMMARY")

        print(f"{'Check':<20} {'Status':<15} {'Result':<20}")
        print("=" * 55)

        passed_count = 0
        failed_count = 0

        for check_name, passed in sorted(self.results.items()):
            status = self.ok if passed else self.err
            result = "PASSED" if passed else "FAILED"
            print(f"{check_name:<20} {status:<15} {result:<20}")
            if passed:
                passed_count += 1
            else:
                failed_count += 1

        print("=" * 55)
        total = len(self.results)
        print(f"\nTotal Checks: {total} | Passed: {passed_count} | Failed: {failed_count}")

        if failed_count == 0:
            print(f"\n{self.ok} ALL CHECKS PASSED - CODE QUALITY VERIFIED!\n")
        else:
            print(f"\n{self.err} {failed_count} CHECK(S) FAILED - PLEASE REVIEW!\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Complete Development Quality Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dev_quality.py --all                         Run all checks
  python dev_quality.py --mypy --ruff                 Run mypy and ruff
  python dev_quality.py --all --fix                   Auto-fix all issues
  python dev_quality.py --pytest --coverage           Run tests with coverage
  python dev_quality.py --bandit --safety --vulture   Security checks
  python dev_quality.py --mypy -p core/device_manager.py  Check specific file
  python dev_quality.py --pytest -k test_device       Run specific tests
  python dev_quality.py --all --verbose               Verbose output
        """,
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks (mypy, ruff, black, isort, flake8, pytest, coverage, bandit, safety, vulture)",
    )
    parser.add_argument(
        "--mypy",
        action="store_true",
        help="Run mypy static type checking",
    )
    parser.add_argument(
        "--ruff",
        action="store_true",
        help="Run ruff linter",
    )
    parser.add_argument(
        "--black",
        action="store_true",
        help="Run black code formatter",
    )
    parser.add_argument(
        "--isort",
        action="store_true",
        help="Run isort import sorting",
    )
    parser.add_argument(
        "--flake8",
        action="store_true",
        help="Run flake8 style guide enforcement",
    )
    parser.add_argument(
        "--pytest",
        action="store_true",
        help="Run pytest unit tests",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run pytest with coverage report",
    )
    parser.add_argument(
        "--bandit",
        action="store_true",
        help="Run bandit security vulnerability scanner",
    )
    parser.add_argument(
        "--safety",
        action="store_true",
        help="Run safety dependency security checker",
    )
    parser.add_argument(
        "--vulture",
        action="store_true",
        help="Run vulture dead code detection",
    )
    parser.add_argument(
        "--pedostyle",
        action="store_true",
        help="Run pedostyle code quality checker",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=None,
        help="Path to file or directory (default: core)",
    )
    parser.add_argument(
        "-k",
        "--pattern",
        type=str,
        default=None,
        help="Test pattern to match (for pytest)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues (ruff, black, isort)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # If no action specified, show help
    if not any(
        [
            args.all,
            args.mypy,
            args.ruff,
            args.black,
            args.isort,
            args.flake8,
            args.pytest,
            args.coverage,
            args.bandit,
            args.safety,
            args.vulture,
            args.pedostyle,
        ]
    ):
        parser.print_help()
        return 0

    tools = QualityTools()

    try:
        if args.all:
            tools.run_all(
                path=args.path,
                pattern=args.pattern,
                fix=args.fix,
                verbose=args.verbose,
            )
        else:
            if args.mypy:
                tools.run_mypy(args.path)
            if args.ruff:
                tools.run_ruff(args.path, args.fix)
            if args.black:
                tools.run_black(args.path, args.fix)
            if args.isort:
                tools.run_isort(args.path, args.fix)
            if args.flake8:
                tools.run_flake8(args.path)
            if args.pytest:
                tools.run_pytest(args.path, args.pattern, args.verbose)
            if args.coverage:
                tools.run_coverage(args.path, args.verbose)
            if args.bandit:
                tools.run_bandit(args.path)
            if args.safety:
                tools.run_safety()
            if args.vulture:
                tools.run_vulture(args.path)
            if args.pedostyle:
                tools.run_pedostyle(args.path, args.fix)

        tools.print_summary()
        return 1 if tools.failed else 0

    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
