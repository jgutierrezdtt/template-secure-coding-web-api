# Paso 6. SSRF — validacion de peticiones salientes

## Objetivo de aprendizaje

Entender que es el Server-Side Request Forgery (SSRF), por que permite a un atacante usar el servidor como proxy para acceder a recursos internos, y como validar las URLs de destino antes de hacer peticiones salientes.

## Por que importa esto

Cuando una aplicacion hace una peticion HTTP a una URL que proviene del usuario (por ejemplo, para previsualizar un enlace, descargar un recurso o llamar a un webhook), el servidor que hace esa peticion puede alcanzar cualquier sistema al que tenga acceso de red. Eso incluye la red interna de la empresa, los metadatos de instancias en la nube, servicios internos sin autenticacion y otros servidores de produccion.

Un atacante que controla la URL puede redirigir la peticion del servidor hacia `http://169.254.169.254/` (el endpoint de metadatos de AWS) para obtener credenciales temporales de la instancia, o hacia `http://internal-api.company.local/admin` para acceder a servicios internos sin autenticacion.

SSRF es uno de los vectores que se usa con mayor frecuencia en ataques a infraestructura cloud porque el servidor legitimo de la aplicacion no necesita credenciales especiales para acceder a esos recursos: ya tiene permiso de red por estar en la misma red o instancia.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `src/routes/proxy.js`. La ruta de proxy acepta una URL del usuario y hace una peticion HTTP a esa URL sin validar si el destino es permitido. Cualquier URL es aceptada, incluyendo IPs privadas, localhost y el endpoint de metadatos de cloud.

## Archivo y seccion que debes modificar

- Archivo objetivo: `src/routes/proxy.js`
- Funcion: handler de la ruta que acepta la URL y hace la peticion saliente

## Cambio base recomendado

```js
const dns = require("dns").promises;
const net = require("net");

// Lista de rangos privados que no deben ser alcanzables
const PRIVATE_RANGES = [
  /^127\./,
  /^10\./,
  /^192\.168\./,
  /^172\.(1[6-9]|2[0-9]|3[01])\./,
  /^169\.254\./, // link-local (metadatos de cloud AWS, GCP)
  /^::1$/,       // IPv6 loopback
  /^fc00:/,      // IPv6 ULA
];

async function isPrivateOrReserved(hostname) {
  try {
    const { address } = await dns.lookup(hostname);
    return PRIVATE_RANGES.some(range => range.test(address));
  } catch {
    return true; // Si no se puede resolver, denegar
  }
}

// SEGURO: validar la URL antes de hacer la peticion
async function proxyHandler(req, res) {
  let targetUrl;
  try {
    targetUrl = new URL(req.query.url);
  } catch {
    return res.status(400).json({ error: "Invalid URL" });
  }

  // Solo permitir HTTP y HTTPS
  if (!["http:", "https:"].includes(targetUrl.protocol)) {
    return res.status(400).json({ error: "Protocol not allowed" });
  }

  // Verificar que el hostname no resuelve a una IP privada
  if (await isPrivateOrReserved(targetUrl.hostname)) {
    return res.status(403).json({ error: "Destination not allowed" });
  }

  // Hacer la peticion solo si paso todas las validaciones
  const response = await fetch(targetUrl.toString(), { redirect: "manual" });
  // ...
}
```

## Que te esta enseñando este cambio

- El riesgo de SSRF no esta en la URL que el usuario escribe sino en la IP a la que esa URL resuelve. Un atacante puede registrar un dominio que resuelve a `169.254.169.254` para evadir validaciones que solo miran el hostname. Por eso la validacion debe hacerse sobre la IP resuelta, no sobre el string de la URL.
- Deshabilitar los redirects automaticos (`redirect: "manual"`) es importante porque un servidor externo puede redirigir a una URL interna como segundo paso. Si el cliente HTTP sigue redirects automaticamente, la validacion del primer paso no protege contra el redirect al destino final.
- El endpoint de metadatos de AWS (`169.254.169.254`) y sus equivalentes en GCP y Azure son el objetivo mas comun en ataques SSRF contra infraestructura cloud porque contienen credenciales de acceso temporales que permiten acceder a todos los recursos de la cuenta.
- La lista de rangos privados RFC 1918 no es la unica lista relevante. Los rangos link-local (169.254.x.x) y loopback (127.x.x.x) tambien deben bloquearse, y en entornos IPv6 tambien los equivalentes.

## Como adaptarlo correctamente

- Si la funcionalidad de proxy o webhook es necesaria para el negocio, considera usar una lista blanca de dominios o URLs permitidas en lugar de una lista negra de rangos privados: es mas seguro por diseno.
- Para funcionalidades de carga de imagenes o previsualizacion de URLs, evalua si puedes hacer la peticion desde un servicio o worker aislado que no tenga acceso a la red interna.
- Audita todas las rutas que aceptan URLs del usuario, incluyendo campos de webhook, configuracion de integraciones y funcionalidades de importacion de datos.
- Usa librerias especializadas en validacion de SSRF cuando esten disponibles para tu lenguaje. Implementar la lista negra correctamente es mas complejo de lo que parece.

## Que deberia verse al terminar

- La ruta valida el protocolo de la URL (solo http/https).
- La ruta resuelve el hostname a IP y verifica que no es privada.
- Los redirects automaticos estan deshabilitados o se valida el destino del redirect.

## Que valida el workflow automaticamente

- `scripts/validate-step-06.py` comprueba que `src/routes/proxy.js` contiene los controles.
- El validador busca la validacion del protocolo.
- El validador busca la verificacion de rangos privados (`PRIVATE_RANGES` o similar).
- El validador busca el control de redirects.

## Criterio de finalizacion

El paso 6 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores.
