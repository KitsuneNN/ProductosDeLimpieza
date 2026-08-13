"use client";

// QR imprimible del local para el mostrador (F-T4)
import { useEffect, useState } from "react";
import QRCode from "qrcode";
import { Boton } from "@/components/ui";

export default function QrAdmin() {
  const [qr, setQr] = useState<string>("");
  const [url, setUrl] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const origen = window.location.origin;
    setUrl(origen);
    QRCode.toDataURL(origen, { width: 480, margin: 2 })
      .then(setQr)
      .catch(() => setQr(""));
  }, []);

  return (
    <div className="flex flex-col items-center gap-5">
      <h1 className="text-xl font-extrabold text-sky-900">QR del local</h1>
      <p className="max-w-md text-center text-sm text-slate-600">
        Imprimí este código y pegalo en el mostrador. Tus clientes lo escanean,
        entran al catálogo, arman el pedido y vos recibís el aviso sonoro.
      </p>

      {qr && (
        <figure className="rounded-2xl border-4 border-sky-700 bg-white p-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={qr} alt="Código QR del local para imprimir" className="h-72 w-72" />
          <figcaption className="mt-2 text-center text-xs font-semibold text-slate-500 break-all">
            {url}
          </figcaption>
        </figure>
      )}

      <div className="flex gap-3">
        <Boton onClick={() => window.print()}>🖨️ Imprimir</Boton>
        <Boton
          variante="secundario"
          onClick={() => {
            if (qr) {
              const a = document.createElement("a");
              a.href = qr;
              a.download = "qr-local-limpieza.png";
              a.click();
            }
          }}
        >
          ⬇️ Descargar imagen
        </Boton>
      </div>
    </div>
  );
}
