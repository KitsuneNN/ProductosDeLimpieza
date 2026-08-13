"use client";

// Edición de producto + carga de foto (F-T3)
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { CategoriaPublic, ProductoAdminPublic } from "@/types";
import { AreaTexto, Boton, Entrada, ErrorBox, ExitoBox } from "@/components/ui";

export default function EditarProducto() {
  const params = useParams<{ id: string }>();
  const [categorias, setCategorias] = useState<CategoriaPublic[]>([]);
  const [form, setForm] = useState({
    categoria_id: "",
    nombre: "",
    descripcion: "",
    precio: "",
    stock_actual: "",
  });
  const [imagenUrl, setImagenUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<{ items: CategoriaPublic[] }>("/categorias"),
      api.get<ProductoAdminPublic>(`/admin/productos/${params.id}`),
    ])
      .then(([cats, p]) => {
        setCategorias(cats.items);
        setForm({
          categoria_id: String(p.categoria_id),
          nombre: p.nombre,
          descripcion: p.descripcion ?? "",
          precio: String(p.precio),
          stock_actual: String(p.stock_actual),
        });
        setImagenUrl(p.imagen_url);
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "No se pudo cargar el producto"),
      );
  }, [params.id]);

  const guardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      await api.put<ProductoAdminPublic>(`/admin/productos/${params.id}`, {
        categoria_id: Number(form.categoria_id),
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        precio: Number(form.precio),
        stock_actual: Number(form.stock_actual),
      });
      setExito("Cambios guardados ✓");
      setTimeout(() => setExito(null), 2500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar");
    } finally {
      setEnviando(false);
    }
  };

  const subirFoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const archivo = e.target.files?.[0];
    if (!archivo) return;
    setError(null);
    try {
      const p = await api.subirImagen<ProductoAdminPublic>(
        `/admin/productos/${params.id}/imagen`,
        archivo,
      );
      setImagenUrl(p.imagen_url);
      setExito("Foto actualizada ✓");
      setTimeout(() => setExito(null), 2500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo subir la foto");
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
      <h1 className="text-xl font-extrabold text-sky-900">Editar producto</h1>

      {error && <ErrorBox mensaje={error} />}
      {exito && <ExitoBox mensaje={exito} />}

      <div className="flex items-center gap-4">
        {imagenUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={imagenUrl} alt="Foto actual del producto" className="h-24 w-24 rounded-2xl object-cover" />
        ) : (
          <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-sky-50 text-4xl">
            📦
          </div>
        )}
        <label className="flex min-h-[44px] cursor-pointer items-center rounded-xl border-2 border-sky-700 bg-white px-4 text-sm font-bold text-sky-800">
          📷 Cambiar foto
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="sr-only"
            onChange={subirFoto}
          />
        </label>
      </div>

      <form onSubmit={guardar} className="flex flex-col gap-4">
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
        />
        <AreaTexto
          etiqueta="Descripción (opcional)"
          rows={2}
          value={form.descripcion}
          onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
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
        />
        <Entrada
          etiqueta="Stock actual"
          type="number"
          required
          min={0}
          inputMode="numeric"
          value={form.stock_actual}
          onChange={(e) => setForm({ ...form, stock_actual: e.target.value })}
        />
        <Boton type="submit" disabled={enviando} className="py-4 text-lg">
          {enviando ? "Guardando…" : "💾 Guardar cambios"}
        </Boton>
      </form>
    </div>
  );
}
