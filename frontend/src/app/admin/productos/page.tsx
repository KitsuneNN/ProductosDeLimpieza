"use client";

// Gestión de productos (F-T3): stock visible SOLO aquí
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, formatearPrecio } from "@/lib/api";
import type { ProductoAdminPublic, ProductosAdminResponse } from "@/types";
import { Boton, Cargando, ErrorBox } from "@/components/ui";

export default function ProductosAdmin() {
  const router = useRouter();
  const [productos, setProductos] = useState<ProductoAdminPublic[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busqueda, setBusqueda] = useState("");

  const cargar = useCallback(async () => {
    try {
      const res = await api.get<ProductosAdminResponse>("/admin/productos", {
        busqueda: busqueda || undefined,
        page: 1,
        page_size: 100,
      });
      setProductos(res.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudieron cargar los productos");
    } finally {
      setCargando(false);
    }
  }, [busqueda]);

  useEffect(() => {
    const t = setTimeout(cargar, 250);
    return () => clearTimeout(t);
  }, [cargar]);

  const toggleEstado = async (p: ProductoAdminPublic) => {
    const nuevoEstado = p.estado === "activo" ? "pausado" : "activo";
    await api.patch<ProductoAdminPublic>(`/admin/productos/${p.id}/estado`, {
      estado: nuevoEstado,
    });
    cargar();
  };

  const eliminar = async (p: ProductoAdminPublic) => {
    if (!confirm(`¿Eliminar "${p.nombre}"? Esta acción no se puede deshacer.`)) return;
    try {
      await api.del(`/admin/productos/${p.id}`);
      cargar();
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "No se pudo eliminar");
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-extrabold text-sky-900">Productos</h1>
        <Boton onClick={() => router.push("/admin/productos/nuevo")}>+ Nuevo</Boton>
      </div>

      <input
        type="search"
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        placeholder="Buscar producto…"
        aria-label="Buscar producto"
        className="min-h-[44px] w-full rounded-xl border-2 border-slate-300 bg-white px-3 text-base focus:border-sky-600 focus:outline-none"
      />

      {error && <ErrorBox mensaje={error} />}

      {cargando ? (
        <Cargando />
      ) : productos.length === 0 ? (
        <p className="py-10 text-center text-slate-500">No hay productos cargados.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {productos.map((p) => (
            <li
              key={p.id}
              className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3"
            >
              {p.imagen_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={p.imagen_url} alt="" className="h-14 w-14 rounded-xl object-cover" />
              ) : (
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-sky-50 text-2xl">
                  📦
                </div>
              )}
              <div className="flex flex-1 flex-col">
                <p className="text-sm font-extrabold text-slate-900">{p.nombre}</p>
                <p className="text-xs text-slate-500">
                  {formatearPrecio(p.precio)} ·{" "}
                  <span className={p.stock_actual === 0 ? "font-extrabold text-red-600" : ""}>
                    Stock: {p.stock_actual}
                  </span>{" "}
                  ·{" "}
                  <span className={p.estado === "activo" ? "text-emerald-700" : "text-amber-600"}>
                    {p.estado === "activo" ? "Activo" : "Pausado"}
                  </span>
                </p>
              </div>
              <div className="flex flex-col gap-1">
                <button
                  type="button"
                  onClick={() => router.push(`/admin/productos/${p.id}`)}
                  className="min-h-[40px] rounded-lg bg-sky-100 px-3 text-xs font-extrabold text-sky-800"
                >
                  Editar
                </button>
                <button
                  type="button"
                  onClick={() => toggleEstado(p)}
                  className="min-h-[40px] rounded-lg bg-slate-100 px-3 text-xs font-extrabold text-slate-700"
                >
                  {p.estado === "activo" ? "Pausar" : "Activar"}
                </button>
                <button
                  type="button"
                  onClick={() => eliminar(p)}
                  className="min-h-[40px] rounded-lg bg-red-50 px-3 text-xs font-extrabold text-red-600"
                >
                  Eliminar
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
