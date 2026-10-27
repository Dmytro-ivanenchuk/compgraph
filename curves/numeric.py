def simpson(f, lo, hi, n=2000):
    """Інтегрування за формулою Сімпсона (n -- парне)."""
    if n % 2:
        n += 1
    h = (hi - lo) / n
    s = f(lo) + f(hi)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * f(lo + i * h)
    return s * h / 3
