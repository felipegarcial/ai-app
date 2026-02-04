# Testing Plan - Legal Document Generator Frontend

## Pre-requisitos

### 1. Iniciar Backend (Flask)
```bash
cd /path/to/backend
python app.py  # o flask run
# Debe correr en http://localhost:5000
```

### 2. Iniciar Frontend
```bash
cd /path/to/frontend
npm run dev
# Abre http://localhost:5173
```

---

## Test Cases

### TC-01: Carga Inicial
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir http://localhost:5173 | Welcome screen visible |
| 2 | Verificar sidebar | Logo "LegalDoc" visible |
| 3 | Verificar phase | Badge "Getting Started" (azul) |
| 4 | Verificar input | Placeholder "Enter a prompt here..." |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-02: Enviar Mensaje Básico
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Escribir "Hola, necesito un NDA" | Texto aparece en input |
| 2 | Click en botón Send (o Enter) | Mensaje del usuario aparece (burbuja derecha) |
| 3 | Esperar respuesta | Respuesta del asistente aparece con streaming |
| 4 | Verificar streaming | Texto aparece token por token con cursor |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-03: Function Call Indicator
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Enviar mensaje que triggere function | Ej: "Quiero un NDA para mi startup" |
| 2 | Observar UI | Indicador "Collecting NDA information" aparece |
| 3 | Esperar completado | Indicador muestra checkmark verde |
| 4 | Indicador desaparece | Después de ~500ms |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-04: Actualización de Estado en Sidebar
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Completar flujo intake | Responder preguntas del bot |
| 2 | Verificar Phase | Cambia a "Clarifying Details" (amarillo) |
| 3 | Verificar Collected Data | Muestra datos recolectados |
| 4 | Verificar Missing Fields | Lista campos faltantes |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-05: Generación de Documento
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Completar todas las preguntas | Bot indica generación |
| 2 | Verificar Phase | Cambia a "Generating Document" (púrpura) |
| 3 | Esperar generación | Documento se genera |
| 4 | Verificar botón flotante | "View Document" aparece |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-06: Preview de Documento
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Click "View Document" | Modal se abre |
| 2 | Verificar contenido | Documento completo visible |
| 3 | Click "Copy" | Texto copiado, botón muestra "Copied!" |
| 4 | Click "Download" | Archivo .txt descargado |
| 5 | Cerrar modal | Click X o fuera del modal |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-07: Reset Conversation
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Click "New Conversation" | Dialog de confirmación aparece |
| 2 | Click "Cancel" | Dialog se cierra, nada cambia |
| 3 | Click "New Conversation" otra vez | Dialog aparece |
| 4 | Click "Reset" | Todo se limpia |
| 5 | Verificar estado | Welcome screen, phase "intake", sin mensajes |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-08: Persistencia de Sesión
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Enviar algunos mensajes | Conversación activa |
| 2 | Refresh página (F5) | Session ID se mantiene |
| 3 | Verificar localStorage | `legal-doc-session` existe |

**Nota:** Los mensajes no persisten (by design), solo el session ID.

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-09: Responsive - Mobile
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Resize ventana < 768px | Sidebar desaparece |
| 2 | Verificar botón hamburguesa | Aparece en top-left |
| 3 | Click hamburguesa | Sidebar se abre como Sheet |
| 4 | Click fuera del sheet | Sheet se cierra |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-10: Manejo de Errores
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Detener backend | Flask no corre |
| 2 | Enviar mensaje | Error alert aparece |
| 3 | Verificar mensaje | "Request failed" o similar |
| 4 | Click X en alert | Alert se cierra |
| 5 | Reiniciar backend | Siguiente mensaje funciona |

**Status:** ⬜ Pass / ⬜ Fail

---

### TC-11: Keyboard Shortcuts
| Step | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Focus en input | Cursor en textarea |
| 2 | Escribir mensaje + Enter | Mensaje se envía |
| 3 | Escribir mensaje + Shift+Enter | Nueva línea (no envía) |

**Status:** ⬜ Pass / ⬜ Fail

---

## Edge Cases

### EC-01: Mensaje Vacío
- Intentar enviar mensaje vacío
- **Esperado:** Botón Send deshabilitado

### EC-02: Mensaje Durante Streaming
- Intentar enviar mientras hay streaming
- **Esperado:** Input deshabilitado, botón muestra loader

### EC-03: Múltiples Resets Rápidos
- Click Reset múltiples veces rápido
- **Esperado:** No errores, solo un reset ejecuta

### EC-04: Documento Muy Largo
- Generar documento extenso
- **Esperado:** Scroll funciona en preview

---

## Flujo Completo E2E

### Escenario: Crear NDA desde cero

```
1. Usuario abre la app
2. Escribe: "Necesito crear un NDA para mi empresa"
3. Bot pregunta tipo de expertise
4. Usuario responde: "Soy principiante"
5. Bot pregunta detalles del NDA
6. Usuario proporciona:
   - Nombre de empresa: "TechCorp"
   - Nombre de contraparte: "John Doe"
   - Duración: "2 años"
   - etc.
7. Bot genera documento
8. Usuario ve preview
9. Usuario descarga documento
10. Usuario inicia nueva conversación
```

---

## Checklist Final

- [ ] TC-01: Carga Inicial
- [ ] TC-02: Enviar Mensaje Básico
- [ ] TC-03: Function Call Indicator
- [ ] TC-04: Actualización de Estado
- [ ] TC-05: Generación de Documento
- [ ] TC-06: Preview de Documento
- [ ] TC-07: Reset Conversation
- [ ] TC-08: Persistencia de Sesión
- [ ] TC-09: Responsive Mobile
- [ ] TC-10: Manejo de Errores
- [ ] TC-11: Keyboard Shortcuts
- [ ] EC-01 a EC-04: Edge Cases
- [ ] E2E: Flujo Completo

---

## Notas de Debug

### Ver logs del store
```javascript
// En consola del browser
window.__ZUSTAND_DEVTOOLS__ // si instalas devtools
```

### Ver session ID
```javascript
localStorage.getItem('legal-doc-session')
```

### Limpiar todo
```javascript
localStorage.clear()
location.reload()
```

### Network tab
- Filtrar por `chat/stream`
- Ver EventStream en la respuesta
