// src/routes/search.js
// PASO 2: SQL Injection avanzada — LIKE parametrizado y second-order

const express = require("express");
const router = express.Router();
const SAFE_TERM = /^[a-zA-Z0-9 _-]{1,100}$/;

router.get("/products", async (req, res) => {
  if (!SAFE_TERM.test(req.query.term || "")) {
    return res.status(400).json({ error: "Invalid search term" });
  }
  const term = `%${req.query.term}%`;
  const result = await db.query(
    "SELECT id, name FROM products WHERE name ILIKE $1",
    [term]
  );
  res.json(result.rows);
});

module.exports = router;
