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
