
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"

RESULTS_DIR.mkdir(exist_ok=True)


def run_command(command, description):
    print(f"\n{'=' * 60}")
    print(description)
    print("=" * 60)

    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )


def main():
    # Step 1: Run unit tests.
    run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "-v",
            "--junitxml=results/pytest-results.xml",
        ],
        "STEP 1: RUNNING PYTEST",
    )

    # Step 2: Run the Ragas baseline.
    run_command(
        [
            sys.executable,
            "ragas_evaluation.py",
        ],
        "STEP 2: RUNNING RAGAS EVALUATION",
    )

    print("\n" + "=" * 60)
    print("ALL TASKS COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print("\nResults saved in:")
    print(RESULTS_DIR)


if __name__ == "__main__":
    main()
