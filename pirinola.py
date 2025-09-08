import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# Función: Simulación de un juego de perinola
def jugar_perinola(jugadores=4, dinero_inicial=100):
    billeteras = [dinero_inicial for _ in range(jugadores)]
    pozo = 0
    historial = [[] for _ in range(jugadores)]
    resultados = ["Pon 1", "Pon 2", "Toma 1", "Toma 2", "Toma todo", "Todos ponen"]

    ronda = 0
    while True:
        ronda += 1
        for turno in range(jugadores):
            if billeteras[turno] <= 0:
                continue
            tiro = random.choice(resultados)

            if tiro == "Pon 1":
                if billeteras[turno] >= 1:
                    billeteras[turno] -= 1
                    pozo += 1
            elif tiro == "Pon 2":
                if billeteras[turno] >= 2:
                    billeteras[turno] -= 2
                    pozo += 2
            elif tiro == "Toma 1":
                if pozo >= 1:
                    billeteras[turno] += 1
                    pozo -= 1
            elif tiro == "Toma 2":
                if pozo >= 2:
                    billeteras[turno] += 2
                    pozo -= 2
            elif tiro == "Toma todo":
                billeteras[turno] += pozo
                pozo = 0
            elif tiro == "Todos ponen":
                for j in range(jugadores):
                    if billeteras[j] > 0:
                        billeteras[j] -= 1
                        pozo += 1

            for j in range(jugadores):
                historial[j].append(billeteras[j])

            jugadores_activos = sum([1 for b in billeteras if b > 0])
            if jugadores_activos == 1:
                return historial, ronda, billeteras

# Funciones de Monte Carlo
def tiempo_para_quedarse_sin_dinero(jugadores=4, dinero_inicial=100, repeticiones=100):
    rondas = []
    for _ in range(repeticiones):
        historial, r, billeteras = jugar_perinola(jugadores, dinero_inicial)
        rondas.append(r)
    return np.mean(rondas), np.std(rondas), rondas

def promedio_juegos_con_ganador(jugadores=4, dinero_inicial=100, repeticiones=100):
    ganadores = 0
    for _ in range(repeticiones):
        historial, r, billeteras = jugar_perinola(jugadores, dinero_inicial)
        if sum([1 for b in billeteras if b > 0]) == 1:
            ganadores += 1
    return ganadores / repeticiones

def efecto_numero_jugadores(max_jugadores=8, dinero_inicial=100, repeticiones=50):
    resultados = {}
    for n in range(2, max_jugadores+1):
        rondas = []
        for _ in range(repeticiones):
            historial, r, billeteras = jugar_perinola(n, dinero_inicial)
            rondas.append(r)
        resultados[n] = (np.mean(rondas), np.std(rondas))
    return resultados

# Gráficas
def graficar_historial(historial):
    fig, ax = plt.subplots()
    for i, h in enumerate(historial):
        ax.plot(h, label=f"Jugador {i+1}")
    ax.set_xlabel("Turnos")
    ax.set_ylabel("Dinero")
    ax.set_title("Evolución de la billetera por jugador")
    ax.legend()
    st.pyplot(fig)

def graficar_histograma_rondas(rondas):
    fig, ax = plt.subplots()
    ax.hist(rondas, bins=30, alpha=0.7, color='blue')
    ax.set_xlabel("Rondas hasta ganador")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de rondas (Monte Carlo)")
    st.pyplot(fig)

def graficar_efecto_jugadores(resultados):
    jugadores = list(resultados.keys())
    medias = [resultados[j][0] for j in jugadores]
    stds = [resultados[j][1] for j in jugadores]

    fig, ax = plt.subplots()
    ax.errorbar(jugadores, medias, yerr=stds, fmt='o-', capsize=5)
    ax.set_xlabel("Número de jugadores")
    ax.set_ylabel("Promedio de rondas hasta ganador")
    ax.set_title("Efecto del número de jugadores en la duración del juego")
    st.pyplot(fig)

#  Streamlit

st.title(" Simulación del Juego de la Perinola")

st.sidebar.header("Parámetros de la simulación")
num_jugadores = st.sidebar.slider("Número de jugadores", 2, 10, 4)
dinero_inicial = st.sidebar.number_input("Dinero inicial por jugador", 10, 500, 100)
repeticiones = st.sidebar.slider("Repeticiones Monte Carlo", 10, 1000, 200)

st.header("Simulación de un juego individual")
historial, rondas, billeteras_final = jugar_perinola(jugadores=num_jugadores, dinero_inicial=dinero_inicial)
st.write(f"Juego terminó en **{rondas} rondas**")
st.write(f"Billeteras finales: {billeteras_final}")
graficar_historial(historial)

st.header("Monte Carlo: Estadísticas")
media, std, rondas_mc = tiempo_para_quedarse_sin_dinero(jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=repeticiones)
st.write(f"Tiempo promedio hasta ganador: **{media:.2f} ± {std:.2f} rondas**")

graficar_histograma_rondas(rondas_mc)

prop_ganadores = promedio_juegos_con_ganador(jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=repeticiones)
st.write(f"Proporción de juegos con ganador: **{prop_ganadores*100:.1f}%**")

st.header("Efecto del número de jugadores")
res = efecto_numero_jugadores(max_jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=int(repeticiones/2))
graficar_efecto_jugadores(res)

