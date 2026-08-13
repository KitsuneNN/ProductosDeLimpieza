"use client";

// Carrito + envío de la solicitud (F-T2)
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError, formatearPrecio } from "@/lib/api";
import {
  cambiarCantidad,
  leerCarrito,
  quitarDelCarrito,
  totalCarrito,
  vaciarCarrito,
  type ItemCarrito,
} from "@/lib/cart";
import type { SolicitudPublic } from "@/types";
import { Boton, ErrorBox } from "@/components/ui";

export default function Carrito() {
  const router = useRouter();
  const [items, setItems] = useState<ItemCarrito[]>([]);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setItems(leerCarrito());
  }, []);

  const total = totalCarrito(items);

  const enviar = async () => {
    setError(null);
    setEnviando(true);
    try {
      const solicitud = await api.post<SolicitudPublic>("/solicitudes", {
        items: items.map((i) => ({ producto_id: i.producto_id, cantidad: i.cantidad })),
      });
      vaciarCarrito();
      setItems([]);
      router.push(`/cliente/solicitudes?nueva=${solicitud.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo enviar el pedido");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-extrabold text-sky-900">Mi carrito</h1>

      {error && <ErrorBox mensaje={error} />}

      {items.length === 0 ? (
        <div className="flex flex-col items-center gap-4 py-10 text-center">
          <div className="text-6xl" aria-hidden>
            🛒
          </div>
          <p className="text-slate-600">Tu carrito está vacío.</p>
          <Boton onClick={() => router.push("/cliente/catalogo")}>
            Ver catálogo
          </Boton>
        </div>
      ) : (
        <>
          <ul className="flex flex-col gap-3">
            {items.map((item) => (
              <li
                key={item.producto_id}
                className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3"
              >
                {item.imagen_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={item.imagen_url}
                    alt=""
                    className="h-16 w-16 rounded-xl object-cover"
                  />
                ) : (
                  <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-sky-50 text-3xl">
                    🧴
                  </div>
                )}
                <div className="flex flex-1 flex-col">
                  <p className="text-sm font-bold text-slate-900">{item.nombre}</p>
                  <p className="text-sm font-semibold text-sky-800">
                    {formatearPrecio(item.precio)}
                  </p>
                  <div className="mt-1 flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        cambiarCantidad(item.producto_id, item.cantidad - 1);
                        setItems(leerCarrito());
                      }}
                      className="h-9 w-9 rounded-lg border-2 border-sky-700 text-lg font-extrabold text-sky-800"
                      aria-label={`Quitar una unidad de ${item.nombre}`}
                    >
                      −
                    </button>
                    <span className="w-8 text-center font-extrabold" aria-live="polite">
                      {item.cantidad}
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        cambiarCantidad(item.producto_id, item.cantidad + 1);
                        setItems(leerCarrito());
                      }}
                      className="h-9 w-9 rounded-lg border-2 border-sky-700 text-lg font-extrabold text-sky-800"
                      aria-label={`Agregar una unidad de ${item.nombre}`}
                    >
                      +
                    </button>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    quitarDelCarrito(item.producto_id);
                    setItems(leerCarrito());
                  }}
                  className="min-h-[44px] rounded-lg px-2 text-2xl text-red-500 hover:bg-red-50"
                  aria-label={`Quitar ${item.nombre} del carrito`}
                >
                  🗑️
                </button>
              </li>
            ))}
          </ul>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between text-lg font-extrabold text-slate-900">
              <span>Total</span>
              <span className="text-sky-800">{formatearPrecio(total)}</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Pagás en el mostrador cuando retirás tu pedido.
            </p>
          </div>

          <Boton onClick={enviar} disabled={enviando} className="py-4 text-lg">
            {enviando ? "Enviando pedido…" : "📨 Enviar pedido al local"}
          </Boton>

          <Link
            href="/cliente/catalogo"
            className="text-center text-sm font-bold text-sky-800 underline underline-offset-4"
          >
            Seguir mirando el catálogo
          </Link>
        </>
      )}
    </div>
  );
}
