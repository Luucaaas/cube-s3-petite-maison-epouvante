import sys
from pathlib import Path

# Make "event" and "rabbitmq" importable whether pytest runs from the repo root or from demo-messaging/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
