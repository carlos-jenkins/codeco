def fibonacci1(n):
    """
    Recursive descendant version.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci1(n - 1) + fibonacci1(n - 2)


def fibonacci2(n):
    """
    Tail recursive ascendant version.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci2_aux(2, n, 0, 1)


def fibonacci2_aux(current, target, before_previous, previous):
    """
    Tail recursive ascendant version - auxiliar function.
    """
    if current == target:
        return before_previous + previous
    return fibonacci2_aux(
        current + 1, target, previous, before_previous + previous
    )


def fibonacci3(n):
    """
    Iterative ascendant version.
    """
    if n == 0:
        return 0
    elif n == 1:
        return 1

    before_previous = 0
    previous = 1
    counter = 2
    temporal = 0

    while counter < n:
        temporal = before_previous
        before_previous = previous
        previous = temporal + before_previous
        counter = counter + 1

    return before_previous + previous
