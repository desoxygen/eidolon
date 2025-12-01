import flet as ft
from src.core import EidolonCore

def main(page: ft.Page):
    # --- 1. Настройка Окна ---
    page.title = "Eidolon Client"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20

    # --- 2. Инициализация Ядра ---
    core = EidolonCore()

    # --- 3. Элементы UI (Определяем заранее, чтобы менять их свойства) ---
    
    # Текстовые поля сайдбара (мы будем их обновлять при смене режима)
    sidebar_name = ft.Text(f"👁️ {core.persona['name']}", size=25, weight="bold")
    sidebar_role = ft.Text(f"{core.persona['role']}", italic=True, color=ft.Colors.GREY_400)
    
    # Чат
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    # --- Функция смены личности ---
    def change_persona(e):
        selected_file = e.control.value # получаем "hacker.json" или "core_persona.json"
        
        # 1. Загружаем новую личность в ядро
        core.load_persona(selected_file)
        
        # 2. Обновляем интерфейс
        sidebar_name.value = f"👁️ {core.persona['name']}"
        sidebar_role.value = f"{core.persona['role']}"
        
        # 3. Пишем системное сообщение в чат
        chat_list.controls.append(
            ft.Row([
                ft.Text(f"🔄 Система переключена в режим: {core.persona['name']}", 
                       color=ft.Colors.GREEN_400, size=12)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        
        page.update()

    # Выпадающий список режимов
    mode_dropdown = ft.Dropdown(
        label="Выберите режим",
        width=230,
        options=[
            ft.dropdown.Option("core_persona.json", "🟢 Друг (Base)"),
            ft.dropdown.Option("hacker.json", "🔴 Хакер (Root)"),
        ],
        value="core_persona.json", # Значение по умолчанию
        on_change=change_persona,   # Какую функцию вызвать при смене
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
        status_text.value = f"🧠 {core.persona['name']} думает..."
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