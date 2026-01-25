from .strategies import StrategyFactory

class CoreService:
    """
    PATRÓN FACADE: Oculta la complejidad matemática y de estrategias.
    SOLID SRP: Este servicio encapsula toda la lógica de negocio.
    """

    @staticmethod
    def _safe_float(valor):
        """Convierte a float de forma segura (evita errores 500)"""
        if valor is None: return 0.0
        try: return float(valor)
        except: return 0.0

    @staticmethod
    def _normalizar(val, min_v, max_v):
        """Normaliza un valor entre 0 y 1 de forma segura"""
        rango = max_v - min_v
        if rango == 0: return 0.0
        return (val - min_v) / rango

    @classmethod
    def calcular_score(cls, modelo, pesos, maximos, minimos):
        """Aplica la fórmula matemática del proyecto"""
        try:
            # 1. Obtener valores limpios
            r = cls._safe_float(modelo.get("rendimiento"))
            p = cls._safe_float(modelo.get("precio"))
            c = cls._safe_float(modelo.get("consumo"))
            t = cls._safe_float(modelo.get("temperatura"))

            # 2. Normalizar
            Rn = cls._normalizar(r, minimos['rend'], maximos['rend'])
            Pn = cls._normalizar(p, minimos['prec'], maximos['prec'])
            Cn = cls._normalizar(c, minimos['cons'], maximos['cons'])
            Tn = cls._normalizar(t, minimos['temp'], maximos['temp'])

            # 3. Pesos
            alpha = cls._safe_float(pesos.get("peso_rendimiento"))
            beta = cls._safe_float(pesos.get("peso_precio"))
            gamma = cls._safe_float(pesos.get("peso_consumo"))
            delta = cls._safe_float(pesos.get("peso_temperatura"))

            return (alpha * Rn) + (beta * (1 - Pn)) + (gamma * (1 - Cn)) + (delta * (1 - Tn))
        except Exception as e:
            print(f"Error cálculo matemático: {e}")
            return 0.0

    @classmethod
    def generar_narrativa_avanzada(cls, perfil_nombre, top3, pesos):
        """Usa Factory + Strategy para crear el texto"""
        if not top3: return "No hay datos suficientes."
        
        ganador = top3[0]
        if len(top3) == 1:
            return f"Para el perfil {perfil_nombre}, la única opción disponible es {ganador['nombre']}."

        segundo = top3[1]

        # 1. Obtener la estrategia de la Fábrica
        estrategia = StrategyFactory.get_strategy(pesos)
        
        # 2. Usamos el patron de diseño de la estrategia
        texto_base = estrategia.generate_text(ganador, segundo)
        
        return f"Para el perfil {perfil_nombre}: {texto_base}"