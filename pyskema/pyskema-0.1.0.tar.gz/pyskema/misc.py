def closest(alternatives, key):
    return min(alternatives, key=lambda s: lev_dist(key, s))


def lev_dist(a, b):
    len_a = len(a) + 1
    len_b = len(b) + 1

    if len_b > len_a:
        return lev_dist(b, a)

    prev = list(range(len_a))
    current = [0] * len_a

    for j in range(1, len_b):
        current[0] = j
        for i in range(1, len_a):
            if a[i - 1] == b[j - 1]:
                current[i] = prev[i - 1]  # mat[i, j] = mat[i - 1, j - 1]
            else:
                current[i] = min(  # mat[i, j] =
                    current[i - 1] + 1,  # deletion mat[i - 1, j] + 1
                    prev[i] + 1,  # insertion mat[i, j - 1]
                    prev[i - 1] + 1,  # substitution  mat[i - 1, j - 1]
                )

        # swap rows
        current, prev = prev, current

    return prev[-1]
