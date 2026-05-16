# Paso 9. Mass assignment y exposicion de datos sensibles

## Objetivo de aprendizaje

Entender que es el mass assignment, como permite a un usuario modificar campos que no deberia poder modificar, y como limitar los datos que una API acepta y devuelve para evitar la exposicion accidental de informacion sensible.

## Por que importa esto

Mass assignment ocurre cuando una API toma el cuerpo completo de la peticion y lo pasa directamente al objeto del modelo o a la query de base de datos sin filtrar que campos son modificables. Si la base de datos tiene un campo `is_admin: false` y la API acepta ese campo del usuario, cualquier usuario puede convertirse en administrador simplemente añadiendo `"is_admin": true` a la peticion de actualizacion de perfil.

La exposicion de datos sensibles es el problema inverso: la API devuelve mas informacion de la que el cliente necesita. Una respuesta que incluye el hash de la contraseña, el numero de tarjeta de credito cifrado o tokens de sesion de otros usuarios es una fuente de informacion para el atacante aunque esos campos no se muestren en el frontend.

Los dos problemas tienen la misma raiz: la API no define explicitamente que campos acepta como entrada ni que campos incluye en la salida.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/profile.js`. La ruta de actualizacion de perfil pasa el cuerpo completo de la peticion al metodo de actualizacion del modelo. La ruta que devuelve el perfil del usuario incluye todos los campos del registro, incluyendo el hash de la contraseña y el campo `is_admin`.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/profile.js`
- Funcion de actualizacion: `PUT /profile` o `PATCH /profile`
- Funcion de lectura: `GET /profile` o `GET /users/:id`

## Cambio base recomendado

Defensa contra mass assignment:

```js
// VULNERABLE: pasa todos los campos del body al update
// await User.update(req.user.id, req.body);

// SEGURO: extraer solo los campos que el usuario puede modificar
const ALLOWED_UPDATE_FIELDS = ["displayName", "bio", "avatarUrl"];
const updates = {};
for (const field of ALLOWED_UPDATE_FIELDS) {
  if (req.body[field] !== undefined) {
    updates[field] = req.body[field];
  }
}

if (Object.keys(updates).length === 0) {
  return res.status(400).json({ error: "No valid fields to update" });
}

await User.update(req.user.id, updates);
```

Defensa contra exposicion de datos sensibles:

```js
// VULNERABLE: devuelve el objeto completo del usuario
// res.json(user);

// SEGURO: proyectar solo los campos que el cliente necesita
const SAFE_USER_FIELDS = ["id", "username", "displayName", "bio", "avatarUrl", "createdAt"];

function sanitizeUser(user) {
  return SAFE_USER_FIELDS.reduce((obj, field) => {
    if (user[field] !== undefined) obj[field] = user[field];
    return obj;
  }, {});
}

res.json(sanitizeUser(user));
```

## Que te esta enseñando este cambio

- La lista blanca de campos aceptados (ALLOWED_UPDATE_FIELDS) es mas segura que la lista negra (excluir campos peligrosos como `is_admin`). Con lista negra, cada vez que se añade un nuevo campo sensible al modelo hay que recordar añadirlo a la lista negra. Con lista blanca, nuevos campos son ignorados por defecto hasta que se decida explicitamente permitirlos.
- La proyeccion en la salida (SAFE_USER_FIELDS) tiene el mismo principio: define que se devuelve, no que se oculta. Es una decision de diseno positiva, no defensiva.
- El hash de la contraseña nunca deberia aparecer en ninguna respuesta de la API, ni en respuestas de error, ni en logs. Si el hash se filtra, un atacante puede intentar crackearlo offline sin limite de intentos.
- Este patron es especialmente importante en ORMs que tienen metodos como `toJSON()` o `serialize()`: asegurate de que esos metodos excluyen campos sensibles antes de serializar para la respuesta.

## Como adaptarlo correctamente

- Usa librerias de validacion de esquema (Zod, Joi) para definir el esquema de entrada de cada ruta. El esquema actua como lista blanca automaticamente al hacer `.pick()` de los campos permitidos.
- Para APIs con multiples roles, los campos permitidos pueden variar. Un administrador puede actualizar `is_admin`; un usuario normal no puede. Modela esa diferencia con esquemas de validacion distintos por rol.
- En logs de errores, nunca incluyas el cuerpo completo de la peticion. Los logs pueden contener contraseñas enviadas en texto plano o datos de tarjetas si el campo llego equivocado.
- Herramientas de documentacion de API como OpenAPI/Swagger pueden ayudar a definir y hacer cumplir el esquema de entrada y salida de cada ruta.

## Que deberia verse al terminar

- La actualizacion de perfil usa una lista blanca de campos permitidos (ALLOWED_UPDATE_FIELDS).
- La respuesta del perfil usa una funcion de proyeccion que excluye campos sensibles.
- No aparecen `passwordHash`, `is_admin` ni campos de sesion en ninguna respuesta de la API de perfil.

## Que valida el workflow automaticamente

- `scripts/validate-step-09.py` comprueba que `src/routes/profile.js` contiene los controles.
- El validador busca el uso de una lista blanca de campos para la actualizacion.
- El validador busca una funcion de sanitizacion o proyeccion de la respuesta.
- El validador verifica que `passwordHash` o `password` no aparece directamente en `res.json`.

## Criterio de finalizacion

El paso 9 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
