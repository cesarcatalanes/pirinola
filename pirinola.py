import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random

# -----------------------------
# Lógica del juego
# -----------------------------

def girar_pirinola():
    return random.choice(["Toma 1", "Toma 2", "Pon 1", "Pon 2", "Todos ponen", "Toma todo"])

def aplicar_resultado(resultado, jugador, saldos, pozo):
    N = len(saldos)
    if resultado == "Toma 1":
        cantidad = min(1, pozo)
        saldos[jugador] += cantidad
        pozo -= cantidad
    elif resultado == "Toma 2":
        cantidad = min(2, pozo)
        saldos[jugador] += cantidad
        pozo -= cantidad
    elif resultado == "Pon 1":
        if saldos[jugador] > 0:
            saldos[jugador] -= 1
            pozo += 1
    elif resultado == "Pon 2":
        cantidad = min(2, saldos[jugador])
        saldos[jugador] -= cantidad
        pozo += cantidad
    elif resultado == "Todos ponen":
        for i in range(N):
            if saldos[i] > 0:
                saldos[i] -= 1
                pozo += 1
    elif resultado == "Toma todo":
        saldos[jugador] += pozo
        pozo = 0
    return saldos, pozo

def simular_pirinola(N, dinero_inicial, max_rondas=5000):
    saldos = [dinero_inicial] * N
    pozo = 0
    rondas = 0
    while rondas < max_rondas:
        for jugador in range(N):
            resultado = girar_pirinola()
            saldos, pozo = aplicar_resultado(resultado, jugador, saldos, pozo)
            rondas += 1
            # Nueva condición de victoria: un jugador tiene todo (saldos + pozo)
            if max(saldos) == N * dinero_inicial and pozo == 0:
                return rondas, saldos
    return rondas, saldos

def montecarlo_pirinola(N, dinero_inicial, repeticiones=1000, max_rondas=5000):
    rondas_totales = []
    for _ in range(repeticiones):
        rondas, _ = simular_pirinola(N, dinero_inicial, max_rondas)
        rondas_totales.append(rondas)
    promedio = np.mean(rondas_totales) if len(rondas_totales) > 0 else 0
    return promedio, rondas_totales

def simular_pirinola_historial(N, dinero_inicial, max_rondas=2000, paso=10):
    saldos = [dinero_inicial] * N
    pozo = 0
    rondas = 0
    historial = [saldos.copy()]
    while rondas < max_rondas:
        for jugador in range(N):
            resultado = girar_pirinola()
            saldos, pozo = aplicar_resultado(resultado, jugador, saldos, pozo)
            rondas += 1
            if rondas % paso == 0:  # Guardar cada "paso" rondas
                historial.append(saldos.copy())
            if max(saldos) == N * dinero_inicial and pozo == 0:
                historial.append(saldos.copy())
                return historial
    return historial

# -----------------------------
# Interfaz Streamlit
# -----------------------------
st.title("🎲 Simulación del Juego de la Pirinola")

# Parámetros configurables
N = st.sidebar.slider("Número de jugadores (N)", 2, 10, 4)
dinero_inicial = st.sidebar.slider("Dinero inicial por jugador", 5, 50, 10)
repeticiones = st.sidebar.slider("Número de simulaciones (Monte-Carlo)", 100, 5000, 1000, step=100)
max_rondas = st.sidebar.slider("Máximo de rondas por juego", 1000, 20000, 5000, step=500)

st.write(f"Jugadores: {N}, Dinero inicial: {dinero_inicial}, Repeticiones: {repeticiones}")

# Estado de botones
if "ejecutar" not in st.session_state:
    st.session_state.ejecutar = False
if "analizar" not in st.session_state:
    st.session_state.analizar = False

if st.button("▶ Ejecutar Simulación"):
    st.session_state.ejecutar = True
if st.button("📊 Analizar efecto de jugadores"):
    st.session_state.analizar = True

# -----------------------------
# Resultados globales
# -----------------------------
if st.session_state.ejecutar:
    promedio, rondas_totales = montecarlo_pirinola(N, dinero_inicial, repeticiones, max_rondas)

    st.subheader("📌 Resultados globales")
    st.write(f"Promedio de rondas hasta que hay un ganador: **{promedio:.2f}**")

    # Histograma
    fig, ax = plt.subplots()
    ax.hist(rondas_totales, bins=30, edgecolor="black")
    ax.set_title("Distribución de rondas hasta que alguien gana")
    ax.set_xlabel("Rondas")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Evolución de saldos
    historial = simular_pirinola_historial(N, dinero_inicial, max_rondas)
    fig2, ax2 = plt.subplots()
    for j in range(len(historial[0])):
        ax2.plot([h[j] for h in historial], label=f"Jugador {j+1}")
    ax2.set_title("Evolución de saldos por jugador (un juego)")
    ax2.set_xlabel("Ronda (cada 10)")
    ax2.set_ylabel("Dinero")
    ax2.legend()
    st.pyplot(fig2)

# -----------------------------
# Efecto del número de jugadores
# -----------------------------
if st.session_state.analizar:
    st.subheader("📊 Efecto del número de jugadores")
    min_jugadores = st.slider("Número mínimo de jugadores", 2, 5, 2)
    max_jugadores = st.slider("Número máximo de jugadores", min_jugadores, 15, 8)

    jugadores = list(range(min_jugadores, max_jugadores + 1))
    promedios = []
    for Nj in jugadores:
        promedio, _ = montecarlo_pirinola(Nj, dinero_inicial, repeticiones//2, max_rondas)
        promedios.append(promedio)

    fig3, ax3 = plt.subplots()
    ax3.plot(jugadores, promedios, marker="o")
    ax3.set_title("Número de jugadores vs rondas promedio")
    ax3.set_xlabel("Número de jugadores")
    ax3.set_ylabel("Rondas promedio")
    st.pyplot(fig3)