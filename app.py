import streamlit as st
import time
from src.core import EidolonCore

# --- 1. Настройка страницы ---
st.set_page_config(
    page_title="Eidolon",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Инициализация Ядра (Кэшируем, чтобы не перезагружать при каждом клике) ---
@st.cache_resource
def get_core():
    return EidolonCore()

try:
    core = get_core()
except Exception as e:
    st.error(f"Ошибка запуска ядра: {e}")
    st.stop()

# --- 3. Боковая панель (Панель состояния "Тамагочи") ---
with st.sidebar:
    st.title(f"👁️ {core.persona['name']}")
    st.caption(f"Role: {core.persona['role']}")
    
    st.divider()
    
    # Имитация динамических метрик (потом подключим к базе)
    st.write("### Состояние системы")
    energy_bar = st.progress(85, text="⚡ Энергия ядра")
    mood_bar = st.progress(90, text="❤️ Отношение (Affection)")
    
    st.divider()
    
    st.write("### Активные цели")
    st.info("🎯 Закончить MVP")
    st.info("📚 Изучить Pandas")

    st.divider()
    if st.button("🧹 Очистить историю чата"):
        st.session_state.messages = []
        st.rerun()

# --- 4. Основной интерфейс Чата ---
st.subheader("Терминал связи")

# Инициализация истории в сессии браузера
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отрисовка предыдущих сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. Логика обработки ввода ---
if prompt := st.chat_input("Отправить сообщение..."):
    
    # 1. Показываем сообщение пользователя сразу
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Генерируем ответ (с эффектом печатания)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Обработка контекста..."):
            # Вызов твоего ядра!
            response_text = core.chat(prompt)
        
        # Эффект печатания текста (для живости)
        for chunk in response_text.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # 3. Сохраняем ответ в историю сессии
    st.session_state.messages.append({"role": "assistant", "content": full_response})