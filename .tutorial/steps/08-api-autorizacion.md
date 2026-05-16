# Paso 8. Autorizacion en APIs — BOLA, IDOR y BFLA

## Objetivo de aprendizaje

Entender la diferencia entre autenticacion y autorizacion, que son BOLA e IDOR, por que son las vulnerabilidades mas frecuentes en APIs segun OWASP, y como implementar controles de autorizacion correctos a nivel de objeto y funcion.

## Por que importa esto

Autenticacion responde a la pregunta: quien eres? Autorizacion responde a: tienes permiso para hacer esto?

Una API puede verificar correctamente la identidad del usuario (autenticacion bien implementada) pero aun asi permitir que ese usuario acceda a datos o funciones que no le corresponden (autorizacion ausente o incorrecta).

BOLA (Broken Object Level Authorization), tambien conocido como IDOR (Insecure Direct Object Reference), ocurre cuando una ruta usa un identificador de objeto en la URL (como `/orders/12345`) pero no verifica que el usuario autenticado sea el propietario de ese objeto. Si el usuario `A` puede acceder a `/orders/12345` y ese pedido pertenece al usuario `B`, hay BOLA.

BFLA (Broken Function Level Authorization) ocurre cuando endpoints administrativos o de funciones privilegiadas no verifican si el usuario tiene el rol correcto, mas alla de estar autenticado.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/orders.js` (BOLA) y `src/routes/admin.js` (BFLA). La ruta de pedidos devuelve cualquier pedido por ID sin verificar que pertenezca al usuario autenticado. La ruta de administracion verifica que el usuario esta autenticado pero no verifica que tenga rol de administrador.

## Archivo y seccion que debes modificar

- Archivo objetivo 1: `src/routes/orders.js` — ruta `GET /orders/:id`
- Archivo objetivo 2: `src/routes/admin.js` — rutas de administracion

## Cambio base recomendado

Corregir BOLA en orders.js:

```js
// VULNERABLE: devuelve cualquier pedido sin verificar propietario
// const order = await db.query("SELECT * FROM orders WHERE id = $1", [req.params.id]);

// SEGURO: la query incluye el userId del token para verificar propiedad
const order = await db.query(
  "SELECT * FROM orders WHERE id = $1 AND user_id = $2",
  [req.params.id, req.user.id]  // req.user viene del middleware de autenticacion
);

if (order.rows.length === 0) {
  return res.status(404).json({ error: "Order not found" });
  // No revelar si existe pero no pertenece al usuario: 404 en ambos casos
}
```

Corregir BFLA en admin.js:

```js
// Middleware especifico para rutas administrativas
function requireAdmin(req, res, next) {
  if (!req.user || req.user.role !== "admin") {
    return res.status(403).json({ error: "Forbidden" });
  }
  next();
}

// SEGURO: todas las rutas administrativas usan requireAdmin despues de requireAuth
router.get("/admin/users", requireAuth, requireAdmin, listUsers);
router.delete("/admin/users/:id", requireAuth, requireAdmin, deleteUser);
```

## Que te esta enseñando este cambio

- La defensa contra BOLA no es ocultar los IDs (usar UUIDs en lugar de numeros secuenciales no es una defensa: el atacante puede descubrirlos). La defensa es siempre incluir el `user_id` del usuario autenticado como condicion de la query. Si el objeto no pertenece al usuario, la query devuelve cero resultados.
- Responder con `404 Not Found` en lugar de `403 Forbidden` cuando el objeto existe pero no pertenece al usuario es una practica de seguridad deliberada: evita confirmar al atacante que el objeto con ese ID existe.
- BFLA ocurre con frecuencia cuando los endpoints administrativos se crean "solo para uso interno" y se añaden al final del desarrollo sin pasar por el mismo proceso de revision de seguridad. Un endpoint que no tiene enlace en el frontend no es un endpoint privado: es un endpoint sin proteccion.
- La separacion entre `requireAuth` (estas autenticado) y `requireAdmin` (tienes rol de admin) es una decision de diseno importante: permite aplicar el control en capas y mantener cada middleware con una responsabilidad clara y testable.

## Como adaptarlo correctamente

- Audita sistematicamente todas las rutas que usan identificadores de objeto en la URL o en el cuerpo de la peticion y verifica que cada una incluye la comprobacion de propiedad.
- Para sistemas con roles mas complejos (admin, moderador, usuario premium), considera usar un modelo RBAC (Role-Based Access Control) centralizado en lugar de condiciones if/else dispersas en cada ruta.
- Los tests de autorizacion deben ser parte obligatoria de la suite de tests. Verifica que el usuario A no puede acceder a los recursos del usuario B, no solo que el usuario A puede acceder a los suyos.
- Herramientas como OWASP ZAP pueden hacer fuzzing automatico de IDOR cambiando sistematicamente los IDs en las respuestas de la API.

## Que deberia verse al terminar

- La query de pedidos incluye `user_id = $2` con el ID del usuario autenticado.
- Existe un middleware `requireAdmin` separado que verifica el rol.
- Las rutas de administracion tienen `requireAdmin` en la cadena de middleware.

## Que valida el workflow automaticamente

- `scripts/validate-step-08.py` comprueba ambos archivos.
- El validador busca la condicion de `user_id` en la query de orders.
- El validador busca la definicion de `requireAdmin` o equivalente.
- El validador verifica que las rutas admin aplican el middleware de rol.

## Criterio de finalizacion

El paso 8 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
