"use client";

// Catálogo del cliente: categorías, búsqueda, etiquetas en vivo (F-T2)
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { agregarAlCarrito, leerCarrito, unidadesCarrito } from "@/lib/cart";
import { useTiempoReal } from "@/lib/ws";
import type { CatalogoResponse, CategoriaPublic, ProductoClientePublic } from "@/types";
import { ProductoCard } from "@/components/ProductoCard";
import { Cargando, ErrorBox } from "@/components/ui";

export default function Catalogo() {
  const router = useRouter();
  const [categorias, setCategorias] = useState<CategoriaPublic[]>([]);
  const [productos, setProductos] = useState<ProductoClientePublic[]>([]);
  const [categoriaSel, setCategoriaSel] = useState<number | undefined>();
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aviso, setAviso] = useState<string | null>(null);
  const [unidades, setUnidades] = useState(0);

  const cargar = useCallback(async (filtros?: { categoria?: number; texto?: string }) => {
    try {
      const [cat, catProd] = await Promise.all([
        api.get<{ items: CategoriaPublic[] }>("/categorias"),
        api.get<CatalogoResponse>("/catalogo", {
          categoria_id: filtros?.categoria ?? categoriaSel,
          busqueda: (filtros?.texto ?? busqueda) || undefined,
          page: 1,
          page_size: 100,
        }),
      ]);
      setCategorias(cat.items);
      setProductos(catProd.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el catálogo");
    } finally {
      setCargando(false);
    }
  }, [categoriaSel, busqueda]);

  useEffect(() => {
    cargar();
    setUnidades(unidadesCarrito(leerCarrito()));
    // Polling de respaldo (10s) si el WS no conecta
    const intervalo = setInterval(() => cargar(), 10000);
    return () => clearInterval(intervalo);
  }, [cargar]);

  useTiempoReal((evento) => {
    if (evento.evento === "stock.actualizado") {
      const porId = new Map(evento.datos.productos.map((p) => [p.producto_id, p.disponibilidad]));
      setProductos((prev) =>
        prev.map((p) =>
          porId.has(p.id) ? { ...p, disponibilidad: porId.get(p.id)! } : p,
        ),
      );
    }
  });

  const agregar = (p: ProductoClientePublic) => {
    agregarAlCarrito({
      producto_id: p.id,
      nombre: p.nombre,
      precio: p.precio,
      imagen_url: p.imagen_url,
      cantidad: 1,
    });
    setUnidades(unidadesCarrito(leerCarrito()));
    setAviso(`${p.nombre} agregado al carrito`);
    setTimeout(() => setAviso(null), 2500);
  };

  const buscar = (e: React.FormEvent) => {
    e.preventDefault();
    cargar({ texto: busqueda });
  };

  const elegirCategoria = (id?: number) => {
    setCategoriaSel(id);
    cargar({ categoria: id });
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-extrabold text-sky-900">Catálogo</h1>
        <button
          type="button"
          onClick={() => router.push("/cliente/carrito")}
          className="relative flex min-h-[44px] items-center gap-2 rounded-xl bg-white px-3 text-sm font-bold text-sky-800 shadow-sm"
        >
          🛒 Carrito
          {unidades > 0 && (
            <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[11px] font-extrabold text-white">
              {unidades}
            </span>
          )}
        </button>
      </div>

      <form onSubmit={buscar} className="flex gap-2">
        <input
          type="search"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          placeholder="Buscar producto…"
          aria-label="Buscar producto"
          className="min-h-[44px] w-full rounded-xl border-2 border-slate-300 bg-white px-3 text-base focus:border-sky-600 focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-200"
        />
        <button
          type="submit"
          className="min-h-[44px] rounded-xl bg-sky-700 px-4 font-bold text-white hover:bg-sky-800"
        >
          Buscar
        </button>
      </form>

      <div
        className="flex gap-2 overflow-x-auto pb-1"
        role="tablist"
        aria-label="Filtrar por categoría"
      >
        <button
          type="button"
          onClick={() => elegirCategoria(undefined)}
          className={`min-h-[44px] whitespace-nowrap rounded-full px-4 text-sm font-bold ${
            categoriaSel === undefined
              ? "bg-sky-700 text-white"
              : "bg-white text-sky-800 shadow-sm"
          }`}
        >
          Todas
        </button>
        {categorias.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => elegirCategoria(c.id)}
            className={`min-h-[44px] whitespace-nowrap rounded-full px-4 text-sm font-bold ${
              categoriaSel === c.id
                ? "bg-sky-700 text-white"
                : "bg-white text-sky-800 shadow-sm"
            }`}
          >
            {c.nombre}
          </button>
        ))}
      </div>

      {aviso && (
        <div
          role="status"
          className="rounded-xl border-2 border-emerald-300 bg-emerald-50 px-4 py-2 text-sm font-bold text-emerald-800"
        >
          ✓ {aviso}
        </div>
      )}

      {error && <ErrorBox mensaje={error} />}

      {cargando ? (
        <Cargando />
      ) : productos.length === 0 ? (
        <p className="py-10 text-center text-slate-500">
          No hay productos para mostrar.
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {productos.map((p) => (
            <ProductoCard
              key={p.id}
              producto={p}
              onAgregar={() => agregar(p)}
              onVer={() => router.push(`/cliente/producto/${p.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
