"""Isolated CLI bootstrap: rehearsal children cannot load model libraries."""
from __future__ import annotations

import importlib.abc
import runpy
import socket
import sys
from pathlib import Path


class NoModelImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"torch", "transformers", "datasets", "peft", "trl"}:
            raise RuntimeError(f"rehearsal_model_import_forbidden:{fullname}")
        return None


def no_network(*args, **kwargs):
    raise RuntimeError("rehearsal_network_forbidden")


def main():
    script = Path(sys.argv[1]).resolve()
    args = sys.argv[2:]
    if script.name == "run_state1_finetune_local_lora.py" and "--dry-run" not in args:
        raise RuntimeError("rehearsal_requires_dry_run")
    sys.meta_path.insert(0, NoModelImports())
    socket.create_connection = no_network
    socket.socket.connect = no_network
    socket.socket.connect_ex = no_network
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script), *args]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
