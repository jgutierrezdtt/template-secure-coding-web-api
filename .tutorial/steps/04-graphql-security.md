# Paso 4. GraphQL — introspection, batch attacks e inyeccion

## Objetivo de aprendizaje

Entender los vectores de ataque especificos de GraphQL que no existen en APIs REST, y como la flexibilidad que hace a GraphQL poderoso también genera superficies de ataque que requieren controles explicitos.

## Por que importa esto

GraphQL permite a los clientes pedir exactamente los datos que necesitan, lo cual es su fortaleza. Esa misma flexibilidad crea tres vectores de ataque que no existen en APIs REST tradicionales.

El primero es la introspection: GraphQL tiene un mecanismo incorporado para que los clientes descubran el esquema completo de la API, todos los tipos, campos y relaciones. En produccion, esto equivale a darle al atacante el mapa completo de tu base de datos.

El segundo son los batch attacks: GraphQL permite enviar multiples queries en una sola peticion. Un atacante puede enviar miles de intentos de fuerza bruta en una sola peticion HTTP, evadiendo los rate limits que solo cuentan peticiones HTTP.

El tercero es la inyeccion en resolvers: si los resolvers de GraphQL construyen queries SQL o comandos con los argumentos de la query GraphQL sin parametrizar, el riesgo de inyeccion es identico al de una API REST.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/graphql.js`. El endpoint GraphQL tiene introspection habilitado, no limita la profundidad ni la complejidad de las queries, y el resolver de busqueda de usuarios construye la query SQL con los argumentos de GraphQL sin parametrizar.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/graphql.js`
- Configuracion del servidor GraphQL: opcion de introspection y limites de query
- Resolver de busqueda: construccion de la query SQL con argumentos de GraphQL

## Cambio base recomendado

Deshabilitar introspection en produccion:

```js
// SEGURO: deshabilitar introspection fuera de entornos de desarrollo
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV === "development",
});
```

Limitar profundidad y complejidad:

```js
// SEGURO: limitar la profundidad maxima de queries anidadas
const depthLimit = require("graphql-depth-limit");
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV === "development",
  validationRules: [depthLimit(5)],
});
```

Parametrizar queries SQL en resolvers:

```js
// SEGURO: el argumento de GraphQL llega como parametro separado a la query SQL
async searchUsers(_, { name }) {
  const result = await db.query(
    "SELECT id, username FROM users WHERE username ILIKE $1",
    [`%${name}%`]
  );
  return result.rows;
}
```

## Que te esta enseñando este cambio

- Introspection es util durante el desarrollo pero en produccion da al atacante la misma informacion que tendria si leyera el codigo fuente. Deshabilitarla no protege el esquema de un atacante determinado, pero elimina el reconocimiento automatico gratuito.
- Los batch attacks contra GraphQL son especialmente efectivos en operaciones de login o verificacion de tokens porque evaden los rate limits basados en numero de peticiones HTTP. El limite debe aplicarse al numero de operaciones por peticion, no solo al numero de peticiones.
- La inyeccion en resolvers GraphQL es identica a la inyeccion SQL clasica en cuanto al mecanismo y la defensa. GraphQL no elimina ese riesgo: cambia el punto de entrada pero el problema subyacente es el mismo.
- La profundidad de queries anidadas no solo es un problema de seguridad: es un problema de rendimiento. Una query con 10 niveles de anidacion puede generar cientos de consultas a la base de datos y colapsar el servidor.

## Como adaptarlo correctamente

- Usa un parser de seguridad para GraphQL que limite el costo de las queries antes de ejecutarlas (graphql-cost-analysis, graphql-query-complexity).
- Para APIs que autentican usuarios, aplica rate limiting a nivel de operacion GraphQL, no solo a nivel HTTP.
- Audita todos los resolvers que aceptan argumentos del cliente y los usan en queries a base de datos, sistema de archivos o servicios externos.
- Considera usar persisted queries en produccion: solo las queries pre-registradas son validas, lo que elimina la superficie de ataques de queries arbitrarias.

## Que deberia verse al terminar

- `introspection` esta deshabilitado cuando `NODE_ENV !== "development"`.
- El servidor incluye limites de profundidad o complejidad de queries.
- Los resolvers que construyen queries SQL usan parametros separados.

## Que valida el workflow automaticamente

- `scripts/validate-step-04.py` comprueba que `src/routes/graphql.js` contiene los controles.
- El validador busca la condicion de `introspection` ligada a `NODE_ENV`.
- El validador busca el uso de `depthLimit` u otro control de complejidad.
- El validador busca queries SQL parametrizadas en los resolvers.

## Criterio de finalizacion

El paso 4 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
