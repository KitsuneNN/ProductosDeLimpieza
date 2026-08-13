"use client";

// Detalle de producto + agregar al carrito (F-T2)
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError, formatearPrecio } from "@/lib/api";
import { agregarAlCarrito } from "@/lib/cart";
import type { ProductoClientePublic } from "@/types";
import { BadgeDisponibilidad, Boton, Cargando, ErrorBox } from "@/components/ui";

export default function DetalleProducto() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [producto, setProducto] = useState<ProductoClientePublic | null>(null);
  const [cantidad, setCantidad] = useState(1);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aviso, setAviso] = useState(false);

  useEffect(() => {
    api
      .get<ProductoClientePublic>(`/catalogo/${params.id}`)
      .then((p) => {
        setProducto(p);
        setCantidad(p.disponibilidad === "sin_stock" ? 0 : 1);
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar"),
      )
      .finally(() => setCargando(false));
  }, [params.id]);

  if (cargando) return <Cargando />;
  if (error || !producto) return <ErrorBox mensaje={error ?? "Producto no disponible"} />;

  const sinStock = producto.disponibilidad === "sin_stock";

  const agregar = () => {
    agregarAlCarrito({
      producto_id: producto.id,
      nombre: producto.nombre,
      precio: producto.precio,
      imagen_url: producto.imagen_url,
      cantidad,
    });
    setAviso(true);
    setTimeout(() => setAviso(false), 2500);
  };

  return (
    <div className="flex flex-col gap-4">
      <Link
        href="/cliente/catalogo"
        className="min-h-[44px] text-sm font-bold text-sky-800 underline underline-offset-4"
      >
        ← Volver al catálogo
      </Link>

      {producto.imagen_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={producto.imagen_url}
          alt={producto.nombre}
          className="h-64 w-full rounded-2xl object-cover"
        />
      ) : (
        <div className="flex h-64 w-full items-center justify-center rounded-2xl bg-sky-50 text-7xl">
          🧴
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-slate-900">{producto.nombre}</h1>
        <BadgeDisponibilidad valor={producto.disponibilidad} />
      </div>

      {producto.descripcion && (
        <p className="text-base text-slate-600">{producto.descripcion}</p>
      )}

      <p className="text-2xl font-extrabold text-sky-800">
        {formatearPrecio(producto.precio)}
      </p>

      {!sinStock && (
        <div className="flex items-center gap-4">
          <span className="text-sm font-bold text-slate-600">Cantidad</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCantidad((c) => Math.max(1, c - 1))}
              className="h-11 w-11 rounded-xl border-2 border-sky-700 bg-white text-xl font-extrabold text-sky-800"
              aria-label="Disminuir cantidad"
            >
              −
            </button>
            <span className="w-10 text-center text-xl font-extrabold" aria-live="polite">
              {cantidad}
            </span>
            <button
              type="button"
              onClick={() => setCantidad((c) => Math.min(999, c + 1))}
              className="h-11 w-11 rounded-xl border-2 border-sky-700 bg-white text-xl font-extrabold text-sky-800"
              aria-label="Aumentar cantidad"
            >
              +
            </button>
          </div>
        </div>
      )}

      {aviso && (
        <div role="status" className="rounded-xl border-2 border-emerald-300 bg-emerald-50 px-4 py-2 text-sm font-bold text-emerald-800">
          ✓ Agregado al carrito
        </div>
      )}

      <div className="mt-2 flex flex-col gap-3">
        <Boton onClick={agregar} disabled={sinStock} className="py-4 text-lg">
          {sinStock ? "Producto sin stock" : `Agregar ${cantidad} al carrito`}
        </Boton>
        <Boton variante="secundario" onClick={() => router.push("/cliente/carrito")}>
          Ir al carrito
        </Boton>
      </div>
    </div>
  );
}
