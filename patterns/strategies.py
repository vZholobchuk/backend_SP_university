from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class GradeStrategy(ABC):
    """Абстрактний базовий клас (інтерфейс) для всіх стратегій обчислення оцінок/рейтингу."""
    @abstractmethod
    def calculate(self, grades: List[float], **kwargs) -> Dict[str, Any]:
        pass

class SimpleAverageStrategy(GradeStrategy):
    """Стратегія простого середнього арифметичного бала."""
    def calculate(self, grades: List[float], **kwargs) -> Dict[str, Any]:
        if not grades:
            return {"average": 0.0, "count": 0, "type": "simple_average"}
        avg = round(sum(grades) / len(grades), 2)
        return {
            "average": avg,
            "count": len(grades),
            "type": "simple_average"
        }

class WeightedGradeStrategy(GradeStrategy):
    """Стратегія середньозваженого бала з урахуванням кредитів дисциплін або ваги робіт."""
    def calculate(self, grades: List[float], **kwargs) -> Dict[str, Any]:
        weights: Optional[List[float]] = kwargs.get("weights")
        if not grades:
            return {"average": 0.0, "total_weight": 0.0, "type": "weighted_average"}
        
        if weights is None:
            raise ValueError("Для обчислення середньозваженого бала необхідно вказати вагові коефіцієнти (weights)")
        if len(grades) != len(weights):
            raise ValueError(f"Кількість оцінок ({len(grades)}) не відповідає кількості ваг ({len(weights)})")
        if any(w < 0 for w in weights):
            raise ValueError("Вагові коефіцієнти не можуть бути від'ємними")
        total_weight = sum(weights)
        if total_weight <= 0:
            raise ValueError("Сума вагових коефіцієнтів має бути додатною")

        weighted_sum = sum(g * w for g, w in zip(grades, weights))
        avg = round(weighted_sum / total_weight, 2)
        return {
            "average": avg,
            "total_weight": total_weight,
            "type": "weighted_average"
        }

class ECTSRatingStrategy(GradeStrategy):
    """Стратегія обчислення академічного рейтингу за Європейською кредитно-трансферною системою (ECTS)."""
    def calculate(self, grades: List[float], **kwargs) -> Dict[str, Any]:
        if not grades:
            return {"average": 0.0, "ects": "F", "description": "Немає даних", "type": "ects_rating"}
        
        avg = round(sum(grades) / len(grades), 2)
        if avg >= 90:
            ects, desc = "A", "Відмінно (Excellent)"
        elif avg >= 82:
            ects, desc = "B", "Дуже добре (Very Good)"
        elif avg >= 74:
            ects, desc = "C", "Добре (Good)"
        elif avg >= 64:
            ects, desc = "D", "Задовільно (Satisfactory)"
        elif avg >= 60:
            ects, desc = "E", "Достатньо (Sufficient)"
        elif avg >= 35:
            ects, desc = "FX", "Незадовільно з можливістю повторного складання"
        else:
            ects, desc = "F", "Незадовільно з обов'язковим повторним курсом"

        return {
            "average": avg,
            "ects": ects,
            "description": desc,
            "type": "ects_rating"
        }

class GradeCalculator:
    """Контекст (Context), що використовує обрану стратегію оцінювання."""
    def __init__(self, strategy: GradeStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> GradeStrategy:
        return self._strategy

    def set_strategy(self, strategy: GradeStrategy):
        """Динамічна зміна стратегії під час виконання програми."""
        self._strategy = strategy

    def compute(self, grades: List[float], **kwargs) -> Dict[str, Any]:
        return self._strategy.calculate(grades, **kwargs)
