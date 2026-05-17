#!/usr/bin/env python3
"""
Actualiza el README del tutorial de forma progresiva y genera la medalla.

- En progreso: reconstruye el README mostrando los pasos ya completados de forma
  resumida y las instrucciones completas del siguiente paso pendiente.
- Completado: reemplaza el README entero con una pagina de certificado visual.
- Siempre escribe docs/MEDALLA.md cuando todos pasan.
"""

import glob
import os
import subprocess
import sys
from datetime import datetime, timezone


STEP_FILES = {
    "validate-step-01": "`src/routes/users.js`",
    "validate-step-02": "`src/routes/search.js`",
    "validate-step-03": "`src/routes/auth.js`",
    "validate-step-04": "`src/routes/graphql.js`",
    "validate-step-05": "`src/routes/comments.js` y `src/middleware/security-headers.js`",
    "validate-step-06": "`src/routes/proxy.js`",
    "validate-step-07": "`src/middleware/auth.js`",
    "validate-step-08": "`src/routes/orders.js` y `src/routes/admin.js`",
    "validate-step-09": "`src/routes/profile.js`",
    "validate-step-10": "`docs/secure-coding-checklist.md`",
}

STEP_TOPICS = {
    "validate-step-01": "SQL injection basica",
    "validate-step-02": "SQL injection avanzada",
    "validate-step-03": "NoSQL injection (MongoDB)",
    "validate-step-04": "GraphQL security",
    "validate-step-05": "XSS y Content Security Policy",
    "validate-step-06": "SSRF",
    "validate-step-07": "JWT y autenticacion en APIs",
    "validate-step-08": "Autorizacion: BOLA e IDOR",
    "validate-step-09": "Mass assignment y exposicion de datos",
    "validate-step-10": "Checklist final",
}

STEP_COMPLETED_SUMMARY = {
    "validate-step-01": (
        "`src/routes/users.js` actualizado con consulta parametrizada usando `$1` y `db.query`."
    ),
    "validate-step-02": (
        "`src/routes/search.js` actualizado con parametro `$1`, patron `SAFE_` y validacion con `test()`."
    ),
    "validate-step-03": (
        "`src/routes/auth.js` actualizado con `typeof` para validacion de tipos y `bcrypt.compare`."
    ),
    "validate-step-04": (
        "`src/routes/graphql.js` actualizado con `introspection:`, `depthLimit` y parametros `$1`."
    ),
    "validate-step-05": (
        "`src/routes/comments.js` con `DOMPurify` y `src/middleware/security-headers.js` "
        "con `Content-Security-Policy` y `X-Content-Type-Options`."
    ),
    "validate-step-06": (
        "`src/routes/proxy.js` actualizado con `PRIVATE_RANGES`, validacion de `protocol` y `redirect`."
    ),
    "validate-step-07": (
        "`src/middleware/auth.js` actualizado con `algorithms:`, `process.env.JWT_SECRET` e `issuer`."
    ),
    "validate-step-08": (
        "`src/routes/orders.js` con `user_id` y `src/routes/admin.js` con `requireAdmin`."
    ),
    "validate-step-09": (
        "`src/routes/profile.js` actualizado con `ALLOWED_UPDATE_FIELDS` y `sanitizeUser`."
    ),
    "validate-step-10": (
        "`docs/secure-coding-checklist.md` completado con los cuatro frentes de seguridad."
    ),
}

STEP_CONTENT = {}

STEP_CONTENT["validate-step-01"] = """
### Por que importa esto

La SQL injection basica es la vulnerabilidad mas documentada de la historia y sigue
apareciendo en produccion. Un parametro de usuario concatenado directamente en una
consulta SQL permite a un atacante leer cualquier tabla, modificar datos o borrar la
base de datos entera.

### Que debes cambiar

**Archivo:** `src/routes/users.js`

La ruta busca usuarios construyendo la consulta con concatenacion de strings.

Antes (vulnerable):

```javascript
// VULNERABLE: SQL injection directa
const query = "SELECT * FROM users WHERE id = " + req.params.id;
const result = await db.query(query);
```

Despues (seguro):

```javascript
// SEGURO: consulta parametrizada
const result = await db.query(
  "SELECT id, username, email FROM users WHERE id = $1",
  [req.params.id]
);
```

La clave es separar el codigo SQL de los datos. El driver de la base de datos
trata `$1` como un literal, nunca como SQL ejecutable.

### Que valida el workflow

`scripts/validate-step-01.py` busca en `src/routes/users.js`:
- `$1`
- `db.query`
"""

STEP_CONTENT["validate-step-02"] = """
### Por que importa esto

La SQL injection avanzada (blind/boolean-based) funciona aunque la aplicacion no
muestre errores ni datos directamente. Un atacante puede extraer cualquier dato de
la base de datos haciendo preguntas binarias (verdadero/falso) y observando si la
respuesta cambia.

### Que debes cambiar

**Archivo:** `src/routes/search.js`

La ruta de busqueda permite inyectar SQL a traves de los parametros de busqueda
sin validacion ni parametrizacion.

Despues (seguro):

```javascript
// SEGURO: parametrizacion + validacion de tipo de entrada
const SAFE_FIELD_PATTERN = /^[a-zA-Z0-9_]+$/;

if (!SAFE_FIELD_PATTERN.test(req.query.field)) {
  return res.status(400).json({ error: "Campo invalido" });
}

const results = await db.query(
  "SELECT * FROM products WHERE $1 ILIKE $2",
  [safeField, "%" + req.query.q + "%"]
);
```

### Que valida el workflow

`scripts/validate-step-02.py` busca en `src/routes/search.js`:
- `$1`
- `SAFE_` (constante de validacion)
- `test(` (validacion con regex)
"""

STEP_CONTENT["validate-step-03"] = """
### Por que importa esto

MongoDB y otros motores NoSQL no usan SQL, pero son vulnerables a injection a traves
de los operadores del motor. Un objeto `{ "$gt": "" }` como valor de contrasena hace
que la consulta sea siempre verdadera, permitiendo autenticarse sin contrasena.

### Que debes cambiar

**Archivo:** `src/routes/auth.js`

La ruta de login pasa directamente el body de la peticion a MongoDB sin validar
que los valores sean del tipo esperado.

Antes (vulnerable):

```javascript
// VULNERABLE: permite { "$gt": "" } como password
const user = await User.findOne({
  username: req.body.username,
  password: req.body.password
});
```

Despues (seguro):

```javascript
// SEGURO: validacion de tipos + comparacion con bcrypt
if (typeof req.body.username !== "string" || typeof req.body.password !== "string") {
  return res.status(400).json({ error: "Formato invalido" });
}

const user = await User.findOne({ username: req.body.username });
if (!user || !await bcrypt.compare(req.body.password, user.passwordHash)) {
  return res.status(401).json({ error: "Credenciales incorrectas" });
}
```

### Que valida el workflow

`scripts/validate-step-03.py` busca en `src/routes/auth.js`:
- `typeof`
- `bcrypt.compare`
"""

STEP_CONTENT["validate-step-04"] = """
### Por que importa esto

GraphQL expone toda la estructura del schema mediante introspection por defecto, lo
que da a un atacante un mapa completo de la API. Ademas, las queries anidadas sin
limite de profundidad permiten ataques de denegacion de servicio con una sola peticion.

### Que debes cambiar

**Archivo:** `src/routes/graphql.js`

La configuracion de GraphQL tiene introspection habilitada en produccion y no limita
la profundidad de las queries.

Despues (seguro):

```javascript
const { createComplexityLimitRule } = require("graphql-validation-complexity");
const depthLimit = require("graphql-depth-limit");

const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== "production",
  validationRules: [
    depthLimit(5),
    createComplexityLimitRule(1000)
  ],
  // Usar parametros $1 en queries SQL dentro de resolvers
});
```

### Que valida el workflow

`scripts/validate-step-04.py` busca en `src/routes/graphql.js`:
- `introspection:`
- `depthLimit`
- `$1`
"""

STEP_CONTENT["validate-step-05"] = """
### Por que importa esto

XSS (Cross-Site Scripting) permite ejecutar JavaScript en el navegador de otros
usuarios. Sin las cabeceras de seguridad correctas, un atacante puede inyectar un
script que roba sesiones, redirige a phishing o modifica el contenido de la pagina.

### Que debes cambiar

**Archivo 1:** `src/routes/comments.js`

Los comentarios se renderizan sin sanitizar, permitiendo inyectar HTML/JS.

```javascript
// SEGURO: sanitizar con DOMPurify antes de guardar o renderizar
const DOMPurify = require("dompurify");
const clean = DOMPurify.sanitize(req.body.content);
await Comment.create({ content: clean, userId: req.user.id });
```

**Archivo 2:** `src/middleware/security-headers.js`

Aniade las cabeceras de seguridad:

```javascript
// SEGURO: cabeceras que mitigan XSS y sniffing
res.setHeader("Content-Security-Policy",
  "default-src \'self\'; script-src \'self\'"
);
res.setHeader("X-Content-Type-Options", "nosniff");
res.setHeader("X-Frame-Options", "DENY");
```

### Que valida el workflow

`scripts/validate-step-05.py` busca:
- `DOMPurify` en `src/routes/comments.js`
- `Content-Security-Policy` y `X-Content-Type-Options` en `src/middleware/security-headers.js`
"""

STEP_CONTENT["validate-step-06"] = """
### Por que importa esto

SSRF (Server-Side Request Forgery) permite usar tu servidor como proxy para acceder a
recursos internos: metadatos de instancias cloud (AWS IMDS en `169.254.169.254`),
servicios internos sin autenticacion, y redes privadas inaccesibles desde internet.

### Que debes cambiar

**Archivo:** `src/routes/proxy.js`

La ruta acepta una URL del usuario y hace la peticion desde el servidor sin validar
a que IP/host se esta conectando.

```javascript
// SEGURO: bloquear rangos privados y validar protocolo
const PRIVATE_RANGES = [
  /^127\./,
  /^10\./,
  /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
  /^192\.168\./,
  /^169\.254\./,     // AWS IMDS
  /^::1$/,            // IPv6 loopback
];

const parsed = new URL(url);
if (parsed.protocol !== "https:") {
  return res.status(400).json({ error: "Solo se permite HTTPS" });
}

// Bloquear redirect a rangos privados
const response = await fetch(url, { redirect: "manual" });
```

### Que valida el workflow

`scripts/validate-step-06.py` busca en `src/routes/proxy.js`:
- `PRIVATE_RANGES`
- `protocol`
- `redirect`
"""

STEP_CONTENT["validate-step-07"] = """
### Por que importa esto

Los JWTs pueden ser vulnerables de varias formas: el algoritmo `none` permite crear
tokens sin firma, usar HS256 con una clave debil permite ataques de fuerza bruta, y
no verificar el `issuer` permite que tokens de otro servicio sean aceptados.

### Que debes cambiar

**Archivo:** `src/middleware/auth.js`

El middleware verifica el JWT sin especificar el algoritmo esperado y sin verificar
el emisor.

Antes (vulnerable):

```javascript
// VULNERABLE: no fija el algoritmo, acepta "none"
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

Despues (seguro):

```javascript
// SEGURO: algoritmo fijado, issuer verificado
const decoded = jwt.verify(token, process.env.JWT_SECRET, {
  algorithms: ["HS256"],
  issuer: "my-api",
});
```

### Que valida el workflow

`scripts/validate-step-07.py` busca en `src/middleware/auth.js`:
- `algorithms:`
- `process.env.JWT_SECRET`
- `issuer`
"""

STEP_CONTENT["validate-step-08"] = """
### Por que importa esto

BOLA (Broken Object Level Authorization) e IDOR son la categoria de vulnerabilidad
mas frecuente en APIs segun OWASP API Top 10. Un usuario autenticado puede acceder
o modificar datos de otros usuarios simplemente cambiando el ID en la peticion.

### Que debes cambiar

**Archivo 1:** `src/routes/orders.js`

La ruta devuelve un pedido por ID sin verificar que pertenece al usuario actual.

```javascript
// SEGURO: filtrar por user_id del token, no confiar en el parametro
const order = await Order.findOne({
  id: req.params.id,
  user_id: req.user.id   // solo puede ver sus propios pedidos
});
```

**Archivo 2:** `src/routes/admin.js`

Las rutas de administracion no verifican que el usuario tenga el rol correcto.

```javascript
// SEGURO: middleware de autorizacion por rol
function requireAdmin(req, res, next) {
  if (!req.user || req.user.role !== "admin") {
    return res.status(403).json({ error: "Acceso denegado" });
  }
  next();
}

router.get("/users", requireAdmin, async (req, res) => { ... });
```

### Que valida el workflow

`scripts/validate-step-08.py` busca:
- `user_id` en `src/routes/orders.js`
- `requireAdmin` en `src/routes/admin.js`
"""

STEP_CONTENT["validate-step-09"] = """
### Por que importa esto

Mass assignment ocurre cuando una API acepta todos los campos de un objeto sin
filtrar. Un usuario puede enviar `{ "role": "admin" }` junto con su peticion de
actualizacion de perfil y escalar privilegios. La exposicion excesiva de datos
ocurre cuando la API devuelve campos que el cliente no deberia ver.

### Que debes cambiar

**Archivo:** `src/routes/profile.js`

La ruta de actualizacion pasa el body directamente al modelo de datos.

Antes (vulnerable):

```javascript
// VULNERABLE: el usuario puede actualizar cualquier campo
await User.update(req.user.id, req.body);
```

Despues (seguro):

```javascript
// SEGURO: lista blanca de campos actualizables
const ALLOWED_UPDATE_FIELDS = ["displayName", "bio", "avatarUrl"];

const update = {};
for (const field of ALLOWED_UPDATE_FIELDS) {
  if (req.body[field] !== undefined) {
    update[field] = req.body[field];
  }
}

await User.update(req.user.id, update);

// SEGURO: no exponer campos internos en la respuesta
function sanitizeUser(user) {
  const { passwordHash, role, internalFlags, ...safe } = user;
  return safe;
}
```

### Que valida el workflow

`scripts/validate-step-09.py` busca en `src/routes/profile.js`:
- `ALLOWED_UPDATE_FIELDS`
- `sanitizeUser`
"""

STEP_CONTENT["validate-step-10"] = """
### Por que importa esto

La seguridad en APIs no es un conjunto de medidas independientes: cada control
refuerza a los demas. Este checklist es tu referencia para auditorias, code reviews
y nuevos proyectos.

### Que debes cambiar

**Archivo:** `docs/secure-coding-checklist.md`

Completa el archivo con los cuatro frentes de seguridad:

```markdown
# Checklist de seguridad -- Web y API

## Frente 1: Inyeccion y validacion de entrada

- [ ] Consultas SQL parametrizadas en todas las rutas
- [ ] Validacion de tipo y formato antes de consultas NoSQL
- [ ] Regex de validacion para campos que van a consultas dinamicas
- [ ] Profundidad maxima en queries GraphQL
- [ ] Introspection desactivada en produccion

## Frente 2: Autenticacion y sesion

- [ ] JWT verificado con algoritmo fijo (no "none")
- [ ] JWT_SECRET desde variable de entorno, no hardcodeado
- [ ] Issuer verificado en tokens
- [ ] Comparacion de contrasenas con bcrypt.compare

## Frente 3: Autorizacion

- [ ] Todas las rutas verifican que el recurso pertenece al usuario actual
- [ ] Rutas de admin protegidas con middleware de rol
- [ ] Lista blanca de campos en todas las actualizaciones (no req.body directo)
- [ ] Respuestas que no exponen campos internos (passwordHash, role)

## Frente 4: Proteccion del navegador y red

- [ ] DOMPurify o equivalente en todo contenido renderizado
- [ ] Content-Security-Policy configurada
- [ ] X-Content-Type-Options: nosniff
- [ ] Validacion de rangos privados en funcionalidades de proxy/fetch externo
- [ ] Solo HTTPS en URLs externas aceptadas del usuario
```

### Que valida el workflow

`scripts/validate-step-10.py` busca en `docs/secure-coding-checklist.md`:
- `Frente 1`, `Frente 2`, `Frente 3`, `Frente 4`
"""


# ---------------------------------------------------------------------------
# Ejecucion de validators
# ---------------------------------------------------------------------------

def run_validators(repo_root):
    scripts_dir = os.path.join(repo_root, "scripts")
    validator_files = sorted(glob.glob(os.path.join(scripts_dir, "validate-step-*.py")))

    if not validator_files:
        print("[FAIL] No se encontraron scripts de validacion en scripts/validate-step-*.py")
        sys.exit(1)

    results = {}
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
        print("PASS" if ok else "FAIL")
        if proc.stdout.strip():
            for line in proc.stdout.strip().splitlines():
                print(f"        {line}")
        if proc.stderr.strip():
            for line in proc.stderr.strip().splitlines():
                print(f"        {line}")

    return results


# ---------------------------------------------------------------------------
# README: modo progresivo (reconstruye entero segun pasos completados)
# ---------------------------------------------------------------------------

def update_readme_progress(repo_root, results):
    passed = sorted([s for s, ok in results.items() if ok])
    pending = sorted([s for s, ok in results.items() if not ok])
    passed_count = len(passed)
    total = len(results)

    lines = []
    lines.append("# Secure Coding Web y API\n")
    lines.append("\n")
    lines.append(
        "Tutorial practico de seguridad para aplicaciones web y APIs REST/GraphQL.\n"
        "Completa los pasos en orden: cada push activa el validador automatico\n"
        "y el README se actualiza con el siguiente paso.\n"
    )
    lines.append("\n")
    lines.append("---\n")
    lines.append("\n")
    lines.append("## Tabla de pasos (resumen de progreso)\n")
    lines.append("\n")
    lines.append(f"**{passed_count}/{total} pasos completados**\n")
    lines.append("\n")
    lines.append("| Paso | Archivo a modificar | Estado |\n")
    lines.append("|------|---------------------|--------|\n")
    lines.append("| Paso 0 | Introduccion -- lee primero | Empezar aqui |\n")
    for step, file_ref in STEP_FILES.items():
        num = int(step.replace("validate-step-", ""))
        estado = "Completado" if results.get(step, False) else "Pendiente"
        lines.append(f"| Paso {num:02d} | {file_ref} | {estado} |\n")

    for step in passed:
        num = int(step.replace("validate-step-", ""))
        topic = STEP_TOPICS[step]
        summary = STEP_COMPLETED_SUMMARY[step]
        lines.append("\n")
        lines.append("---\n")
        lines.append("\n")
        lines.append(f"## Paso {num:02d}. {topic} -- Completado\n")
        lines.append("\n")
        lines.append(f"{summary}\n")

    if pending:
        current = pending[0]
        num = int(current.replace("validate-step-", ""))
        topic = STEP_TOPICS[current]
        content = STEP_CONTENT[current]
        lines.append("\n")
        lines.append("---\n")
        lines.append("\n")
        lines.append("## Empezar tutorial\n")
        lines.append("\n")
        lines.append(
            "Haz un commit con los cambios del paso actual para que el workflow "
            "automatico valide tu progreso y actualice este README.\n"
        )
        lines.append("\n")
        lines.append("---\n")
        lines.append("\n")
        lines.append(f"## Paso {num:02d}. {topic}\n")
        lines.append(content)

    upcoming = pending[1:] if len(pending) > 1 else []
    if upcoming:
        lines.append("\n")
        lines.append("---\n")
        lines.append("\n")
        lines.append("## Proximos pasos\n")
        lines.append("\n")
        lines.append("| Paso | Tema |\n")
        lines.append("|------|------|\n")
        for step in upcoming:
            num = int(step.replace("validate-step-", ""))
            lines.append(f"| {num:02d} | {STEP_TOPICS[step]} |\n")

    readme_path = os.path.join(repo_root, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"[OK] README actualizado: {passed_count}/{total} pasos completados")


# ---------------------------------------------------------------------------
# README: pagina de certificado cuando todos pasan
# ---------------------------------------------------------------------------

def write_readme_completed(repo_root, actor, repo, run_id, sha, results):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    commit_url = f"https://github.com/{repo}/commit/{sha}"
    total = len(results)

    step_rows = ""
    for step, topic in STEP_TOPICS.items():
        num = int(step.replace("validate-step-", ""))
        step_rows += f"| {num:02d} | {topic} | PASS |\n"

    content = f"""# Secure Coding Web y API -- Completado

> Repositorio de **{actor}**

---

## Certificado de finalizacion

Este repositorio ha superado los {total} controles de seguridad del tutorial
**Secure Coding Web y API**.

| | |
|---|---|
| **Alumno** | {actor} |
| **Repositorio** | [{repo}](https://github.com/{repo}) |
| **Fecha** | {now} |
| **Pasos** | {total}/{total} |
| **Medalla** | [docs/MEDALLA.md](docs/MEDALLA.md) |

---

## Controles de seguridad implementados

| Paso | Control implementado | Resultado |
|------|----------------------|-----------|
{step_rows}
---

## Prueba de integridad

La medalla fue generada automaticamente por `github-actions[bot]` cuando los
{total} validators pasaron. La prueba es publica y permanente:

- **Run:** {run_url}
- **Commit:** {commit_url}
- **SHA:** `{sha}`

Cualquier persona puede abrir el run y verificar que todos los validators
retornaron PASS en ese commit exacto.

---

## Que has aprendido

- SQL injection: parametrizacion y consultas preparadas
- NoSQL injection: validacion de tipos antes de consultas
- GraphQL: introspection, depth limits y parametrizacion
- XSS: sanitizacion de HTML y cabeceras Content-Security-Policy
- SSRF: validacion de rangos IP y protocolos
- JWT: algoritmos fijos, issuer y secretos desde variables de entorno
- BOLA/IDOR: autorizacion a nivel de objeto y middleware de rol
- Mass assignment: listas blancas de campos y sanitizacion de respuestas

---

_Generado por github-actions[bot] -- [{repo}](https://github.com/{repo})_
"""

    readme_path = os.path.join(repo_root, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("[OK] README reemplazado con pagina de certificado")


# ---------------------------------------------------------------------------
# Escritura de la medalla
# ---------------------------------------------------------------------------

def write_medal(repo_root, repo, actor, run_id, sha, completed_steps):
    total = len(completed_steps)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    commit_url = f"https://github.com/{repo}/commit/{sha}"
    rows = "\n".join(f"| {s} | PASS |" for s in sorted(completed_steps))

    content = f"""# Medalla de finalizacion -- Secure Coding Web y API

| | |
|---|---|
| **Alumno** | {actor} |
| **Repositorio** | {repo} |
| **Fecha** | {now} |
| **Pasos completados** | {total}/{total} |

## Prueba de integridad

- **Run:** [{run_url}]({run_url})
- **Commit:** [{sha[:7]}]({commit_url})

La medalla fue generada automaticamente por `github-actions[bot]` cuando los {total}
validators pasaron en el run indicado. El run es publico e inmutable.

## Pasos completados

| Paso | Estado |
|------|--------|
{rows}

---
_Generado por github-actions[bot] -- no editar manualmente._
"""

    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    medal_path = os.path.join(docs_dir, "MEDALLA.md")
    with open(medal_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Medalla escrita en {medal_path}")
    print(f"[OK] Prueba de integridad: {run_url}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    actor = os.environ.get("GITHUB_ACTOR", "desconocido")
    repo = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "0")
    sha = os.environ.get("GITHUB_SHA", "0000000")

    print("=== Ejecutando validators ===")
    results = run_validators(repo_root)

    passed = [s for s, ok in results.items() if ok]
    failed = [s for s, ok in results.items() if not ok]

    print(f"\n=== Resultado: {len(passed)}/{len(results)} pasos completados ===\n")

    if failed:
        print(f"[INFO] {len(failed)} pasos pendientes:")
        for s in sorted(failed):
            print(f"  - {s}")
        update_readme_progress(repo_root, results)
    else:
        print("[OK] Todos los validators pasaron. Generando certificado...")
        write_medal(repo_root, repo, actor, run_id, sha, passed)
        write_readme_completed(repo_root, actor, repo, run_id, sha, results)


if __name__ == "__main__":
    main()
