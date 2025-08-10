from secrets import token_hex


def generate_guest_username() -> str:
  """Generate a unique guest username."""
  return token_hex(6)
