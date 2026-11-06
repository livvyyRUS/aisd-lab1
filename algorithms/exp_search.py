from .bisect_left import bisect_left


def exp_search(a: list[int], b: list[int]):
    if len(a) > len(b):
        a, b = b, a

    n = len(b)

    bound = 0

    for target in a:
        if bound >= n:
            break

        step = 1
        right = bound
        while right < n and b[right] < target:
            bound = right
            right += step
            step *= 2

        right = min(right, n)

        low = bisect_left(b, target, bound, right)

        if low < n and b[low] == target:
            return True

        bound = low
    return False


if __name__ == "__main__":
    a = [10]  # элемент больше всех в b
    b = [1, 2, 3]
    print(exp_search(a, b))
