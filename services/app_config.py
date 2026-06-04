class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            #cls._instance.moneda_default = "ARS"
            cls._instance.categorias_default = [
                "Sueldo",
                "Comida",
                "Transporte",
                "Servicios",
                "Ocio",
                "Salud",
                "Otros",
            ]
        return cls._instance