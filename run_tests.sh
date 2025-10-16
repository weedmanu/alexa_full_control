#!/usr/bin/env bash
###############################################################################
#
# Complete Development Quality Testing Suite for Alexa Full Control
#
# Manages virtual environment activation and runs comprehensive quality checks
# including: mypy, ruff, black, isort, flake8, pytest, coverage, bandit, safety, vulture
#
# Usage:
#   ./run_tests.sh --all                    # All checks
#   ./run_tests.sh --mypy --ruff            # Specific checks
#   ./run_tests.sh --pytest --coverage      # Tests with coverage
#   ./run_tests.sh --all --fix --verbose    # Auto-fix with verbose output
#   ./run_tests.sh --no-venv --bandit       # Skip venv, run bandit
#
###############################################################################

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${PROJECT_ROOT}/venv"
PYTHON_EXE="python3"
VENV_ACTIVATED=false

# Flags (default: false)
ALL=false
MYPY=false
RUFF=false
BLACK=false
ISORT=false
FLAKE8=false
PYTEST=false
COVERAGE=false
BANDIT=false
SAFETY=false
VULTURE=false
FIX=false
VERBOSE=false
NO_VENV=false
TARGET_PATH=""
TEST_PATTERN=""

# Track results
PASSED_CHECKS=()
FAILED_CHECKS=()

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Indicators
OK_MARK="[OK]"
FAIL_MARK="[FAIL]"
INFO_MARK="[INFO]"
RUN_MARK="[RUN]"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    local message="$1"
    echo -e "\n${CYAN}$(printf '=%.0s' {1..80})${NC}"
    echo -e "${CYAN}${message}${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
}

print_success() {
    local message="$1"
    echo -e "${GREEN}${OK_MARK} ${message}${NC}"
}

print_error() {
    local message="$1"
    echo -e "${RED}${FAIL_MARK} ${message}${NC}"
}

print_info() {
    local message="$1"
    echo -e "${YELLOW}${INFO_MARK} ${message}${NC}"
}

print_running() {
    local message="$1"
    echo -e "${CYAN}${RUN_MARK} Running: ${message}${NC}"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                ALL=true
                shift
                ;;
            --mypy)
                MYPY=true
                shift
                ;;
            --ruff)
                RUFF=true
                shift
                ;;
            --black)
                BLACK=true
                shift
                ;;
            --isort)
                ISORT=true
                shift
                ;;
            --flake8)
                FLAKE8=true
                shift
                ;;
            --pytest)
                PYTEST=true
                shift
                ;;
            --coverage)
                COVERAGE=true
                shift
                ;;
            --bandit)
                BANDIT=true
                shift
                ;;
            --safety)
                SAFETY=true
                shift
                ;;
            --vulture)
                VULTURE=true
                shift
                ;;
            --fix)
                FIX=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --no-venv)
                NO_VENV=true
                shift
                ;;
            --path|-p)
                TARGET_PATH="$2"
                shift 2
                ;;
            --pattern|-k)
                TEST_PATTERN="$2"
                shift 2
                ;;
            --help|-h)
                print_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                print_help
                exit 1
                ;;
        esac
    done
}

print_help() {
    cat << EOF
${CYAN}Development Quality Testing Suite${NC}

${CYAN}USAGE:${NC}
  $(basename "$0") [OPTIONS]

${CYAN}OPTIONS:${NC}
  --all                 Run all quality checks (default if no option)
  --mypy                Run mypy static type checking
  --ruff                Run ruff linter
  --black               Run black code formatter
  --isort               Run isort import sorting
  --flake8              Run flake8 style guide check
  --pytest              Run pytest unit tests
  --coverage            Run pytest with coverage report
  --bandit              Run bandit security check
  --safety              Run safety dependency check
  --vulture             Run vulture dead code detection

  --fix                 Auto-fix issues (ruff, black, isort)
  -v, --verbose         Verbose output
  --no-venv             Skip virtual environment
  -p, --path PATH       Specific path to check
  -k, --pattern PATTERN Test pattern (pytest -k)
  -h, --help            Show this help message

${CYAN}EXAMPLES:${NC}
  $(basename "$0") --all
  $(basename "$0") --mypy --ruff --pytest
  $(basename "$0") --pytest --coverage
  $(basename "$0") --all --fix --verbose
  $(basename "$0") --bandit --safety
  $(basename "$0") --pytest -k test_device
  $(basename "$0") --mypy -p core/device_manager.py

EOF
}

initialize_venv() {
    if [[ "$NO_VENV" == true ]]; then
        print_info "Skipping venv (--no-venv specified)"
        return
    fi

    print_info "Virtual Environment Setup"

    if [[ ! -d "$VENV_PATH" ]]; then
        print_info "Creating virtual environment at $VENV_PATH"
        python3 -m venv "$VENV_PATH"
    fi

    print_info "Activating virtual environment"
    # shellcheck source=/dev/null
    source "${VENV_PATH}/bin/activate"
    PYTHON_EXE="python"
    VENV_ACTIVATED=true
    print_success "Virtual environment activated"
}

run_check() {
    local check_name="$1"
    local command="$2"

    print_header "$check_name"
    print_running "$command"

    if eval "$command"; then
        print_success "$check_name passed"
        PASSED_CHECKS+=("$check_name")
        return 0
    else
        print_error "$check_name failed (exit code: $?)"
        FAILED_CHECKS+=("$check_name")
        return 1
    fi
}

get_target_path() {
    if [[ -n "$TARGET_PATH" ]]; then
        echo "$TARGET_PATH"
    else
        echo "core"
    fi
}

# ============================================================================
# QUALITY CHECK FUNCTIONS
# ============================================================================

invoke_mypy() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m mypy \"${target_path}\" --strict"
    [[ "$VERBOSE" == true ]] && cmd+=" -v"
    run_check "MYPY - Static Type Checking" "$cmd"
}

invoke_ruff() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m ruff check \"${target_path}\" --select E,W,F"
    [[ "$FIX" == true ]] && cmd+=" --fix"
    local mode=$([ "$FIX" = true ] && echo "[AUTO-FIX]" || echo "[CHECK]")
    run_check "RUFF - Linting $mode" "$cmd"
}

invoke_black() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m black \"${target_path}\""
    [[ "$FIX" != true ]] && cmd+=" --check"
    [[ "$VERBOSE" == true ]] && cmd+=" -v"
    local mode=$([ "$FIX" = true ] && echo "[AUTO-FIX]" || echo "[CHECK]")
    run_check "BLACK - Code Formatting $mode" "$cmd"
}

invoke_isort() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m isort \"${target_path}\""
    [[ "$FIX" != true ]] && cmd+=" --check-only"
    [[ "$VERBOSE" == true ]] && cmd+=" -v"
    local mode=$([ "$FIX" = true ] && echo "[AUTO-FIX]" || echo "[CHECK]")
    run_check "ISORT - Import Sorting $mode" "$cmd"
}

invoke_flake8() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m flake8 \"${target_path}\" --max-line-length=120"
    run_check "FLAKE8 - Style Guide Enforcement" "$cmd"
}

invoke_pytest() {
    local target_path
    target_path="${TARGET_PATH:-Dev/pytests}"
    local cmd="${PYTHON_EXE} -m pytest \"${target_path}\" --tb=short"

    if [[ -n "$TEST_PATTERN" ]]; then
        cmd+=" -k \"${TEST_PATTERN}\""
    fi

    if [[ "$VERBOSE" == true ]]; then
        cmd+=" -v"
    else
        cmd+=" -q"
    fi

    export PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
    run_check "PYTEST - Unit Tests" "$cmd"
    unset PYTEST_DISABLE_PLUGIN_AUTOLOAD
}

invoke_coverage() {
    local target_path
    target_path="${TARGET_PATH:-Dev/pytests}"
    local cmd="${PYTHON_EXE} -m pytest \"${target_path}\" --cov=core --cov-report=html --cov-report=term-missing --tb=short"

    if [[ "$VERBOSE" == true ]]; then
        cmd+=" -v"
    else
        cmd+=" -q"
    fi

    export PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
    run_check "COVERAGE - Code Coverage Report" "$cmd"
    unset PYTEST_DISABLE_PLUGIN_AUTOLOAD

    print_info "Coverage report generated in htmlcov/index.html"
}

invoke_bandit() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m bandit -r \"${target_path}\" -f json"
    run_check "BANDIT - Security Check" "$cmd"
}

invoke_safety() {
    local cmd="${PYTHON_EXE} -m safety check --json"
    run_check "SAFETY - Dependency Security Check" "$cmd"
}

invoke_vulture() {
    local target_path
    target_path=$(get_target_path)
    local cmd="${PYTHON_EXE} -m vulture \"${target_path}\" --min-confidence 80"
    run_check "VULTURE - Dead Code Detection" "$cmd"
}

invoke_all() {
    invoke_mypy
    invoke_ruff
    invoke_black
    invoke_isort
    invoke_flake8
    invoke_coverage
    invoke_bandit
    invoke_safety
    invoke_vulture
}

# ============================================================================
# PRINT SUMMARY
# ============================================================================

print_summary() {
    print_header "SUMMARY"

    if [[ ${#PASSED_CHECKS[@]} -gt 0 ]]; then
        echo -e "\n${GREEN}${OK_MARK} Passed Checks (${#PASSED_CHECKS[@]}):${NC}"
        for check in "${PASSED_CHECKS[@]}"; do
            echo -e "  ${GREEN}-${NC} $check"
        done
    fi

    if [[ ${#FAILED_CHECKS[@]} -gt 0 ]]; then
        echo -e "\n${RED}${FAIL_MARK} Failed Checks (${#FAILED_CHECKS[@]}):${NC}"
        for check in "${FAILED_CHECKS[@]}"; do
            echo -e "  ${RED}-${NC} $check"
        done
    fi

    echo -e "\n${CYAN}$(printf '=%.0s' {1..80})${NC}\n"

    if [[ ${#FAILED_CHECKS[@]} -eq 0 ]]; then
        print_success "ALL CHECKS PASSED!"
        return 0
    else
        print_error "SOME CHECKS FAILED!"
        return 1
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    parse_args "$@"

    # Initialize virtual environment
    initialize_venv

    # If no specific check is selected, run all
    if [[ "$ALL" == false ]] && [[ "$MYPY" == false ]] && [[ "$RUFF" == false ]] && \
       [[ "$BLACK" == false ]] && [[ "$ISORT" == false ]] && [[ "$FLAKE8" == false ]] && \
       [[ "$PYTEST" == false ]] && [[ "$COVERAGE" == false ]] && [[ "$BANDIT" == false ]] && [[ "$SAFETY" == false ]] && \
       [[ "$VULTURE" == false ]]; then
        ALL=true
    fi

    # Run selected checks
    if [[ "$ALL" == true ]]; then
        invoke_all
    else
        [[ "$MYPY" == true ]] && invoke_mypy
        [[ "$RUFF" == true ]] && invoke_ruff
        [[ "$BLACK" == true ]] && invoke_black
        [[ "$ISORT" == true ]] && invoke_isort
        [[ "$PYTEST" == true ]] && invoke_pytest
        [[ "$COVERAGE" == true ]] && invoke_coverage
        [[ "$BANDIT" == true ]] && invoke_bandit
        [[ "$SAFETY" == true ]] && invoke_safety
        [[ "$VULTURE" == true ]] && invoke_vulture
    fi

    # Print summary
    print_summary
    exit $?
}

# Run main function with all arguments
main "$@"
