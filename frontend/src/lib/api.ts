// Cliente HTTP tipado contra la API FastAPI (F-T1)
// Las rutas relativas /api/* se resuelven contra el mismo origen
// (en dev, Next.js las proxea al backend vía rewrites).
import type { FaltanteInfo } from "@/types";
import { getToken, limpiarSesion } from "./auth";

const BASE = "/api";

export class ApiError extends Error {
  status: number;
  faltantes?: FaltanteInfo[];

  constructor(mensaje: string, status: number, faltantes?: FaltanteInfo[]) {
    super(mensaje);
    this.status = status;
    this.faltantes = faltantes;
  }
}

async function peticion<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {};
  const esFormData = opciones.body instanceof FormData;
  if (opciones.body && !esFormData) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const respuesta = await fetch(`${BASE}${ruta}`, { ...opciones, headers });

  if (respuesta.status === 401 && !ruta.startsWith("/auth/")) {
    limpiarSesion();
    if (typeof window !== "undefined") window.location.href = "/cliente/login";
    throw new ApiError("Sesión expirada", 401);
  }
  if (!respuesta.ok) {
    let cuerpo: { detail?: string; faltantes?: FaltanteInfo[] } | null = null;
    try {
      cuerpo = await respuesta.json();
    } catch {
      // respuesta sin cuerpo JSON
    }
    throw new ApiError(
      cuerpo?.detail ?? `Error ${respuesta.status}`,
      respuesta.status,
      cuerpo?.faltantes,
    );
  }
  if (respuesta.status === 204) return undefined as T;
  return (await respuesta.json()) as T;
}

type Params = Record<string, string | number | boolean | undefined>;

export const api = {
  get: <T>(ruta: string, params?: Params) => {
    const qs = params
      ? "?" +
        new URLSearchParams(
          Object.entries(params)
            .filter(([, v]) => v !== undefined)
            .map(([k, v]) => [k, String(v)]),
        ).toString()
      : "";
    return peticion<T>(ruta + qs);
  },
  post: <T>(ruta: string, cuerpo?: unknown) =>
    peticion<T>(ruta, {
      method: "POST",
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    }),
  put: <T>(ruta: string, cuerpo?: unknown) =>
    peticion<T>(ruta, { method: "PUT", body: JSON.stringify(cuerpo) }),
  patch: <T>(ruta: string, cuerpo?: unknown) =>
    peticion<T>(ruta, { method: "PATCH", body: JSON.stringify(cuerpo) }),
  del: <T>(ruta: string) => peticion<T>(ruta, { method: "DELETE" }),
  subirImagen: <T>(ruta: string, archivo: File) => {
    const form = new FormData();
    form.append("archivo", archivo);
    return peticion<T>(ruta, { method: "POST", body: form });
  },
};

export function formatearPrecio(valor: number): string {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
    maximumFractionDigits: 2,
  }).format(valor);
}

export function formatearFecha(iso: string): string {
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
