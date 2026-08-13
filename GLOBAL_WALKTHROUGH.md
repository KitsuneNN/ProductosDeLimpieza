# GLOBAL_WALKTHROUGH — Sistema Web Catálogo e Inventario (Local de Limpieza)

## 📌 Estado general
- **Fecha:** 2026-08-13
- **Fase:** PLANIFICACIÓN (plan maestro y contratos presentados — esperando aprobación del dueño)
- **Repo:** github.com/KitsuneNN/ProductosDeLimpieza
- **Conexión GitHub:** ✅ SSH deploy key con write access verificada (clone + push OK)

## 🚦 Línea de tiempo
| Fecha | Evento | Estado |
|-------|--------|--------|
| 2026-08-13 | Conexión SSH + clone + verificación de push | ✅ OK |
| 2026-08-13 | Recepción de requisitos (cuestionario IA central) | ✅ OK |
| 2026-08-13 | Equipo definido (5 agentes) + contratos creados | ✅ OK |
| 2026-08-13 | Plan maestro + task.md + ADR-001 creados | 🟩 ESPERANDO_APROBACIÓN |

## 🧾 Decisiones clave
- **ADR-001:** stack propuesto (React+Vite+TS+Tailwind / FastAPI / PostgreSQL / Cloudinary) — pendiente confirmación.
- **Flujo Git:** ramas `chef-master/<tarea>`, nada directo a `main` sin aprobación.

## 📂 Convenciones del repo
- Rama default: `main` (⚠️ pendiente cambio en GitHub Settings: hoy la default es la rama de test)
- Ramas de trabajo: `chef-master/<tarea>`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)
- Secretos: solo en `.env` (referencias en `.env.example`); nunca commitear credenciales
- Idioma de UI, comentarios y docs: español

## ⏳ Próximos pasos
1. Aprobación del dueño: equipo, stack (ADR-001), cuentas Cloudinary/deploy.
2. Cambio de rama default en GitHub (acción manual del dueño).
3. Inicio FASE CRÍTICA: ARQ-T1 → ARQ-T2 → B-T1/B-T2/F-T1.
