# Paso 0. Introduccion al tutorial de Secure Coding para Web y API

Bienvenido al tutorial de programacion segura para aplicaciones web y APIs.

## Que vas a aprender

Este tutorial cubre las vulnerabilidades mas frecuentes en aplicaciones web y APIs modernas. No se trata de teoria: vas a ver codigo vulnerable real, entender exactamente por que es peligroso y aplicar el patron de mitigacion correcto con explicacion de por que funciona.

Los 10 pasos cubren:

| Paso | Tema |
| ---- | ---- |
| 1 | Inyeccion SQL basica — sentencias preparadas |
| 2 | Inyeccion SQL avanzada — blind, time-based, second-order |
| 3 | Inyeccion NoSQL — operadores MongoDB |
| 4 | GraphQL — introspection, batch attacks, inyeccion |
| 5 | XSS y CSP — reflected, stored, DOM y cabeceras de seguridad |
| 6 | SSRF — validacion de peticiones salientes |
| 7 | Autenticacion en APIs — JWT, tokens y sesiones |
| 8 | Autorizacion en APIs — BOLA, IDOR y BFLA |
| 9 | Mass assignment y exposicion de datos sensibles |
| 10 | Medalla final — consolidacion del programa de secure coding |

## A quien va dirigido

A desarrolladores que construyen APIs o aplicaciones web y quieren entender la seguridad desde el codigo, no solo desde los escaneadores. No se asume conocimiento previo de seguridad: cada paso explica el riesgo desde cero.

## Como funciona el tutorial

1. Lee el paso correspondiente en `.tutorial/steps/`.
2. Estudia el codigo vulnerable en `src/`.
3. Aplica el cambio indicado siguiendo el patron de mitigacion.
4. El workflow de GitHub Actions valida automaticamente que el cambio es correcto.

## Empezar tutorial

Ejecuta el workflow `Start Tutorial` desde la pestana Actions de este repositorio.

## Tabla de pasos

| Paso | Archivo de instrucciones |
| ---- | ------------------------ |
| Paso 0 | `.tutorial/steps/00-introduccion.md` |
| Paso 1 | `.tutorial/steps/01-sql-injection-basica.md` |
| Paso 2 | `.tutorial/steps/02-sql-injection-avanzada.md` |
| Paso 3 | `.tutorial/steps/03-nosql-injection.md` |
| Paso 4 | `.tutorial/steps/04-graphql-security.md` |
| Paso 5 | `.tutorial/steps/05-xss-y-csp.md` |
| Paso 6 | `.tutorial/steps/06-ssrf.md` |
| Paso 7 | `.tutorial/steps/07-api-autenticacion.md` |
| Paso 8 | `.tutorial/steps/08-api-autorizacion.md` |
| Paso 9 | `.tutorial/steps/09-mass-assignment.md` |
| Paso 10 | `.tutorial/steps/10-medalla-final.md` |
