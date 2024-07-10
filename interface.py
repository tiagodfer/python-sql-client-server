import sys
from PyQt5.QtWidgets import QApplication, QWidget

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Minha Primeira Interface PyQt')
    window.setGeometry(100, 100, 280, 80)  # Posição (x, y) e tamanho (largura, altura)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
