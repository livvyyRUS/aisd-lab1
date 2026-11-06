from .bisect_left import bisect_left


def double_binary(a: list[int], b: list[int]):
    if len(a) > len(b):
        a, b = b, a

    m = len(a)
    n = len(b)

    def micro_bisect(l: int, r: int, b_l: int, b_r: int):
        if l >= r:
            return False

        mid = (l + r) // 2
        mid_el = a[mid]

        idx = bisect_left(b, mid_el, b_l, b_r)

        if idx < b_r and idx < n and mid_el == b[idx]:
            return True

        return micro_bisect(l, mid, b_l, idx) or micro_bisect(mid + 1, r, idx, b_r)

    return micro_bisect(0, m, 0, n)

if __name__ == "__main__":
    a = [1]
    b = [1, 2, 3, 10, 11]

    print(double_binary(a, b))
