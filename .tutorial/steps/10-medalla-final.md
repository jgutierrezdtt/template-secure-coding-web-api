# Paso 10. Medalla final — consolidacion del programa de secure coding web y API

## Objetivo de aprendizaje

Cerrar el tutorial consolidando la vision de conjunto de las vulnerabilidades que has trabajado, entendiendo como se relacionan entre si, y verificando que el repositorio muestra el nivel minimo requerido en cada uno de los vectores cubiertos.

## Por que importa esto

Los nueve pasos anteriores cubrieron vulnerabilidades distintas con mecanismos distintos, pero tienen algo en comun: todas ocurren cuando el codigo no distingue entre datos de confianza y datos del usuario, o cuando no verifica que el usuario tiene permiso para la accion que solicita.

Ese patron es la raiz de la mayoria de las vulnerabilidades en aplicaciones web y APIs. SQL injection, NoSQL injection y XSS son variantes del mismo problema: datos del usuario se mezclan con codigo sin separacion clara. SSRF y BOLA son variantes del mismo problema: la aplicacion actua sobre datos del usuario sin verificar si esa accion esta permitida.

Entender esa estructura comun es lo que permite reconocer nuevas variantes que no aparecen en este tutorial y aplicar el patron de defensa correcto aunque la tecnologia o el lenguaje sean diferentes.

## Que vas a cambiar y por que

En este paso vas a trabajar sobre `docs/secure-coding-checklist.md`. El checklist es el artefacto de cierre que verifica que los controles de los nueve pasos anteriores estan presentes en el repositorio y conectados entre si.

El proposito no es repetir lo que ya esta hecho, sino confirmar que el repositorio muestra un nivel profesional minimo en cada uno de los cuatro frentes del programa de secure coding.

## Archivo y seccion que debes modificar

- Archivo objetivo: `docs/secure-coding-checklist.md`
- El checklist debe cubrir los cuatro frentes: inyeccion, autenticacion y autorizacion, exposicion de datos, y defensa en profundidad

## Cambio base recomendado

```markdown
# Secure Coding Checklist — Web y API

## Frente 1: Prevencion de inyeccion

- [ ] Todas las queries SQL usan sentencias preparadas con parametros
- [ ] Las queries de MongoDB validan el tipo de entrada antes de la consulta
- [ ] Los resolvers GraphQL parametrizan las queries a base de datos
- [ ] Ningun endpoint construye queries concatenando valores del usuario

## Frente 2: Autenticacion y autorizacion

- [ ] JWT verifica con algoritmo especifico (no acepta "none")
- [ ] El secreto de firma viene de variable de entorno sin valor por defecto hardcodeado
- [ ] Cada ruta con datos de objeto verifica que pertenece al usuario autenticado
- [ ] Las rutas administrativas tienen middleware de verificacion de rol separado

## Frente 3: Exposicion de datos y mass assignment

- [ ] Las actualizaciones de perfil usan lista blanca de campos modificables
- [ ] Las respuestas de la API proyectan solo los campos necesarios
- [ ] Ningun endpoint devuelve campos sensibles como passwordHash o tokens

## Frente 4: Defensa en profundidad

- [ ] Content-Security-Policy esta configurada en el middleware de cabeceras
- [ ] X-Content-Type-Options nosniff esta habilitado
- [ ] Los endpoints de proxy o fetch externo validan la IP destino
- [ ] GraphQL tiene introspection deshabilitado en produccion
```

## Que te esta enseñando este cambio

- Los cuatro frentes del checklist no son independientes: se refuerzan mutuamente. Una API con autenticacion correcta pero sin autorizacion a nivel de objeto (BOLA) sigue siendo explotable. Una API sin inyeccion pero con mass assignment permite escalada de privilegios.
- El checklist como artefacto de cierre tiene valor practico mas alla del tutorial: es la lista de preguntas que deberia hacerse en cualquier revision de codigo de una API o aplicacion web.
- El nivel profesional en secure coding no significa ausencia de vulnerabilidades: significa que los vectores mas frecuentes y mas explotados tienen controles activos, y que esos controles son visibles y verificables.
- Lo que sigue despues de este tutorial es integrar estas verificaciones en el ciclo de desarrollo: en revisiones de codigo, en pipelines de CI con SAST, y en pruebas de seguridad periodicas con herramientas especializadas.

## Como adaptarlo correctamente

- Usa este checklist como base para las revisiones de codigo de nuevas rutas en tu API.
- Integra herramientas de SAST (como las del tutorial de SAST que complementa este) para detectar automaticamente algunos de estos patrones en cada PR.
- Establece tests de seguridad automaticos que verifiquen al menos los vectores de BOLA y autorizacion de rol: son los mas frecuentes y los mas dificiles de detectar con SAST estatico.
- Comparte el checklist con el equipo y usalo como criterio de aceptacion en la definicion de "done" para nuevas funcionalidades de la API.

## Que deberia verse al terminar

- `docs/secure-coding-checklist.md` existe y cubre los cuatro frentes.
- El checklist incluye marcadores verificables de cada uno de los controles principales.
- Los controles de los pasos anteriores estan todos presentes en el repositorio.

## Que valida el workflow automaticamente

- `scripts/validate-step-10.py` comprueba que `docs/secure-coding-checklist.md` contiene los marcadores de los cuatro frentes.
- El validador busca marcadores de prevencion de inyeccion.
- El validador busca marcadores de autenticacion y autorizacion.
- El validador busca marcadores de exposicion de datos.
- El validador busca marcadores de defensa en profundidad.

## Criterio de finalizacion

El paso 10 queda completado cuando el workflow de GitHub Actions valida este cambio sin errores. La medalla del tutorial se otorga al completar todos los pasos.
