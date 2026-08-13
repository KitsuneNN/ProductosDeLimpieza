// Sesión del usuario en localStorage (F-T1)
import type { UsuarioPublic } from "@/types";

const CLAVE_TOKEN = "pl_token";
const CLAVE_USUARIO = "pl_usuario";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(CLAVE_TOKEN);
}

export function getUsuario(): UsuarioPublic | null {
  if (typeof window === "undefined") return null;
  try {
    const crudo = localStorage.getItem(CLAVE_USUARIO);
    return crudo ? (JSON.parse(crudo) as UsuarioPublic) : null;
  } catch {
    return null;
  }
}

export function guardarSesion(token: string, usuario: UsuarioPublic): void {
  localStorage.setItem(CLAVE_TOKEN, token);
  localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
}

export function limpiarSesion(): void {
  localStorage.removeItem(CLAVE_TOKEN);
  localStorage.removeItem(CLAVE_USUARIO);
}

export function destinoSegunRol(usuario: UsuarioPublic): string {
  return usuario.rol === "admin" ? "/admin/dashboard" : "/cliente/catalogo";
}
