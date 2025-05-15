from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class AbsensiScreen(QWidget):
    """
    Screen absensi dengan pengenalan wajah
    """
    # Signal untuk navigasi
    navigate_to_dashboard = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # Tambahkan atribut untuk menyimpan data kelas
        self.kelas_info = None
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """Inisialisasi komponen UI absensi screen"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        self.lbl_title = QLabel("Absensi Face Recognition")
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        
        # Placeholder text - untuk menunjukkan ini adalah Absensi Screen
        self.lbl_screen_type = QLabel("ABSENSI SCREEN")
        self.lbl_screen_type.setStyleSheet("font-size: 18px; color: #e74c3c;")
        self.lbl_screen_type.setAlignment(Qt.AlignCenter)
        
        # Content frame
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f6fa;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        
        self.lbl_info = QLabel("Di sini akan ditampilkan kamera dan proses pengenalan wajah")
        self.lbl_info.setStyleSheet("font-size: 16px;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        
        content_layout.addWidget(self.lbl_info)
        content_layout.addWidget(self.lbl_screen_type)
        content_layout.addStretch()
        
        # Button untuk kembali
        self.btn_back = QPushButton("Kembali ke Dashboard")
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_back.setMinimumHeight(40)
        
        # Menambahkan widget ke layout
        main_layout.addWidget(self.lbl_title)
        main_layout.addWidget(content_frame, 1)  # Stretch factor 1
        main_layout.addWidget(self.btn_back)
        
        # Set layout
        self.setLayout(main_layout)
    
    def _setup_connections(self):
        """Setup event handlers"""
        self.btn_back.clicked.connect(self._navigate_to_dashboard)
    
    def _navigate_to_dashboard(self):
        """Handler untuk navigasi kembali ke dashboard"""
        self.navigate_to_dashboard.emit()
        
     # Tambahkan metode baru ini
    def set_kelas_info(self, kelas_info):
        """
        Mengatur informasi kelas yang dipilih
        
        Args:
            kelas_info (dict): Informasi kelas yang dipilih
        """
        self.kelas_info = kelas_info
        # Update UI dengan informasi kelas
        self._update_ui_with_kelas_info()
        
    # Tambahkan metode baru ini
    def _update_ui_with_kelas_info(self):
        """Update UI dengan informasi kelas yang dipilih"""
        if not self.kelas_info:
            return
            
        # Update judul dengan informasi kelas
        self.lbl_title.setText(f"Absensi Face Recognition - {self.kelas_info['nama_kelas']}")
        
        # Update informasi kelas di label info
        info_text = (f"Kode Kelas: {self.kelas_info['kode_kelas']}\n"
                    f"Pertemuan: {self.kelas_info['nomor_pertemuan']}\n"
                    f"Dosen: {self.kelas_info['dosen']['nama']} (ID: {self.kelas_info['dosen']['id']})")
        self.lbl_info.setText(info_text)
        
        # Tampilkan jenis screen
        self.lbl_screen_type.setText("ABSENSI SEDANG BERJALAN")