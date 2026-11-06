import csv
import glob
import os
import sys

import pytest

print("[conftest] LOADED", file=sys.stderr, flush=True)

columns = ["scenario_name", "algorithm", "m", "n", "execution_time", "execution_time_ms"]


def _is_worker() -> bool:
    """PYTEST_XDIST_WORKER задаётся только в воркерах xdist (gw0, gw1, ...)."""
    return "PYTEST_XDIST_WORKER" in os.environ


def _natural_worker_key(path: str):
    """Сортировка gw0, gw1, ..., gw10, gw11 — по номеру воркера."""
    base = os.path.basename(path)
    suffix = base[len("test_results_"):-len(".csv")]
    if suffix.startswith("gw") and suffix[2:].isdigit():
        return (0, int(suffix[2:]))
    return (1, suffix)


def _merge_results():
    files = sorted(glob.glob("test_results_*.csv"), key=_natural_worker_key)
    print(
        f"[merge] controller: found {len(files)} worker files: "
        f"{[os.path.basename(f) for f in files]}",
        file=sys.stderr,
        flush=True,
    )
    if not files:
        return

    total = 0
    with open("test_results.csv", mode="w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        for path in files:
            with open(path, mode="r", encoding="utf-8", newline="") as inp:
                for row in csv.DictReader(inp):
                    writer.writerow(row)
                    total += 1

    print(f"[merge] wrote {total} rows to test_results.csv", file=sys.stderr, flush=True)

    for path in files:
        try:
            os.remove(path)
        except OSError:
            pass


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Вызывается в контроллере после того, как все воркеры завершились."""
    if _is_worker():
        return
    _merge_results()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Страховка: если по какой-то причине sessionfinish не сделал merge — повторим."""
    if _is_worker():
        return
    if os.path.exists("test_results.csv"):
        return
    _merge_results()
