def two_pointers(a: list[int], b: list[int]):
    a_i = 0
    b_i = 0

    m = len(a)
    n = len(b)

    while a_i < m and b_i < n:
        if a[a_i] == b[b_i]:
            return True
        elif a[a_i] < b[b_i]:
            a_i += 1
        else:
            b_i += 1

    return False

if __name__ == "__main__":
    a = [1, 2, 3]
    b = [3, 4, 5]
    print(two_pointers(a, b))
