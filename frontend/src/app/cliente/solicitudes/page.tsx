"use client";

// Mis solicitudes (F-T2) — se actualiza en vivo vía WS y polling
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, formatearFecha, formatearPrecio } from "@/lib/api";
import { useTiempoReal } from "@/lib/ws";
import type { SolicitudPublic, SolicitudesResponse } from "@/types";
import { BadgeSolicitud, Cargando, ErrorBox, ExitoBox } from "@/components/ui";

export default function MisSolicitudes() {
  const router = useRouter();
  const [solicitudes, setSolicitudes] = useState<SolicitudPublic[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nuevaId, setNuevaId] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      const res = await api.get<SolicitudesResponse>("/solicitudes/mias", {
        page: 1,
        page_size: 50,
      });
      setSolicitudes(res.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudieron cargar los pedidos");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const nueva = params.get("nueva");
    if (nueva) {
      setNuevaId(nueva);
      router.replace("/cliente/solicitudes");
    }
    cargar();
    const intervalo = setInterval(cargar, 10000);
    return () => clearInterval(intervalo);
  }, [cargar, router]);

  useTiempoReal((evento) => {
    if (evento.evento === "solicitud.pagada" || evento.evento === "solicitud.cancelada") {
      cargar();
    }
  });

  if (cargando) return <Cargando />;

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-extrabold text-sky-900">Mis pedidos</h1>

      {nuevaId && (
        <ExitoBox mensaje={`¡Pedido #${nuevaId} enviado! El local ya lo está preparando.`} />
      )}
      {error && <ErrorBox mensaje={error} />}

      {solicitudes.length === 0 ? (
        <p className="py-10 text-center text-slate-500">Todavía no hiciste pedidos.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {solicitudes.map((s) => (
            <li key={s.id} className="rounded-2xl border border-slate-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-extrabold text-slate-900">
                  Pedido #{s.id}
                </p>
                <BadgeSolicitud valor={s.estado} />
              </div>
              <p className="mt-1 text-xs text-slate-500">
                {formatearFecha(s.creado_en)}
              </p>
              <ul className="mt-2 flex flex-col gap-1 text-sm text-slate-700">
                {s.items.map((item) => (
                  <li key={item.producto_id} className="flex justify-between">
                    <span>
                      {item.cantidad} × {item.nombre_producto}
                    </span>
                    <span className="font-semibold">
                      {formatearPrecio(item.precio_unitario * item.cantidad)}
                    </span>
                  </li>
                ))}
              </ul>
              <p className="mt-2 border-t border-slate-100 pt-2 text-right text-base font-extrabold text-sky-800">
                Total: {formatearPrecio(s.total)}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
