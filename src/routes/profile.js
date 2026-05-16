// src/routes/profile.js
// PASO 9: Mass assignment y exposicion de datos sensibles

const express = require("express");
const router = express.Router();

const ALLOWED_UPDATE_FIELDS = ["displayName", "bio", "avatarUrl"];
const SAFE_USER_FIELDS = ["id", "username", "displayName", "bio", "avatarUrl", "createdAt"];

function sanitizeUser(user) {
  return SAFE_USER_FIELDS.reduce((obj, field) => {
    if (user[field] !== undefined) obj[field] = user[field];
    return obj;
  }, {});
}

router.get("/", async (req, res) => {
  const result = await db.query("SELECT * FROM users WHERE id = $1", [req.user.id]);
  if (result.rows.length === 0) return res.status(404).json({ error: "Not found" });
  res.json(sanitizeUser(result.rows[0]));
});

router.patch("/", async (req, res) => {
  const updates = {};
  for (const field of ALLOWED_UPDATE_FIELDS) {
    if (req.body[field] !== undefined) updates[field] = req.body[field];
  }
  if (Object.keys(updates).length === 0) {
    return res.status(400).json({ error: "No valid fields to update" });
  }
  const fields = Object.keys(updates).map((k, i) => `${k} = $${i + 2}`).join(", ");
  const values = [req.user.id, ...Object.values(updates)];
  await db.query(`UPDATE users SET ${fields} WHERE id = $1`, values);
  res.json({ message: "Profile updated" });
});

module.exports = router;
