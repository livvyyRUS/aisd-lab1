import csv
import math
import os
import random
import time
from collections.abc import Callable

import pytest

# Импортирование алгоритмов
from algorithms.binary_search import binary_search
from algorithms.double_binary import double_binary
from algorithms.exp_search import exp_search
from algorithms.two_pointers import two_pointers

# =====================================================================
# УРОВНИ ТЕСТИРОВАНИЯ (ГЕНЕРАТОРЫ ДАННЫХ)
# =====================================================================


def gen_random(m: int, n: int):
    """1. Рандомный уровень (Средний случай)"""
    max_val = max(m, n) * 10
    a = sorted([random.randint(0, max_val) for _ in range(m)])
    b = sorted([random.randint(0, max_val) for _ in range(n)])
    answer = len(set(a).intersection(set(b))) > 0
    return a, b, answer


def gen_worst_case(m: int, n: int):
    """2. Худший уровень (Разная четность, пересечений нет)"""
    max_val = max(m, n) * 2
    a = sorted(random.sample(range(0, max_val, 2), m))
    b = sorted(random.sample(range(1, max_val, 2), n))
    return a, b, False


def gen_best_case(m: int, n: int):
    """3. Лучший уровень (Пересечение на первых элементах)"""
    max_val = max(m, n) * 10
    a = sorted([random.randint(1, max_val) for _ in range(m)])
    b = sorted([random.randint(1, max_val) for _ in range(n)])
    a[0] = 0
    b[0] = 0
    return a, b, True


def gen_duplicates(m: int, n: int):
    """4. Уровень с дубликатами (Мало уникальных значений)"""
    a = sorted([random.randint(0, 5) for _ in range(m)])
    b = sorted([random.randint(3, 8) for _ in range(n)])
    answer = len(set(a).intersection(set(b))) > 0
    return a, b, answer


SCENARIOS = {
    "RANDOM": gen_random,
    "WORST_CASE": gen_worst_case,
    "BEST_CASE": gen_best_case,
    "DUPLICATES": gen_duplicates,
}

test_sizes = [(10**i, 10**j) for i in range(1, 8) for j in range(1, 8)]

data = []

columns = ["scenario_name", "algorithm", "m", "n", "execution_time", "execution_time_ms"]


# =====================================================================
# ДВИЖОК ТЕСТИРОВАНИЯ
# =====================================================================


def start_test(func: Callable, scenario_name: str, m: int, n: int):
    generator = SCENARIOS[scenario_name]
    a, b, answer = generator(m, n)

    start_time = time.perf_counter()
    result = func(a, b)
    end_time = time.perf_counter()

    execution_time = end_time - start_time

    data.append(
        {
            "scenario_name": scenario_name,
            "algorithm": func.__name__,
            "m": m,
            "n": n,
            "execution_time": f"{execution_time:.6f}",
            "execution_time_ms": f"{execution_time * 1000:.6f}"
        }
    )

    assert result == answer


def id_func(val):
    scenario_name, (m, n) = val
    p_m = int(math.log10(m))
    p_n = int(math.log10(n))
    return f"{scenario_name}-M=10^{p_m}_N=10^{p_n}"


test_parameters = [(scenario, size) for scenario in SCENARIOS for size in test_sizes]


@pytest.mark.parametrize("scenario_and_size", test_parameters, ids=id_func)
def test_two_pointers(scenario_and_size):
    scenario_name, (m, n) = scenario_and_size
    start_test(two_pointers, scenario_name, m, n)


@pytest.mark.parametrize("scenario_and_size", test_parameters, ids=id_func)
def test_binary_search(scenario_and_size):
    scenario_name, (m, n) = scenario_and_size
    start_test(binary_search, scenario_name, m, n)


@pytest.mark.parametrize("scenario_and_size", test_parameters, ids=id_func)
def test_exp_search(scenario_and_size):
    scenario_name, (m, n) = scenario_and_size
    start_test(exp_search, scenario_name, m, n)


@pytest.mark.parametrize("scenario_and_size", test_parameters, ids=id_func)
def test_double_binary(scenario_and_size):
    scenario_name, (m, n) = scenario_and_size
    start_test(double_binary, scenario_name, m, n)


# =====================================================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ (per-worker).
# Слияние в test_results.csv выполняет conftest.py на контроллере.
# =====================================================================


@pytest.fixture(scope="session", autouse=True)
def save_results():
    """
    Каждый воркер пишет свой файл test_results_<worker_id>.csv,
    чтобы не затирать данные других воркеров.
    Слияние в один test_results.csv делает conftest.py (pytest_sessionfinish).
    """
    yield
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    path = f"test_results_{worker_id}.csv"
    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
