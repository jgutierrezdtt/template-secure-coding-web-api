# Paso 7. Autenticacion en APIs — JWT, tokens y sesiones

## Objetivo de aprendizaje

Entender los errores mas comunes en la implementacion de autenticacion con JWT y tokens de sesion, por que algunos de esos errores permiten a un atacante falsificar su identidad, y como implementar correctamente la verificacion de tokens.

## Por que importa esto

JWT (JSON Web Token) se usa ampliamente para autenticacion en APIs. El problema no es el estandar en si: es que muchas implementaciones cometen errores que permiten a un atacante fabricar tokens validos sin conocer el secreto.

El error mas grave es aceptar el algoritmo `none` en el JWT. El estandar permite que el campo `alg` del header tenga el valor `none`, lo que significa que el token no tiene firma. Si el servidor acepta eso, cualquier atacante puede crear un token con el `userId` que quiera, simplemente sin firmarlo. El servidor lo acepta porque no hay firma que verificar.

El segundo error frecuente es usar una clave secreta debil o predecible (como `"secret"`, `"password"`, o el nombre del proyecto). Los ataques de fuerza bruta contra JWTs son practicos si la clave es corta.

El tercer error es no verificar claims estandar como `exp` (expiracion) o `iss` (emisor), lo que puede permitir usar tokens caducados o tokens emitidos por otros servicios.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/middleware/auth.js`. El middleware que verifica JWTs acepta el algoritmo que venga en el header del token en lugar de exigir un algoritmo especifico, no verifica la expiracion, y la clave secreta esta hardcodeada con un valor predecible.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/middleware/auth.js`
- Funcion: middleware de verificacion de JWT
- La clave secreta esta en el mismo archivo o en un archivo de configuracion sin gestionar secretos

## Cambio base recomendado

Antes (vulnerable):

```js
// VULNERABLE: acepta cualquier algoritmo, incluyendo "none"
const decoded = jwt.verify(token, process.env.JWT_SECRET || "secret");
```

Despues (seguro):

```js
// SEGURO: forzar algoritmo especifico, verificar claims, usar secreto de entorno
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) {
  throw new Error("JWT_SECRET environment variable is required");
}

try {
  const decoded = jwt.verify(token, JWT_SECRET, {
    algorithms: ["HS256"],   // Lista blanca de algoritmos — nunca "none"
    issuer: "my-api",        // Verificar que el token fue emitido por este servicio
    audience: "my-api-users" // Verificar la audiencia
  });
  req.user = decoded;
  next();
} catch (err) {
  return res.status(401).json({ error: "Invalid or expired token" });
}
```

## Que te esta enseñando este cambio

- La opcion `algorithms: ["HS256"]` en `jwt.verify` es la defensa critica contra el ataque del algoritmo `none`. Sin esa restriccion, la libreria acepta lo que venga en el header del token. Con ella, rechaza cualquier token cuyo algoritmo no este en la lista blanca.
- El JWT_SECRET en el codigo fuente es un secreto comprometido desde el primer commit. Cualquier persona que tenga acceso al repositorio (presente o futuro) lo conoce. Los secretos deben vivir en variables de entorno o en un gestor de secretos, nunca en codigo.
- Verificar `issuer` y `audience` es una defensa de defensa en profundidad: impide que un token emitido por otro servicio de la misma organizacion (que puede usar el mismo algoritmo pero diferente secreto o contexto) sea aceptado como valido en este servicio.
- El tiempo de expiracion `exp` lo verifica la libreria automaticamente cuando se usa `jwt.verify`. No uses `jwt.decode` (que no verifica firma ni claims) donde deberia usarse `jwt.verify`.

## Como adaptarlo correctamente

- Para APIs publicas, considera usar RS256 (clave asimetrica) en lugar de HS256: la clave privada se guarda en el servidor que emite tokens, y la clave publica es suficiente para verificar. Eso permite que multiples servicios verifiquen tokens sin compartir un secreto.
- Implementa revocacion de tokens para casos criticos (logout, cambio de contraseña, compromiso de cuenta). JWT por diseno es stateless y no tiene revocacion nativa: necesitas una lista negra de tokens revocados o usar tokens de corta duracion con refresh tokens.
- Audita el tiempo de vida de los tokens. Tokens con expiracion de dias o semanas son un riesgo si son robados. Tokens de una hora o menos con refresh tokens son la practica recomendada.
- No almacenes tokens de sesion en localStorage en el frontend: son accesibles por JavaScript y vulnerables a XSS. Usa cookies HttpOnly que el navegador gestiona y protege.

## Que deberia verse al terminar

- `jwt.verify` usa la opcion `algorithms` con una lista blanca que excluye `none`.
- El secreto viene exclusivamente de `process.env.JWT_SECRET`, con fallo explicito si no existe.
- Se verifican al menos `issuer` o `audience` como claims adicionales.

## Que valida el workflow automaticamente

- `scripts/validate-step-07.py` comprueba que `src/middleware/auth.js` contiene los controles.
- El validador busca el uso de `algorithms:` en la llamada a `jwt.verify`.
- El validador verifica que el secreto se carga de `process.env` sin valor por defecto hardcodeado.
- El validador busca verificacion de al menos un claim adicional (issuer o audience).

## Criterio de finalizacion

El paso 7 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
