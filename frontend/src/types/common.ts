// Tipos compartidos — espejo EXACTO de backend/app/schemas/common.py (Regla 5)
export type Disponibilidad = "disponible" | "pocas" | "sin_stock";
export type EstadoProducto = "activo" | "pausado";
export type EstadoSolicitud = "pendiente" | "pagada" | "cancelada";
export type RolUsuario = "cliente" | "admin";
export type TokenType = "bearer";

// Espejo de backend/app/schemas/common.py — HealthResponse
export interface HealthResponse {
  status: "ok";
}
