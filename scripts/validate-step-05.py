#!/usr/bin/env python3
import os, sys
STEP = 5
ARTIFACTS = ['src/routes/comments.js', 'src/middleware/security-headers.js']
MARKERS = {
    'src/routes/comments.js': ['DOMPurify'],
    'src/middleware/security-headers.js': ['Content-Security-Policy', 'X-Content-Type-Options'],
}

def main():
    errors = []
    for artifact in ARTIFACTS:
        if not os.path.exists(artifact):
            errors.append(f'Artifact not found: {artifact}')
            continue
        with open(artifact, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for marker in MARKERS[artifact]:
            if marker not in content:
                errors.append(f'Missing marker in {artifact}: {marker}')
    if errors:
        print('STEP VALIDATION FAILED')
        for err in errors: print(f'- {err}')
        return 1
    print(f'STEP {STEP} VALID')
    return 0

if __name__ == '__main__':
    sys.exit(main())
