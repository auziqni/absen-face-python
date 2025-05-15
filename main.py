import sys
from PyQt5.QtWidgets import QApplication, QMainWindow ,QShortcut, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


# Import screen modules
from splash_screen import SplashScreen
from dashboard_screen import DashboardScreen
from absensi_screen import AbsensiScreen

class MainWindow(QMainWindow):
    """
    Main window sebagai container utama untuk semua screen
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Absensi Face Recognition")
        
        # Set window ke fullscreen
        self.setWindowState(Qt.WindowFullScreen)
        
        # Inisialisasi stacked widget untuk pengelolaan screen
        self.stacked_widget = QStackedWidget()
        
        # Inisialisasi semua screen
        self.dashboard_screen = DashboardScreen()
        self.absensi_screen = AbsensiScreen()
        
        # Tambahkan screens ke stacked widget
        self.stacked_widget.addWidget(self.dashboard_screen)  # index 0
        self.stacked_widget.addWidget(self.absensi_screen)    # index 1
        
        # Set stacked widget sebagai central widget
        self.setCentralWidget(self.stacked_widget)
        
        # Setup navigasi antar screen
        self._setup_navigation()
        
        # Buat dan mulai splash screen
        self.splash = SplashScreen()
        self.splash.finished.connect(self.show_main_window)
        
        # Tambahkan shortcut Alt+Q untuk keluar aplikasi
        self.quit_shortcut = QShortcut(QKeySequence("Alt+Q"), self)
        self.quit_shortcut.activated.connect(self.close)
        
    def _setup_navigation(self):
        """Setup navigasi antar screen"""
        # Dashboard -> Absensi
        self.dashboard_screen.navigate_to_absensi.connect(
            self._navigate_to_absensi
        )
        
        # Absensi -> Dashboard
        self.absensi_screen.navigate_to_dashboard.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )
    
        # Tambahkan metode baru ini
    def _navigate_to_absensi(self, kelas_info):
        """
        Navigasi ke layar absensi dengan informasi kelas
        
        Args:
            kelas_info (dict): Informasi kelas yang dipilih
        """
        # Kirim informasi kelas ke layar absensi
        self.absensi_screen.set_kelas_info(kelas_info)
        
        # Pindah ke layar absensi
        self.stacked_widget.setCurrentIndex(1)
        
    def show_main_window(self):
        """Tampilkan main window setelah splash screen selesai"""
        self.show()
        self.stacked_widget.setCurrentIndex(0)  # Mulai dari dashboard

def main():
    """
    Fungsi utama untuk menjalankan aplikasi
    """
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Buat main window
    main_window = MainWindow()
    
    # Mulai splash screen
    main_window.splash.start_splash()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()