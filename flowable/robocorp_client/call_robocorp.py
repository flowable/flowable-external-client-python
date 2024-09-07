import subprocess
import sys


def call_robocorp(args, mod_name='robocorp.actions'):
    call_args = [sys.executable, "-m", mod_name]
    call_args.extend(args)
    try:
        return subprocess.run(call_args, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print("ERROR: failed to call robocorp", exc.returncode, exc.output)

