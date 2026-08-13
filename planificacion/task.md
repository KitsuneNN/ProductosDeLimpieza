# TASK.md — CHECKLIST DEL PROYECTO

**Proyecto:** Sistema Web de Catálogo e Inventario — Local de Limpieza
**Repo:** github.com/KitsuneNN/ProductosDeLimpieza
**Última actualización:** 2026-08-13 · **Fase actual:** PLANIFICACIÓN

**Estados:** ⬜ PENDIENTE · 🟦 EN_PROGRESO · 🟩 ESPERANDO_APROBACIÓN · ✅ APPROVED ·
⚠️ APPROVED_WITH_NOTES · 🔄 MINOR_CHANGES · ❌ REJECTED · 🔒 BLOQUEADO

---

## 🔴 FASE CRÍTICA (infraestructura base)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| ARQ-T1 | Modelo de datos + migración + seed + ERD | 📐 | ⬜ | — |
| ARQ-T2 | Contrato API + eventos WS + types TS | 📐 | ⬜ | — |
| B-T1 | Scaffold backend + conexión DB + healthcheck | 🔧 | ⬜ | — |
| B-T2 | Auth JWT + roles + seed admin | 🔧 | ⬜ | — |
| F-T1 | Scaffold frontend + rutas + tema + api client | 🎨 | ⬜ | — |

## 🟡 FASE ALTA (funcionalidad core)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| B-T3 | CRUD productos admin + imágenes | 🔧 | ⬜ | — |
| B-T4 | Catálogo cliente + etiquetas disponibilidad | 🔧 | ⬜ | — |
| B-T5 | Solicitudes (crear/listar/estados) | 🔧 | ⬜ | — |
| B-T6 | Pago transaccional + umbrales + broadcast WS | 🔧 | ⬜ | — |
| F-T2 | Pantallas cliente mobile-first | 🎨 | ⬜ | — |
| F-T3 | Panel admin + aviso sonoro | 🎨 | ⬜ | — |

## 🟢 FASE NORMAL (features adicionales)
| ID | Tarea | Agente | Estado | Evidencia |
|----|-------|--------|--------|-----------|
| F-T4 | QR imprimible | 🎨 | ⬜ | — |
| QA-T1 | pytest backend (stock/checkout ≥80%) | ⚡ | ⬜ | — |
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
- [ ] Código implementado según instrucciones
- [ ] Compilación/build sin errores (exit code 0)
- [ ] Servidor/app corre sin crashes
- [ ] Tests pasan (pytest + Vitest + Playwright)
- [ ] Lint sin errores críticos
- [ ] Accesibilidad verificada (Regla 13: botones ≥44px, contraste, focus)
- [ ] Idioma español verificado en toda la UI
- [ ] Dependencias instaladas y documentadas
- [ ] Integrado → importado, enlazado, navegable
- [ ] Performance: catálogo <2s en gama media
- [ ] Walkthroughs de agentes actualizados
- [ ] GLOBAL_WALKTHROUGH actualizado
- [ ] Screenshot/video evidencia del flujo de oro
- [ ] Aprobación Chef solicitada y obtenida

## 📌 HITOS CRÍTICOS DEL PROYECTO
- [ ] Etiquetas de stock (sin números) visibles para clientes — **3.5 requisito duro**
- [ ] Umbral "Pocas unidades" configurable por admin — **20.1 requisito duro**
- [ ] Sonido característico en PC del admin — **19.3 requisito duro**
- [ ] "Pagado" → descuento instantáneo visible en clientes — **2.3 criterio de éxito**
- [ ] QR escaneable → login → catálogo — **3.1 imprescindible**
