"use client";

// Hook de tiempo real: WebSocket con reintentos + estado (F-T2/F-T3).
// En producción/preview puede no alcanzar el WS (proxies) — las pantallas
// que lo usan SIEMPRE mantienen polling de respaldo (10s).
import { useEffect, useRef, useState } from "react";
import type { WsEvento } from "@/types";
import { getToken } from "./auth";

export type EstadoWs = "conectando" | "conectado" | "reintentando" | "sin_token";

export function useTiempoReal(onEvento: (evento: WsEvento) => void): EstadoWs {
  const [estado, setEstado] = useState<EstadoWs>("conectando");
  const ref = useRef(onEvento);
  ref.current = onEvento;

  useEffect(() => {
    let ws: WebSocket | null = null;
    let cerrado = false;
    let reintentos = 0;
    let temporizador: ReturnType<typeof setTimeout> | null = null;

    const token = getToken();
    if (!token) {
      setEstado("sin_token");
      return;
    }

    const conectar = () => {
      if (cerrado) return;
      setEstado(reintentos === 0 ? "conectando" : "reintentando");
      const protocolo = window.location.protocol === "https:" ? "wss" : "ws";
      // Ruta relativa: el rewrite de Next la lleva al backend en dev Y en preview.
      // NEXT_PUBLIC_WS_URL permite apuntar a un host explícito en despliegues.
      const url =
        process.env.NEXT_PUBLIC_WS_URL ??
        `${protocolo}://${window.location.host}/ws?token=${token}`;
      try {
        ws = new WebSocket(url);
      } catch {
        programarReintento();
        return;
      }
      ws.onopen = () => {
        reintentos = 0;
        setEstado("conectado");
      };
      ws.onmessage = (ev) => {
        try {
          ref.current(JSON.parse(ev.data as string) as WsEvento);
        } catch {
          // mensaje malformado: ignorar
        }
      };
      ws.onclose = () => {
        if (!cerrado) programarReintento();
      };
      ws.onerror = () => {
        ws?.close();
      };
    };

    const programarReintento = () => {
      const espera = Math.min(15000, 1000 * 2 ** Math.min(reintentos, 4));
      reintentos += 1;
      temporizador = setTimeout(conectar, espera);
    };

    conectar();
    return () => {
      cerrado = true;
      if (temporizador) clearTimeout(temporizador);
      ws?.close();
    };
  }, []);

  return estado;
}
