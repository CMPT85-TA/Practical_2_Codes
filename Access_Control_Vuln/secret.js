// secret.js
const express = require('express');
const r = express.Router();

r.get('/', (req, res) => res.json({ ok: true })); // <-- root

module.exports = r;
