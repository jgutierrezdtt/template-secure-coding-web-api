#!/usr/bin/env python3
import os, sys
STEP = 10
EXPECTED_ARTIFACT = 'docs/secure-coding-checklist.md'
REQUIRED_MARKERS = ['Frente 1', 'Frente 2', 'Frente 3', 'Frente 4']

def main():
    errors = []
    if not os.path.exists(EXPECTED_ARTIFACT):
        errors.append(f'Artifact not found: {EXPECTED_ARTIFACT}')
    else:
        with open(EXPECTED_ARTIFACT, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for marker in REQUIRED_MARKERS:
            if marker not in content:
                errors.append(f'Missing marker in {EXPECTED_ARTIFACT}: {marker}')
    if errors:
        print('STEP VALIDATION FAILED')
        for err in errors: print(f'- {err}')
        return 1
    print(f'STEP {STEP} VALID')
    return 0

if __name__ == '__main__':
    sys.exit(main())
