"""Check final package integrity using Python 3 standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit


def blob_sha(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def verify(root, staged=False):
    manifest = json.loads((root / 'docs/artifact_manifest.json').read_text(encoding='utf-8'))
    archive = json.loads((root / manifest['archive_manifest']).read_text(encoding='utf-8'))
    checks = []
    if len(manifest['files']) != 5 or len({f['path'] for f in manifest['files']}) != 5:
        raise ValueError('Expected five unique retained supplied files')
    for entry in manifest['files']:
        data = (root / entry['path']).read_bytes()
        if (len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']
                or blob_sha(data) != entry['git_blob_sha1']):
            raise ValueError(f'Original file integrity mismatch: {entry["path"]}')
    checks.append('Five retained supplied files match sizes, SHA-256, and Git blob hashes')
    archive_files = {f'{archive["publication_root"]}/{f["path"]}': f['git_blob_sha1'] for f in archive['files']}
    old_readme = archive['previous_main_readme']
    archive_files[old_readme['path']] = old_readme['git_blob_sha1']
    if not staged:
        for path, expected_sha in archive_files.items():
            if blob_sha((root / path).read_bytes()) != expected_sha:
                raise ValueError(f'Historical file changed: {path}')
        checks.append(f'{len(archive_files)} historical files match recorded Git blob hashes')
    else:
        checks.append('Staging mode: historical subtree is validated separately through GitHub')
    virtual = {(root / p).resolve() for p in archive_files}
    for document in root.rglob('*.md'):
        rel = document.relative_to(root).as_posix()
        if rel.startswith(archive['publication_root'] + '/') or rel == old_readme['path']:
            continue
        body = re.sub(r'```[\s\S]*?```', '', document.read_text(encoding='utf-8'))
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            link = urlsplit(target.strip('<>'))
            if link.scheme or link.netloc or not link.path:
                continue
            path = (document.parent / unquote(link.path)).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError(f'Link escapes repository: {rel}: {target}')
            if not path.exists() and not (staged and (path in virtual or any(path in p.parents for p in virtual))):
                raise ValueError(f'Broken local link: {rel}: {target}')
    checks.append('Final Markdown local link targets resolve; external links and anchors are not fetched')
    for check in checks:
        print(f'PASS: {check}')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true', help='Skip physical archive checks before attaching the unchanged Git subtree')
    args = parser.parse_args()
    verify(Path(__file__).resolve().parents[1], args.staged)
