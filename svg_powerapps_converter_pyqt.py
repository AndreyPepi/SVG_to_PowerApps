
import sys
import re
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QButtonGroup,
    QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SVGConverter(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SVG → Power Apps Converter")
        self.resize(1100, 760)

        self.setup_ui()

    def setup_ui(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #111827;
                color: #F9FAFB;
                font-family: 'Segoe UI';
                font-size: 13px;
            }

            QTextEdit, QLineEdit {
                background-color: #1F2937;
                border: 1px solid #374151;
                border-radius: 10px;
                padding: 10px;
                color: white;
                selection-background-color: #2563EB;
            }

            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 10px;
                padding: 12px;
                color: white;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QLabel {
                color: #E5E7EB;
            }

            QRadioButton {
                spacing: 8px;
            }

            QFrame {
                background-color: #1F2937;
                border-radius: 14px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # TITLE
        title = QLabel("SVG → Power Apps Converter")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))

        subtitle = QLabel(
            "Cole qualquer SVG do Tabler Icons e converta automaticamente "
            "para um código compatível com a propriedade Image do Power Apps."
        )
        subtitle.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # INPUT CARD
        input_card = QFrame()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(18, 18, 18, 18)

        input_label = QLabel("SVG Original")
        input_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.svg_input = QTextEdit()
        self.svg_input.setPlaceholderText(
            "Cole aqui o SVG original do Tabler Icons..."
        )

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.svg_input)

        main_layout.addWidget(input_card)

        # COLOR CARD
        color_card = QFrame()
        color_layout = QVBoxLayout(color_card)
        color_layout.setContentsMargins(18, 18, 18, 18)

        color_title = QLabel("Configuração de Cor")
        color_title.setFont(QFont("Segoe UI", 11, QFont.Bold))

        color_layout.addWidget(color_title)

        radio_layout = QHBoxLayout()

        self.hex_radio = QRadioButton("HEX")
        self.hex_radio.setChecked(True)

        self.rgb_radio = QRadioButton("RGB")

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.hex_radio)
        self.radio_group.addButton(self.rgb_radio)

        radio_layout.addWidget(self.hex_radio)
        radio_layout.addWidget(self.rgb_radio)
        radio_layout.addStretch()

        color_layout.addLayout(radio_layout)

        # HEX
        hex_layout = QHBoxLayout()

        hex_label = QLabel("HEX:")
        self.hex_input = QLineEdit("#FFFFFF")

        hex_layout.addWidget(hex_label)
        hex_layout.addWidget(self.hex_input)

        color_layout.addLayout(hex_layout)

        # RGB
        rgb_layout = QHBoxLayout()

        self.r_input = QLineEdit("255")
        self.g_input = QLineEdit("255")
        self.b_input = QLineEdit("255")

        self.r_input.setMaximumWidth(80)
        self.g_input.setMaximumWidth(80)
        self.b_input.setMaximumWidth(80)

        rgb_layout.addWidget(QLabel("R"))
        rgb_layout.addWidget(self.r_input)

        rgb_layout.addWidget(QLabel("G"))
        rgb_layout.addWidget(self.g_input)

        rgb_layout.addWidget(QLabel("B"))
        rgb_layout.addWidget(self.b_input)

        rgb_layout.addStretch()

        color_layout.addLayout(rgb_layout)

        main_layout.addWidget(color_card)

        # BUTTONS
        button_layout = QHBoxLayout()

        convert_button = QPushButton("Converter SVG")
        convert_button.clicked.connect(self.convert_svg)

        copy_button = QPushButton("Copiar Resultado")
        copy_button.clicked.connect(self.copy_result)

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_fields)

        button_layout.addWidget(convert_button)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

        # OUTPUT
        output_card = QFrame()
        output_layout = QVBoxLayout(output_card)
        output_layout.setContentsMargins(18, 18, 18, 18)

        output_title = QLabel("Código Power Apps")
        output_title.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)

        output_layout.addWidget(output_title)
        output_layout.addWidget(self.output_text)

        main_layout.addWidget(output_card)

        self.setLayout(main_layout)

    def get_color(self):

        if self.hex_radio.isChecked():

            color = self.hex_input.text().strip()

            if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
                QMessageBox.warning(
                    self,
                    "Cor inválida",
                    "Informe um HEX válido.\nExemplo: #FFFFFF"
                )
                return None

            return color

        try:
            r = int(self.r_input.text())
            g = int(self.g_input.text())
            b = int(self.b_input.text())

            if not all(0 <= value <= 255 for value in [r, g, b]):
                raise ValueError

            return f"rgb({r},{g},{b})"

        except ValueError:
            QMessageBox.warning(
                self,
                "RGB inválido",
                "Os valores RGB devem estar entre 0 e 255."
            )
            return None

    def transform_svg(self, svg, color):

        # PASSO 1 → remover class
        svg = re.sub(r"class='[^']*'", "", svg)
        svg = re.sub(r'class="[^"]*"', "", svg)

        # PASSO 2 → trocar currentColor
        svg = svg.replace('stroke="currentColor"', f"stroke='{color}'")
        svg = svg.replace("stroke='currentColor'", f"stroke='{color}'")

        # PASSO 3 → trocar aspas duplas por simples
        svg = svg.replace('"', "'")

        # PASSO 4 → limpar espaços extras
        svg = re.sub(r"\s+\>", ">", svg)

        return svg

    def convert_svg(self):

        svg = self.svg_input.toPlainText().strip()

        if not svg:
            QMessageBox.warning(
                self,
                "SVG vazio",
                "Cole um SVG antes de converter."
            )
            return

        color = self.get_color()

        if not color:
            return

        final_svg = self.transform_svg(svg, color)

        result = (
            '"data:image/svg+xml;utf8," &\n'
            'EncodeUrl(\n'
            '"\n'
            f'{final_svg}\n'
            '"\n'
            ')'
        )

        self.output_text.setPlainText(result)

    def copy_result(self):

        result = self.output_text.toPlainText()

        if not result:
            QMessageBox.warning(
                self,
                "Sem conteúdo",
                "Converta um SVG primeiro."
            )
            return

        QApplication.clipboard().setText(result)

        QMessageBox.information(
            self,
            "Copiado",
            "Código copiado para a área de transferência."
        )

    def clear_fields(self):

        self.svg_input.clear()
        self.output_text.clear()
        self.hex_input.setText("#FFFFFF")

        self.r_input.setText("255")
        self.g_input.setText("255")
        self.b_input.setText("255")


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SVGConverter()
    window.show()

    sys.exit(app.exec_())
