# TechAdvisor – Sistema de Recomendación de Hardware

**Universidad de las Américas**  
**Ingeniería Web**

**TechAdvisor** es una plataforma web avanzada diseñada para recomendar computadoras (Laptops y Escritorio) utilizando un **algoritmo de decisión multicriterio**. El sistema conecta un back-office administrativo con un front-office para el usuario final, ofreciendo recomendaciones basadas en perfiles de uso específicos.

---

## 1. Arquitectura e Ingeniería de Software

Este proyecto destaca por la refactorización de su núcleo lógico ("Core"), pasando de una estructura monolítica a una arquitectura modular basada en **Principios SOLID** y **Patrones de Diseño**.

### Patrones de Diseño Aplicados (Gang of Four)

1.  **Facade Pattern (Fachada):**
    *   **Ubicación:** `app/services.py` -> `CoreService`
    *   **Propósito:** Oculta la complejidad del cálculo matemático (normalización, limpieza de datos, ponderación) detrás de una interfaz simplificada. Los controladores solo piden "calcular" sin saber cómo funciona la matemática interna.

2.  **Strategy Pattern (Estrategia):**
    *   **Ubicación:** `app/strategies.py`
    *   **Propósito:** Define una familia de algoritmos para la **"Narrativa de Recomendación"**.
    *   *Funcionamiento:* Si el usuario prioriza el precio, se activa la estrategia `PriceFocused`. Si prioriza la potencia, se activa `PerformanceFocused`. Esto permite cambiar el comportamiento del texto sin usar condicionales complejos.

3.  **Factory Method Pattern:**
    *   **Ubicación:** `app/strategies.py` -> `StrategyFactory`
    *   **Propósito:** Centraliza la creación de las estrategias. La fábrica recibe los pesos del perfil y decide dinámicamente qué "experto narrativo" instanciar.

### 📐 Principios SOLID Implementados

*   **SRP (Single Responsibility Principle):**
    *   `routes.py`: Solo maneja peticiones HTTP y redirecciones.
    *   `services.py`: Solo contiene la lógica de negocio y matemática.
    *   `models.py`: Solo gestiona el acceso a la Base de Datos.
*   **OCP (Open/Closed Principle):**
    *   El sistema de recomendaciones está abierto a extensión (podemos agregar nuevas estrategias de texto) pero cerrado a modificación (no necesitamos tocar el código base funcional).

---

## 2. Core Matemático (IEG)

El sistema calcula el **Índice de Eficiencia Global (IEG)** para cada computadora.

**Fórmula:**
`IEG = (α * Rn) + (β * (1 - Pn)) + (γ * (1 - Cn)) + (δ * (1 - Tn))`

Donde:
*   **Rn, Pn, Cn, Tn:** Son los valores normalizados (0 a 1) de Rendimiento, Precio, Consumo y Temperatura.
*   **α, β, γ, δ:** Son los pesos asignados por el Perfil de Uso (configurables desde el Admin).
*   **Lógica:** Se maximiza el beneficio (Rendimiento) y se minimizan los costos (Precio, Consumo, Calor).

---

## 3. Módulos del Sistema

### Módulo Administrativo (Admin)
*   **Dashboard:** Estadísticas visuales y métricas clave.
*   **CRUDs Completos:** Gestión de Marcas, Perfiles de Uso y Modelos.
*   **Calibrador del Core:** Simulador en tiempo real para ajustar los pesos del algoritmo y probar resultados antes de salir a producción.

### Módulo de Usuario (Cliente)
*   **Buscador Híbrido:** Algoritmo capaz de buscar, fusionar y comparar simultáneamente colecciones de **PC de Escritorio** y **Laptops**.
*   **Filtros Inteligentes:** Selección en cascada (Perfil -> Marca).
*   **Podio de Resultados:** Visualización de los Top 3 modelos ganadores.
*   **Recomendación con IA Simbólica:** Generación de texto natural explicando por qué ganó un modelo (gracias al patrón Strategy).
*   **Tiendas y Mapas:** Módulo de geolocalización de tiendas según la ciudad.

---

## 4. Stack Tecnológico

*   **Lenguaje:** Python 3.10+
*   **Backend:** Flask (Blueprints)
*   **Base de Datos:** MongoDB Atlas (NoSQL en la nube)
*   **ORM/Driver:** PyMongo
*   **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript (Fetch API)
*   **Seguridad:** Hashing de contraseñas (Werkzeug), Variables de entorno (.env)
