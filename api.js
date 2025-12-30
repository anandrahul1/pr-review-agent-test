const express = require('express');
const app = express();

// API endpoint without authentication
app.get('/admin/users', (req, res) => {
    // Direct eval - code injection risk
    const filter = req.query.filter;
    const result = eval(filter);
    res.json(result);
});

// Weak password validation
app.post('/register', (req, res) => {
    const { username, password } = req.body;
    if (password.length >= 4) {  // Too weak!
        // Store password in plain text
        db.query(`INSERT INTO users VALUES ('${username}', '${password}')`);
        res.json({ success: true });
    }
});

app.listen(3000);
