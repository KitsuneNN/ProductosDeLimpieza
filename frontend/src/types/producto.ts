// Espejo de backend/app/schemas/producto.py (Regla 5)
//
// REGLA DE ORO DEL NEGOCIO:
// - stock_actual SOLO existe en ProductoAdminPublic (vista admin).
// - El cliente recibe ProductoClientePublic con la etiqueta `disponibilidad`.
// - Montos: número (float) en JSON; precisión Decimal del lado servidor.
import type { Disponibilidad, EstadoProducto } from "./common";

export interface ProductoAdminPublic {
  id: number;
  categoria_id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  stock_actual: number;
  imagen_url: string | null;
  estado: EstadoProducto;
  creado_en: string; // ISO 8601
  actualizado_en: string; // ISO 8601
}

export interface ProductoCreate {
  categoria_id: number;
  nombre: string;
  descripcion?: string | null;
  precio: number;
  stock_actual?: number;
  imagen_url?: string | null;
  estado?: EstadoProducto;
}

export interface ProductoUpdate {
  categoria_id?: number;
  nombre?: string;
  descripcion?: string | null;
  precio?: number;
  stock_actual?: number;
  imagen_url?: string | null;
  estado?: EstadoProducto;
}

export interface ProductoEstadoUpdate {
  estado: EstadoProducto;
}

export interface ProductoClientePublic {
  id: number;
  categoria_id: number;
  nombre: string;
  descripcion: string | null;
  precio: number;
  imagen_url: string | null;
  disponibilidad: Disponibilidad;
}

export interface ProductosAdminResponse {
  items: ProductoAdminPublic[];
  page: number;
  page_size: number;
  total: number;
}
