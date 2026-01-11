from abc import ABC, abstractmethod

# PATRÓN 1: STRATEGY (Comportamiento)

class NarrativeStrategy(ABC):
    @abstractmethod
    def generate_text(self, ganador, segundo):
        pass

# Estrategia A: Enfocada en Ahorro
class PriceFocusedStrategy(NarrativeStrategy):
    def generate_text(self, ganador, segundo):
        ahorro = float(segundo['precio']) - float(ganador['precio'])
        return (f"¡La opción inteligente! Te recomiendo la <strong>{ganador['nombre']}</strong>. "
                f"Aunque compite de cerca con la {segundo['nombre']}, esta opción protege tu bolsillo "
                f"permitiéndote <strong>ahorrar ${ahorro:.0f}</strong> sin sacrificar calidad.")

# Estrategia B: Enfocada en Potencia
class PerformanceFocusedStrategy(NarrativeStrategy):
    def generate_text(self, ganador, segundo):
        diff = float(ganador['rendimiento']) - float(segundo['rendimiento'])
        return (f"Para tu perfil exigente, la ganadora indiscutible es la <strong>{ganador['nombre']}</strong>. "
                f"Su rendimiento es superior por <strong>{diff:.0f} puntos</strong> frente a la {segundo['nombre']}. "
                f"Vale la pena la inversión por esa potencia extra.")

# Estrategia C: Enfocada en Equilibrio
class BalancedStrategy(NarrativeStrategy):
    def generate_text(self, ganador, segundo):
        return (f"La <strong>{ganador['nombre']}</strong> es la ganadora técnica. "
                f"Logra el mejor balance general (Score: {ganador['score']}) superando "
                f"ligeramente a la {segundo['nombre']} en la combinación de tus requisitos.")

# PATRÓN 2: FACTORY METHOD (Creación)

class StrategyFactory:
    """
    Esta fábrica decide QUÉ estrategia usar basándose en los pesos del perfil.
    """
    @staticmethod
    def get_strategy(pesos):
        mayor_peso = max(pesos, key=pesos.get)
        
        if mayor_peso == "peso_precio":
            return PriceFocusedStrategy()
        elif mayor_peso == "peso_rendimiento":
            return PerformanceFocusedStrategy()
        else:
            return BalancedStrategy()