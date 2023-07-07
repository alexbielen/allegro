def ordered_pc_interval_structure(s):
    """Assumes that pitch classes are in normal order"""
    res = []
    initial = s[0]

    for elem in s:
        distance = (elem - initial) % 12
        res.append(distance)

    return res


def pc_transpose(pitch, by):
    return (pitch + by) % 12


def pc_transpose_product(xs, ys):
    res = []

    for x in xs:
        for y in ys:
            res.append(pc_transpose(x, y))

    return res


def boulez_multiplication(x, y):
    ois = ordered_pc_interval_structure(x)
    res = pc_transpose_product(ois, y)

    return set(res)
