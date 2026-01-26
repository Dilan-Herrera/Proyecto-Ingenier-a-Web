from app.services import CoreService

def test_calcular_score_retorna_float():
    modelo = {
        "rendimiento": 80,
        "precio": 1000,
        "consumo": 60,
        "temperatura": 70
    }

    pesos = {
        "peso_rendimiento": 0.4,
        "peso_precio": 0.3,
        "peso_consumo": 0.2,
        "peso_temperatura": 0.1
    }

    maximos = {
        "rend": 100,
        "prec": 1500,
        "cons": 100,
        "temp": 90
    }

    minimos = {
        "rend": 50,
        "prec": 800,
        "cons": 40,
        "temp": 50
    }

    score = CoreService.calcular_score(modelo, pesos, maximos, minimos)

    # Validaciones
    assert isinstance(score, float)
    assert score >= 0
