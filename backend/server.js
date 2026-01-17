import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ---- In-memory storage for live dashboard ----
const clients = new Set();       // SSE connections
const lastAlerts = [];           // keeps recent alerts (for page refresh)
const MAX_ALERTS = 50;

const app = express();
app.use(cors());
app.use(express.json());


app.post("/alert", (req, res) => {
    console.log(" ALERT RECEIVED FROM EDGE:");
    console.log(req.body);
    // Store last alerts
    lastAlerts.unshift(req.body);
    if (lastAlerts.length > MAX_ALERTS) lastAlerts.pop();
    // Broadcast to SSE clients
    const payload = `data: ${JSON.stringify(req.body)}\n\n`;
    for (const client of clients) {
        client.write(payload);
    }
    res.json({ status: "ok" });
});

app.get("/events", (req, res) => {
    // SSE headers
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders?.();

    // Send existing alerts on connect (so refresh shows history)
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


app.get("/dashboard", (req, res) => {
    res.sendFile(path.join(__dirname, "dashboard.html"));
});


app.get("/", (req, res) => {
    res.send("SmartHealth Backend is running");
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(" Backend server running on http://localhost:" + PORT);
});
