#per non avere eX quando non serve
def fmts(x : float) -> str:
    fmt = ".3e" if abs(x) < 0.1 and x != 0 else ".3f"
    return f"{x:{fmt}}"