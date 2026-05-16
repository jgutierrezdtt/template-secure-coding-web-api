// src/routes/auth.js
// PASO 3: NoSQL injection — validacion de tipo y bcrypt fuera de query

const express = require("express");
const bcrypt = require("bcrypt");
const router = express.Router();

router.post("/login", async (req, res) => {
  if (typeof req.body.username !== "string" || typeof req.body.password !== "string") {
    return res.status(400).json({ error: "Invalid input type" });
  }

  const user = await User.findOne({ username: req.body.username });
  if (!user || !await bcrypt.compare(req.body.password, user.passwordHash)) {
    return res.status(401).json({ error: "Invalid credentials" });
  }

  const token = generateToken(user);
  res.json({ token });
});

module.exports = router;
