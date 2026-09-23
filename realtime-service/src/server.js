import "dotenv/config";
import crypto from "node:crypto";
import express from "express";
import cors from "cors";
import { createServer } from "node:http";
import { Server } from "socket.io";

const app = express();
const port = Number(process.env.PORT || 3001);
const frontendUrl = process.env.FRONTEND_URL || "http://localhost:5173";
const apiKey = process.env.BACKEND_API_KEY || "";
app.use(cors({ origin: frontendUrl, methods: ["GET", "POST"], credentials: true }));
app.use(express.json({ limit: "100kb" }));
const server = createServer(app);
const io = new Server(server, { cors: { origin: frontendUrl, methods: ["GET", "POST"], credentials: true } });

function authorized(request) {
  const supplied = request.get("X-Backend-Key") || "";
  return apiKey.length > 0 && supplied.length === apiKey.length && crypto.timingSafeEqual(Buffer.from(supplied), Buffer.from(apiKey));
}

app.get("/health", (_request, response) => response.json({ status: "healthy" }));
app.post("/internal/broadcast", (request, response) => {
  if (!authorized(request)) return response.status(401).json({ detail: "Unauthorized" });
  const { event, data } = request.body || {};
  if (event !== "sheet_updated" || !Array.isArray(data)) return response.status(400).json({ detail: "Invalid broadcast payload" });
  io.emit("sheet_updated", data);
  return response.json({ delivered: true, clients: io.engine.clientsCount });
});
io.on("connection", (socket) => {
  console.log(`Socket connected: ${socket.id}`);

  socket.on("disconnect", (reason) => {
    console.log(
      `Socket disconnected: ${socket.id} - ${reason}`
    );
  });

  socket.on("error", (error) => {
    console.error(
      `Socket error: ${socket.id}`,
      error
    );
  });
});
server.listen(port, () => console.log(`Realtime service listening on ${port}`));

