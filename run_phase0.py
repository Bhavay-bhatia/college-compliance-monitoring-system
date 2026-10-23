"""
AICTE SETU — Root Runner for Phase 0 Verification
Executes the deterministic Rule Engine against sample college fixtures.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from phase0_runner import run_phase_0_demo

if __name__ == "__main__":
    run_phase_0_demo()
