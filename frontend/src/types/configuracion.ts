// Espejo de backend/app/schemas/configuracion.py (Regla 5)
export interface ConfiguracionPublic {
  clave: string;
  valor: string;
}

export interface ConfiguracionUpdate {
  valor: string;
}

export interface UmbralResponse {
  umbral_pocas_unidades: number;
}
