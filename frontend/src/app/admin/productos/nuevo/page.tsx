"use client";

// Alta de producto (F-T3)
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { CategoriaPublic, ProductoAdminPublic } from "@/types";
import { AreaTexto, Boton, Entrada, ErrorBox } from "@/components/ui";

export default function NuevoProducto() {
  const router = useRouter();
  const [categorias, setCategorias] = useState<CategoriaPublic[]>([]);
  const [form, setForm] = useState({
    categoria_id: "",
    nombre: "",
    descripcion: "",
    precio: "",
    stock_actual: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api
      .get<{ items: CategoriaPublic[] }>("/categorias")
      .then((res) => {
        setCategorias(res.items);
        if (res.items[0]) setForm((f) => ({ ...f, categoria_id: String(res.items[0].id) }));
      })
      .catch(() => setError("No se pudieron cargar las categorías"));
  }, []);

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await api.post<ProductoAdminPublic>("/admin/productos", {
        categoria_id: Number(form.categoria_id),
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        precio: Number(form.precio),
        stock_actual: Number(form.stock_actual || 0),
      });
      router.push("/admin/productos");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear el producto");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Link
        href="/admin/productos"
        className="min-h-[44px] text-sm font-bold text-sky-800 underline underline-offset-4"
      >
        ← Volver a productos
      </Link>
      <h1 className="text-xl font-extrabold text-sky-900">Nuevo producto</h1>

      {error && <ErrorBox mensaje={error} />}

      <form onSubmit={enviar} className="flex flex-col gap-4">
        <label className="block">
          <span className="mb-1 block text-sm font-semibold text-slate-700">Categoría</span>
          <select
            required
            value={form.categoria_id}
            onChange={(e) => setForm({ ...form, categoria_id: e.target.value })}
            className="min-h-[44px] w-full rounded-xl border-2 border-slate-300 bg-white px-3 text-base"
          >
            {categorias.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
        </label>
        <Entrada
          etiqueta="Nombre"
          required
          value={form.nombre}
          onChange={(e) => setForm({ ...form, nombre: e.target.value })}
          placeholder="Ej. Lavandina 1 litro"
        />
        <AreaTexto
          etiqueta="Descripción (opcional)"
          rows={2}
          value={form.descripcion}
          onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
          placeholder="Detalles del producto"
        />
        <Entrada
          etiqueta="Precio ($)"
          type="number"
          required
          min={0}
          step="0.01"
          inputMode="decimal"
          value={form.precio}
          onChange={(e) => setForm({ ...form, precio: e.target.value })}
          placeholder="1250.50"
        />
        <Entrada
          etiqueta="Stock inicial"
          type="number"
          min={0}
          inputMode="numeric"
          value={form.stock_actual}
          onChange={(e) => setForm({ ...form, stock_actual: e.target.value })}
          placeholder="0"
        />
        <Boton type="submit" disabled={enviando} className="py-4 text-lg">
          {enviando ? "Guardando…" : "💾 Guardar producto"}
        </Boton>
      </form>
    </div>
  );
}
