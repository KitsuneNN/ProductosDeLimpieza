// Sesión del usuario en localStorage (F-T1)
// Acceso blindado: en iframes sandboxeados sin allow-same-origin el acceso a
// localStorage LANZA SecurityError — nunca debe tumbar la app.
import type { UsuarioPublic } from "@/types";

const CLAVE_TOKEN = "pl_token";
const CLAVE_USUARIO = "pl_usuario";

function leer(clave: string): string | null {
  try {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(clave);
  } catch {
    return null;
  }
}

function escribir(clave: string, valor: string): void {
  try {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(clave, valor);
  } catch {
    // sin persistencia disponible: la sesión vive solo en memoria de React
  }
}

function borrar(clave: string): void {
  try {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(clave);
  } catch {
    // nada que borrar
  }
}

export function getToken(): string | null {
  return leer(CLAVE_TOKEN);
}

export function getUsuario(): UsuarioPublic | null {
  try {
    const crudo = leer(CLAVE_USUARIO);
    return crudo ? (JSON.parse(crudo) as UsuarioPublic) : null;
  } catch {
    return null;
  }
}

export function guardarSesion(token: string, usuario: UsuarioPublic): void {
  escribir(CLAVE_TOKEN, token);
  escribir(CLAVE_USUARIO, JSON.stringify(usuario));
}

export function limpiarSesion(): void {
  borrar(CLAVE_TOKEN);
  borrar(CLAVE_USUARIO);
}

export function destinoSegunRol(usuario: UsuarioPublic): string {
  return usuario.rol === "admin" ? "/admin/dashboard" : "/cliente/catalogo";
}
