"use client";

// Dashboard del admin: pedidos pendientes + aviso sonoro en vivo (F-T3)
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, formatearFecha, formatearPrecio } from "@/lib/api";
import { desbloquearAudio, tocarAviso } from "@/lib/sonido";
import { useTiempoReal, type EstadoWs } from "@/lib/ws";
import type { SolicitudAdminPublic, SolicitudesAdminResponse } from "@/types";
import { Boton, Cargando, ErrorBox } from "@/components/ui";

const ETIQUETA_WS: Record<EstadoWs, string> = {
  conectando: "Conectando…",
  conectado: "EN VIVO",
  reintentando: "Reconectando…",
  sin_token: "Sin conexión",
};

export default function Dashboard() {
  const router = useRouter();
  const [pendientes, setPendientes] = useState<SolicitudAdminPublic[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nueva, setNueva] = useState<SolicitudAdminPublic | null>(null);

  const cargar = useCallback(async () => {
    try {
      const res = await api.get<SolicitudesAdminResponse>("/admin/solicitudes", {
        estado: "pendiente",
        page: 1,
        page_size: 20,
      });
      setPendientes(res.items);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudieron cargar los pedidos");
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    desbloquearAudio(); // primera interacción habilita el sonido
    cargar();
    const intervalo = setInterval(cargar, 10000); // respaldo si el WS falla
    return () => clearInterval(intervalo);
  }, [cargar]);

  const estadoWs = useTiempoReal((evento) => {
    if (evento.evento === "solicitud.creada") {
      tocarAviso();
      void cargar().then(() => {
        // marcar la nueva para resaltarla
        setNueva((prev) => prev ?? null);
      });
      // construir vista rápida de la nueva solicitud
      setNueva({
        id: evento.datos.solicitud_id,
        usuario_id: evento.datos.usuario.id,
        estado: "pendiente",
        total: evento.datos.total,
        creado_en: evento.datos.creado_en,
        pagada_en: null,
        items: evento.datos.resumen.map((r) => ({
          producto_id: r.producto_id,
          nombre_producto: r.nombre,
          cantidad: r.cantidad,
          precio_unitario: 0,
        })),
        usuario: {
          id: evento.datos.usuario.id,
          nombre: evento.datos.usuario.nombre,
          telefono: "",
          email: "",
          rol: "cliente",
          creado_en: evento.datos.creado_en,
        },
      });
      setTimeout(() => setNueva(null), 12000);
    }
    if (evento.evento === "solicitud.pagada" || evento.evento === "solicitud.cancelada") {
      void cargar();
    }
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-extrabold text-sky-900">Pedidos pendientes</h1>
        <span
          className={`rounded-full px-3 py-1 text-xs font-extrabold ${
            estadoWs === "conectado"
              ? "bg-emerald-100 text-emerald-800"
              : "bg-slate-100 text-slate-500"
          }`}
        >
          {estadoWs === "conectado" ? "🟢" : "🟡"} {ETIQUETA_WS[estadoWs]}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <Boton
          variante="secundario"
          onClick={() => {
            desbloquearAudio();
            tocarAviso();
          }}
        >
          🔊 Probar sonido
        </Boton>
        <p className="text-xs text-slate-500">
          Dejá esta pantalla abierta: sonará al recibir un pedido.
        </p>
      </div>

      {nueva && (
        <div
          role="alert"
          className="animate-pulse rounded-2xl border-4 border-red-500 bg-red-50 p-4"
        >
          <p className="text-lg font-extrabold text-red-700">
            🛎️ ¡NUEVO PEDIDO! #{nueva.id} — {nueva.usuario.nombre}
          </p>
          <p className="text-sm font-bold text-red-600">
            Total: {formatearPrecio(nueva.total)}
          </p>
          <Boton
            variante="peligro"
            className="mt-2"
            onClick={() => router.push(`/admin/solicitudes/${nueva.id}`)}
          >
            Ver y cobrar
          </Boton>
        </div>
      )}

      {error && <ErrorBox mensaje={error} />}

      {cargando ? (
        <Cargando />
      ) : pendientes.length === 0 ? (
        <p className="py-10 text-center text-slate-500">
          No hay pedidos pendientes. ¡Todo al día! 🎉
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {pendientes.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                onClick={() => router.push(`/admin/solicitudes/${s.id}`)}
                className="w-full rounded-2xl border-2 border-sky-200 bg-white p-4 text-left shadow-sm transition-colors hover:border-sky-500 focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-300"
              >
                <div className="flex items-center justify-between">
                  <p className="text-base font-extrabold text-slate-900">
                    #{s.id} · {s.usuario.nombre}
                  </p>
                  <p className="text-base font-extrabold text-sky-800">
                    {formatearPrecio(s.total)}
                  </p>
                </div>
                <p className="mt-1 text-xs text-slate-500">{formatearFecha(s.creado_en)}</p>
                <p className="mt-2 text-sm text-slate-700">
                  {s.items.map((i) => `${i.cantidad}× ${i.nombre_producto}`).join(" · ")}
                </p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
