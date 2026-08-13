// Espejo de backend/app/schemas/auth.py — UsuarioPublic (Regla 5)
import type { RolUsuario } from "./common";

export interface UsuarioPublic {
  id: number;
  nombre: string;
  telefono: string;
  email: string;
  rol: RolUsuario;
  creado_en: string; // ISO 8601
}
