# Medalla de completacion — template-secure-coding-web-api

**Token de integridad:** `E512D4291380B8ED06A6BF4B1759A76364E25FC0`

| Campo | Valor |
|-------|-------|
| Repositorio | `jgutierrezdtt/template-secure-coding-web-api` |
| Completado por | `jgutierrezdtt` |
| Pasos verificados | 10 de 10 |
| Fecha | 2026-05-16 19:30 UTC |
| Run ID | `25970880871` |

---

## Que garantiza este token

- Los 10 validators ejecutaron en GitHub Actions y todos retornaron exit 0.
- El token esta vinculado a este repositorio (`jgutierrezdtt/template-secure-coding-web-api`) y a este usuario (`jgutierrezdtt`).
- No puede generarse sin que todos los archivos modificados en cada paso contengan los marcadores correctos verificados por los scripts de validacion.
- Cada fork del repositorio produce un token distinto porque el campo `repo` es parte del payload firmado.

---

## Como verificar este token

El token es SHA-256 del payload canonico. Puedes verificarlo localmente:

```python
import hashlib, json

payload = json.dumps(
    {
        "repo": "jgutierrezdtt/template-secure-coding-web-api",
        "actor": "jgutierrezdtt",
        "completed_steps": ["validate-step-01", "validate-step-02", "validate-step-03", "validate-step-04", "validate-step-05", "validate-step-06", "validate-step-07", "validate-step-08", "validate-step-09", "validate-step-10"],
        "total": 10,
    },
    sort_keys=True,
    separators=(",", ":"),
).encode()

token = hashlib.sha256(payload).hexdigest()[:40].upper()
print(token)  # debe coincidir con el token de arriba
```

Si el token coincide, la completacion es autentica para este repositorio y usuario.
Si configuraste `COMPLETION_SECRET` en el repositorio, el token usa HMAC-SHA256
con esa clave — en ese caso la verificacion requiere conocer el secreto.
