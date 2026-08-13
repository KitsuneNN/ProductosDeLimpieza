"use client";

// Registro de cliente (F-T2)
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { destinoSegunRol, guardarSesion } from "@/lib/auth";
import type { TokenResponse } from "@/types";
import { Boton, Entrada, ErrorBox } from "@/components/ui";

export default function Registro() {
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [telefono, setTelefono] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const res = await api.post<TokenResponse>("/auth/registro", {
        nombre,
        telefono,
        email,
        password,
      });
      guardarSesion(res.access_token, res.usuario);
      router.replace(destinoSegunRol(res.usuario));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error inesperado");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-lg flex-col justify-center gap-5 px-6 py-10">
      <header className="text-center">
        <div className="text-5xl" aria-hidden>
          🧽
        </div>
        <h1 className="mt-2 text-2xl font-extrabold text-sky-900">
          Crear mi cuenta
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Solo nombre, teléfono y email para empezar a pedir
        </p>
      </header>

      {error && <ErrorBox mensaje={error} />}

      <form onSubmit={enviar} className="flex flex-col gap-4">
        <Entrada
          etiqueta="Nombre"
          type="text"
          required
          minLength={2}
          autoComplete="name"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          placeholder="Tu nombre"
        />
        <Entrada
          etiqueta="Teléfono"
          type="tel"
          required
          autoComplete="tel"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
          placeholder="261 555 1234"
        />
        <Entrada
          etiqueta="Email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@email.com"
        />
        <Entrada
          etiqueta="Contraseña"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mínimo 8 caracteres"
        />
        <Boton type="submit" disabled={enviando} className="py-4 text-lg">
          {enviando ? "Creando cuenta…" : "Crear cuenta"}
        </Boton>
      </form>

      <p className="text-center text-sm text-slate-600">
        ¿Ya tenés cuenta?{" "}
        <Link
          href="/cliente/login"
          className="font-bold text-sky-800 underline underline-offset-4"
        >
          Iniciar sesión
        </Link>
      </p>
    </main>
  );
}
