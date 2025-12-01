import flet as ft
from pathlib import Path
from src.core import EidolonCore

def main(page: ft.Page):
    # --- 1. Настройка Окна ---
    page.title = "Eidolon Client"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20

    # --- 2. Инициализация Ядра (Грузим дефолтный профиль Friend) ---
    core = EidolonCore(profile_folder="Friend")

    # --- 3. Элементы UI ---
    
    # Текстовые поля сайдбара
    sidebar_name = ft.Text(f"👁️ {core.persona.get('name', 'Unknown')}", size=25, weight="bold")
    sidebar_role = ft.Text(f"{core.persona.get('role', 'System')}", italic=True, color=ft.Colors.GREY_400)
    
    # Чат
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    # --- ЛОГИКА СМЕНЫ ЛИЧНОСТИ ---
    
    # 1. Сканируем папку data/profiles и ищем подпапки
    base_dir = Path(__file__).parent
    profiles_dir = base_dir / "profiles"
    
    # Получаем список названий папок (Friend, Hacker и т.д.)
    # Проверка на существование папки, чтобы не упало при первом старте
    if profiles_dir.exists():
        available_profiles = [p.name for p in profiles_dir.iterdir() if p.is_dir()]
    else:
        available_profiles = ["Friend"] # Фолбэк

    # Функция смены
    def change_persona(e):
        folder_name = e.control.value 
        
        # Загружаем новую личность
        core.load_persona(folder_name)
        
        # Обновляем UI
        sidebar_name.value = f"👁️ {core.persona.get('name')}"
        sidebar_role.value = f"{core.persona.get('role')}"
        
        # Пишем в чат о смене
        chat_list.controls.append(
            ft.Row([ft.Text(f"🔄 Загружен профиль: {folder_name}", color="green")], 
                   alignment=ft.MainAxisAlignment.CENTER)
        )
        page.update()

    # Создаем опции для дропдауна динамически
    dropdown_options = [ft.dropdown.Option(name) for name in available_profiles]

    mode_dropdown = ft.Dropdown(
        label="Выберите профиль",
        width=230,
        options=dropdown_options,
        value="Friend", # Значение по умолчанию
        on_change=change_persona,
        bgcolor=ft.Colors.BLUE_GREY_900,
    )

    # --- Хелперы для чата ---
    def create_message_ui(text, sender="user"):
        if sender == "user":
            return ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=ft.Colors.WHITE),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_800,
                        border_radius=10,
                    ),
                    ft.Icon(name=ft.Icons.PERSON, color=ft.Colors.BLUE_200)
                ],
                alignment=ft.MainAxisAlignment.END
            )
        else:
            # Markdown для бота
            markdown_content = ft.Markdown(
                text, 
                selectable=True, 
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                code_theme="atom-one-dark"
            )
            
            row = ft.Row(
                [
                    ft.Icon(name=ft.Icons.SMART_TOY, color=ft.Colors.PURPLE_200),
                    ft.Container(
                        content=markdown_content,
                        padding=15,
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=10,
                        width=600
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            )
            return row, markdown_content

    # Обработка отправки
    def send_click(e):
        if not new_message.value: return
        
        user_text = new_message.value
        new_message.value = ""
        new_message.focus()
        
        # Юзер
        chat_list.controls.append(create_message_ui(user_text, "user"))
        page.update()

        # Бот (пустой пузырь)
        ai_row, ai_text_control = create_message_ui("", "eidolon")
        chat_list.controls.append(ai_row)
        
        progress_bar.visible = True
        status_text.value = f"🧠 {core.persona.get('name')} думает..."
        page.update()

        # Стриминг ответа
        full_response = ""
        for chunk in core.chat(user_text):
            full_response += chunk
            ai_text_control.value = full_response
            ai_text_control.update()
        
        progress_bar.visible = False
        status_text.value = "Готов"
        page.update()
        
    # Поле ввода
    new_message = ft.TextField(
        hint_text="Команда или вопрос...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_click
    )

    send_button = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_color="blue400",
        icon_size=40,
        on_click=send_click
    )

    # --- 4. Сборка Сайдбара ---
    sidebar = ft.Container(
        width=250,
        padding=20,
        bgcolor=ft.Colors.BLACK26,
        border_radius=10,
        content=ft.Column([
            # Наши переменные элементы
            sidebar_name,
            sidebar_role,
            
            ft.Divider(),
            
            # Переключатель режимов!
            mode_dropdown,
            
            ft.Divider(),
            ft.Text("Состояние:", weight="bold"),
            ft.ProgressBar(value=0.85, color="amber", height=10),
            ft.Text("⚡ Энергия: 85%", size=12),
        ])
    )

    progress_bar = ft.ProgressBar(width=None, color="purple", visible=False)
    status_text = ft.Text("Готов к работе", size=12, color=ft.Colors.GREY_500)

    # --- 5. Макет ---
    layout = ft.Row(
        [sidebar, ft.VerticalDivider(width=1, color="grey"), 
         ft.Column([chat_list, progress_bar, status_text, ft.Row([new_message, send_button])], expand=True)],
        expand=True,
    )

    page.add(layout)

ft.app(target=main)