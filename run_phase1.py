"""
AICTE SETU — Root Runner for Phase 1 Verification
Executes Authentication, RBAC, Application Lifecycle, and Revision Auditing.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from phase1_runner import run_phase_1_demo

if __name__ == "__main__":
    run_phase_1_demo()
