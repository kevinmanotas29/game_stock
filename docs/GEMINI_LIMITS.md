# Información sobre Gemini API - Cuotas y Límites

## Error: "RESOURCE_EXHAUSTED" / "429 Quota Exceeded"

Este error significa que **has alcanzado el límite de solicitudes gratuitas** de Gemini API.

## Límites del Plan Gratuito

### Gemini 1.5 Flash
- **Límite diario**: 1,500 solicitudes por día
- **Límite por minuto**: 15 solicitudes por minuto
- **Tokens por solicitud**: 1 millón de tokens

### Gemini 2.5 Flash (modelo actual)
- **Límite diario**: 20 solicitudes por día (advertencia: muy bajo)
- **Límite por minuto**: 2 solicitudes por minuto

**Por esta razón, si necesitas más cuota, considera usar Gemini 1.5 Flash que tiene una cuota mucho más generosa.**

## Soluciones Implementadas

### 1. Cambio de Modelo (Opcional)
- **Actual**: `gemini-2.5-flash` (20 req/día)
- **Alternativa**: `gemini-1.5-flash` (1,500 req/día)

### 2. Detección de Errores de Cuota
El sistema ahora detecta automáticamente cuando se agota la cuota y muestra un mensaje claro:
```
Has alcanzado el límite de consultas gratuitas de Gemini API.

Límite: 20 solicitudes por día (plan gratuito)
Intenta nuevamente en: X minutos

Mientras tanto, puedes usar el formulario manual.
```

### 3. Logging Completo
Todos los errores se registran en los logs para análisis.

## Consejos para Optimizar el Uso

### Usa Comandos Directos en Lugar de Consultas
En lugar de preguntar "¿Qué productos tengo?", simplemente mira la tabla del inventario.

### Comandos Eficientes
- **"Agrega FIFA 24, cantidad 10, precio 50000"** - Acción directa (recomendado)
- **"Hola, ¿cómo estás? ¿Puedes ayudarme?"** - Gasta cuota sin hacer nada útil (evitar)

### Usa el Formulario Manual
Para operaciones simples, usa el formulario de la izquierda:
- Agregar productos
- Actualizar productos
- Eliminar productos

**Reserva Gemini para:**
- Consultas complejas sobre el inventario
- Análisis de datos
- Recomendaciones

## Opciones si Necesitas Más Cuota

### Opción 1: Esperar (Gratis)
- Las cuotas se resetean cada 24 horas
- También hay límites por minuto que se recuperan rápido

### Opción 2: Usar Otra API Key (Gratis)
- Crea otro proyecto en Google AI Studio
- Obtén una nueva API key
- Reemplaza en el archivo `.env`

**Pasos:**
1. Ve a: https://aistudio.google.com/app/apikey
2. Crea un nuevo proyecto
3. Genera una nueva API key
4. Reemplázala en `.env`:
   ```
   GOOGLE_API_KEY=tu_nueva_api_key
   ```

### Opción 3: Actualizar a Plan de Pago
Google ofrece planes de pago con límites mucho más altos:
- **Pay-as-you-go**: $0.35 por 1 millón de tokens de entrada
- Sin límites estrictos de solicitudes
- Más información: https://ai.google.dev/pricing

### Opción 4: Usar Otro Modelo de IA
Puedes cambiar a otra API:
- **OpenAI GPT** (requiere cuenta de pago)
- **Anthropic Claude** (tiene plan gratuito con más cuota)
- **Ollama** (local, totalmente gratis, no requiere API)

## Monitorear Tu Uso

### Ver estadísticas de uso:
1. Ve a: https://aistudio.google.com/app/apikey
2. Selecciona tu API key
3. Verás el uso actual y los límites

### En los logs de GameStock:
```bash
cd /Users/kevinmanotas/Desktop/Game_stock
python ver_historial_logs.py | grep "gemini_chat"
```

Esto te mostrará:
- Cuántos mensajes has enviado
- Cuándo se enviaron
- Errores de cuota

## Resumen

1. El sistema detecta y maneja errores de cuota
2. Usa el formulario manual para operaciones simples
3. Reserva Gemini para consultas complejas
4. Si necesitas más cuota, crea otra API key gratis
5. Considera cambiar a `gemini-1.5-flash` para más cuota (1,500 req/día)

## Enlaces Útiles

- **Documentación de límites**: https://ai.google.dev/gemini-api/docs/rate-limits
- **Monitorear uso**: https://ai.dev/rate-limit
- **Crear API keys**: https://aistudio.google.com/app/apikey
- **Precios**: https://ai.google.dev/pricing
