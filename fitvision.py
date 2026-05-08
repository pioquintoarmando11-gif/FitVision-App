import streamlit as st
import google.generativeai as genai
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred_info = st.secrets["firebase_credentials"]
    cred = credentials.Certificate(dict(cred_info))
    firebase_admin.initialize_app(cred)

db = firestore.client()
# --- 1. CONFIGURACIÓN IA (GEMINI) ---
# REEMPLAZA EL TEXTO DE ABAJO CON TU CLAVE REAL
genai.configure(api_key="AIzaSyC5IhoVE1Bd8QUITjTHTWCnkZHfvBGNygg")
model = genai.GenerativeModel('gemini-1.5-flash')
st.set_page_config(page_title="FitVision AI", page_icon="🏋️‍♂️", layout="wide")

def registrar_usuario(usuario, password, nombre_real):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        user_ref.set({
            "password": password,
            "nombre": nombre_real,
            "puntos": 0
        })
        st.success(f"¡Usuario {usuario} creado con éxito! ✅")
        st.session_state.pantalla = "Login"
    except Exception as e:
        st.error(f"Error al guardar en la nube: {e}")

def validar_usuario(usuario, password):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        doc = user_ref.get()
        if doc.exists:
            datos = doc.to_dict()
            if datos["password"] == password:
                return True
        return False
    except Exception as e:
        st.error(f"Error al conectar con la nube: {e}")
        return False


# --- 3. ESTADO DE SESIÓN ---
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "Inicio"
    st.session_state.user = None

def cambiar_pantalla(nombre):
    st.session_state.pantalla = nombre
    st.rerun()

# --- PANTALLAS DE ACCESO (Inicio, Registro, Login) ---
if st.session_state.pantalla == "Inicio":
    st.title("🏋️‍♂️ FitVision AI")
    st.subheader("Tu asistente personal con Inteligencia Artificial")
    col1, col2 = st.columns(2)
    if col1.button("Iniciar Sesión", use_container_width=True): cambiar_pantalla("Login")
    if col2.button("Crear Cuenta", use_container_width=True): cambiar_pantalla("Registro")

elif st.session_state.pantalla == "Registro":
        st.title("📝 Crear Cuenta")
        nombre = st.text_input("Nombre completo")
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        
        if st.button("Registrarme"):
            if nombre and user and pw:
                registrar_usuario(user, pw, nombre)
            else:
                st.warning("Por favor, llena todos los campos ⚠️")
        
        # Este es el botón de la línea 81, ahora bien alineado
        if st.button("Volver"):
            st.session_state.pantalla = "Login"
            st.rerun()
           
         

elif st.session_state.pantalla == "Login":
    st.title("🔑 Entrar")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        # Verificamos los datos en la nube de Google
        if validar_usuario(user, pw):
            st.success(f"¡Bienvenido de nuevo, {user}! 👋")
            st.session_state.user = user
            st.session_state.logueado = True
            st.session_state.pantalla = "Menu"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")
        
       
        if st.button("Volver"):
            st.session_state.pantalla = "Inicio"
            st.rerun()

# --- 4. MENÚ PRINCIPAL (PANTALLA 3) ---
elif st.session_state.pantalla == "Menu":
    st.sidebar.title(f"Bienvenido, {st.session_state.user} 👋")
    opcion = st.sidebar.radio("Elige una opción:", ["🏠 Inicio", "📊 Analizador de Nutrientes", "💪 Mi Rutina", "💡 Consejos"])
    
   # Bloque 1: Cerrar Sesión
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        cambiar_pantalla("Inicio")

    # Bloque 2: Eliminar Cuenta (FUERA del bloque anterior)
    st.sidebar.markdown("---") 
    if st.sidebar.button("⚠️ Eliminar Cuenta", type="primary"):
        try:
            db.collection("usuarios").document(st.session_state.user).delete()
            st.session_state.user = None
            # Agregamos esta línea para asegurar que se limpie el acceso
            st.session_state.logueado = False 
            cambiar_pantalla("Inicio")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    if opcion == "🏠 Inicio":
        st.header("🎯 Objetivo de hoy")
        st.write("Usa el menú de la izquierda para apoyarte de la mejor manera. SUERTE!.")

    elif opcion == "📊 Analizador de Nutrientes":
        st.header("📊 Analizador de Nutrientes")
        st.write("Selecciona un alimento de la lista para conocer su aporte nutricional por porción estándar.")

        # 1. Catálogo extendido de alimentos
        ALIMENTOS = {
            "Pollo a la plancha (100g)": {"Cal": "165", "Prot": "31g", "Gras": "3.6g", "Nota": "Proteína magra de alta calidad."},
            "Arroz blanco cocido (1 taza)": {"Cal": "205", "Prot": "4.3g", "Gras": "0.4g", "Nota": "Fuente principal de energía."},
            "Huevo hervido (1 pieza)": {"Cal": "78", "Prot": "6g", "Gras": "5g", "Nota": "Proteína completa y grasas buenas."},
            "Carne de res magra (100g)": {"Cal": "250", "Prot": "26g", "Gras": "15g", "Nota": "Rica en hierro y vitamina B12."},
            "Salmón a la plancha (100g)": {"Cal": "208", "Prot": "22g", "Gras": "13g", "Nota": "Alto en Omega-3 para el corazón."},
            "Atún en agua (1 lata)": {"Cal": "120", "Prot": "25g", "Gras": "1g", "Nota": "Práctico y muy alto en proteína."},
            "Avena en hojuelas (1/2 taza)": {"Cal": "150", "Prot": "5g", "Gras": "3g", "Nota": "Excelente fibra para la digestión."},
            "Pan integral (1 rebanada)": {"Cal": "80", "Prot": "4g", "Gras": "1g", "Nota": "Mejor opción que el pan blanco."},
            "Leche descremada (1 taza)": {"Cal": "90", "Prot": "8g", "Gras": "0g", "Nota": "Aporta calcio y vitamina D."},
            "Yogurt Griego natural (150g)": {"Cal": "100", "Prot": "15g", "Gras": "0g", "Nota": "Genial para la flora intestinal."},
            "Frijoles cocidos (1/2 taza)": {"Cal": "110", "Prot": "7g", "Gras": "0.5g", "Nota": "Proteína vegetal y mucha fibra."},
            "Lentejas cocidas (1/2 taza)": {"Cal": "115", "Prot": "9g", "Gras": "0.5g", "Nota": "Hierro y energía estable."},
            "Aguacate (1/2 pieza)": {"Cal": "160", "Prot": "2g", "Gras": "15g", "Nota": "Grasas saludables necesarias."},
            "Almendras (10 piezas)": {"Cal": "70", "Prot": "2.5g", "Gras": "6g", "Nota": "Snack saludable, controla el hambre."},
            "Manzana (1 pieza)": {"Cal": "95", "Prot": "0.5g", "Gras": "0.3g", "Nota": "Fibra que da saciedad."},
            "Plátano (1 pieza)": {"Cal": "105", "Prot": "1.3g", "Gras": "0.4g", "Nota": "Potasio para evitar calambres."},
            "Pechuga de Pavo (3 rebanadas)": {"Cal": "60", "Prot": "12g", "Gras": "1g", "Nota": "Bajo en grasa, ideal para cenas."},
            "Pasta cocida (1 taza)": {"Cal": "220", "Prot": "8g", "Gras": "1.3g", "Nota": "Carbohidrato para entrenos intensos."},
            "Papa cocida (1 mediana)": {"Cal": "110", "Prot": "3g", "Gras": "0.1g", "Nota": "Más saciante que el arroz."},
            "Brócoli al vapor (1 taza)": {"Cal": "31", "Prot": "2.5g", "Gras": "0.4g", "Nota": "Súper alimento lleno de vitaminas."},
            "Espinacas crudas (2 tazas)": {"Cal": "14", "Prot": "2g", "Gras": "0.2g", "Nota": "Casi cero calorías, mucho volumen."},
            "Queso Panela (40g)": {"Cal": "100", "Prot": "7g", "Gras": "8g", "Nota": "Opción de queso baja en grasa."},
            "Tortilla de maíz (1 pieza)": {"Cal": "50", "Prot": "1.4g", "Gras": "0.5g", "Nota": "Buena fuente de calcio."},
            "Crema de cacahuate (1 cda)": {"Cal": "95", "Prot": "4g", "Gras": "8g", "Nota": "Energética, cuidado con la porción."},
            "Tofu (100g)": {"Cal": "76", "Prot": "8g", "Gras": "4.8g", "Nota": "Proteína vegetal completa."},
            "Quinoa cocida (1/2 taza)": {"Cal": "110", "Prot": "4g", "Gras": "2g", "Nota": "Supercereal con aminoácidos."},
            "Zanahoria cruda (1 pieza)": {"Cal": "41", "Prot": "0.9g", "Gras": "0.2g", "Nota": "Vitamina A para la vista."},
            "Naranja (1 pieza)": {"Cal": "62", "Prot": "1.2g", "Gras": "0.2g", "Nota": "Vitamina C pura."},
            "Cacahuates naturales (1 puñado)": {"Cal": "160", "Prot": "7g", "Gras": "14g", "Nota": "Proteína y grasa saludable."},
            "Bubu-Lubu Mini (1 pieza)": {"Cal": "92", "Prot": "0.6g", "Gras": "3g", "Nota": "Snack dulce ocasional."},
            "Café negro (1 taza)": {"Cal": "2", "Prot": "0g", "Gras": "0g", "Nota": "Acelera el metabolismo sin calorías."},
            "Galletas de arroz (2 piezas)": {"Cal": "70", "Prot": "1.5g", "Gras": "0.5g", "Nota": "Snack ligero para antes de entrenar."}
        }

        # 2. Selector con búsqueda automática
        alimento_elegido = st.selectbox("Busca tu alimento:", sorted(list(ALIMENTOS.keys())))

        # 3. Botón de analizar con efecto de carga
        if st.button("🔍 Analizar alimento"):
            with st.spinner("Buscando información nutricional..."):
                import time
                time.sleep(0.6) # Simula el proceso de análisis
                
                info = ALIMENTOS[alimento_elegido]
                st.write("---")
                st.subheader(f"📋 Ficha de: {alimento_elegido}")
                
                # Mostrar métricas en columnas
                c1, c2, c3 = st.columns(3)
                c1.metric("🔥 Calorías", f"{info['Cal']} kcal")
                c2.metric("💪 Proteína", info['Prot'])
                c3.metric("🥑 Grasa", info['Gras'])
                
                st.success(f"💡 **Tip del Coach:** {info['Nota']}"
    
    elif opcion == "💪 Mi Rutina":
        st.header("📋 Tu Entrenamiento Personalizado")

        # El diccionario debe tener esta sangría (8 espacios desde el borde)
        RUTINAS_AUTO = {
            "Pecho": ["Lagartijas - 4x12", "Press con mancuernas - 4x10", "Aperturas - 3x15"],
            "Pierna": ["Sentadillas - 4x12", "Desplantes - 3x15", "Peso muerto - 4x10"],
            "Espalda": ["Dominadas - 4x10", "Remo con mancuerna - 4x12", "Jalón al pecho - 3x10"],
            "Cuerpo Completo": ["Burpees - 3x10", "Sentadillas - 3x15", "Plancha - 3x45s"]
        }

        # Estas líneas TAMBIÉN deben estar hacia la derecha
        opcion_entrenamiento = st.selectbox("¿Qué quieres entrenar hoy?", ["Cuerpo Completo", "Pecho", "Pierna", "Espalda"])

        if st.button("Generar mi rutina de hoy"):
            rutina_lista = RUTINAS_AUTO.get(opcion_entrenamiento, [])
            if rutina_lista:
                st.markdown(f"### 🔥 Rutina para {opcion_entrenamiento}")
                for ejercicio in rutina_lista:
                    st.write(f"✅ {ejercicio}")
       
                
                
    elif opcion == "💡 Consejos":
        st.header("🌟 Consejos del Coach FitVision")

        # 1. Catálogo de consejos predeterminados
        CONSEJOS_FIT = {
            "Pierde Grasa": [
                "Mantén un déficit calórico ligero (come un poco menos de lo que quemas).",
                "Prioriza el consumo de proteínas para proteger tu músculo.",
                "Aumenta tu actividad diaria: intenta caminar 10,000 pasos al día.",
                "Duerme entre 7 y 8 horas; el descanso es clave para regular el hambre."
            ],
            "Gana Músculo": [
                "Entrena con pesas o resistencia al menos 3 a 4 veces por semana.",
                "Consume suficiente proteína (aprox. 1.8g por cada kilo de tu peso).",
                "No ignores los carbohidratos; son la energía para tus entrenamientos.",
                "Aumenta el peso gradualmente en tus ejercicios (sobrecarga progresiva)."
            ],
            "Mantener Forma": [
                "Busca un equilibrio: combina ejercicios de fuerza con algo de cardio.",
                "Mantente hidratado: bebe al menos 2 a 3 litros de agua diarios.",
                "Sé constante: es mejor entrenar 30 minutos diario que 3 horas un solo día.",
                "Escucha a tu cuerpo: si te sientes muy agotado, tómate un día de descanso."
            ]
        }

        # 2. Selector de objetivo (con sangría para que no se salga de la sección)
        objetivo_seleccionado = st.selectbox("¿En qué área necesitas ayuda hoy?", list(CONSEJOS_FIT.keys()))

        # 3. Botón para mostrar los consejos
        if st.button("Obtener consejos ahora"):
            consejos = CONSEJOS_FIT.get(objetivo_seleccionado, [])
            
            if consejos:
                st.markdown(f"### ✨ Tips para {objetivo_seleccionado}:")
                for item in consejos:
                    st.write(f"✅ {item}")
            else:
                st.error("No se encontraron consejos para esta categoría.")

elif opcion == "📸 Mi Progreso":
        st.header("⚖️ Mi Perfil Físico")
        
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso actual (kg):", min_value=10.0, max_value=200.0, value=70.0)
            altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
        with col2:
            edad = st.number_input("Edad:", min_value=5, max_value=100, value=17)
            genero = st.selectbox("Género:", ["Hombre", "Mujer"])

        if st.button("Calcular mi estado físico"):
            # Fórmula del IMC
            altura_m = altura / 100
            imc = peso / (altura_m ** 2)
            
            st.metric("Tu IMC es:", f"{imc:.2f}")
            
            if imc < 18.5: st.warning("Bajo peso")
            elif 18.5 <= imc < 25: st.success("Peso normal (Saludable)")
            else: st.error("Sobrepeso")
            
            # Fórmula de Calorías Base (Harris-Benedict)
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
            st.write(f"🔥 Tu cuerpo quema **{tmb:.0f} calorías** al día solo por existir.")
