from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QMessageBox, QFrame, QComboBox, QFormLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont, QIcon
import os

# Import db_manager untuk fungsi login
from db_manager import DatabaseManager

class DashboardScreen(QWidget):
    """
    Dashboard screen yang berisi navigasi ke layar absensi dengan tampilan navbar dan background
    """
    # Signal untuk navigasi
    navigate_to_absensi = pyqtSignal(dict)
    
    # Tambahkan atribut untuk menyimpan info dosen yang login
    current_user = None
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """Inisialisasi komponen UI dashboard screen"""
        # Mengatur window title (meskipun tidak terlihat dalam QWidget)
        self.setWindowTitle("Sistem Absensi Face Recognition")
        
        # Set warna background default jika gambar tidak ada
        self.setStyleSheet("background-color: #f5f6fa;")
        
        # Coba set background image jika ada
        bg_path = "assets/background.png"
        if os.path.exists(bg_path):
            self._set_background_image(bg_path)
        else:
            print(f"Warning: Background image not found at {bg_path}")
        
        # Membuat navbar
        self._create_navbar()
        
        
        # Set layout utama
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 140, 20, 20)  # Margin atas diperbesar untuk navbar
        main_layout.setSpacing(15)
        
        # Set layout
        self.setLayout(main_layout)
    
    def _set_background_image(self, image_path):
        """
        Mengatur gambar latar belakang yang menyesuaikan ukuran layar tanpa stretch.
        
        Args:
            image_path (str): Path ke file gambar latar belakang.
        """
        try:
            # Mengambil ukuran layar
            screen_size = self.size()
            
            # Memuat gambar
            pixmap = QPixmap(image_path)
            
            # Mengubah ukuran gambar agar sesuai dengan layar tanpa stretch (mempertahankan aspect ratio)
            scaled_pixmap = pixmap.scaled(screen_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Membuat palette untuk background
            palette = QPalette()
            
            # Mengatur gambar sebagai background
            brush = QBrush(scaled_pixmap)
            palette.setBrush(QPalette.Background, brush)
            
            # Menerapkan palette ke window
            self.setAutoFillBackground(True)
            self.setPalette(palette)
        except Exception as e:
            print(f"Error saat memuat gambar latar belakang: {e}")
    
    def _create_navbar(self):
        """
        Membuat navbar menu dengan logo dan grup tombol secara individual.
        """
        # Membuat widget untuk navbar dengan parent self
        self.navbar = QWidget(self)
        
        # Pastikan navbar selalu di atas gambar latar belakang
        self.navbar.raise_()
        
        # Mengatur ukuran dan posisi navbar (lebar penuh, tinggi 120px, di paling atas)
        self.navbar.setGeometry(0, 0, self.width(), 120)
        
        # Mengatur warna latar belakang navbar menjadi biru muda
        self.navbar.setStyleSheet("background-color: #87CEFA;")
        
        # Membuat layout horizontal untuk navbar
        navbar_layout = QHBoxLayout(self.navbar)
        
        # Mengatur margin layout (kiri, atas, kanan, bawah)
        navbar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Membuat label untuk logo "FACE"
        logo_label = QLabel("FACE")
        logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        logo_label.setStyleSheet("color: #333333;")
        
        # Menambahkan logo ke navbar layout
        navbar_layout.addWidget(logo_label)
        
        # Label untuk user (tersembunyi di awal)
        self.user_label = QLabel("")
        self.user_label.setFont(QFont("Arial", 12))
        self.user_label.setStyleSheet("color: #333333; margin-left: 20px;")
        self.user_label.hide()  # Sembunyikan di awal
        navbar_layout.addWidget(self.user_label)
        
        # Menambahkan spacer untuk mendorong tombol ke kanan
        navbar_layout.addStretch()
        
        # Definisi style dasar untuk tombol
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """
        
        # Tombol 1: Kelas
        self.btn_kelas = QPushButton("Sync")
        self.btn_kelas.setFixedSize(120, 40)
        self.btn_kelas.setFont(QFont("Arial", 10))
        self.btn_kelas.setStyleSheet(button_style)
        self.btn_kelas.setCursor(Qt.PointingHandCursor)
        self.btn_kelas.clicked.connect(self._on_sync_clicked)
        navbar_layout.addWidget(self.btn_kelas)
        
        # Spasi antara tombol
        navbar_layout.addSpacing(10)
        
        # Tombol 2: Dosen
        self.btn_dosen = QPushButton("Train")
        self.btn_dosen.setFixedSize(120, 40)
        self.btn_dosen.setFont(QFont("Arial", 10))
        self.btn_dosen.setStyleSheet(button_style)
        self.btn_dosen.setCursor(Qt.PointingHandCursor)
        self.btn_dosen.clicked.connect(self._on_train_clicked)
        navbar_layout.addWidget(self.btn_dosen)
        
        # Spasi antara tombol
        navbar_layout.addSpacing(10)
        
        # Tombol 3: Mulai kelas (disabled at start)
        self.btn_mulai_kelas = QPushButton("Mulai kelas")
        self.btn_mulai_kelas.setFixedSize(120, 40)
        self.btn_mulai_kelas.setFont(QFont("Arial", 10))
        self.btn_mulai_kelas.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.btn_mulai_kelas.setEnabled(False)  # Disable the button initially
        self.btn_mulai_kelas.clicked.connect(self._on_mulai_kelas_clicked)
        navbar_layout.addWidget(self.btn_mulai_kelas)
        
        # Spasi antara tombol
        navbar_layout.addSpacing(10)
        
        # Tombol 4: Masuk - hijau
        self.btn_auth = QPushButton("Masuk")
        self.btn_auth.setFixedSize(120, 40)
        self.btn_auth.setFont(QFont("Arial", 10))
        self.btn_auth.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_auth.setCursor(Qt.PointingHandCursor)
        self.btn_auth.clicked.connect(self._on_auth_clicked)
        navbar_layout.addWidget(self.btn_auth)
        
        # Pastikan navbar terlihat
        self.navbar.show()
    
    def resizeEvent(self, event):
        """
        Menangani event saat ukuran window berubah.
        
        Args:
            event: Event resize.
        """
        # Pastikan navbar selalu memiliki lebar penuh saat window di-resize
        if hasattr(self, 'navbar'):
            self.navbar.setGeometry(0, 0, self.width(), 120)
        
        # Update posisi dan ukuran frame konten
        if hasattr(self, 'content_frame'):
            self.content_frame.setGeometry(
                int(self.width() * 0.1),    # X position (10% dari lebar)
                int(self.height() * 0.25),  # Y position (25% dari tinggi)
                int(self.width() * 0.8),    # Width (80% dari lebar)
                int(self.height() * 0.5)    # Height (50% dari tinggi)
            )
        
        # Perbarui background image jika ada
        bg_path = "assets/background.png"
        if os.path.exists(bg_path):
            self._set_background_image(bg_path)
        
        # Panggil method parent class
        super().resizeEvent(event)
    
    def _setup_connections(self):
        """Setup event handlers"""
        # Koneksi sudah diatur di _create_navbar
        pass
    
    def _update_navbar_with_user(self, user_data):
        """
        Update navbar dengan nama dosen yang berhasil login
        
        Args:
            user_data (dict): Data dosen yang berhasil login
        """
        if hasattr(self, 'user_label'):
            self.user_label.setText(f"Dosen: {user_data['nama']}")
            self.user_label.show()
        
        # Enable tombol mulai kelas
        self.btn_mulai_kelas.setEnabled(True)
        self.btn_mulai_kelas.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.btn_mulai_kelas.setCursor(Qt.PointingHandCursor)
        
        # Ubah tombol masuk menjadi keluar (merah)
        self.btn_auth.setText("Keluar")
        self.btn_auth.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
    
    def _reset_navbar_after_logout(self):
        """
        Reset navbar setelah logout
        """
        # Sembunyikan label user
        self.user_label.hide()
        
        # Disable tombol mulai kelas
        self.btn_mulai_kelas.setEnabled(False)
        self.btn_mulai_kelas.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.btn_mulai_kelas.setCursor(Qt.ArrowCursor)
        
        # Ubah tombol keluar menjadi masuk (hijau)
        self.btn_auth.setText("Masuk")
        self.btn_auth.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
    
    def _navigate_to_absensi(self, kelas_info):
        """
        Handler untuk navigasi ke screen absensi
        
        Args:
            kelas_info (dict): Informasi kelas yang dipilih
        """
        # Hanya navigasi jika sudah login dan ada informasi kelas
        if self.current_user and kelas_info:
            # Kirim data kelas ke absensi screen
            self.navigate_to_absensi.emit(kelas_info)
        else:
            QMessageBox.warning(self, "Peringatan", "Data kelas tidak lengkap!")
    
    def _on_sync_clicked(self):
        """
        Menangani event saat tombol Sync diklik.
        """
        print("Tombol 'Sync' diklik")
        
        # Tampilkan dialog konfirmasi
        confirmation = QMessageBox.question(
            self,
            "Konfirmasi Sinkronisasi",
            "Apakah Anda yakin ingin melakukan sinkronisasi data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirmation == QMessageBox.Yes:
            # Inisialisasi database manager
            db_manager = DatabaseManager()
            db_manager.connect()
            
            # Jalankan sinkronisasi
            status, result = db_manager.sync_db_to_server()
            
            # Tutup koneksi database
            db_manager.close()
            
            # Tampilkan hasil sinkronisasi
            if status:
                # Format pesan berhasil
                success_count = result.get('synced', 0)
                failed_count = result.get('failed', 0)
                total_count = result.get('total', 0)
                
                message = f"Sinkronisasi selesai.\n\n"
                message += f"Berhasil: {success_count}\n"
                message += f"Gagal: {failed_count}\n"
                message += f"Total: {total_count}"
                
                # Jika ada kegagalan, tambahkan detail
                if failed_count > 0 and result.get('failed_details'):
                    message += "\n\nDetail kegagalan:"
                    for i, detail in enumerate(result['failed_details']):
                        message += f"\n{i+1}. ID Absensi: {detail.get('id', 'N/A')}"
                        if 'status_code' in detail:
                            message += f"\n   Status: {detail.get('status_code', 'N/A')}"
                            message += f"\n   Pesan: {detail.get('message', 'N/A')}"
                        else:
                            message += f"\n   Error: {detail.get('error', 'N/A')}"
                
                # Tampilkan pesan berhasil
                QMessageBox.information(
                    self,
                    "Sinkronisasi Berhasil",
                    message,
                    QMessageBox.Ok
                )
            else:
                # Tampilkan pesan error
                QMessageBox.critical(
                    self,
                    "Sinkronisasi Gagal",
                    f"Error: {result.get('message', 'Terjadi kesalahan yang tidak diketahui.')}",
                    QMessageBox.Ok
                )
    
    def _on_train_clicked(self):
        """
        Menangani event saat tombol Dosen diklik.
        """
        print("Tombol 'train' diklik")
        # Tambahkan logika untuk tombol Dosen di sini
    
    def _on_mulai_kelas_clicked(self):
        """
        Menangani event saat tombol Mulai kelas diklik.
        """
        print("Tombol 'Mulai kelas' diklik")
        # Buka dialog pilih kelas jika tombol enabled dan sudah login
        if self.btn_mulai_kelas.isEnabled() and self.current_user:
            select_class_dialog = SelectClassDialog(self.current_user, self)
            if select_class_dialog.exec_() == QDialog.Accepted:
                # Jika dialog ditutup dengan status Accepted, ambil data kelas yang dipilih
                kelas_info = select_class_dialog.get_selected_class_info()
                print(f"Kelas dipilih: {kelas_info}")
                
                # Navigasi ke layar absensi dengan data kelas
                self._navigate_to_absensi(kelas_info)
    
    def _on_auth_clicked(self):
        """
        Menangani event saat tombol Masuk/Keluar diklik.
        """
        if self.current_user:  # Sudah login, lakukan logout
            print("Tombol 'Keluar' diklik, melakukan logout")
            self.current_user = None
            self._reset_navbar_after_logout()
            QMessageBox.information(
                self,
                "Logout Berhasil",
                "Anda telah keluar dari sistem.",
                QMessageBox.Ok
            )
        else:  # Belum login, tampilkan dialog login
            print("Tombol 'Masuk' diklik")
            login_dialog = LoginDialog(self)
            login_dialog.login_success.connect(self._handle_login_success)
            login_dialog.exec_()
    
    def _handle_login_success(self, user_data):
        """
        Menangani proses setelah login berhasil
        
        Args:
            user_data (dict): Data dosen yang berhasil login
        """
        # Simpan data user saat ini
        self.current_user = user_data
        
        # Update navbar dengan nama dosen
        self._update_navbar_with_user(user_data)
        
        # Tampilkan pesan sukses
        QMessageBox.information(
            self,
            "Login Berhasil",
            f"Selamat datang, {user_data['nama']}!",
            QMessageBox.Ok
        )


class LoginDialog(QDialog):
    """
    Dialog popup untuk login dosen
    """
    # Signal ketika login berhasil
    login_success = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login Dosen")
        self.setFixedSize(1000, 700)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()
        self._setup_connections()
        
    def _init_ui(self):
        """Inisialisasi komponen UI login dialog"""
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Area kiri (gambar)
        left_widget = QWidget()
        left_widget.setFixedWidth(400)
        left_widget.setStyleSheet("background-color: #3498db;")
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo dan judul di area kiri
        logo_label = QLabel("FACE")
        logo_label.setFont(QFont("Arial", 36, QFont.Bold))
        logo_label.setStyleSheet("color: white;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Sistem Absensi Wajah")
        subtitle_label.setFont(QFont("Arial", 16))
        subtitle_label.setStyleSheet("color: white; margin-top: 10px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(logo_label)
        left_layout.addWidget(subtitle_label)
        
        # Area kanan (form login)
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            background-color: white;
            border-left: 1px solid #e0e0e0;
        """)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Header login
        login_header = QLabel("Login Dosen")
        login_header.setFont(QFont("Arial", 24, QFont.Bold))
        login_header.setStyleSheet("color: #333333; margin-bottom: 20px;")
        login_header.setAlignment(Qt.AlignCenter)
        
        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # Input ID Dosen
        id_label = QLabel("ID Dosen:")
        id_label.setFont(QFont("Arial", 12))
        id_label.setStyleSheet("color: #555555;")
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Masukkan ID Dosen")
        self.id_input.setFont(QFont("Arial", 12))
        self.id_input.setMinimumHeight(40)
        self.id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """)
        
        # Input Password
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 12))
        password_label.setStyleSheet("color: #555555;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """)
        
        # Tombol Login
        self.login_button = QPushButton("Login")
        self.login_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        
        # Tambahkan semua widget ke form layout
        form_layout.addWidget(id_label)
        form_layout.addWidget(self.id_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button)
        form_layout.addWidget(self.status_label)
        
        # Tambahkan widget ke right layout
        right_layout.addWidget(login_header)
        right_layout.addWidget(form_container)
        right_layout.addStretch()
        
        # Tambahkan left dan right widget ke main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        # Set layout
        self.setLayout(main_layout)
    
    def _setup_connections(self):
        """Setup event handlers"""
        self.login_button.clicked.connect(self._process_login)
        self.password_input.returnPressed.connect(self._process_login)
        self.id_input.returnPressed.connect(lambda: self.password_input.setFocus())
    
    def _process_login(self):
        """Proses login dosen"""
        # Reset status
        self.status_label.setText("")
        
        # Ambil input
        dosen_id = self.id_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validasi input
        if not dosen_id:
            self.status_label.setText("ID Dosen tidak boleh kosong")
            self.id_input.setFocus()
            return
        
        if not password:
            self.status_label.setText("Password tidak boleh kosong")
            self.password_input.setFocus()
            return
        
        # Konversi ID ke integer
        try:
            dosen_id = int(dosen_id)
        except ValueError:
            self.status_label.setText("ID Dosen harus berupa angka")
            self.id_input.setFocus()
            return
        
        # Koneksi database
        db_manager = DatabaseManager()
        db_manager.connect()
        db_manager.create_tables_if_not_exist()
        
        # Cek login
        status, result = db_manager.login(dosen_id, password)
        
        # Tutup koneksi
        db_manager.close()
        
        # Proses hasil login
        if status:
            # Login berhasil
            self.login_success.emit(result)
            self.accept()  # Tutup dialog dengan status berhasil
        else:
            # Login gagal
            self.status_label.setText(result["message"])


class SelectClassDialog(QDialog):
    """
    Dialog untuk memilih kelas dan pertemuan
    """
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Pilih Kelas")
        self.setFixedSize(900, 800)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
        
        # Data kelas dan pertemuan yang dipilih
        self.selected_class_info = None
        
        # Inisialisasi database manager
        self.db_manager = DatabaseManager()
        self.db_manager.connect()
        self.db_manager.create_tables_if_not_exist()
        
        # Load data kelas dari database
        self.class_data = self._load_class_data()
        
        self._init_ui()
        self._setup_connections()
    
    def _init_ui(self):
        """Inisialisasi komponen UI dialog pilih kelas"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Pilih Kelas dan Pertemuan")
        header_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_label.setStyleSheet("color: #333333; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignCenter)
        
        # Info dosen
        dosen_frame = QFrame()
        dosen_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                padding: 10px;
            }
        """)
        
        dosen_layout = QVBoxLayout(dosen_frame)
        
        # Tampilkan info dosen
        dosen_title = QLabel("Informasi Dosen")
        dosen_title.setFont(QFont("Arial", 14, QFont.Bold))
        dosen_title.setStyleSheet("color: #2c3e50;")
        
        dosen_id_label = QLabel(f"ID: {self.user_data['id']}")
        dosen_id_label.setFont(QFont("Arial", 12))
        
        dosen_nama_label = QLabel(f"Nama: {self.user_data['nama']}")
        dosen_nama_label.setFont(QFont("Arial", 12))
        
        dosen_layout.addWidget(dosen_title)
        dosen_layout.addWidget(dosen_id_label)
        dosen_layout.addWidget(dosen_nama_label)
        
        # Form untuk memilih kelas dan pertemuan
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                padding: 15px;
            }
        """)
        
        form_layout = QFormLayout(form_frame)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setSpacing(15)
        
        # Dropdown untuk memilih kelas
        kelas_label = QLabel("Kelas:")
        kelas_label.setFont(QFont("Arial", 12))
        kelas_label.setStyleSheet("color: #333333;")
        
        self.kelas_combo = QComboBox()
        self.kelas_combo.setFont(QFont("Arial", 12))
        self.kelas_combo.setMinimumHeight(40)
        self.kelas_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: blue;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(assets/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Isi dropdown kelas dari database
        if self.class_data:
            for kelas in self.class_data:
                self.kelas_combo.addItem(f"{kelas['kodeKelas']} - {kelas['namaKelas']}", kelas['kodeKelas'])
        
        # Dropdown untuk memilih pertemuan (1-16)
        pertemuan_label = QLabel("Pertemuan:")
        pertemuan_label.setFont(QFont("Arial", 12))
        pertemuan_label.setStyleSheet("color: #333333;")
        
        self.pertemuan_combo = QComboBox()
        self.pertemuan_combo.setFont(QFont("Arial", 12))
        self.pertemuan_combo.setMinimumHeight(40)
        self.pertemuan_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: 0px
            }
            QComboBox::down-arrow {
                image: url(assets/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Isi dropdown pertemuan (1-16)
        for i in range(1, 17):
            self.pertemuan_combo.addItem(f"Pertemuan {i}", i)
        
        # Input untuk PIN kelas
        pin_label = QLabel("PIN Kelas:")
        pin_label.setFont(QFont("Arial", 12))
        pin_label.setStyleSheet("color: #333333;")
        
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Masukkan PIN Kelas")
        self.pin_input.setFont(QFont("Arial", 12))
        self.pin_input.setMinimumHeight(40)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        # Tambahkan fields ke form layout
        form_layout.addRow(kelas_label, self.kelas_combo)
        form_layout.addRow(pertemuan_label, self.pertemuan_combo)
        form_layout.addRow(pin_label, self.pin_input)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        
        # Tombol Submit
        self.submit_button = QPushButton("Mulai Sesi Absensi")
        self.submit_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.submit_button.setMinimumHeight(50)
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        # Tombol Batal
        self.cancel_button = QPushButton("Batal")
        self.cancel_button.setFont(QFont("Arial", 12))
        self.cancel_button.setMinimumHeight(50)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7d;
            }
        """)
        
        # Layout untuk tombol-tombol
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.submit_button)
        
        # Tambahkan semua elemen ke main layout
        main_layout.addWidget(header_label)
        main_layout.addWidget(dosen_frame)
        main_layout.addWidget(form_frame)
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(main_layout)
    
    def _setup_connections(self):
        """Setup event handlers"""
        self.submit_button.clicked.connect(self._process_selection)
        self.cancel_button.clicked.connect(self.reject)
        self.kelas_combo.currentIndexChanged.connect(self._update_max_pertemuan)
    
    def _load_class_data(self):
        """
        Mengambil data kelas dari database yang dimiliki oleh dosen yang login
        
        Returns:
            list: List berisi dict data kelas
        """
        try:
            # Jalankan query untuk mendapatkan kelas yang diajar oleh dosen ini
            self.db_manager.cursor.execute("""
                SELECT kodeKelas, namaKelas, pinKelas, jumlahPertemuan
                FROM kelas
                WHERE dosenUtamaId = ? OR dosenPendampingId = ?
                ORDER BY namaKelas
            """, (self.user_data['id'], self.user_data['id']))
            
            columns = ['kodeKelas', 'namaKelas', 'pinKelas', 'jumlahPertemuan']
            result = self.db_manager.cursor.fetchall()
            
            # Konversi hasil query ke list dict
            class_data = []
            for row in result:
                class_dict = {columns[i]: row[i] for i in range(len(columns))}
                class_data.append(class_dict)
            
            return class_data
            
        except Exception as e:
            print(f"Error saat mengambil data kelas: {e}")
            return []
    
    def _update_max_pertemuan(self):
        """Update jumlah pertemuan maksimum sesuai dengan kelas yang dipilih"""
        if not self.class_data:
            return
        
        # Ambil kode kelas yang dipilih
        current_index = self.kelas_combo.currentIndex()
        if current_index < 0:
            return
            
        kode_kelas = self.kelas_combo.itemData(current_index)
        
        # Cari data kelas yang sesuai
        selected_class = None
        for kelas in self.class_data:
            if kelas['kodeKelas'] == kode_kelas:
                selected_class = kelas
                break
        
        if not selected_class:
            return
            
        # Jumlah pertemuan dari database
        max_pertemuan = selected_class.get('jumlahPertemuan', 16)
        if not max_pertemuan or max_pertemuan <= 0:
            max_pertemuan = 16
        
        # Perbarui dropdown pertemuan
        self.pertemuan_combo.clear()
        for i in range(1, max_pertemuan + 1):
            self.pertemuan_combo.addItem(f"Pertemuan {i}", i)
    
    def _process_selection(self):
        """Proses pemilihan kelas dan pertemuan"""
        # Reset status
        self.status_label.setText("")
        
        # Ambil nilai yang dipilih
        kelas_index = self.kelas_combo.currentIndex()
        pertemuan_index = self.pertemuan_combo.currentIndex()
        pin_kelas = self.pin_input.text().strip()
        
        # Validasi input
        if kelas_index < 0:
            self.status_label.setText("Silakan pilih kelas")
            return
            
        if pertemuan_index < 0:
            self.status_label.setText("Silakan pilih pertemuan")
            return
            
        if not pin_kelas:
            self.status_label.setText("PIN kelas tidak boleh kosong")
            self.pin_input.setFocus()
            return
        
        # Ambil data yang dipilih
        kode_kelas = self.kelas_combo.itemData(kelas_index)
        nomor_pertemuan = self.pertemuan_combo.itemData(pertemuan_index)
        
        # Validasi pin kelas dan data lainnya menggunakan db_manager
        status, result = self.db_manager.pilih_kelas(
            self.user_data['id'],
            kode_kelas,
            pin_kelas,
            nomor_pertemuan
        )
        
        if status:
            # Ambil info kelas lengkap untuk ditampilkan
            kelas_status, kelas_info = self.db_manager.get_kelas_info(kode_kelas)
            
            if kelas_status:
                # Susun informasi kelas dan pertemuan
                self.selected_class_info = {
                    'kode_kelas': kode_kelas,
                    'nama_kelas': kelas_info.get('nama_kelas', ''),
                    'nomor_pertemuan': nomor_pertemuan,
                    'dosen': {
                        'id': self.user_data['id'],
                        'nama': self.user_data['nama']
                    }
                }
                
                self.accept()  # Tutup dialog dengan status Accepted
            else:
                self.status_label.setText(f"Error: {kelas_info.get('message', 'Terjadi kesalahan')}")
        else:
            self.status_label.setText(result.get('message', 'Terjadi kesalahan'))
    
    def get_selected_class_info(self):
        """
        Mendapatkan informasi kelas yang dipilih
        
        Returns:
            dict: Informasi kelas yang dipilih
        """
        return self.selected_class_info
    
    def closeEvent(self, event):
        """Handler saat dialog ditutup"""
        # Tutup koneksi database
        if hasattr(self, 'db_manager') and self.db_manager.conn:
            self.db_manager.close()
        
        # Lanjutkan event close
        super().closeEvent(event)