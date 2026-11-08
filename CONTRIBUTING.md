# Contributing Guidelines / Guía de Contribución

[🇪🇸 Español](#guía-de-contribución-español) | [🇬🇧 English](#contributing-guidelines-english)

---

<a name="contributing-guidelines-english"></a>
## 🇬🇧 Contributing Guidelines (English)

Thank you for your interest in improving **Thermor Onix DHW Plus**!

### How to contribute:
1. **Report bugs:** Open an issue on GitHub detailing the symptom, your device model, and Home Assistant logs (without exposing passwords or personal tokens).
2. **Propose enhancements:** If your water heater model supports additional commands (e.g. customized programming slots, anti-freeze thresholds), please open an issue or pull request.
3. **Pull Requests:**
   - Follow clean code practices (PEP 8, type hints).
   - Ensure `pyoverkiz` commands and state names are backwards compatible.
   - Test locally on your Home Assistant instance before opening a PR.

---

<a name="guía-de-contribución-español"></a>
## 🇪🇸 Guía de Contribución (Español)

¡Muchas gracias por tu interés en colaborar con **Thermor Onix DHW Plus**!

### Cómo contribuir:
1. **Reportar errores:** Abre una incidencia (*Issue*) en GitHub indicando el modelo exacto de tu termo, los síntomas observados y las líneas relevantes del registro de Home Assistant (ocultando siempre contraseñas o tokens).
2. **Sugerir mejoras:** Si tu modelo de termo (Thermor, Atlantic o Sauter) dispone de parámetros adicionales que quieras integrar (como franjas horarias personalizadas o perfiles de ausencia), abre una propuesta o Pull Request.
3. **Pull Requests:**
   - Respeta las buenas prácticas de Python (PEP 8 y tipado estricto).
   - Mantén las entidades desacopladas y no agregues dependencias pesadas innecesarias.
   - Prueba siempre los cambios en una instalación de Home Assistant antes de enviar la PR.
