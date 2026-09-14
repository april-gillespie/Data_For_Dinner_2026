"""Check final package integrity using Python 3 standard library only."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit


def blob_sha(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def milliseconds(timestamp):
    h, m, s, ms = map(int, re.split(r'[:,]', timestamp))
    if m > 59 or s > 59:
        raise ValueError(f'Invalid time: {timestamp}')
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def parse_captions(text):
    cues = []
    for block in re.split(r'\r?\n\s*\r?\n', text.strip()):
        lines = block.splitlines()
        if len(lines) < 2 or not re.fullmatch(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', lines[1]):
            raise ValueError('Malformed caption block')
        start, end = lines[1].split(' --> ')
        cue = {'index': int(lines[0]), 'start': start, 'end': end, 'text': '\n'.join(lines[2:])}
        if cue['index'] != len(cues) + 1 or milliseconds(start) >= milliseconds(end):
            raise ValueError(f'Invalid caption index or duration: {cue["index"]}')
        if cues and milliseconds(start) < milliseconds(cues[-1]['end']):
            raise ValueError(f'Overlapping caption: {cue["index"]}')
        cues.append(cue)
    return cues


def transcript_text(cues):
    text = ('# Presentation transcript\n\n'
            'Mechanical extraction of the nonempty blocks in the [original captions](Data%20for%20Dinner%20Captions.srt). '
            'Wording, spelling, and line breaks are preserved. Empty timed blocks are omitted here but remain in the SRT. '
            'Names and tool spellings may contain recognition errors. The [final presentation](../presentation/DataForDinnerTeam_WiDDatathon2026_Presentation_Final_13Sept2026.pdf) '
            'takes precedence for the final project narrative and credits.\n\n')
    for cue in cues:
        if cue['text'].strip():
            text += f'## {cue["start"]} to {cue["end"]}, cue {cue["index"]}\n\n```text\n{cue["text"]}\n```\n\n'
    return text


def verify(root, staged=False):
    manifest = json.loads((root / 'docs/artifact_manifest.json').read_text(encoding='utf-8'))
    archive = json.loads((root / manifest['archive_manifest']).read_text(encoding='utf-8'))
    checks = []
    if len(manifest['files']) != 8 or len({f['path'] for f in manifest['files']}) != 8:
        raise ValueError('Expected eight unique original files')
    for entry in manifest['files']:
        data = (root / entry['path']).read_bytes()
        if (len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']
                or blob_sha(data) != entry['git_blob_sha1']):
            raise ValueError(f'Original file integrity mismatch: {entry["path"]}')
    checks.append('Eight original files match sizes, SHA-256, and Git blob hashes')
    cues = parse_captions((root / manifest['captions']['path']).read_text(encoding='utf-8-sig'))
    expected = manifest['captions']
    actual = (len(cues), sum(bool(c['text'].strip()) for c in cues), sum(not c['text'].strip() for c in cues), cues[0]['start'], cues[-1]['end'])
    if actual != tuple(expected[k] for k in ('blocks', 'text_blocks', 'empty_blocks', 'first_start', 'last_end')):
        raise ValueError('Caption structure differs from manifest')
    if (root / 'video/transcript.md').read_text(encoding='utf-8') != transcript_text(cues):
        raise ValueError('Transcript differs from mechanical caption extraction')
    checks.append('Caption order, positive durations, no overlaps, counts, and transcript match')
    archive_files = {f'{archive["publication_root"]}/{f["path"]}': f['git_blob_sha1'] for f in archive['files']}
    old_readme = archive['previous_main_readme']
    archive_files[old_readme['path']] = old_readme['git_blob_sha1']
    if not staged:
        for path, expected_sha in archive_files.items():
            if blob_sha((root / path).read_bytes()) != expected_sha:
                raise ValueError(f'Historical file changed: {path}')
        checks.append(f'{len(archive_files)} historical files match original Git blob hashes')
    else:
        checks.append('Staging mode: historical subtree is validated separately through GitHub')
    virtual = {(root / p).resolve() for p in archive_files}
    for document in root.rglob('*.md'):
        rel = document.relative_to(root).as_posix()
        if rel.startswith(archive['publication_root'] + '/') or rel == old_readme['path']:
            continue
        # Skip fenced source text so caption wording is never treated as Markdown links.
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
