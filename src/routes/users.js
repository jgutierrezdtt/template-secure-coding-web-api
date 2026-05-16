// src/routes/users.js
// PASO 1: SQL Injection basica — sentencias preparadas
// TODO: La siguiente ruta es vulnerable a SQL injection. Aplicar sentencia preparada.

const express = require("express");
const router = express.Router();

// VULNERABLE (punto de inicio del ejercicio):
// router.get("/:id", async (req, res) => {
//   const query = "SELECT * FROM users WHERE id = " + req.params.id;
//   const result = await db.query(query);
//   res.json(result.rows[0]);
// });

// Despues de completar el paso 1, la ruta debe verse asi:
router.get("/:id", async (req, res) => {
  const query = "SELECT id, username, displayName FROM users WHERE id = $1";
  const result = await db.query(query, [req.params.id]);
  if (result.rows.length === 0) return res.status(404).json({ error: "User not found" });
  res.json(result.rows[0]);
});

module.exports = router;
