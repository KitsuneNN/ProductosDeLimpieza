// Espejo de backend/app/schemas/categoria.py (Regla 5)
export interface CategoriaPublic {
  id: number;
  nombre: string;
  orden: number;
}

export interface CategoriaCreate {
  nombre: string;
  orden?: number;
}

export interface CategoriaUpdate {
  nombre?: string;
  orden?: number;
}
