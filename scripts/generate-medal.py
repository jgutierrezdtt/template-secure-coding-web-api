#!/usr/bin/env python3
"""
Genera la medalla de completacion del tutorial.

Solo produce el token de integridad si TODOS los validators de pasos
previos retornan exit code 0. Si alguno falla, el script termina con
exit code 1 y no escribe ningun archivo.

Token de integridad:
  HMAC-SHA256(payload, COMPLETION_SECRET) — requiere el secret del repositorio.
  Sin COMPLETION_SECRET el script termina con exit 1: el secret es obligatorio
  para que el token no sea forgeable por cualquiera con acceso publico.

  payload = JSON canonico de: repo, actor, run_id, pasos_completados, total

  - run_id hace el token unico por ejecucion de Actions (no reutilizable).
  - COMPLETION_SECRET (nunca visible para el alumno) hace el HMAC inforgeable.
  - El token es verificable externamente con la clave y los metadatos del .md.

Uso:
  GITHUB_REPOSITORY=owner/repo GITHUB_ACTOR=user GITHUB_RUN_ID=123 \\
  COMPLETION_SECRET=<secret> python3 scripts/generate-medal.py
"""

import glob
import hashlib
import hmac as hmac_module
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Ejecucion de validators
# ---------------------------------------------------------------------------

def run_validators(repo_root: str) -> dict[str, bool]:
    scripts_dir = os.path.join(repo_root, "scripts")
    validator_files = sorted(
        glob.glob(os.path.join(scripts_dir, "validate-step-*.py"))
    )

    if not validator_files:
        print("[FAIL] No se encontraron scripts de validacion en scripts/validate-step-*.py")
        sys.exit(1)

    results: dict[str, bool] = {}
    for script_path in validator_files:
        step_name = os.path.basename(script_path).replace(".py", "")
        print(f"[CHECK] {step_name} ...", end=" ", flush=True)
        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0
        results[step_name] = ok
        status = "PASS" if ok else "FAIL"
        print(status)
        if proc.stdout.strip():
            for line in proc.stdout.strip().splitlines():
                print(f"        {line}")
        if proc.stderr.strip():
            for line in proc.stderr.strip().splitlines():
                print(f"        {line}")

    return results


# ---------------------------------------------------------------------------
# Generacion del token
# ---------------------------------------------------------------------------

def generate_token(repo: str, actor: str, run_id: str, completed_steps: list[str], secret: str) -> str:
    payload = json.dumps(
        {
            "repo": repo,
            "actor": actor,
            "run_id": run_id,
            "completed_steps": sorted(completed_steps),
            "total": len(completed_steps),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    raw = hmac_module.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return raw[:40].upper()


# ---------------------------------------------------------------------------
# Escritura del archivo de medalla
# ---------------------------------------------------------------------------

def build_verification_snippet(repo: str, actor: str, run_id: str, total_steps: int) -> str:
    steps_list = json.dumps(
        [f"validate-step-{i:02d}" for i in range(1, total_steps + 1)],
        separators=(", ", ": "),
    )
    return f"""\
```python
import hashlib, hmac, json

# Requiere COMPLETION_SECRET — solo el propietario del repositorio lo conoce.
# Sin el secreto el token no puede verificarse ni reproducirse.
secret = b"<COMPLETION_SECRET>"

payload = json.dumps(
    {{
        "repo": "{repo}",
        "actor": "{actor}",
        "run_id": "{run_id}",
        "completed_steps": {steps_list},
        "total": {total_steps},
    }},
    sort_keys=True,
    separators=(",", ":"),
).encode()

token = hmac.new(secret, payload, hashlib.sha256).hexdigest()[:40].upper()
print(token)  # debe coincidir con el token de arriba
```"""


def write_medal(repo: str, actor: str, token: str, total_steps: int, run_id: str, repo_root: str) -> str:
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    medal_path = os.path.join(docs_dir, "MEDALLA.md")

    repo_name = repo.split("/")[-1] if "/" in repo else repo
    completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    verification = build_verification_snippet(repo, actor, run_id, total_steps)

    content = f"""\
# Medalla de completacion — {repo_name}

**Token de integridad:** `{token}`

| Campo | Valor |
|-------|-------|
| Repositorio | `{repo}` |
| Completado por | `{actor}` |
| Pasos verificados | {total_steps} de {total_steps} |
| Fecha | {completed_at} |
| Run ID | `{run_id}` |

---

## Que garantiza este token

- Los {total_steps} validators ejecutaron en GitHub Actions y todos retornaron exit 0.
- El token es HMAC-SHA256 del payload firmado con `COMPLETION_SECRET`, un secreto del repositorio que el alumno nunca puede leer.
- Sin `COMPLETION_SECRET` es imposible calcular un token valido, aunque se conozcan todos los demas campos del payload.
- El `run_id` hace el token unico para esta ejecucion concreta — no puede reutilizarse de otra run.
- Cada fork del repositorio produce un token distinto porque `repo` y `actor` son parte del payload firmado.

---

## Como verificar este token (requiere el secreto)

{verification}

La verificacion solo puede hacerla el propietario del repositorio que conoce `COMPLETION_SECRET`.
Un alumno no puede forjar ni verificar el token por si mismo.
"""
    with open(medal_path, "w", encoding="utf-8") as f:
        f.write(content)

    return medal_path


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "unknown/unknown")
    actor = os.environ.get("GITHUB_ACTOR", "unknown")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    secret = os.environ.get("COMPLETION_SECRET") or None

    if not secret:
        print("[FAIL] COMPLETION_SECRET no esta configurado.")
        print("[FAIL] Configura el secret en el repositorio de GitHub para poder generar tokens de integridad.")
        print("[FAIL] Sin el secret el token seria calculable por cualquiera — la medalla no tendria valor.")
        return 1

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"[MEDAL] Repositorio : {repo}")
    print(f"[MEDAL] Usuario     : {actor}")
    print(f"[MEDAL] Run ID      : {run_id}")
    print()

    results = run_validators(repo_root)

    passed = [step for step, ok in results.items() if ok]
    failed = [step for step, ok in results.items() if not ok]

    print()
    print(f"[MEDAL] Pasos completados : {len(passed)} / {len(results)}")

    if failed:
        print(f"[FAIL]  Pasos pendientes  : {failed}")
        print()
        print("[FAIL]  La medalla no puede otorgarse hasta que todos los pasos esten completos.")
        return 1

    token = generate_token(repo, actor, run_id, passed, secret)
    medal_path = write_medal(repo, actor, run_id, token, len(passed), repo_root)

    print()
    print(f"[MEDAL] Token de integridad : {token}")
    print(f"[MEDAL] Medalla escrita en  : {medal_path}")
    print()
    print("[MEDAL] Tutorial completado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
