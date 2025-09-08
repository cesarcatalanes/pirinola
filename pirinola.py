import random
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Reglas de la Perinola
resultados = ["Pon 1", "Pon 2", "Toma 1", "Toma 2", "Toma todo", "Todos ponen"]

# Función para jugar un turno
def jugar_turno(jugador, jugadores, pozocomun, billeteras):
    accion = random.choice(resultados)
    if accion == "Pon 1":
        if billeteras[jugador] > 0:
            billeteras[jugador] -= 1
            pozocomun += 1
    elif accion == "Pon 2":
        if billeteras[jugador] >= 2:
            billeteras[jugador] -= 2
            pozocomun += 2
        elif billeteras[jugador] > 0:
            pozocomun += billeteras[jugador]
            billeteras[jugador] = 0
    elif accion == "Toma 1":
        if pozocomun > 0:
            billeteras[jugador] += 1
            pozocomun -= 1
    elif accion == "Toma 2":
        if pozocomun >= 2:
            billeteras[jugador] += 2
            pozocomun -= 2
        elif pozocomun > 0:
            billeteras[jugador] += pozocomun
            pozocomun = 0
    elif accion == "Toma todo":
        billeteras[jugador] += pozocomun
        pozocomun = 0
    elif accion == "Todos ponen":
        for j in range(jugadores):
            if billeteras[j] > 0:
                billeteras[j] -= 1
                pozocomun += 1
    return pozocomun, billeteras

# Simulación completa
def simular_perinola(jugadores=4, juegos=100, dinero_inicial=10):
    billeteras = [dinero_inicial]*jugadores
    pozocomun = jugadores  # cada jugador pone 1 al inicio
    for j in range(jugadores):
        billeteras[j] -= 1

    historial = [[] for _ in range(jugadores)]

    for g in range(juegos):
        for turno in range(jugadores):
            pozocomun, billeteras = jugar_turno(turno, jugadores, pozocomun, billeteras)
            for j in range(jugadores):
                historial[j].append(billeteras[j])
            if sum(b > 0 for b in billeteras) == 1:
                return historial, g+1, billeteras  # un ganador con todo el dinero
    return historial, juegos, billeteras

# Streamlit App

st.title("Simulación del Juego de la Perinola 🎲")

# Parámetros configurables
jugadores = st.slider("Número de jugadores", 2, 10, 4)
dinero_inicial = st.slider("Dinero inicial por jugador", 5, 50, 15)
repeticiones = st.slider("Número de repeticiones Monte Carlo", 10, 500, 100)
max_jugadores = st.slider("Máximo número de jugadores para análisis comparativo", 2, 10, 6)

if st.button("Ejecutar simulación"):
    # Simulación simple
    historial, juegos_necesarios, billeteras_finales = simular_perinola(jugadores=jugadores, juegos=500, dinero_inicial=dinero_inicial)

    st.write(f"Se necesitaron **{juegos_necesarios}** juegos para que un jugador se quedara con todo el dinero o se terminara la simulación.")

    # Gráfica evolución
    st.subheader("Evolución de cada jugador")
    fig, ax = plt.subplots(figsize=(10,6))
    for idx, h in enumerate(historial):
        ax.plot(h, label=f"Jugador {idx+1}")
    ax.set_xlabel("Turnos")
    ax.set_ylabel("Dinero en billetera")
    ax.set_title("Evolución de la simulación de la Perinola")
    ax.legend()
    st.pyplot(fig)

    # Gráfica de Ganancia/Pérdida final
    st.subheader("Ganancia o pérdida final por jugador")
    fig2, ax2 = plt.subplots(figsize=(8,5))
    final_ganancia = [b - dinero_inicial for b in billeteras_finales]
    ax2.bar([f"Jugador {i+1}" for i in range(len(billeteras_finales))], final_ganancia, color='skyblue')
    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_xlabel("Jugadores")
    ax2.set_ylabel("Ganancia / Pérdida final")
    ax2.set_title("Ganancia o pérdida al término de la simulación")
    st.pyplot(fig2)

    # Promedio de juegos hasta un ganador
    promedio = promedio_juegos_para_ganador(jugadores=jugadores, dinero_inicial=dinero_inicial, repeticiones=repeticiones)
    if promedio:
        st.success(f"En promedio, con {jugadores} jugadores se necesitan {promedio:.2f} juegos para que haya un ganador.")

    # Efecto del número de jugadores
    st.subheader("Efecto del número de jugadores en la duración del juego")
    jugadores_list, promedios = efecto_numero_jugadores(max_jugadores=max_jugadores, dinero_inicial=dinero_inicial, repeticiones=int(repeticiones/2))
    fig3, ax3 = plt.subplots(figsize=(8,5))
    ax3.plot(jugadores_list, promedios, marker='o')
    ax3.set_xlabel("Número de jugadores")
    ax3.set_ylabel("Juegos promedio hasta que alguien gana todo")
    ax3.set_title("Efecto del número de jugadores en la duración del juego")
    ax3.grid(True)
    st.pyplot(fig3)
