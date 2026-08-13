"use client";

// Layout del cliente: guard de sesión + navegación inferior táctil (F-T2)
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getUsuario, limpiarSesion } from "@/lib/auth";
import { leerCarrito, unidadesCarrito } from "@/lib/cart";

const NAV = [
  { href: "/cliente/catalogo", texto: "Catálogo", icono: "🧴" },
  { href: "/cliente/carrito", texto: "Carrito", icono: "🛒" },
  { href: "/cliente/solicitudes", texto: "Mis pedidos", icono: "📋" },
];

export default function ClienteLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [listo, setListo] = useState(false);
  const [unidades, setUnidades] = useState(0);

  useEffect(() => {
    const usuario = getUsuario();
    if (!usuario) {
      router.replace("/cliente/login");
      return;
    }
    if (usuario.rol === "admin") {
      router.replace("/admin/dashboard");
      return;
    }
    setListo(true);
  }, [router]);

  useEffect(() => {
    setUnidades(unidadesCarrito(leerCarrito()));
  }, [pathname]);

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
    <div className="mx-auto flex min-h-screen max-w-lg flex-col bg-slate-50 pb-24">
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
        <Link href="/cliente/catalogo" className="text-lg font-extrabold text-sky-900">
          🧼 Local de Limpieza
        </Link>
        <button
          type="button"
          onClick={salir}
          className="min-h-[44px] rounded-lg px-2 text-sm font-bold text-slate-500 hover:bg-slate-100"
        >
          Salir
        </button>
      </header>

      <main className="flex-1 px-4 py-4">{children}</main>

      <nav
        aria-label="Navegación principal"
        className="fixed inset-x-0 bottom-0 z-10 mx-auto max-w-lg border-t border-slate-200 bg-white"
      >
        <div className="grid grid-cols-3">
          {NAV.map((item) => {
            const activo = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={activo ? "page" : undefined}
                className={`relative flex min-h-[60px] flex-col items-center justify-center gap-0.5 text-xs font-bold ${
                  activo ? "text-sky-800" : "text-slate-500"
                }`}
              >
                <span className="text-xl" aria-hidden>
                  {item.icono}
                </span>
                {item.texto}
                {item.href === "/cliente/carrito" && unidades > 0 && (
                  <span className="absolute right-1/2 top-1.5 ml-4 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[11px] font-extrabold text-white">
                    {unidades}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
