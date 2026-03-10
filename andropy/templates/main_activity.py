from andropy import ui
from andropy.ui import layout as L

class MainUI(ui.ActivityUI):
    def build(self):
        return ui.UiScrollView(
            ui.UiColumn(
                ui.UiText("Welcome to Andropy!", text_size=24, bold=True, width=L.W1, padding=L.P4),
                ui.UiSpace(height=16),
                ui.UiText("Edit main/main_activity.py to get started.", text_size=14, width=L.W1, padding=L.P2),
            )
        )

class MainLogic(ui.ActivityLogic):
    def on_create(self):
        pass