#Flores Estopier Rodrigo
#Aplicaciones para comunicaciones en red 6CV1
#Fecha de creacion: 28/09/2024
#Algoritmo que calcula los dias vividos de una persona
#Entradas: dia, mes, año (nacimiento) y dia, mes, año (actual)
#Salidas: dias vividos modulo tres de los dias vividos

# Función para verificar si un año es bisiesto
def es_bisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)

# Función para obtener los días del mes según el año
def dias_en_mes(mes, anio):
    # Días por cada mes (en años normales)
    dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # En febrero, si es año bisiesto, se asigna 29 días
    if mes == 2 and es_bisiesto(anio):
        return 29
    return dias_por_mes[mes - 1]

# Función principal para calcular los días vividos
def calcular_dias_vividos_sin_librerias(fecha_nacimiento, fecha_actual):
    # Separar el año, mes y día de las fechas
    nacimiento_anio, nacimiento_mes, nacimiento_dia = map(int, fecha_nacimiento.split('-'))
    actual_anio, actual_mes, actual_dia = map(int, fecha_actual.split('-'))

    # Verificar si la fecha actual es anterior a la fecha de nacimiento
    if (actual_anio, actual_mes, actual_dia) < (nacimiento_anio, nacimiento_mes, nacimiento_dia):
        raise ValueError("La fecha actual no puede ser anterior a la fecha de nacimiento.")

    # Inicializamos el contador de días
    dias_vividos = 0

    # Si las fechas están en el mismo año
    if nacimiento_anio == actual_anio:
        # Si están en el mismo mes
        if nacimiento_mes == actual_mes:
            dias_vividos = actual_dia - nacimiento_dia
        else:
            # Días restantes en el mes de nacimiento
            dias_vividos += dias_en_mes(nacimiento_mes, nacimiento_anio) - nacimiento_dia
            # Días completos de los meses intermedios
            for mes in range(nacimiento_mes + 1, actual_mes):
                dias_vividos += dias_en_mes(mes, nacimiento_anio)
            # Días en el mes actual
            dias_vividos += actual_dia
    else:
        # Días restantes en el año de nacimiento
        dias_vividos += dias_en_mes(nacimiento_mes, nacimiento_anio) - nacimiento_dia
        for mes in range(nacimiento_mes + 1, 13):
            dias_vividos += dias_en_mes(mes, nacimiento_anio)

        # Días de los años completos entre nacimiento y año actual
        for anio in range(nacimiento_anio + 1, actual_anio):
            dias_vividos += 366 if es_bisiesto(anio) else 365

        # Días transcurridos en el año actual
        for mes in range(1, actual_mes):
            dias_vividos += dias_en_mes(mes, actual_anio)
        dias_vividos += actual_dia

    return dias_vividos

# Ejemplo de uso:
fecha_nacimiento = "2003-02-03"  # Formato: YYYY-MM-DD
fecha_actual = "2024-09-25"      # Formato: YYYY-MM-DD

dias = calcular_dias_vividos_sin_librerias(fecha_nacimiento, fecha_actual)
print(f"Has vivido {dias} días hasta la fecha {fecha_actual}.")
print(f"El modulo de días vividos por 3 es: {dias % 3}")
