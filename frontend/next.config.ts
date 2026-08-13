import type { NextConfig } from "next";

// En producción, apuntar a la API desplegada (Render) vía variable de entorno.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_URL}/api/:path*` },
      { source: "/uploads/:path*", destination: `${API_URL}/uploads/:path*` },
      { source: "/ws", destination: `${API_URL}/ws` },
    ];
  },
};

export default nextConfig;
