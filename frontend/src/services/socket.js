

import { io } from "socket.io-client";

export const createSocket = () =>
  io(
    import.meta.env.VITE_SOCKET_URL || "http://localhost:3001",
    {
      transports: ["polling", "websocket"],
      withCredentials: true,
    }
  );