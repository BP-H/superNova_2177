class ndarray(list):
    """Very small stand-in mimicking ``numpy.ndarray`` for tests."""

    def mean(self, axis=None):  # pragma: no cover - trivial
        if not self:
            return 0.0 if axis is None else []
        if axis is None:
            return sum(float(x) for x in self) / len(self)
        if axis == 0:
            length = len(self[0]) if self and isinstance(self[0], (list, ndarray)) else 0
            return [
                sum(float(row[i]) for row in self) / len(self)
                for i in range(length)
            ]
        raise NotImplementedError

def array(seq, dtype=float):  # pragma: no cover - trivial
    return ndarray(dtype(x) for x in seq)

def zeros(shape, dtype=float):  # pragma: no cover - trivial
    if isinstance(shape, int):
        return ndarray(dtype(0) for _ in range(shape))
    rows, cols = shape
    return ndarray([ndarray(dtype(0) for _ in range(cols)) for _ in range(rows)])

def stack(arrays):  # pragma: no cover - trivial
    return ndarray(arrays)

def linspace(start, stop, num, endpoint=True):  # pragma: no cover - simplified
    if num <= 0:
        return ndarray()
    if num == 1:
        return ndarray([float(stop if endpoint else start)])
    if endpoint:
        step = (stop - start) / (num - 1)
        return ndarray(start + i * step for i in range(num))
    step = (stop - start) / num
    return ndarray(start + i * step for i in range(num))

def trapz(y, x):  # pragma: no cover - simplified
    area = 0.0
    for i in range(1, len(x)):
        area += (x[i] - x[i - 1]) * (y[i] + y[i - 1]) / 2.0
    return area

bool_ = bool

__all__ = [
    "ndarray",
    "array",
    "zeros",
    "stack",
    "linspace",
    "trapz",
    "bool_",
]
