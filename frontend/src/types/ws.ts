// Tipos de eventos WebSocket — espejo de docs/WS_EVENTS.md (contrato ARQ-T2)
import type { Disponibilidad } from "./common";

export interface ResumenProductoWs {
  producto_id: number;
  nombre: string;
  cantidad: number;
}

export interface SolicitudCreadaDatos {
  solicitud_id: number;
  usuario: { id: number; nombre: string };
  total: number;
  creado_en: string; // ISO 8601
  resumen: ResumenProductoWs[];
}

export interface SolicitudPagadaDatos {
  solicitud_id: number;
  usuario_id: number;
  pagada_en: string; // ISO 8601
}

export interface SolicitudCanceladaDatos {
  solicitud_id: number;
  usuario_id: number;
  por: "cliente" | "admin";
}

export interface StockActualizadoDatos {
  // SOLO etiquetas — nunca números de stock (requisito 3.5)
  productos: { producto_id: number; disponibilidad: Disponibilidad }[];
}

export type WsEvento =
  | { evento: "solicitud.creada"; datos: SolicitudCreadaDatos }
  | { evento: "solicitud.pagada"; datos: SolicitudPagadaDatos }
  | { evento: "solicitud.cancelada"; datos: SolicitudCanceladaDatos }
  | { evento: "stock.actualizado"; datos: StockActualizadoDatos };
