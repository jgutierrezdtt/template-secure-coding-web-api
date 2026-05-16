# Paso 3. Inyeccion NoSQL — operadores de MongoDB

## Objetivo de aprendizaje

Entender que las bases de datos NoSQL como MongoDB tienen su propio tipo de inyeccion, que los mecanismos de defensa son distintos a los de SQL, y como un atacante puede usar operadores de MongoDB para eludir la autenticacion o extraer datos.

## Por que importa esto

Muchos desarrolladores que migraron de bases de datos relacionales a MongoDB piensan que al no usar SQL ya no existe el riesgo de inyeccion. Ese supuesto es incorrecto y ha causado numerosas brechas de seguridad.

MongoDB acepta objetos JSON como condiciones de consulta. Si tu aplicacion toma un valor del usuario y lo inserta directamente como condicion de busqueda sin validar su tipo, el usuario puede enviar un objeto JSON en lugar de un string simple. Ese objeto puede contener operadores de MongoDB como `$ne`, `$gt` o `$where` que cambian completamente el comportamiento de la consulta.

El caso mas critico es el login: si la condicion de autenticacion acepta un objeto con `$ne: null` en lugar de la contraseña real, MongoDB devuelve el primer usuario cuya contraseña sea distinta de null, lo que significa cualquier usuario. El atacante puede autenticarse sin conocer ninguna contraseña.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/auth.js`. La ruta de login toma `username` y `password` del cuerpo de la peticion y los pasa directamente a la query de MongoDB. No valida que sean strings, lo que permite enviar objetos con operadores.

El cambio requiere validar el tipo de los campos de entrada antes de usarlos en la consulta y, en el caso de la contraseña, usar un proceso de comparacion que no pase el valor plano a la query.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/auth.js`
- Funcion: handler de la ruta `POST /login`
- Busca donde se construye el objeto de query de MongoDB con los campos de entrada

## Cambio base recomendado

Antes (vulnerable):

```js
// VULNERABLE: si password es { $ne: null }, MongoDB devuelve el primer usuario
const user = await User.findOne({
  username: req.body.username,
  password: req.body.password
});
```

Despues (seguro):

```js
// SEGURO: validar tipo antes de usar en query + comparar hash fuera de la query
if (typeof req.body.username !== "string" || typeof req.body.password !== "string") {
  return res.status(400).json({ error: "Invalid input type" });
}

// Buscar solo por username (campo no sensible), comparar password con bcrypt
const user = await User.findOne({ username: req.body.username });
if (!user || !await bcrypt.compare(req.body.password, user.passwordHash)) {
  return res.status(401).json({ error: "Invalid credentials" });
}
```

Por que funciona: al validar que el valor es un string, se descarta cualquier objeto JSON que contenga operadores. Al separar la busqueda del usuario de la verificacion de la contraseña, se elimina el riesgo de que la query de MongoDB evalue la contraseña como condicion.

## Que te esta enseñando este cambio

- Las bases de datos NoSQL no son inmunes a inyeccion: tienen su propio modelo de ataque. El problema raiz es el mismo que en SQL: mezclar datos del usuario con la logica de la consulta sin validar el tipo o la estructura de esos datos.
- Validar que el tipo de entrada es el esperado (`typeof x === "string"`) es la defensa mas simple y directa contra la inyeccion de operadores en MongoDB. No requiere librerias adicionales.
- Almacenar contraseñas como hash (bcrypt, argon2) y compararlas fuera de la query de base de datos es la practica correcta independientemente de la inyeccion: protege tambien contra filtraciones de base de datos.
- El operador `$where` de MongoDB permite ejecutar JavaScript arbitrario en el servidor de base de datos. Es especialmente peligroso y deberia estar deshabilitado en produccion (`--noscripting`) si no se usa explicitamente.

## Como adaptarlo correctamente

- Usa validacion de esquema (Joi, Zod, express-validator) para verificar el tipo y formato de todos los campos de entrada en cada ruta, no solo en el login.
- Para consultas que aceptan filtros dinamicos (APIs de busqueda), construye el objeto de query programaticamente a partir de campos conocidos en lugar de aceptar objetos de consulta completos del usuario.
- Si usas Mongoose, los schemas de Mongoose ofrecen una capa de validacion de tipos que rechaza tipos incorrectos. Sin embargo, si usas el driver nativo de MongoDB, esa proteccion no existe automaticamente.
- Audita todas las rutas que pasan cuerpo de peticion directamente a metodos como `find`, `findOne`, `update` o `delete` de MongoDB.

## Que deberia verse al terminar

- La ruta de login valida el tipo de `username` y `password` antes de la query.
- La verificacion de la contraseña se hace fuera de la condicion de MongoDB.
- No se pasan objetos de cuerpo de peticion directamente a la query sin validacion de tipo.

## Que valida el workflow automaticamente

- `scripts/validate-step-03.py` comprueba que `src/routes/auth.js` contiene los marcadores de defensa.
- El validador busca la validacion de tipo con `typeof`.
- El validador busca el uso de comparacion de hash separada de la query (patron `bcrypt.compare` o similar).

## Criterio de finalizacion

El paso 3 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
