def parse_bool(val: str | bool) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        val = val.strip().lower()
        if val in ("true", "t", "1"):
            return True
        if val in ("false", "f", "0", "n"):
            return False
    raise ValueError(f"Invalid truth value: {val}")
