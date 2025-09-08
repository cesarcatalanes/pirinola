import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# Simulación de un juego de perinola con límite de rondas
def jugar_perinola(jugadores=4, dinero_inicial=100, max_rondas=2000):
    billeteras = [dinero_inicial for _ in range(jugadores)]
    pozo = 0
    historial = [[] for _ in range(jugadores)]
    resultados = ["Pon 1", "Pon 2", "Toma 1", "Toma 2", "Toma todo", "Todos ponen"]

    for ronda in range(1, max_rondas+1):
        for turno in range(jugadores):
            if billeteras[turno] <= 0:
                continue
            tiro = random.choice(resultados)

            if tiro == "Pon 1" and billeteras[turno] >= 1:
                billeteras[turno] -= 1; pozo += 1
            elif tiro == "Pon 2" and billeteras[turno] >= 2:
                billeteras[turno] -= 2; pozo += 2
            elif tiro == "Toma 1" and pozo >= 1:
                billeteras[turno] += 1; pozo -= 1
            elif tiro == "Toma 2" and pozo >= 2:
                billeteras[turno] += 2; pozo -= 2
            elif tiro == "Toma todo":
                billeteras[turno] += pozo; pozo = 0
            elif tiro == "Todos ponen":
                for j in range(jugadores):
                    if billeteras[j] > 0:
                        billeteras[j] -= 1; pozo += 1

            for j in range(jugadores):
                historial[j].append(billeteras[j])

            jugadores_activos = sum([1 for b in billeteras if b > 0])
            if jugadores_activos == 1:
                return historial, ronda, billeteras, True  # True = hubo ganador
    
    return historial, max_rondas, billeteras, False  # False = no hubo ganador

# 1. Tiempo hasta que un jugador se queda sin dinero
def tiempo_hasta_primer_quebrado(jugadores=4, dinero_inicial=100, repeticiones=100, max_rondas=2000):
    rondas = []
    for _ in range(repeticiones):
        billeteras = [dinero_inicial for _ in range(jugadores)]
        pozo = 0
        resultados = ["Pon 1", "Pon 2", "Toma 1", "Toma 2", "Toma todo", "Todos ponen"]
        for ronda in range(1, max_rondas+1):
            for turno in range(jugadores):
                if billeteras[turno] <= 0:
                    continue
                tiro = random.choice(resultados)
                if tiro == "Pon 1" and billeteras[turno] >= 1:
                    billeteras[turno] -= 1; pozo += 1
                elif tiro == "Pon 2" and billeteras[turno] >= 2:
                    billeteras[turno] -= 2; pozo += 2
                elif tiro == "Toma 1" and pozo >= 1:
                    billeteras[turno] += 1; pozo -= 1
                elif tiro == "Toma 2" and pozo >= 2:
                    billeteras[turno] += 2; pozo -= 2
                elif tiro == "Toma todo":
                    billeteras[turno] += pozo; pozo = 0
                elif tiro == "Todos ponen":
                    for j in range(jugadores):
                        if billeteras[j] > 0:
                            billeteras[j] -= 1; pozo += 1
                # si alguien quiebra
                if billeteras[turno] == 0:
                    rondas.append(ronda)
                    break
            else:
                continue
            break
    return np.mean(rondas), np.std(rondas), rondas

# 2. Proporción de juegos con ganador
def promedio_juegos_con_ganador(jugadores=4, dinero_inicial=100, repeticiones=100, max_rondas=2000):
    ganadores = 0
    for _ in range(repeticiones):
        _, _, _, hubo_ganador = jugar_perinola(jugadores, dinero_inicial, max_rondas)
        if hubo_ganador:
            ganadores += 1
    return ganadores / repeticiones

# 3. Efecto del número de jugadores
def efecto_numero_jugadores(max_jugadores=8, dinero_inicial=100, repeticiones=50, max_rondas=2000):
    resultados = {}
    for n in range(2, max_jugadores+1):
        rondas = []
        for _ in range(repeticiones):
            _, r, _, _ = jugar_perinola(n, dinero_inicial, max_rondas)
            rondas.append(r)
        resultados[n] = (np.mean(rondas), np.std(rondas))
    return resultados
 
# Interfaz Streamlit

st.title("Simulación del Juego de la Perinola")

st.sidebar.header("Parámetros de la simulación")
num_jugadores = st.sidebar.slider("Número de jugadores", 2, 10, 4)
dinero_inicial = st.sidebar.number_input("Dinero inicial por jugador", 10, 500, 100)
repeticiones = st.sidebar.slider("Repeticiones Monte Carlo", 10, 1000, 200)
max_rondas = st.sidebar.slider("Máximo de rondas por juego", 100, 10000, 2000, step=100)

# Simulación de un juego
st.header("Simulación de un juego individual")
historial, rondas, billeteras_final, hubo_ganador = jugar_perinola(
    jugadores=num_jugadores, dinero_inicial=dinero_inicial, max_rondas=max_rondas)
st.write(f"Juego terminó en **{rondas} rondas**")
st.write(f"Billeteras finales: {billeteras_final}")
st.write(f"¿Hubo ganador?: {'Sí' if hubo_ganador else 'No'}")

# Graficar historial
fig, ax = plt.subplots()
for i, h in enumerate(historial):
    ax.plot(h, label=f"Jugador {i+1}")
ax.set_xlabel("Turnos")
ax.set_ylabel("Dinero")
ax.set_title("Evolución de la billetera por jugador")
ax.legend()
st.pyplot(fig)

# Monte Carlo
st.header("Monte Carlo: Estadísticas")
media, std, rondas_mc = tiempo_hasta_primer_quebrado(
    jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=repeticiones, max_rondas=max_rondas)
st.write(f"Tiempo promedio hasta que un jugador quiebra: **{media:.2f} ± {std:.2f} rondas**")

fig, ax = plt.subplots()
ax.hist(rondas_mc, bins=30, alpha=0.7, color='blue')
ax.set_xlabel("Rondas")
ax.set_ylabel("Frecuencia")
ax.set_title("Distribución de rondas hasta primer jugador quebrado")
st.pyplot(fig)

prop_ganadores = promedio_juegos_con_ganador(
    jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=repeticiones, max_rondas=max_rondas)
st.write(f"Proporción de juegos con ganador: **{prop_ganadores*100:.1f}%**")

# Efecto del número de jugadores
st.header("Efecto del número de jugadores")
res = efecto_numero_jugadores(
    max_jugadores=num_jugadores, dinero_inicial=dinero_inicial, repeticiones=int(repeticiones/2), max_rondas=max_rondas)

jugadores = list(res.keys())
medias = [res[j][0] for j in jugadores]
stds = [res[j][1] for j in jugadores]

fig, ax = plt.subplots()
ax.errorbar(jugadores, medias, yerr=stds, fmt='o-', capsize=5)
ax.set_xlabel("Número de jugadores")
ax.set_ylabel("Promedio de rondas hasta ganador")
ax.set_title("Efecto del número de jugadores en la duración del juego")
st.pyplot(fig)

