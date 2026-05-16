# Paso 5. XSS y CSP — reflected, stored, DOM y cabeceras de seguridad

## Objetivo de aprendizaje

Entender como funciona el Cross-Site Scripting (XSS), por que permite a un atacante ejecutar codigo JavaScript en el navegador de otro usuario, y como Content Security Policy (CSP) añade una capa de defensa que limita el impacto incluso cuando aparece una vulnerabilidad XSS.

## Por que importa esto

XSS es la vulnerabilidad que permite a un atacante inyectar JavaScript en una pagina web que luego se ejecuta en el navegador de otros usuarios. Ese JavaScript tiene los mismos permisos que el codigo legitimo del sitio: puede leer cookies de sesion, capturar lo que el usuario escribe, hacer peticiones en nombre del usuario o redirigirlo a paginas falsas.

Hay tres tipos principales. Reflected XSS ocurre cuando el servidor toma datos del usuario (tipicamente de la URL) y los incluye en la respuesta sin escapar. Stored XSS ocurre cuando los datos maliciosos se guardan en la base de datos y se muestran a otros usuarios mas adelante: es mas peligroso porque un atacante puede comprometer miles de usuarios con una sola inyeccion. DOM XSS ocurre completamente en el cliente cuando JavaScript del sitio manipula el DOM con datos del usuario sin sanitizar.

Content Security Policy es una cabecera HTTP que le dice al navegador que recursos son legitimos para esa pagina. Aunque aparezca una vulnerabilidad XSS, una CSP estricta puede impedir que el script inyectado se ejecute o que exfiltre datos.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/comments.js` y `src/middleware/security-headers.js`. La ruta de comentarios almacena el contenido en la base de datos y lo devuelve sin escapar el HTML. El middleware de cabeceras no configura Content-Security-Policy.

## Archivo y seccion que debes modificar

- Archivo objetivo 1: `src/routes/comments.js` — funcion que devuelve comentarios
- Archivo objetivo 2: `src/middleware/security-headers.js` — configuracion de cabeceras HTTP

## Cambio base recomendado

Sanitizar contenido HTML antes de almacenarlo o al renderizarlo:

```js
const createDOMPurify = require("dompurify");
const { JSDOM } = require("jsdom");
const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

// SEGURO: sanitizar el contenido antes de almacenarlo
const sanitizedContent = DOMPurify.sanitize(req.body.content);
await db.query("INSERT INTO comments (content) VALUES ($1)", [sanitizedContent]);
```

Añadir Content-Security-Policy:

```js
// SEGURO: CSP que deshabilita scripts inline y restringe el origen de recursos
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none';"
  );
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  next();
});
```

## Que te esta enseñando este cambio

- La defensa principal contra XSS es escapar o sanitizar el output en el momento de renderizarlo, no filtrar el input. Escaping convierte caracteres HTML especiales (`<`, `>`, `"`) en sus equivalentes HTML que el navegador muestra como texto, no ejecuta como codigo.
- La diferencia entre escapar y sanitizar: escapar hace que el contenido sea texto plano; sanitizar (como DOMPurify) permite cierto HTML pero elimina los elementos y atributos peligrosos. Usa sanitizacion cuando necesitas que los usuarios puedan usar formato (negrita, itálica). Usa escapado cuando el contenido debe ser siempre texto plano.
- Content Security Policy es una segunda linea de defensa. Una politica `script-src 'self'` impide que el navegador ejecute scripts de cualquier origen que no sea el propio sitio. Eso bloquea la exfiltracion de datos aunque el XSS se haya inyectado correctamente.
- `X-Content-Type-Options: nosniff` impide que el navegador intente "adivinar" el tipo MIME de un recurso. Sin esta cabecera, un atacante que sube un archivo de texto con contenido HTML puede conseguir que el navegador lo ejecute como HTML.

## Como adaptarlo correctamente

- En aplicaciones con frameworks de frontend (React, Vue, Angular), el framework escapa automaticamente los valores interpolados. El riesgo XSS reaparece cuando se usan mecanismos como `dangerouslySetInnerHTML` (React) o `v-html` (Vue) con datos del usuario.
- Para CSP, empieza con una politica de report-only (`Content-Security-Policy-Report-Only`) para detectar violaciones sin bloquear funcionalidad. Luego ajusta la politica y activa el modo de bloqueo.
- Evita las directivas `unsafe-inline` y `unsafe-eval` en CSP: eliminan la proteccion efectiva contra XSS.
- Audita los endpoints que devuelven HTML o JSON con contenido generado por usuarios y verifica que el contenido esta correctamente escapado o sanitizado.

## Que deberia verse al terminar

- Los comentarios pasan por sanitizacion antes de ser almacenados o devueltos.
- El middleware de cabeceras incluye `Content-Security-Policy` con al menos `script-src 'self'`.
- El middleware incluye `X-Content-Type-Options: nosniff`.

## Que valida el workflow automaticamente

- `scripts/validate-step-05.py` comprueba ambos archivos.
- El validador busca el uso de `DOMPurify` o equivalente en la ruta de comentarios.
- El validador busca `Content-Security-Policy` en el middleware de cabeceras.
- El validador busca `X-Content-Type-Options` en el middleware de cabeceras.

## Criterio de finalizacion

El paso 5 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
