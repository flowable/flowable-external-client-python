import os
import subprocess
import sys


def call_python_module(args, mod_name, env=None):
    if env is None:
        env = os.environ.copy()
    call_args = [sys.executable, "-m", mod_name]
    call_args.extend(args)
    try:
        return subprocess.run(call_args, capture_output=True, text=True, env=env)
    except subprocess.CalledProcessError as exc:
        print("ERROR: failed to call rpa framework", exc.returncode, exc.output)

