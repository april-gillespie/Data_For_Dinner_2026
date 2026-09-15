"""Verify publication file integrity and local links using Python 3.9 or later."""
import hashlib
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def mp4_boxes(data):
    offset = 0
    while offset < len(data):
        size, name = struct.unpack_from('>I4s', data, offset)
        header = 8
        if size == 1:
            size = struct.unpack_from('>Q', data, offset + 8)[0]
            header = 16
        elif size == 0:
            size = len(data) - offset
        if size < header or offset + size > len(data):
            raise ValueError('Invalid MP4 box length')
        yield name, data[offset + header:offset + size]
        offset += size


def milliseconds(value):
    h, m, s, ms = map(int, re.split('[:,]', value))
    if m > 59 or s > 59:
        raise ValueError('Invalid caption timestamp')
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def verify():
    manifest = json.loads((ROOT / 'docs/artifact_manifest.json').read_text(encoding='utf-8'))
    paths = [entry['path'] for entry in manifest['files']]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate manifest path')
    for entry in manifest['files']:
        data = (ROOT / entry['path']).read_bytes()
        actual = (len(data), hashlib.sha256(data).hexdigest(),
                  hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest())
        if actual != (entry['bytes'], entry['sha256'], entry['git_blob_sha1']):
            raise ValueError(f'File integrity mismatch: {entry["path"]}')
    print(f'PASS: {len(paths)} published artifacts match sizes and hashes')

    boxes = list(mp4_boxes((ROOT / 'video/Data_for_Dinner_2026.mp4').read_bytes()))
    names = [name for name, _ in boxes]
    if names.index(b'moov') > names.index(b'mdat'):
        raise ValueError('MP4 metadata must precede media for progressive playback')
    movie = next(payload for name, payload in boxes if name == b'moov')
    header = next(payload for name, payload in mp4_boxes(movie) if name == b'mvhd')
    scale = struct.unpack_from('>I', header, 20 if header[0] else 12)[0]
    duration = struct.unpack_from('>Q' if header[0] else '>I', header, 24 if header[0] else 16)[0] / scale
    if not 401.85 <= duration <= 402:
        raise ValueError(f'Unexpected published video duration: {duration}')
    print(f'PASS: MP4 structure, progressive playback metadata, and {duration:.3f}s duration')

    source = (ROOT / manifest['captions']['path']).read_text(encoding='utf-8-sig')
    cues = []
    for block in re.split(r'\n\s*\n', source.strip()):
        lines = block.splitlines()
        if len(lines) < 2 or not re.fullmatch(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', lines[1]):
            raise ValueError('Malformed caption block')
        start, end = lines[1].split(' --> ')
        start_ms, end_ms = milliseconds(start), milliseconds(end)
        if int(lines[0]) != len(cues) + 1 or start_ms >= end_ms or end_ms > duration * 1000:
            raise ValueError('Invalid caption sequence or duration')
        if cues and start_ms < cues[-1]['end_ms']:
            raise ValueError('Overlapping captions')
        cues.append({'start': start, 'end': end, 'end_ms': end_ms, 'text': '\n'.join(lines[2:])})
    populated = [c for c in cues if c['text'].strip()]
    expected = manifest['captions']
    if (len(cues), len(populated), len(cues) - len(populated), cues[-1]['end_ms']) != tuple(
            expected[k] for k in ['blocks', 'text_blocks', 'empty_blocks', 'last_end_ms']):
        raise ValueError('Caption counts or endpoint differ from manifest')
    transcript = (ROOT / 'video/transcript.md').read_text(encoding='utf-8')
    if re.findall(r'(?ms)^```text\n(.*?)\n```$', transcript) != [c['text'] for c in populated]:
        raise ValueError('Transcript differs from original caption wording')
    for index, cue in enumerate(cues, 1):
        if cue['text'].strip() and f'## {cue["start"]} to {cue["end"]}, cue {index}' not in transcript:
            raise ValueError('Transcript timestamp differs from original captions')
    print('PASS: Caption sequence, duration bounds, original wording, and transcript')

    count = 0
    for document in ROOT.rglob('*.md'):
        if '.git' in document.parts:
            continue
        body = re.sub(r'```[\s\S]*?```', '', document.read_text(encoding='utf-8'))
        targets = re.findall(r'\[[^\]]*\]\(([^)]+)\)', body) + re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', body)
        for target in targets:
            url = urlsplit(target.strip('<>'))
            if url.scheme or url.netloc or not url.path:
                continue
            path = (document.parent / unquote(url.path)).resolve()
            if not path.is_relative_to(ROOT.resolve()) or not path.exists():
                raise ValueError(f'Broken local link in {document.name}: {target}')
            count += 1
    print(f'PASS: {count} local Markdown links and HTML image paths resolve')


if __name__ == '__main__':
    verify()
