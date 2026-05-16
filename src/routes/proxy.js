// src/routes/proxy.js
// PASO 6: SSRF — validacion de IP destino

const express = require("express");
const dns = require("dns").promises;
const router = express.Router();

const PRIVATE_RANGES = [
  /^127\./,
  /^10\./,
  /^192\.168\./,
  /^172\.(1[6-9]|2[0-9]|3[01])\./,
  /^169\.254\./,
  /^::1$/,
  /^fc00:/,
];

async function isPrivateOrReserved(hostname) {
  try {
    const { address } = await dns.lookup(hostname);
    return PRIVATE_RANGES.some(range => range.test(address));
  } catch {
    return true;
  }
}

router.get("/fetch", async (req, res) => {
  let targetUrl;
  try { targetUrl = new URL(req.query.url); } catch {
    return res.status(400).json({ error: "Invalid URL" });
  }
  if (!["http:", "https:"].includes(targetUrl.protocol)) {
    return res.status(400).json({ error: "Protocol not allowed" });
  }
  if (await isPrivateOrReserved(targetUrl.hostname)) {
    return res.status(403).json({ error: "Destination not allowed" });
  }
  const response = await fetch(targetUrl.toString(), { redirect: "manual" });
  const body = await response.text();
  res.send(body);
});

module.exports = router;
