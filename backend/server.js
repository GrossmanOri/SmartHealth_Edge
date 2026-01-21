import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ---- In-memory storage for live dashboard ----
const clients = new Set();
const lastAlerts = [];
const MAX_ALERTS = 50;

const app = express();
app.use(cors());
app.use(express.json());

// ------- API endpoint receiving alerts -------
app.post("/alert", (req, res) => {
    console.log(" ALERT RECEIVED FROM EDGE:");
    console.log(req.body);

    lastAlerts.unshift(req.body);
    if (lastAlerts.length > MAX_ALERTS) lastAlerts.pop();

    const payload = `data: ${JSON.stringify(req.body)}\n\n`;
    for (const client of clients) {
        client.write(payload);
    }

    res.json({ status: "ok" });
});

// ------- SSE endpoint -------
app.get("/events", (req, res) => {
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders?.();

    for (const a of lastAlerts) {
        res.write(`data: ${JSON.stringify(a)}\n\n`);
    }

    clients.add(res);
    console.log("Dashboard client connected. Total:", clients.size);

    req.on("close", () => {
        clients.delete(res);
        console.log("Dashboard client disconnected. Total:", clients.size);
    });
});

// ------- DASHBOARD HTML -------
app.get("/dashboard", (req, res) => {
    res.sendFile(path.join(__dirname, "dashboard.html"));
});

// ------- IMPORTANT: Redirect root to dashboard -------
app.get("/", (req, res) => {
    res.redirect("/dashboard");
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(" Backend server running on http://localhost:" + PORT);
});