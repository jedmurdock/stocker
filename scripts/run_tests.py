"""
Simple test runner script.
Run this to execute all tests.
"""
import subprocess
import sys


def run_tests():
    """Run pytest tests"""
    print("=" * 60)
    print("Running Automated Tests")
    print("=" * 60)
    print()
    
    # Run pytest with verbose output
    result = subprocess.run(
        ['pytest', 'tests/', '-v', '--tb=short'],
        capture_output=False
    )
    
    return result.returncode == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

