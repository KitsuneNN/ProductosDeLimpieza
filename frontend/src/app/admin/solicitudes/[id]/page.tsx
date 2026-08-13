"use client";

// Detalle de pedido: cobrar ("Pagado") o cancelar (F-T3)
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError, formatearFecha, formatearPrecio } from "@/lib/api";
import { desbloquearAudio } from "@/lib/sonido";
import type { FaltanteInfo, PagoResponse, SolicitudAdminPublic } from "@/types";
import { BadgeSolicitud, Boton, Cargando, ErrorBox, ExitoBox } from "@/components/ui";

export default function DetalleSolicitud() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [solicitud, setSolicitud] = useState<SolicitudAdminPublic | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);
  const [faltantes, setFaltantes] = useState<FaltanteInfo[] | null>(null);
  const [ocupado, setOcupado] = useState(false);

  const cargar = useCallback(async () => {
    try {
      const s = await api.get<SolicitudAdminPublic>(`/admin/solicitudes/${params.id}`);
      setSolicitud(s);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el pedido");
    } finally {
      setCargando(false);
    }
  }, [params.id]);

  useEffect(() => {
    desbloquearAudio();
    cargar();
  }, [cargar]);

  const pagar = async () => {
    if (!solicitud) return;
    if (!confirm(`¿Cobrar y marcar como PAGADO el pedido #${solicitud.id} por ${formatearPrecio(solicitud.total)}? El stock se descontará automáticamente.`)) return;
    setOcupado(true);
    setError(null);
    setFaltantes(null);
    try {
      const res = await api.post<PagoResponse>(`/admin/solicitudes/${solicitud.id}/pagar`);
      setExito(
        `✅ Pedido #${solicitud.id} PAGADO — se descontaron ${res.unidades_descontadas} unidad(es) de stock.`,
      );
      cargar();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        if (err.faltantes && err.faltantes.length > 0) setFaltantes(err.faltantes);
        setError(err.message);
      } else {
        setError(err instanceof ApiError ? err.message : "No se pudo procesar el pago");
      }
    } finally {
      setOcupado(false);
    }
  };

  const cancelar = async () => {
    if (!solicitud) return;
    if (!confirm(`¿Cancelar el pedido #${solicitud.id}?`)) return;
    setOcupado(true);
    setError(null);
    try {
      await api.post(`/admin/solicitudes/${solicitud.id}/cancelar`);
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cancelar");
    } finally {
      setOcupado(false);
    }
  };

  if (cargando) return <Cargando />;
  if (error && !solicitud) return <ErrorBox mensaje={error} />;
  if (!solicitud) return null;

  return (
    <div className="flex flex-col gap-4">
      <Link
        href="/admin/solicitudes"
        className="min-h-[44px] text-sm font-bold text-sky-800 underline underline-offset-4"
      >
        ← Volver a pedidos
      </Link>

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-slate-900">Pedido #{solicitud.id}</h1>
        <BadgeSolicitud valor={solicitud.estado} />
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <p className="text-sm font-bold text-slate-900">👤 Cliente</p>
        <p className="text-base text-slate-700">{solicitud.usuario.nombre}</p>
        <p className="text-sm text-slate-500">📞 {solicitud.usuario.telefono || "sin teléfono"}</p>
        <p className="mt-2 text-xs text-slate-400">
          Recibido: {formatearFecha(solicitud.creado_en)}
          {solicitud.pagada_en ? ` · Pagado: ${formatearFecha(solicitud.pagada_en)}` : ""}
        </p>
      </div>

      <ul className="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-white p-4">
        {solicitud.items.map((item) => (
          <li key={item.producto_id} className="flex justify-between text-base">
            <span className="font-semibold text-slate-800">
              {item.cantidad} × {item.nombre_producto}
            </span>
            <span className="font-bold text-slate-600">
              {formatearPrecio(item.precio_unitario * item.cantidad)}
            </span>
          </li>
        ))}
        <li className="mt-2 flex justify-between border-t border-slate-200 pt-2 text-lg font-extrabold">
          <span className="text-slate-900">TOTAL</span>
          <span className="text-sky-800">{formatearPrecio(solicitud.total)}</span>
        </li>
      </ul>

      {error && <ErrorBox mensaje={error} />}
      {exito && <ExitoBox mensaje={exito} />}

      {faltantes && faltantes.length > 0 && (
        <div role="alert" className="rounded-2xl border-2 border-red-300 bg-red-50 p-4">
          <p className="text-sm font-extrabold text-red-800">
            ⚠️ Stock insuficiente para estos productos:
          </p>
          <ul className="mt-2 flex flex-col gap-1 text-sm text-red-700">
            {faltantes.map((f) => (
              <li key={f.producto_id}>
                • {f.nombre}: pidieron {f.solicitado}, hay {f.disponible}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-red-600">
            No se descontó nada. Ajustá el stock en Productos o cancelá el pedido.
          </p>
        </div>
      )}

      {solicitud.estado === "pendiente" && (
        <div className="flex flex-col gap-3">
          <Boton variante="exito" onClick={pagar} disabled={ocupado} className="py-5 text-xl">
            💵 Marcar como PAGADO
          </Boton>
          <Boton variante="peligro" onClick={cancelar} disabled={ocupado}>
            Cancelar pedido
          </Boton>
        </div>
      )}

      <button
        type="button"
        onClick={() => router.push("/admin/dashboard")}
        className="text-center text-sm font-bold text-slate-500 underline underline-offset-4"
      >
        Ir al panel
      </button>
    </div>
  );
}
