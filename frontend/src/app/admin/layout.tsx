"use client";

// Layout del admin: guard de rol + barra de navegación (F-T3)
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getUsuario, limpiarSesion } from "@/lib/auth";

const NAV = [
  { href: "/admin/dashboard", texto: "Panel", icono: "🔔" },
  { href: "/admin/productos", texto: "Productos", icono: "📦" },
  { href: "/admin/solicitudes", texto: "Pedidos", icono: "📋" },
  { href: "/admin/config", texto: "Ajustes", icono: "⚙️" },
  { href: "/admin/qr", texto: "QR", icono: "📱" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [listo, setListo] = useState(false);

  useEffect(() => {
    const usuario = getUsuario();
    if (!usuario) {
      router.replace("/cliente/login");
      return;
    }
    if (usuario.rol !== "admin") {
      router.replace("/cliente/catalogo");
      return;
    }
    setListo(true);
  }, [router]);

  if (!listo) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-500">
        Cargando…
      </div>
    );
  }

  const salir = () => {
    limpiarSesion();
    router.replace("/");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col bg-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
        <div className="flex items-center justify-between px-4 py-3">
          <Link href="/admin/dashboard" className="text-lg font-extrabold text-sky-900">
            🧼 Panel del local
          </Link>
          <button
            type="button"
            onClick={salir}
            className="min-h-[44px] rounded-lg px-2 text-sm font-bold text-slate-500 hover:bg-slate-100"
          >
            Salir
          </button>
        </div>
        <nav
          aria-label="Navegación del administrador"
          className="flex gap-1 overflow-x-auto px-2 pb-2"
        >
          {NAV.map((item) => {
            const activo = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`flex min-h-[44px] items-center gap-1.5 whitespace-nowrap rounded-xl px-3 text-sm font-bold ${
                  activo ? "bg-sky-700 text-white" : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <span aria-hidden>{item.icono}</span>
                {item.texto}
              </Link>
            );
          })}
        </nav>
      </header>

      <main className="flex-1 px-4 py-4">{children}</main>
    </div>
  );
}
