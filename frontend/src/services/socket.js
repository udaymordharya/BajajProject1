

import { io } from "socket.io-client";

export const createSocket = () =>
  io(
    import.meta.env.VITE_SOCKET_URL || window.location.origin,
    {
      transports: ["polling", "websocket"],
      withCredentials: true,
    }
  );
