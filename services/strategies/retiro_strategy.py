from abc import ABC, abstractmethod


class RetiroStrategy(ABC):

    @abstractmethod
    def obtener_tasa(self):
        pass


class ConservadoraStrategy(RetiroStrategy):

    def obtener_tasa(self):
        return 3.0


class EstandarStrategy(RetiroStrategy):

    def obtener_tasa(self):
        return 4.0


class AgresivaStrategy(RetiroStrategy):

    def obtener_tasa(self):
        return 5.0


class RetiroStrategyFactory:

    @staticmethod
    def create(tipo):

        if tipo == "conservadora":
            return ConservadoraStrategy()

        if tipo == "agresiva":
            return AgresivaStrategy()

        return EstandarStrategy()