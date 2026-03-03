"""
Test runner script with coverage.

Usage:
    python scripts/run_tests.py             # Run all tests
    python scripts/run_tests.py --watch     # Watch mode
    python scripts/run_tests.py --cov       # With coverage
    python scripts/run_tests.py tests/test_auth.py  # Specific file
"""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument("target", nargs="?", default="tests/", help="Test file or directory")
    parser.add_argument("--watch", action="store_true", help="Watch mode (requires pytest-watch)")
    parser.add_argument("--cov", action="store_true", help="Run with coverage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--failfast", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Build command
    cmd = ["pytest", args.target]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.failfast:
        cmd.append("-x")
    
    if args.watch:
        cmd.append("--watch")
    
    if args.cov:
        # Check if pytest-cov is installed
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=70,
        ])
    
    # Add asyncio mode
    cmd.append("--asyncio-mode=auto")
    
    print(f"🧪 Running tests: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
