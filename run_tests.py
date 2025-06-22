#!/usr/bin/env python3
"""
Test runner script for YouTube Downloader API.

This script runs the test suite with various options and provides
a convenient way to run specific test categories.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and return the exit code."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"{'='*60}")
    
    print(f"Command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=False)
    return result.returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for YouTube Downloader API")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--services", action="store_true", help="Run only service tests")
    parser.add_argument("--models", action="store_true", help="Run only model tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--parallel", "-n", type=int, default=1, help="Run tests in parallel")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add parallel execution if requested
    if args.parallel > 1:
        cmd.extend(["-n", str(args.parallel)])
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=src/youtube_downloader/api",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Select specific test categories
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.api:
        cmd.append("tests/api/")
    elif args.services:
        cmd.append("tests/services/")
    elif args.models:
        cmd.append("tests/models/")
    else:
        # Run all tests
        cmd.append("tests/")
    
    # Run the tests
    exit_code = run_command(cmd, "Running test suite")
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(exit_code)


if __name__ == "__main__":
    main() 