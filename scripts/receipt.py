"""Bind a local review round to explicitly named files. Uses Python 3.8+."""
import argparse
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sys


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def member(root, name, receipt):
    relative = Path(name)
    if relative.is_absolute() or relative.drive or relative.root:
        raise ValueError('Use file names relative to the receipt directory.')
    if '..' in relative.parts:
        raise ValueError('Parent traversal is not allowed: ' + name)
    path = (root / relative).resolve(strict=True)
    path.relative_to(root)
    if not path.is_file() or path == receipt:
        raise ValueError('Expected an evidence file distinct from the receipt: ' + name)
    return relative.as_posix(), path


def create(args, path):
    files = {}
    for name in args.files:
        key, candidate = member(path.parent, name, path)
        if key in files:
            raise ValueError('Duplicate input: ' + key)
        files[key] = {'target': str(candidate), 'sha256': digest(candidate)}
    receipt = {'round': args.round, 'readback_code': secrets.token_hex(16), 'files': files}
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print('Created local receipt for {} ({} files).'.format(args.round, len(files)))


def check(args, path):
    receipt = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(receipt, dict) or receipt.get('round') != args.round:
        raise ValueError('Round mismatch.')
    code = receipt.get('readback_code')
    if not isinstance(code, str) or len(code) != 32 or any(c not in '0123456789abcdef' for c in code):
        raise ValueError('Invalid local readback code.')
    if not hmac.compare_digest(code.encode(), args.readback.encode()):
        raise ValueError('Readback mismatch.')
    files = receipt.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Missing path bindings; create a new round and receipt.')
    for name, entry in files.items():
        _, candidate = member(path.parent, name, path)
        if not isinstance(entry, dict) or not isinstance(entry.get('target'), str):
            raise ValueError('Invalid path binding: ' + name)
        if Path(entry['target']) != candidate:
            raise ValueError('Evidence path target changed: ' + name)
        if digest(candidate) != entry.get('sha256'):
            raise ValueError('File changed: ' + name)
    print('Round, readback, targets and {} file hashes match.'.format(len(files)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('create', 'check'):
        sub = actions.add_parser(name)
        sub.add_argument('receipt', type=Path)
        sub.add_argument('--round', required=True)
        if name == 'create':
            sub.add_argument('files', nargs='+', help='Paths relative to the receipt directory')
        else:
            sub.add_argument('--readback', required=True)
    args = parser.parse_args()
    try:
        if not args.round.strip():
            raise ValueError('Round must be non-empty.')
        # Resolve the parent only. Exclusive creation also rejects an existing symlink.
        path = args.receipt.parent.resolve(strict=True) / args.receipt.name
        if path.is_symlink():
            raise ValueError('Receipt may not be a symlink.')
        (create if args.action == 'create' else check)(args, path)
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
