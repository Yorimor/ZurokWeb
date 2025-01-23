from app import app
import sys
import os

_dir = os.path.dirname(__file__)

sys.path.insert(0, _dir)
# sys.path.insert(0, os.path.join(_dir, "main"))

if __name__ == "__main__":
    app.run()