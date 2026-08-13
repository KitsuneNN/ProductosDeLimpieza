"use client";

// Pedidos del admin con filtro por estado (F-T3)
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, formatearFecha, formatearPrecio } from "@/lib/api";
import { useTiempoReal } from "@/lib/ws";
import type { EstadoSolicitud, SolicitudAdminPublic, SolicitudesAdminResponse } from "@/types";
import { BadgeSolicitud, Cargando, ErrorBox } from "@/components/ui";

const FILTROS: { id: string; texto: string }[] = [
  { id: "", texto: "Todas" },
  { id: "pendiente", texto: "Pendientes" },
  { id: "pagada", texto: "Pagadas" },
  { id: "cancelada", texto: "Canceladas" },
];

export default function SolicitudesAdmin() {
  const router = useRouter();
  const [filtro, setFiltro] = useState("");
  const [solicitudes, setSolicitudes] = useState<SolicitudAdminPublic[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      const res = await api.get<SolicitudesAdminResponse>("/admin/solicitudes", {
        estado: filtro || undefined,
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
  }, [filtro]);

  useEffect(() => {
    cargar();
    const intervalo = setInterval(cargar, 10000);
    return () => clearInterval(intervalo);
  }, [cargar]);

  useTiempoReal((evento) => {
    if (
      evento.evento === "solicitud.creada" ||
      evento.evento === "solicitud.pagada" ||
      evento.evento === "solicitud.cancelada"
    ) {
      void cargar();
    }
  });

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-extrabold text-sky-900">Pedidos</h1>

      <div className="flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Filtrar por estado">
        {FILTROS.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setFiltro(f.id)}
            className={`min-h-[44px] whitespace-nowrap rounded-full px-4 text-sm font-bold ${
              filtro === f.id ? "bg-sky-700 text-white" : "bg-white text-sky-800 shadow-sm"
            }`}
          >
            {f.texto}
          </button>
        ))}
      </div>

      {error && <ErrorBox mensaje={error} />}

      {cargando ? (
        <Cargando />
      ) : solicitudes.length === 0 ? (
        <p className="py-10 text-center text-slate-500">No hay pedidos en esta vista.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {solicitudes.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => router.push(`/admin/solicitudes/${s.id}`)}
                className="w-full rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-colors hover:border-sky-400 focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-300"
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-base font-extrabold text-slate-900">
                    #{s.id} · {s.usuario.nombre}
                  </p>
                  <BadgeSolicitud valor={s.estado as EstadoSolicitud} />
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {formatearFecha(s.creado_en)} · {s.items.length} producto(s)
                </p>
                <p className="mt-2 text-base font-extrabold text-sky-800">
                  {formatearPrecio(s.total)}
                </p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
