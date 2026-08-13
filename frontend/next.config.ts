import type { NextConfig } from "next";

// En producción, apuntar a la API desplegada (Render) vía variable de entorno.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // El preview de Arena sirve la app bajo un host proxy (https://<puerto>-<id>.e2b.app).
  // Next.js 16 bloquea por defecto los recursos de desarrollo (chunks JS, HMR)
  // cuando el Origin difiere del host del dev server → página en blanco.
  // Esto autoriza explícitamente esos orígenes.
  allowedDevOrigins: ["*.e2b.app", "*.e2b.dev"],

  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API_URL}/api/:path*` },
      { source: "/uploads/:path*", destination: `${API_URL}/uploads/:path*` },
      { source: "/ws", destination: `${API_URL}/ws` },
    ];
  },
};

export default nextConfig;
