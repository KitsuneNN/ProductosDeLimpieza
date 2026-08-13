// Espejo de backend/app/schemas/catalogo.py (Regla 5)
import type { CategoriaPublic } from "./categoria";
import type { ProductoClientePublic } from "./producto";

export interface CategoriasResponse {
  items: CategoriaPublic[];
}

export interface CatalogoResponse {
  items: ProductoClientePublic[];
  page: number;
  page_size: number;
  total: number;
}
