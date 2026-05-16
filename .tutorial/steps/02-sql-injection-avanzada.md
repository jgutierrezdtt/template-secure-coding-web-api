# Paso 2. Inyeccion SQL avanzada — blind, time-based y second-order

## Objetivo de aprendizaje

Entender que la inyeccion SQL no siempre produce un error visible ni devuelve datos directamente, y que las variantes ciegas y de segundo orden requieren defensas adicionales mas alla de las sentencias preparadas en la consulta inicial.

## Por que importa esto

Despues del paso 1, un desarrollador podria pensar que ha resuelto la inyeccion SQL. Las sentencias preparadas protegen las consultas donde se usan, pero el riesgo persiste en dos escenarios que muchos equipos no anticipan.

El primero es la inyeccion ciega: el atacante no ve el resultado de la consulta ni recibe un mensaje de error, pero puede hacer preguntas de si o no a la base de datos interpretando el comportamiento de la aplicacion (cambia la respuesta, cambia el tiempo de respuesta). Con paciencia y automatizacion, puede extraer toda la base de datos sin un solo mensaje de error visible.

El segundo es la inyeccion de segundo orden: el valor malicioso se almacena en la base de datos de forma segura (con sentencia preparada), pero mas tarde otro fragmento del codigo lo recupera y lo usa en una nueva consulta sin parametrizar. El atacante no explota el punto de entrada, sino el punto de uso posterior.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/search.js`. La ruta de busqueda usa el termino que introduce el usuario en una query de tipo LIKE sin parametrizar. Ademas, el endpoint `/users/:username/profile` recupera datos de un campo almacenado previamente y los usa en una segunda consulta sin proteccion.

El cambio requiere parametrizar correctamente ambas consultas y añadir una capa de validacion de entrada que limite el conjunto de caracteres aceptados en los campos de busqueda.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/search.js`
- Funcion de busqueda: query con LIKE que concatena el termino
- Funcion de perfil: segunda consulta que usa datos recuperados de la base de datos

## Cambio base recomendado

Antes (vulnerable — blind injection via LIKE):

```js
// VULNERABLE: el termino de busqueda se inserta directamente
const query = `SELECT * FROM products WHERE name LIKE '%${req.query.term}%'`;
```

Despues (seguro):

```js
// SEGURO: el wildcard forma parte del valor parametrizado, no de la estructura
const term = `%${req.query.term}%`;
const query = "SELECT * FROM products WHERE name LIKE $1";
const result = await db.query(query, [term]);
```

Proteccion adicional contra second-order:

```js
// Validar que el campo solo contiene caracteres esperados antes de usarlo en otra query
const SAFE_USERNAME = /^[a-zA-Z0-9_-]{1,64}$/;
if (!SAFE_USERNAME.test(username)) {
  return res.status(400).json({ error: "Invalid username format" });
}
const profileQuery = "SELECT * FROM profiles WHERE username = $1";
```

## Que te esta enseñando este cambio

- La inyeccion ciega no produce errores visibles pero es igual de explotable que la inyeccion directa. Los atacantes usan herramientas automatizadas (sqlmap) que pueden extraer una base de datos completa haciendo miles de peticiones con variaciones minimas.
- La inyeccion time-based es una variante de la ciega donde el atacante mide el tiempo de respuesta para inferir informacion. Consultas como `IF(1=1, SLEEP(5), 0)` cambian el tiempo de respuesta dependiendo del resultado de la condicion.
- La inyeccion de segundo orden es especialmente peligrosa porque pasa los controles de seguridad en el punto de entrada y explota un punto diferente. El principio de defensa es: cualquier dato que venga de la base de datos debe tratarse con la misma desconfianza que los datos del usuario, porque pudo haber sido manipulado antes de ser almacenado.
- La validacion de formato (lista blanca de caracteres) no reemplaza las sentencias preparadas: las complementa. Es util para detectar intentos de inyeccion antes de que lleguen a la base de datos y para limitar la superficie de ataque en campos de segundo orden.

## Como adaptarlo correctamente

- Audita todas las rutas que usan valores de la base de datos como entrada de otras consultas.
- Para busquedas de texto libre donde LIKE es necesario, considera usar busqueda de texto completo (full-text search) del motor de base de datos, que es mas segura y mas eficiente.
- Los logs de la aplicacion pueden revelar inyecciones ciegas: patrones de consultas con variaciones sistematicas en parametros numericos o logicos son señal de reconnaissance automatizado.
- Las herramientas de WAF (Web Application Firewall) pueden detectar patrones conocidos de inyeccion SQL, pero no son la defensa principal: el codigo debe ser seguro independientemente del WAF.

## Que deberia verse al terminar

- La query de busqueda con LIKE usa parametro separado con el wildcard incluido en el valor.
- La consulta de segundo orden valida el formato del campo antes de usarlo.
- No hay ninguna consulta SQL que concatene un valor sin pasar por parametro o validacion de lista blanca.

## Que valida el workflow automaticamente

- `scripts/validate-step-02.py` comprueba que `src/routes/search.js` contiene marcadores de proteccion.
- El validador busca el uso de query parametrizada en la funcion de busqueda.
- El validador busca la validacion de formato (expresion regular o similar) antes de la consulta de segundo orden.

## Criterio de finalizacion

El paso 2 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
