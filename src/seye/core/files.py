"""Shared local file checks for callers operating inside a trusted workspace."""
import os
from pathlib import Path
import stat


def resolve_path(path):
    """Resolve existing ancestors strictly while allowing a new output path."""
    candidate = Path(path).expanduser()
    missing = []
    while True:
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError:
            # A dangling link is not a new path the caller can claim.
            if candidate.is_symlink():
                raise PermissionError('Dangling symbolic link at operation path')
            if candidate.name == '..':
                raise PermissionError('Parent traversal through a missing path')
            missing.append(candidate.name)
            candidate = candidate.parent
        except (OSError, RuntimeError) as error:
            raise PermissionError('Operation path could not be resolved') from error
        else:
            if missing and not resolved.is_dir():
                raise PermissionError('Operation path has a non-directory ancestor')
            return resolved.joinpath(*reversed(missing))


def read_bounded(path, max_bytes):
    """Check file type and bound both the stat size and the actual read."""
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NONBLOCK', 0)
    path = Path(path)
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('Input must be a regular file')
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Input must be a regular file')
        if info.st_size > max_bytes:
            raise ValueError('Input exceeds byte limit')
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError('Input exceeds byte limit')
    return raw
