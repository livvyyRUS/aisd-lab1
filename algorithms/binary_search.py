from bisect import bisect_left


def binary_search(a: list[int], b: list[int]):
    if len(a) > len(b):
        a, b = b, a

    for target in a:
        idx = bisect_left(b, target)
        if idx < len(b) and b[idx] == target:
            return True
    return False
