"use client";

// Ajustes del local: umbral de "Pocas unidades" (F-T3) — requisito 20.1
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { UmbralResponse } from "@/types";
import { Boton, Entrada, ErrorBox, ExitoBox } from "@/components/ui";

export default function ConfigAdmin() {
  const [umbral, setUmbral] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api
      .get<UmbralResponse>("/admin/config/umbral-pocas-unidades")
      .then((res) => setUmbral(String(res.umbral_pocas_unidades)))
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar la configuración"),
      )
      .finally(() => setCargando(false));
  }, []);

  const guardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setExito(null);
    setEnviando(true);
    try {
      const res = await api.put<UmbralResponse>("/admin/config/umbral-pocas-unidades", {
        valor: umbral,
      });
      setUmbral(String(res.umbral_pocas_unidades));
      setExito(
        `Listo: los clientes verán "¡Pocas unidades!" cuando queden ${res.umbral_pocas_unidades} o menos.`,
      );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-xl font-extrabold text-sky-900">Ajustes del local</h1>

      {cargando ? (
        <p className="py-8 text-center text-slate-500">Cargando configuración…</p>
      ) : (
        <form
          onSubmit={guardar}
          className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5"
        >
          <div>
            <h2 className="text-base font-extrabold text-slate-900">
              Umbral de “Pocas unidades”
            </h2>
            <p className="mt-1 text-sm text-slate-600">
              A partir de cuántas unidades un producto se muestra como{" "}
              <strong>“¡Pocas unidades!”</strong> a los clientes. Con stock en 0 se
              muestra “Sin stock”. Los clientes nunca ven el número exacto.
            </p>
          </div>

          <Entrada
            etiqueta="Umbral (unidades)"
            type="number"
            required
            min={1}
            inputMode="numeric"
            value={umbral}
            onChange={(e) => setUmbral(e.target.value)}
          />

          {error && <ErrorBox mensaje={error} />}
          {exito && <ExitoBox mensaje={exito} />}

          <Boton type="submit" disabled={enviando} className="py-4">
            {enviando ? "Guardando…" : "💾 Guardar"}
          </Boton>
        </form>
      )}
    </div>
  );
}
