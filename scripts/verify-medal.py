#!/usr/bin/env python3
"""
Verifica que docs/MEDALLA.md no ha sido manipulada manualmente.

Si el archivo existe, extrae el token y el run_id del contenido y
comprueba que el token es el HMAC correcto para ese run_id.

Si el archivo NO existe, el script pasa sin error: la medalla aun no
ha sido generada (el alumno no ha completado el tutorial todavia).

Si el archivo EXISTE pero el token no cuadra con el HMAC esperado, el
script falla con exit 1: alguien edito el archivo a mano.

Requiere: COMPLETION_SECRET configurado como secret en el repositorio.
Si el secret no esta disponible en el entorno, el script pasa sin verificar
(modo sin secret: no podemos verificar pero tampoco bloqueamos).

Uso en CI:
  GITHUB_REPOSITORY=owner/repo COMPLETION_SECRET=<secret> python3 scripts/verify-medal.py
"""

import hashlib
import hmac as hmac_module
import json
import os
import re
import sys


MEDAL_PATH = "docs/MEDALLA.md"


def extract_field(content: str, label: str) -> str | None:
    """Extrae el valor de una fila de tabla markdown: | label | `value` |"""
    pattern = rf"\|\s*{re.escape(label)}\s*\|\s*`([^`]+)`\s*\|"
    match = re.search(pattern, content)
    return match.group(1) if match else None


def extract_token(content: str) -> str | None:
    """Extrae el token de la linea **Token de integridad:** `TOKEN`"""
    match = re.search(r"\*\*Token de integridad:\*\*\s*`([A-F0-9]{40})`", content)
    return match.group(1) if match else None


def extract_step_count(content: str) -> int | None:
    """Extrae 'N de N' de la fila Pasos verificados."""
    match = re.search(r"\|\s*Pasos verificados\s*\|\s*(\d+)\s*de\s*(\d+)\s*\|", content)
    if match:
        return int(match.group(1))
    return None


def recompute_token(repo: str, actor: str, run_id: str, total_steps: int, secret: str) -> str:
    completed_steps = sorted([f"validate-step-{i:02d}" for i in range(1, total_steps + 1)])
    payload = json.dumps(
        {
            "repo": repo,
            "actor": actor,
            "run_id": run_id,
            "completed_steps": completed_steps,
            "total": total_steps,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    raw = hmac_module.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return raw[:40].upper()


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "unknown/unknown")
    secret = os.environ.get("COMPLETION_SECRET") or None

    if not os.path.exists(MEDAL_PATH):
        print("[VERIFY] docs/MEDALLA.md no existe aun — el tutorial no ha sido completado.")
        print("[VERIFY] OK — no hay nada que verificar.")
        return 0

    if not secret:
        print("[VERIFY] COMPLETION_SECRET no disponible en este entorno.")
        print("[VERIFY] SKIP — no se puede verificar el token sin el secreto.")
        return 0

    with open(MEDAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    token_in_file = extract_token(content)
    if not token_in_file:
        print("[FAIL] docs/MEDALLA.md no contiene un token de integridad valido.")
        print("[FAIL] El archivo puede haber sido manipulado manualmente.")
        return 1

    repo_in_file = extract_field(content, "Repositorio")
    actor_in_file = extract_field(content, "Completado por")
    run_id_in_file = extract_field(content, "Run ID")
    total_steps = extract_step_count(content)

    if not all([repo_in_file, actor_in_file, run_id_in_file, total_steps]):
        print("[FAIL] docs/MEDALLA.md tiene metadatos incompletos.")
        print("[FAIL] El archivo puede haber sido manipulado manualmente.")
        return 1

    # El repositorio en el archivo debe coincidir con el repositorio actual
    if repo_in_file != repo:
        print(f"[FAIL] El repositorio en la medalla ({repo_in_file}) no coincide con el actual ({repo}).")
        print("[FAIL] No se puede importar una medalla de otro repositorio.")
        return 1

    expected_token = recompute_token(repo_in_file, actor_in_file, run_id_in_file, total_steps, secret)

    if not hmac_module.compare_digest(token_in_file, expected_token):
        print("[FAIL] El token de integridad NO coincide con el HMAC esperado.")
        print("[FAIL] La medalla ha sido modificada manualmente o pertenece a otra ejecucion.")
        print(f"[FAIL] Token en archivo : {token_in_file}")
        print(f"[FAIL] Token esperado   : {expected_token}")
        return 1

    print(f"[VERIFY] Token verificado correctamente.")
    print(f"[VERIFY] Repositorio : {repo_in_file}")
    print(f"[VERIFY] Usuario     : {actor_in_file}")
    print(f"[VERIFY] Run ID      : {run_id_in_file}")
    print(f"[VERIFY] Pasos       : {total_steps}")
    print("[VERIFY] OK — la medalla es autentica.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
