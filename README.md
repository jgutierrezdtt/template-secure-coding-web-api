# template-secure-coding-web-api

Tutorial interactivo de programacion segura para aplicaciones web y APIs. Aprende a identificar y corregir las vulnerabilidades mas frecuentes trabajando directamente sobre codigo real.

## Por que este tutorial

La mayoria de los tutoriales de seguridad explican que existe una vulnerabilidad pero no te hacen sentir por que es un problema real ni te explican por que la mitigacion funciona. Este tutorial hace las dos cosas: cada paso muestra codigo vulnerable, explica exactamente como un atacante lo explotaria, y luego explica por que el patron de mitigacion correcto elimina el riesgo estructuralmente.

Esta pensado para desarrolladores que construyen APIs o aplicaciones web y quieren entender la seguridad desde el codigo. No se asume conocimiento previo de seguridad.

## Que vas a aprender

| Paso | Vulnerabilidad | Por que es peligrosa |
| ---- | -------------- | -------------------- |
| 1 | SQL injection basica | Permite leer o modificar toda la base de datos sin credenciales |
| 2 | SQL injection avanzada | Funciona incluso sin errores visibles ni respuestas directas |
| 3 | NoSQL injection (MongoDB) | Permite autenticarse sin contraseña usando operadores del motor |
| 4 | GraphQL security | La flexibilidad del protocolo crea vectores que no existen en REST |
| 5 | XSS y Content Security Policy | Ejecuta JavaScript en el navegador de otros usuarios |
| 6 | SSRF | Usa tu servidor como proxy para atacar redes internas y cloud |
| 7 | JWT y autenticacion en APIs | Permite fabricar tokens de sesion sin conocer el secreto |
| 8 | Autorizacion: BOLA e IDOR | Accede a datos de otros usuarios aunque esten autenticados correctamente |
| 9 | Mass assignment y exposicion de datos | Escala privilegios y extrae informacion sensible de la API |
| 10 | Checklist final | Consolida todos los controles y verifica cobertura completa |

## Como funciona el tutorial

1. Ejecuta el workflow `Start Tutorial` desde la pestana Actions.
2. Lee el paso en `.tutorial/steps/` — cada paso explica el riesgo y la mitigacion.
3. Estudia el codigo vulnerable en `src/`.
4. Aplica el cambio indicado siguiendo el patron de mitigacion del paso.
5. Haz push — el workflow de GitHub Actions valida automaticamente tu cambio.

## Estructura del repositorio

```
src/
  routes/        Rutas de la API con el codigo del ejercicio
  middleware/    Middleware de autenticacion y cabeceras de seguridad
  models/        Modelos de datos
docs/
  secure-coding-checklist.md   Checklist del paso final
scripts/
  validate-step-NN.py          Validadores automaticos por paso
  tutorial_engine.py           Motor de estado del tutorial
.tutorial/
  steps/         Instrucciones de cada paso
  config.yml     Configuracion del tutorial
.github/workflows/
  validate-steps.yml   Ejecuta todos los validadores
  start.yml            Inicia el tutorial
  completion.yml       Marca el tutorial como completado
```

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

## Nivel y prerrequisitos

- Nivel: professional
- Lenguaje del tutorial: español
- Conocimientos previos recomendados: JavaScript/Node.js basico, nociones de como funciona una API REST
- No se requiere experiencia previa en seguridad

## Creditos

Este tutorial forma parte de la serie de tutoriales de seguridad de `jgutierrezdtt`. Para SAST, SCA y otros temas, consulta los repositorios de la organizacion.
