#!/usr/bin/env python3
"""
Test runner script for resume.ai test suite.
Provides convenient commands for running different test suites.
"""
import sys
import subprocess
from typing import List


def run_command(cmd: List[str]) -> int:
    """Run a command and return exit code."""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    return subprocess.call(cmd)


def run_all_tests():
    """Run all tests with coverage."""
    return run_command([
        "pytest",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ])


def run_unit_tests():
    """Run only unit tests (fast)."""
    return run_command(["pytest", "-m", "unit", "-v"])


def run_integration_tests():
    """Run only integration tests."""
    return run_command(["pytest", "-m", "integration", "-v"])


def run_agent_tests():
    """Run only agent tests."""
    return run_command(["pytest", "-m", "agents", "-v"])


def run_api_tests():
    """Run only API tests."""
    return run_command(["pytest", "-m", "api", "-v"])


def run_fast_tests():
    """Run all tests except slow ones."""
    return run_command(["pytest", "-m", "not slow", "-v"])


def run_parallel_tests():
    """Run tests in parallel for speed."""
    return run_command(["pytest", "-n", "auto", "-v"])


def run_specific_file(filepath: str):
    """Run tests in a specific file."""
    return run_command(["pytest", filepath, "-v"])


def show_coverage():
    """Show coverage report."""
    return run_command(["pytest", "--cov=.", "--cov-report=term-missing"])


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Resume.AI Test Runner")
        print("\nUsage: python run_tests.py <command> [args]")
        print("\nCommands:")
        print("  all              - Run all tests with coverage")
        print("  unit             - Run only unit tests")
        print("  integration      - Run only integration tests")
        print("  agents           - Run only agent tests")
        print("  api              - Run only API tests")
        print("  fast             - Run all tests except slow ones")
        print("  parallel         - Run tests in parallel")
        print("  coverage         - Show coverage report")
        print("  file <path>      - Run tests in specific file")
        print("\nExamples:")
        print("  python run_tests.py all")
        print("  python run_tests.py unit")
        print("  python run_tests.py file tests/agents/test_parser_agent.py")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "all":
        return run_all_tests()
    elif command == "unit":
        return run_unit_tests()
    elif command == "integration":
        return run_integration_tests()
    elif command == "agents":
        return run_agent_tests()
    elif command == "api":
        return run_api_tests()
    elif command == "fast":
        return run_fast_tests()
    elif command == "parallel":
        return run_parallel_tests()
    elif command == "coverage":
        return show_coverage()
    elif command == "file":
        if len(sys.argv) < 3:
            print("Error: Please specify file path")
            return 1
        return run_specific_file(sys.argv[2])
    else:
        print(f"Error: Unknown command '{command}'")
        return 1


if __name__ == "__main__":
    sys.exit(main())

