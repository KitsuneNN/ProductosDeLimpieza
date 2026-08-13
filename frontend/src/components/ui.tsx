"use client";

// Componentes UI base — botones táctiles ≥44px, alto contraste (Regla 13)
import type { Disponibilidad, EstadoSolicitud } from "@/types";

export function Boton({
  children,
  variante = "primario",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variante?: "primario" | "secundario" | "peligro" | "exito" | "fantasma";
}) {
  const estilos: Record<string, string> = {
    primario:
      "bg-sky-700 text-white hover:bg-sky-800 active:bg-sky-900 disabled:bg-slate-300",
    secundario:
      "bg-white text-sky-800 border-2 border-sky-700 hover:bg-sky-50 active:bg-sky-100 disabled:border-slate-300 disabled:text-slate-400",
    peligro:
      "bg-red-600 text-white hover:bg-red-700 active:bg-red-800 disabled:bg-slate-300",
    exito:
      "bg-emerald-600 text-white hover:bg-emerald-700 active:bg-emerald-800 disabled:bg-slate-300",
    fantasma:
      "bg-transparent text-sky-800 hover:bg-sky-50 active:bg-sky-100 disabled:text-slate-400",
  };
  return (
    <button
      className={`inline-flex min-h-[44px] items-center justify-center gap-2 rounded-xl px-4 py-2 text-base font-semibold transition-colors focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-300 ${estilos[variante]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Entrada({
  etiqueta,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { etiqueta: string }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-semibold text-slate-700">
        {etiqueta}
      </span>
      <input
        className="w-full min-h-[44px] rounded-xl border-2 border-slate-300 bg-white px-3 text-base text-slate-900 focus:border-sky-600 focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-200"
        {...props}
      />
    </label>
  );
}

export function AreaTexto({
  etiqueta,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { etiqueta: string }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-semibold text-slate-700">
        {etiqueta}
      </span>
      <textarea
        className="w-full rounded-xl border-2 border-slate-300 bg-white px-3 py-2 text-base text-slate-900 focus:border-sky-600 focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-200"
        {...props}
      />
    </label>
  );
}

const ESTILOS_DISPONIBILIDAD: Record<Disponibilidad, string> = {
  disponible: "bg-emerald-100 text-emerald-900 border-emerald-300",
  pocas: "bg-amber-100 text-amber-900 border-amber-400",
  sin_stock: "bg-slate-100 text-slate-500 border-slate-300",
};

const TEXTO_DISPONIBILIDAD: Record<Disponibilidad, string> = {
  disponible: "Disponible",
  pocas: "¡Pocas unidades!",
  sin_stock: "Sin stock",
};

export function BadgeDisponibilidad({
  valor,
}: {
  valor: Disponibilidad;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-bold ${ESTILOS_DISPONIBILIDAD[valor]}`}
      aria-label={`Disponibilidad: ${TEXTO_DISPONIBILIDAD[valor]}`}
    >
      {TEXTO_DISPONIBILIDAD[valor]}
    </span>
  );
}

const ESTILOS_SOLICITUD: Record<EstadoSolicitud, string> = {
  pendiente: "bg-sky-100 text-sky-900 border-sky-300",
  pagada: "bg-emerald-100 text-emerald-900 border-emerald-300",
  cancelada: "bg-slate-100 text-slate-500 border-slate-300",
};

const TEXTO_SOLICITUD: Record<EstadoSolicitud, string> = {
  pendiente: "Pendiente",
  pagada: "Pagada",
  cancelada: "Cancelada",
};

export function BadgeSolicitud({ valor }: { valor: EstadoSolicitud }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-bold ${ESTILOS_SOLICITUD[valor]}`}
    >
      {TEXTO_SOLICITUD[valor]}
    </span>
  );
}

export function Cargando() {
  return (
    <div
      className="flex min-h-[40vh] items-center justify-center text-slate-500"
      role="status"
      aria-label="Cargando"
    >
      <div className="flex items-center gap-3">
        <span className="h-6 w-6 animate-spin rounded-full border-4 border-sky-700 border-t-transparent" />
        Cargando…
      </div>
    </div>
  );
}

export function ErrorBox({ mensaje }: { mensaje: string }) {
  return (
    <div
      role="alert"
      className="my-3 rounded-xl border-2 border-red-300 bg-red-50 px-4 py-3 text-sm font-semibold text-red-800"
    >
      {mensaje}
    </div>
  );
}

export function ExitoBox({ mensaje }: { mensaje: string }) {
  return (
    <div
      role="status"
      className="my-3 rounded-xl border-2 border-emerald-300 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-800"
    >
      {mensaje}
    </div>
  );
}
