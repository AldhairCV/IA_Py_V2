# web_app.py (equivalente a main.py en Streamlit)
import streamlit as st
from model.logica_difusa import generar_recomendacion
from model.preprocesamiento import codificar_respuestas
from nlp.analisis_sentimientos import analizar_sentimiento
import joblib

modelo = joblib.load('model/modelo_clasificacion.pkl')

# Opciones para las preguntas tipo Likert
opciones = ["Nunca", "A veces", "Frecuentemente", "Siempre"]
preguntas = [
    "¿Con qué frecuencia se siente desmotivado?",
    "¿Ha perdido interés en actividades?",
    "¿Le cuesta concentrarse?",
    "¿Siente tristeza sin razón?",
    "¿Tiene problemas para dormir?"
]

def evaluar_emocional():
    st.title("🧠 Sistema de Apoyo Emocional")
    st.subheader("Evaluación para Estudiantes")

    nombre = st.text_input("👤 Nombre del estudiante")
    texto = st.text_area("📝 ¿Cómo te sientes hoy?")

    respuestas_texto = []
    for i, pregunta in enumerate(preguntas):
        respuesta = st.selectbox(f"❓ {pregunta}", opciones, key=f"pregunta_{i}")
        respuestas_texto.append(respuesta)

    if st.button("🟢 Evaluar"):
        if not nombre or not texto:
            st.warning("⚠️ Por favor, complete todos los campos.")
            return

        respuestas_codificadas = [codificar_respuestas(r) for r in respuestas_texto]
        sentimiento = analizar_sentimiento(texto)
        riesgo = modelo.predict([respuestas_codificadas])[0]
        recomendacion = generar_recomendacion(riesgo, sentimiento)

        st.success("✅ Evaluación completada")
        st.write(f"**Estudiante:** {nombre}")
        st.write(f"**Riesgo emocional detectado:** {riesgo}")
        st.write(f"**Sentimiento expresado:** {sentimiento}")
        st.info(f"**Recomendación:** {recomendacion}")

        guardar_respuesta(
            nombre=nombre,
            texto=texto,
            respuestas_texto=respuestas_texto,
            riesgo=riesgo,
            sentimiento=sentimiento
        )
        st.success("📝 Respuesta guardada en CSV y Firebase")

def panel_docente():
    import csv

    st.title("📋 Panel del Tutor")

    try:
        with open("data/respuestas_guardadas.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

            if rows:
                header = ["Fecha", "Nombre", "Mensaje", "R1", "R2", "R3", "R4", "R5", "Riesgo", "Sentimiento"]
                data = rows

                for row in data:
                    riesgo = row[8].strip().lower()
                    color = "🔴" if riesgo == "muy_alto" else "🟡" if riesgo in ["alto", "medio"] else "🟢"
                    with st.expander(f"{color} {row[1]} - {row[0]}"):
                        for i, h in enumerate(header):
                            st.write(f"**{h}:** {row[i]}")
            else:
                st.info("No hay datos registrados.")
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo de respuestas.")

def main():
    st.sidebar.title("🔐 Selección de Rol")
    rol = st.sidebar.radio("Selecciona tu rol:", ["Estudiante", "Docente"])

    if rol == "Estudiante":
        evaluar_emocional()
    else:
        clave = st.sidebar.text_input("Clave de acceso", type="password")
        if clave == "tutor123":
            panel_docente()
        elif clave:
            st.sidebar.error("Clave incorrecta")

if __name__ == "__main__":
    main()
