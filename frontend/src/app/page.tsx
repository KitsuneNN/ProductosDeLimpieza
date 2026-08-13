"use client";

// Landing: QR del local + accesos (F-T1/F-T4)
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import QRCode from "qrcode";
import { destinoSegunRol, getUsuario } from "@/lib/auth";
import { Boton } from "@/components/ui";

export default function Landing() {
  const router = useRouter();
  const [qr, setQr] = useState<string>("");
  const [listo, setListo] = useState(false);

  useEffect(() => {
    const usuario = getUsuario();
    if (usuario) {
      router.replace(destinoSegunRol(usuario));
      return;
    }
    setListo(true);
    if (typeof window !== "undefined") {
      QRCode.toDataURL(window.location.origin, { width: 360, margin: 2 })
        .then(setQr)
        .catch(() => setQr(""));
    }
  }, [router]);

  if (!listo) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        Cargando…
      </div>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center gap-6 px-6 py-10 text-center">
      <div>
        <div className="mb-3 text-6xl" aria-hidden>
          🧼
        </div>
        <h1 className="text-3xl font-extrabold text-sky-900">
          Local de Limpieza
        </h1>
        <p className="mt-2 text-base text-slate-600">
          Escaneá el código, armá tu pedido y retiralo pagando en el mostrador.
        </p>
      </div>

      {qr && (
        <figure className="rounded-2xl border-4 border-sky-700 bg-white p-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={qr}
            alt="Código QR para abrir el catálogo del local"
            className="h-52 w-52"
          />
          <figcaption className="mt-2 text-xs font-semibold text-slate-500">
            Escaneame con la cámara del celular
          </figcaption>
        </figure>
      )}

      <div className="flex w-full flex-col gap-3">
        <Boton
          className="w-full py-4 text-lg"
          onClick={() => router.push("/cliente/login")}
        >
          Entrar al catálogo
        </Boton>
        <Boton
          variante="secundario"
          className="w-full"
          onClick={() => router.push("/cliente/registro")}
        >
          Crear mi cuenta
        </Boton>
        <button
          type="button"
          onClick={() => router.push("/cliente/login")}
          className="mt-2 text-sm font-semibold text-slate-500 underline underline-offset-4"
        >
          Soy del local (acceso administrador)
        </button>
      </div>
    </main>
  );
}
