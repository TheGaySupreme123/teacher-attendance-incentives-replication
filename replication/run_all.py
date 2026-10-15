#!/usr/bin/env python3
"""Run the quick, read-only replication package checks and exhibit build."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ENV = os.environ.copy()
ENV.setdefault("MPLCONFIGDIR", "/private/tmp/teacher-attendance-replication-mpl")


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=PACKAGE, env=ENV, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-analysis", action="store_true", help="rerun the supplied Python transition audits, including both 9,999-draw bootstraps")
    args = parser.parse_args()
    if args.full_analysis:
        for name in [
            "audit_transition_extension.py",
            "audit_transition_scope.py",
            "audit_sentinel_measurement.py",
            "audit_transition_sentinels.py",
        ]:
            run([sys.executable, "scripts/" + name])
    run([sys.executable, "scripts/verify_results.py"])
    run([sys.executable, "code/build_exhibits.py"])
    print("Quick replication complete. See results/verification.json and results/table*.csv/results/figure1.*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
