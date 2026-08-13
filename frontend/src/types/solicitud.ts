// Espejo de backend/app/schemas/solicitud.py (Regla 5)
import type { EstadoSolicitud } from "./common";
import type { UsuarioPublic } from "./usuario";

export interface ItemSolicitudCreate {
  producto_id: number;
  cantidad: number;
}

export interface SolicitudCreate {
  items: ItemSolicitudCreate[];
}

export interface DetalleSolicitudPublic {
  producto_id: number;
  nombre_producto: string;
  cantidad: number;
  precio_unitario: number;
}

export interface SolicitudPublic {
  id: number;
  usuario_id: number;
  estado: EstadoSolicitud;
  total: number;
  creado_en: string; // ISO 8601
  pagada_en: string | null; // ISO 8601 | null
  items: DetalleSolicitudPublic[];
}

export interface SolicitudAdminPublic extends SolicitudPublic {
  usuario: UsuarioPublic;
}

export interface SolicitudesResponse {
  items: SolicitudPublic[];
  page: number;
  page_size: number;
  total: number;
}

export interface SolicitudesAdminResponse {
  items: SolicitudAdminPublic[];
  page: number;
  page_size: number;
  total: number;
}

export interface PagoResponse {
  solicitud_id: number;
  estado: "pagada";
  total: number;
  pagada_en: string; // ISO 8601
  unidades_descontadas: number;
}

export interface FaltanteInfo {
  producto_id: number;
  nombre: string;
  solicitado: number;
  disponible: number;
}

export interface FaltantesResponse {
  detail: string;
  faltantes: FaltanteInfo[];
}
