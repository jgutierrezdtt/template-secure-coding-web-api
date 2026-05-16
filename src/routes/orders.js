// src/routes/orders.js
// PASO 8: BOLA — verificacion de propiedad del objeto

const express = require("express");
const router = express.Router();

router.get("/:id", async (req, res) => {
  const order = await db.query(
    "SELECT * FROM orders WHERE id = $1 AND user_id = $2",
    [req.params.id, req.user.id]
  );
  if (order.rows.length === 0) {
    return res.status(404).json({ error: "Order not found" });
  }
  res.json(order.rows[0]);
});

module.exports = router;
