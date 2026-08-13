# TASK.md — CHECKLIST DEL PROYECTO

**Proyecto:** Sistema Web de Catálogo e Inventario — Local de Limpieza
**Repo:** github.com/KitsuneNN/ProductosDeLimpieza
**Última actualización:** 2026-08-13 · **Fase actual:** 🟡→🟢 FASE ALTA completada (front incluido) — resta QA-T2/T3 y FASE FINAL

**Estados:** ⬜ PENDIENTE · 🟦 EN_PROGRESO · 🟩 ESPERANDO_APROBACIÓN · ✅ APPROVED ·
⚠️ APPROVED_WITH_NOTES · 🔄 MINOR_CHANGES · ❌ REJECTED · 🔒 BLOQUEADO

---

## 🔴 FASE CRÍTICA (infraestructura base)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| ARQ-T1 | Modelo de datos + migración + seed + ERD | 📐 | ✅ | migración REAL up/down + seed ×2 + paridad modelos↔migración |
| ARQ-T2 | Contrato API + eventos WS + types TS | 📐 | ✅ | verify_contract.py: 30 pares espejo + 5 eventos WS |
| B-T1 | Scaffold backend + conexión DB + healthcheck | 🔧 | ✅ | PostgreSQL 17 real, /api/health 200 |
| B-T2 | Auth JWT + roles + seed admin | 🔧 | ✅ | tests auth + login/me/403 en vivo |
| F-T1 | Scaffold frontend Next.js + rutas + tema + api client | 🎨 | ✅ | build exit 0 + rewrites verificados |

## 🟡 FASE ALTA (funcionalidad core)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| B-T3 | CRUD productos admin + imágenes | 🔧 | ✅ | CRUD+estado+imagen probado (pytest + curl) |
| B-T4 | Catálogo cliente + etiquetas disponibilidad | 🔧 | ✅ | test: sin stock numérico, etiquetas correctas |
| B-T5 | Solicitudes (crear/listar/estados) | 🔧 | ✅ | snapshot precios, máquina de estados |
| B-T6 | Pago transaccional + umbrales + broadcast WS | 🔧 | ✅ | E2E 11/11: WS real, 409 faltantes, doble pago |
| F-T2 | Pantallas cliente mobile-first | 🎨 | 🟩 | build OK, preview vivo |
| F-T3 | Panel admin + aviso sonoro | 🎨 | 🟩 | build OK, preview vivo, sonido Web Audio |

## 🟢 FASE NORMAL (features adicionales)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| F-T4 | QR imprimible | 🎨 | 🟩 | landing + admin/qr con QR real del origin |
| QA-T1 | pytest backend (stock/checkout ≥80%) | ⚡ | ✅ | 28 tests · services 95% |
| QA-T2 | Vitest componentes clave | ⚡ | ⬜ | — |

## 🔵 FASE FINAL (testing, deploy, docs)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| QA-T3 | E2E Playwright flujo de oro | ⚡ | ⬜ | — |
| D-T1 | CI/CD + deploy Vercel/Render/Neon | 🚀 | ⬜ | — |
| D-T2 | Documentación final + manual admin | 🚀 | ⬜ | — |
| CHEF-FINAL | Verificación end-to-end + aprobación final | 👨‍🍳 | ⬜ | — |

---

## ✅ CHECKLIST GLOBAL DE FINALIZACIÓN (Regla 1 — 14 puntos)
- [x] Código implementado según instrucciones
- [x] Compilación/build sin errores (backend pytest + frontend next build exit 0)
- [x] Servidor/app corre sin crashes (API + Next dev vivos en preview)
- [x] Tests pasan (28 pytest · cobertura services 95%)
- [ ] Lint sin errores críticos (sin ESLint configurado aún — Next 16 lo quitó del build)
- [x] Accesibilidad verificada (botones ≥44px, aria-labels, focus-visible, contraste alto)
- [x] Idioma español en toda la UI
- [x] Dependencias instaladas y documentadas (requirements.txt + package.json)
- [x] Integrado → importado, enlazado, navegable (rewrites, rutas, WS)
- [ ] Performance: catálogo <2s en gama media (pendiente medición real)
- [x] Walkthroughs de agentes actualizados
- [x] GLOBAL_WALKTHROUGH actualizado
- [ ] Screenshot/video evidencia del flujo de oro (pendiente — se puede probar en preview)
- [ ] Aprobación Chef final

## 📌 HITOS CRÍTICOS DEL PROYECTO
- [x] Etiquetas de stock (sin números) visibles para clientes — **3.5 requisito duro**
- [x] Umbral "Pocas unidades" configurable por admin — **20.1 requisito duro**
- [x] Sonido característico en PC del admin — **19.3 requisito duro**
- [x] "Pagado" → descuento instantáneo visible en clientes — **2.3 criterio de éxito**
- [x] QR escaneable → login → catálogo — **3.1 imprescindible**
