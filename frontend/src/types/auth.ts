// Espejo de backend/app/schemas/auth.py (Regla 5)
import type { TokenType } from "./common";
import type { UsuarioPublic } from "./usuario";

export interface RegistroRequest {
  nombre: string;
  telefono: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: TokenType;
  usuario: UsuarioPublic;
}
