"use client";

// Login unificado cliente/admin (F-T2)
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { destinoSegunRol, guardarSesion } from "@/lib/auth";
import { desbloquearAudio } from "@/lib/sonido";
import type { TokenResponse } from "@/types";
import { Boton, Entrada, ErrorBox } from "@/components/ui";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const enviar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    desbloquearAudio(); // gesto del usuario: habilita el sonido del panel admin
    try {
      const res = await api.post<TokenResponse>("/auth/login", {
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
          🧼
        </div>
        <h1 className="mt-2 text-2xl font-extrabold text-sky-900">
          Iniciar sesión
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Entrá con tu cuenta para ver el catálogo
        </p>
      </header>

      {error && <ErrorBox mensaje={error} />}

      <form onSubmit={enviar} className="flex flex-col gap-4">
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
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />
        <Boton type="submit" disabled={enviando} className="py-4 text-lg">
          {enviando ? "Entrando…" : "Entrar"}
        </Boton>
      </form>

      <p className="text-center text-sm text-slate-600">
        ¿No tenés cuenta?{" "}
        <Link
          href="/cliente/registro"
          className="font-bold text-sky-800 underline underline-offset-4"
        >
          Crear cuenta
        </Link>
      </p>
      <Link
        href="/"
        className="text-center text-sm font-semibold text-slate-500 underline underline-offset-4"
      >
        ← Volver al inicio
      </Link>
    </main>
  );
}
