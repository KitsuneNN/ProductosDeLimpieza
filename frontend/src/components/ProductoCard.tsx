"use client";

// Tarjeta de producto para el catálogo del cliente (F-T2)
import { formatearPrecio } from "@/lib/api";
import type { ProductoClientePublic } from "@/types";
import { BadgeDisponibilidad } from "./ui";

export function ProductoCard({
  producto,
  onAgregar,
  onVer,
}: {
  producto: ProductoClientePublic;
  onAgregar?: () => void;
  onVer?: () => void;
}) {
  const sinStock = producto.disponibilidad === "sin_stock";
  return (
    <article className="flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={onVer}
        className="text-left focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-300"
        aria-label={`Ver detalle de ${producto.nombre}`}
      >
        {producto.imagen_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={producto.imagen_url}
            alt={producto.nombre}
            className="h-36 w-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex h-36 w-full items-center justify-center bg-sky-50 text-5xl">
            🧴
          </div>
        )}
      </button>
      <div className="flex flex-1 flex-col gap-2 p-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-bold leading-snug text-slate-900">
            {producto.nombre}
          </h3>
          <BadgeDisponibilidad valor={producto.disponibilidad} />
        </div>
        <p className="text-base font-extrabold text-sky-800">
          {formatearPrecio(producto.precio)}
        </p>
        {onAgregar && (
          <button
            type="button"
            onClick={onAgregar}
            disabled={sinStock}
            className="mt-auto min-h-[44px] rounded-xl bg-sky-700 px-3 py-2 text-sm font-bold text-white transition-colors hover:bg-sky-800 active:bg-sky-900 disabled:bg-slate-300 disabled:text-slate-500"
            aria-label={`Agregar ${producto.nombre} al carrito`}
          >
            {sinStock ? "No disponible" : "+ Agregar"}
          </button>
        )}
      </div>
    </article>
  );
}
