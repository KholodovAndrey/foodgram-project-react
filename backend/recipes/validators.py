from django.core.validators import RegexValidator


class ColorValidator(RegexValidator):
    regex = '^#([A-Fa-f0-9]{3,6})$'
    message = 'Значение должно являться HEX-кодом'
