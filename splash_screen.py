from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

class SplashScreen(QWidget):
    """
    Splash screen yang ditampilkan saat aplikasi dimulai
    """
    # Custom signal untuk memberitahu MainWindow ketika splash screen selesai
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Set window flags untuk membuat window tanpa border dan selalu di atas
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # Ukuran splash screen
        # self.setFixedSize(500, 300)
        self.showFullScreen()
        
        # Membuat dan mengatur UI
        self._init_ui()
        
        # Timer untuk simulasi loading
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.counter = 0
        
    def _init_ui(self):
        """Inisialisasi komponen UI splash screen"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        self.lbl_title = QLabel("Sistem Absensi Face Recognition")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        
        # Placeholder text - untuk menunjukkan ini adalah Splash Screen
        self.lbl_screen_type = QLabel("SPLASH SCREEN")
        self.lbl_screen_type.setStyleSheet("font-size: 18px; color: #e74c3c;")
        self.lbl_screen_type.setAlignment(Qt.AlignCenter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Label untuk status loading
        self.lbl_loading = QLabel("Loading...")
        self.lbl_loading.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.lbl_loading.setAlignment(Qt.AlignCenter)
        
        # Menambahkan widget ke layout
        main_layout.addStretch()
        main_layout.addWidget(self.lbl_title)
        main_layout.addWidget(self.lbl_screen_type)
        main_layout.addStretch()
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.lbl_loading)
        
        # Set layout
        self.setLayout(main_layout)
        
        # Styling splash screen
        self.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            border: 2px solid #bdc3c7;
        """)
    
    def start_splash(self):
        """Memulai splash screen dan timer"""
        self.show()
        self.timer.start(30)  # Update setiap 30ms
    
    def _update_progress(self):
        """Update progress bar dan teks loading"""
        self.counter += 1
        self.progress_bar.setValue(self.counter)
        
        # Update teks loading berdasarkan progress
        if self.counter <= 33:
            self.lbl_loading.setText("Memuat komponen...")
        elif self.counter <= 66:
            self.lbl_loading.setText("Menginisialisasi data...")
        else:
            self.lbl_loading.setText("Hampir selesai...")
        
        # Jika progress mencapai 100%, hentikan timer dan pindah ke main window
        if self.counter >= 100:
            self.timer.stop()
            self.finished.emit()  # Emit signal bahwa splash screen sudah selesai
            self.close()