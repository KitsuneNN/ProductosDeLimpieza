import type { NextConfig } from "next";

// En producción, apuntar a la API desplegada (Render) vía variable de entorno.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Next.js 16 bloquea por defecto los recursos de desarrollo (chunks JS, HMR)
  // cuando el Origin del navegador no está permitido. Se necesitan:
  //  - "127.0.0.1" y "localhost": orígenes del navegador local (sin esto, React
  //    nunca hidrata → pantallas congeladas en "Cargando…").
  //  - "*.e2b.app" / "*.e2b.dev": hosts del preview de Arena (el dev server
  //    corre con --hostname 0.0.0.0 y el preview llega vía host proxy).
  allowedDevOrigins: ["*.e2b.app", "*.e2b.dev", "127.0.0.1", "localhost"],

  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_URL}/api/:path*` },
      { source: "/uploads/:path*", destination: `${API_URL}/uploads/:path*` },
      { source: "/ws", destination: `${API_URL}/ws` },
    ];
  },
};

export default nextConfig;
