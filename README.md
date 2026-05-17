# Secure Coding Web y API

Tutorial practico de seguridad para aplicaciones web y APIs REST/GraphQL.
Aprende a identificar y corregir las vulnerabilidades mas frecuentes trabajando
directamente sobre codigo real.

---

## Por que este tutorial

La mayoria de los tutoriales de seguridad explican que existe una vulnerabilidad
pero no te hacen sentir por que es un problema real ni explican por que la mitigacion
funciona. Este tutorial hace las dos cosas: cada paso muestra codigo vulnerable, explica
exactamente como un atacante lo explotaria, y luego explica por que el patron de
mitigacion correcto elimina el riesgo estructuralmente.

---

## Inicio del tutorial

[Empezar tutorial](https://github.com/jgutierrezdtt/template-secure-coding-web-api/fork)

Si ya tienes tu fork, ve a la pestana **Actions** de tu repositorio y ejecuta el
workflow **Start Tutorial** para ver el primer paso.

---

## Gestion del progreso

- [Validar progreso](../../actions/workflows/completion.yml)
- [Iniciar tutorial](../../actions/workflows/start.yml)
- [Reiniciar tutorial](../../actions/workflows/reset-tutorial.yml)

---

## Tabla de pasos

| Paso | Tema | Vulnerabilidad que resuelves |
|------|------|------------------------------|
| 0 | Introduccion | Lee esto primero |
| 1 | SQL injection basica | Leer o modificar toda la base de datos sin credenciales |
| 2 | SQL injection avanzada | Extraccion de datos sin errores visibles |
| 3 | NoSQL injection (MongoDB) | Autenticarse sin contrasena con operadores del motor |
| 4 | GraphQL security | Introspection y ataques de denegacion de servicio |
| 5 | XSS y Content Security Policy | JavaScript del atacante en el navegador de tus usuarios |
| 6 | SSRF | Usar tu servidor como proxy contra redes internas y cloud |
| 7 | JWT y autenticacion | Fabricar tokens de sesion sin conocer el secreto |
| 8 | Autorizacion: BOLA e IDOR | Acceder a datos de otros usuarios autenticados correctamente |
| 9 | Mass assignment y exposicion | Escalar privilegios y extraer informacion sensible |
| 10 | Checklist final | Consolida todos los controles |

---

## Paso 0

Cada paso de este tutorial muestra un archivo con una vulnerabilidad real en el codigo
fuente del repositorio. Tu tarea es aplicar el patron de mitigacion correcto en ese
archivo. Cuando hagas push, el workflow valida automaticamente tu cambio y actualiza
este README con el siguiente paso.

No se necesita instalar nada local. Todo el feedback es automatico.

---

## Nivel y prerrequisitos

- Nivel: profesional
- Lenguaje del tutorial: espanol
- Conocimientos recomendados: JavaScript/Node.js basico, nociones de como funciona una API REST
- No se requiere experiencia previa en seguridad
