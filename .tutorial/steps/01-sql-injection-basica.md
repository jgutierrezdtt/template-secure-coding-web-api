# Paso 1. Inyeccion SQL basica — sentencias preparadas

## Objetivo de aprendizaje

Entender que es la inyeccion SQL, por que permite a un atacante leer o modificar cualquier dato de la base de datos, y como las sentencias preparadas eliminan ese vector de forma definitiva.

## Por que importa esto

La inyeccion SQL lleva en el top 1 de vulnerabilidades web mas de 20 anos. Es el ataque que permite a alguien que no tiene cuenta en tu aplicacion leer todos los registros de tu base de datos, modificarlos o borrarlos.

El problema no es una libreria ni una configuracion: es una forma de construir consultas SQL concatenando texto directamente con datos del usuario. Cuando haces eso, el motor de base de datos no sabe donde termina la consulta que tu escribiste y donde empieza el texto que introdujo el usuario. Un atacante que entiende eso puede reescribir tu consulta para que haga lo que el quiera.

Este paso es el primero del tutorial porque la inyeccion SQL es el ejemplo mas claro de por que la validacion de entrada no es la defensa correcta: la defensa correcta es no mezclar codigo con datos.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/users.js`. La ruta `/users/:id` construye la consulta SQL concatenando directamente el parametro de la URL. Eso significa que cualquier valor en `:id` se convierte en parte de la consulta.

El cambio es simple pero fundamental: en lugar de concatenar el valor, vas a usar una sentencia preparada que separa la estructura de la consulta de los datos. La base de datos recibe los dos por separado y nunca los mezcla.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/users.js`
- Funcion: handler de la ruta `GET /users/:id`
- Busca la linea donde se construye la query con concatenacion de strings

## Cambio base recomendado

Antes (vulnerable):

```js
// VULNERABLE: el valor de req.params.id se inserta directamente en la query
const query = "SELECT * FROM users WHERE id = " + req.params.id;
const result = await db.query(query);
```

Despues (seguro):

```js
// SEGURO: la query tiene estructura fija, el valor llega como parametro separado
const query = "SELECT * FROM users WHERE id = $1";
const result = await db.query(query, [req.params.id]);
```

Por que funciona: el driver de base de datos envía la estructura de la query y los parametros por canales separados. El motor SQL nunca interpreta los parametros como parte de la sintaxis de la query, independientemente de lo que contengan. Aunque el usuario ponga `1 OR 1=1`, llega como un valor de texto, no como SQL.

## Que te esta enseñando este cambio

- Las sentencias preparadas no son una "buena practica opcional": son el unico mecanismo que elimina structuralmente la inyeccion SQL. Los filtros de entrada (escapar comillas, validar formato) son capas adicionales, no la defensa principal.
- El problema original no es que el codigo sea "descuidado": es que concatenar strings para construir queries es el patron mas natural cuando aprendes a trabajar con bases de datos. Este paso enseña a reconocer ese patron y reemplazarlo siempre.
- Las sentencias preparadas funcionan igual para INSERT, UPDATE y DELETE. Siempre que un valor del usuario forme parte de una consulta SQL, debe llegar como parametro separado.
- El cambio no afecta al rendimiento en consultas de lectura simples. En consultas que se ejecutan muchas veces (bucles, batch jobs), las sentencias preparadas son incluso mas eficientes porque el motor compila el plan de ejecucion una sola vez.

## Como adaptarlo correctamente

- Aplica el mismo patron a todas las queries del archivo, no solo a la que indica el tutorial.
- Si usas un ORM (Sequelize, TypeORM, Prisma), el ORM ya usa sentencias preparadas internamente. El riesgo reaparece si ejecutas "raw queries" con interpolacion de strings.
- No uses `eval()` ni `Function()` con datos del usuario para construir queries dinamicas: es el equivalente en JavaScript.
- Cuando el valor del usuario determina el nombre de una columna o tabla (no el valor), las sentencias preparadas no protegen esa parte. Esos casos requieren validar contra una lista blanca de nombres permitidos.

## Que deberia verse al terminar

- La ruta `/users/:id` usa la forma parametrizada con `$1` (o `?` segun el driver).
- No hay ninguna concatenacion de strings para construir la query en esa ruta.
- El codigo diferencia claramente entre la estructura de la query y los valores que recibe.

## Que valida el workflow automaticamente

- `validate-steps.yml` se ejecuta con `push`, `pull_request` y `workflow_dispatch`.
- `scripts/validate-step-01.py` comprueba que `src/routes/users.js` contiene el marcador de sentencia preparada.
- El validador busca el patron parametrizado (`$1` o `?`) en la query de la ruta de usuarios.
- El validador verifica que no existe concatenacion directa en la query de esa ruta.

## Criterio de finalizacion

El paso 1 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
