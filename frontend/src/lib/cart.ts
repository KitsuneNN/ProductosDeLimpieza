// Carrito de compras persistente (F-T2)
export interface ItemCarrito {
  producto_id: number;
  nombre: string;
  precio: number;
  imagen_url: string | null;
  cantidad: number;
}

const CLAVE = "pl_carrito";

export function leerCarrito(): ItemCarrito[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(CLAVE) ?? "[]") as ItemCarrito[];
  } catch {
    return [];
  }
}

function guardar(items: ItemCarrito[]): void {
  localStorage.setItem(CLAVE, JSON.stringify(items));
}

export function agregarAlCarrito(item: ItemCarrito): void {
  const items = leerCarrito();
  const indice = items.findIndex((i) => i.producto_id === item.producto_id);
  if (indice >= 0) {
    items[indice].cantidad += item.cantidad;
  } else {
    items.push(item);
  }
  guardar(items);
}

export function cambiarCantidad(producto_id: number, cantidad: number): void {
  const items = leerCarrito()
    .map((i) => (i.producto_id === producto_id ? { ...i, cantidad } : i))
    .filter((i) => i.cantidad > 0);
  guardar(items);
}

export function quitarDelCarrito(producto_id: number): void {
  guardar(leerCarrito().filter((i) => i.producto_id !== producto_id));
}

export function vaciarCarrito(): void {
  localStorage.removeItem(CLAVE);
}

export function totalCarrito(items: ItemCarrito[]): number {
  return items.reduce((suma, i) => suma + i.precio * i.cantidad, 0);
}

export function unidadesCarrito(items: ItemCarrito[]): number {
  return items.reduce((suma, i) => suma + i.cantidad, 0);
}
