// src/routes/comments.js
// PASO 5: XSS — sanitizacion con DOMPurify

const express = require("express");
const createDOMPurify = require("dompurify");
const { JSDOM } = require("jsdom");
const router = express.Router();
const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

router.post("/", async (req, res) => {
  const sanitizedContent = DOMPurify.sanitize(req.body.content);
  await db.query("INSERT INTO comments (content, user_id) VALUES ($1, $2)", [
    sanitizedContent,
    req.user.id,
  ]);
  res.status(201).json({ message: "Comment created" });
});

module.exports = router;
