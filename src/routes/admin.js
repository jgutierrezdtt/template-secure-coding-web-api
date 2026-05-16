// src/routes/admin.js
// PASO 8: BFLA — middleware de verificacion de rol

const express = require("express");
const router = express.Router();

function requireAdmin(req, res, next) {
  if (!req.user || req.user.role !== "admin") {
    return res.status(403).json({ error: "Forbidden" });
  }
  next();
}

const requireAuth = require("../middleware/auth");

router.get("/users", requireAuth, requireAdmin, async (req, res) => {
  const result = await db.query("SELECT id, username, role FROM users");
  res.json(result.rows);
});

router.delete("/users/:id", requireAuth, requireAdmin, async (req, res) => {
  await db.query("DELETE FROM users WHERE id = $1", [req.params.id]);
  res.status(204).end();
});

module.exports = router;
