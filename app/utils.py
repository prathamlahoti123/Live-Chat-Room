import random
from datetime import datetime


def generate_guest_username() -> str:
  """Generate a unique guest username with timestamp to avoid collisions"""
  timestamp = datetime.now().strftime("%H%M")
  return f"Guest{timestamp}{random.randint(1000, 9999)}"
