#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database manager untuk mengelola data dosen dan kelas.
Modul ini dapat digunakan sebagai library atau dijalankan langsung untuk pengujian.
"""

import os
import sys
import sqlite3
import requests
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,  # Ubah kembali ke INFO untuk penggunaan normal
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('db-manager')


class DatabaseManager:
    """Class untuk mengelola database dosen dan kelas."""

    def __init__(self, db_name: str = "local"):
        """
        Inisialisasi database manager.
        
        Args:
            db_name: Nama file database SQLite, default "local"
        """
        self.db_name = f"{db_name}.db"
        self.conn = None
        self.cursor = None
        self.api_url_getdosen = "https://www.face.my.id/api/getdosen"
        self.api_url_getkelas = "https://www.face.my.id/api/getclasses"
        self.api_url_getmahasiswa = "https://www.face.my.id/api/getmahasiswa"
        self.api_url_updateabsensi = "https://www.face.my.id/api/updateabsensi"

    def connect(self) -> None:
        """Membuat koneksi ke database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            logger.info(f"Berhasil terhubung ke database {self.db_name}")
        except sqlite3.Error as e:
            logger.error(f"Error saat menghubungkan ke database: {e}")
            sys.exit(1)

    def close(self) -> None:
        """Menutup koneksi database."""
        if self.conn:
            self.conn.close()
            logger.info("Koneksi database ditutup")

    def create_tables_if_not_exist(self) -> None:
        """Membuat tabel dosen, kelas, mahasiswa, dan absensi jika belum ada."""
        try:
            # Tabel dosen
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dosen (
                id INTEGER PRIMARY KEY,
                nama TEXT,
                nip TEXT,
                email TEXT,
                password TEXT
            )
            ''')
            
            # Tabel mahasiswa
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id INTEGER PRIMARY KEY,
                nama TEXT,
                email TEXT
            )
            ''')
            
            # Tabel kelas dengan foreign key dan id sebagai TEXT
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kelas (
                id TEXT PRIMARY KEY,
                kodeKelas TEXT,
                namaKelas TEXT,
                pinKelas TEXT,
                dosenUtamaId INTEGER,
                dosenPendampingId INTEGER,
                jumlahPertemuan INTEGER,
                deskripsi TEXT,
                FOREIGN KEY (dosenUtamaId) REFERENCES dosen(id),
                FOREIGN KEY (dosenPendampingId) REFERENCES dosen(id)
            )
            ''')
            
            # Tabel absensi
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS absensi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mahasiswaId INTEGER NOT NULL,
                noPertemuan INTEGER NOT NULL,
                kodeKelas TEXT NOT NULL,
                statusSync TEXT DEFAULT 'pending',
                jamAbsen TEXT NOT NULL,
                FOREIGN KEY (mahasiswaId) REFERENCES mahasiswa(id),
                FOREIGN KEY (kodeKelas) REFERENCES kelas(kodeKelas)
            )
            ''')
            
            self.conn.commit()
            logger.info("Tabel dosen, kelas, mahasiswa, dan absensi siap digunakan")
        except sqlite3.Error as e:
            logger.error(f"Error saat membuat tabel: {e}")
            self.conn.rollback()

    def fetch_data_from_api(self, api_url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Mengambil data dari API.
        
        Args:
            api_url: URL API yang akan diakses
            
        Returns:
            List data atau None jika terjadi error
        """
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            raw_data = response.text
            logger.debug(f"Raw API Response: {raw_data[:200]}...")  # Tampilkan bagian awal response
            
            data = response.json()
            
            # Periksa struktur data
            if isinstance(data, dict):
                # Jika response adalah dictionary, coba ambil data dari key yang umum
                if 'data' in data:
                    data = data['data']
                elif 'results' in data:
                    data = data['results']
                else:
                    # Konversi dictionary ke list jika tidak ada key yang umum
                    data = [data]
            
            if not isinstance(data, list):
                logger.error(f"Data dari API tidak dalam format yang diharapkan: {type(data)}")
                return None
                
            # Pre-process data - pastikan field numeric dikonversi dengan benar
            # Namun tetap simpan ID kelas sebagai string
            for item in data:
                if isinstance(item, dict):
                    # Konversi ID ke int untuk API dosen dan mahasiswa
                    if (api_url == self.api_url_getdosen or api_url == self.api_url_getmahasiswa) and 'id' in item and item['id']:
                        try:
                            item['id'] = int(item['id'])
                        except (ValueError, TypeError):
                            logger.warning(f"Gagal mengkonversi ID '{item['id']}' ke integer")
                    
                    # Jika API getkelas, konversi field numerik kecuali ID
                    if api_url == self.api_url_getkelas:
                        # Pastikan ID kelas sebagai string
                        if 'id' in item and item['id'] is not None:
                            item['id'] = str(item['id'])
                            
                        # Konversi dosenUtamaId
                        if 'dosenUtamaId' in item and item['dosenUtamaId']:
                            try:
                                item['dosenUtamaId'] = int(item['dosenUtamaId']) 
                            except (ValueError, TypeError):
                                logger.warning(f"Gagal mengkonversi dosenUtamaId '{item['dosenUtamaId']}' ke integer")
                        
                        # Konversi dosenPendampingId
                        if 'dosenPendampingId' in item and item['dosenPendampingId']:
                            try:
                                item['dosenPendampingId'] = int(item['dosenPendampingId'])
                            except (ValueError, TypeError):
                                logger.warning(f"Gagal mengkonversi dosenPendampingId '{item['dosenPendampingId']}' ke integer")
                        
                        # Konversi jumlahPertemuan
                        if 'jumlahPertemuan' in item and item['jumlahPertemuan']:
                            try:
                                item['jumlahPertemuan'] = int(item['jumlahPertemuan'])
                            except (ValueError, TypeError):
                                item['jumlahPertemuan'] = 0
                                logger.warning(f"Gagal mengkonversi jumlahPertemuan, menggunakan default 0")
                
            logger.info(f"Berhasil mengambil {len(data)} data dari {api_url}")
            
            # Tampilkan contoh data untuk debugging
            if data and len(data) > 0:
                logger.debug(f"Contoh data pertama setelah konversi: {json.dumps(data[0], indent=2)}")
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error saat mengambil data dari API: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error saat parsing response JSON: {e}")
            logger.debug(f"Response yang tidak dapat di-parse: {response.text[:500]}...")
            return None

    def save_dosen_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Menyimpan data dosen ke database. Jika ID sudah ada, data diperbarui.
        Jika belum ada, data ditambahkan.
        
        Args:
            data: List data dosen dari API
        """
        if not data:
            logger.warning("Tidak ada data dosen untuk disimpan")
            return

        try:
            for item in data:
                # Pastikan item adalah dictionary
                if not isinstance(item, dict):
                    logger.warning(f"Melewati item non-dictionary: {item}")
                    continue
                    
                # Debug item data
                logger.debug(f"Processing dosen item: {json.dumps(item, indent=2)}")
                
                # Pastikan item['id'] adalah integer
                dosen_id = self.safe_int_convert(item.get('id'))
                
                if dosen_id is None:
                    # Jika tidak ada ID, coba gunakan auto-increment
                    logger.warning(f"Dosen tanpa ID valid, mencoba generate ID: {item}")
                    
                    # Dapatkan ID maksimum saat ini dan tambahkan 1
                    self.cursor.execute("SELECT MAX(id) FROM dosen")
                    max_id = self.cursor.fetchone()[0]
                    dosen_id = 1 if max_id is None else max_id + 1
                    logger.info(f"Generated ID untuk dosen: {dosen_id}")
                
                # Cek apakah ID sudah ada
                self.cursor.execute("SELECT id FROM dosen WHERE id = ?", (dosen_id,))
                existing_id = self.cursor.fetchone()
                
                if existing_id:
                    # Update data yang sudah ada
                    self.cursor.execute('''
                    UPDATE dosen 
                    SET nama = ?, nip = ?, email = ?, password = ?
                    WHERE id = ?
                    ''', (
                        str(item.get('nama', '')),
                        str(item.get('nip', '')),
                        str(item.get('email', '')),
                        str(item.get('password', '')),
                        dosen_id
                    ))
                    logger.debug(f"Updated data for dosen ID: {dosen_id}")
                else:
                    # Tambah data baru
                    self.cursor.execute('''
                    INSERT INTO dosen (id, nama, nip, email, password)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        dosen_id,
                        str(item.get('nama', '')),
                        str(item.get('nip', '')),
                        str(item.get('email', '')),
                        str(item.get('password', ''))
                    ))
                    logger.debug(f"Inserted new data for dosen ID: {dosen_id}")
            
            self.conn.commit()
            logger.info(f"Berhasil menyimpan {len(data)} data dosen ke database")
        except sqlite3.Error as e:
            logger.error(f"Error saat menyimpan data dosen ke database: {e}")
            logger.debug(f"Stack trace: ", exc_info=True)
            self.conn.rollback()

    def save_mahasiswa_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Menyimpan data mahasiswa ke database. Jika ID sudah ada, data diperbarui.
        Jika belum ada, data ditambahkan.
        
        Args:
            data: List data mahasiswa dari API
        """
        if not data:
            logger.warning("Tidak ada data mahasiswa untuk disimpan")
            return

        try:
            for item in data:
                # Pastikan item adalah dictionary
                if not isinstance(item, dict):
                    logger.warning(f"Melewati item non-dictionary: {item}")
                    continue
                    
                # Debug item data
                logger.debug(f"Processing mahasiswa item: {json.dumps(item, indent=2)}")
                
                # Pastikan item['id'] adalah integer
                mahasiswa_id = self.safe_int_convert(item.get('id'))
                
                if mahasiswa_id is None:
                    # Jika tidak ada ID, coba gunakan auto-increment
                    logger.warning(f"Mahasiswa tanpa ID valid, mencoba generate ID: {item}")
                    
                    # Dapatkan ID maksimum saat ini dan tambahkan 1
                    self.cursor.execute("SELECT MAX(id) FROM mahasiswa")
                    max_id = self.cursor.fetchone()[0]
                    mahasiswa_id = 1 if max_id is None else max_id + 1
                    logger.info(f"Generated ID untuk mahasiswa: {mahasiswa_id}")
                
                # Cek apakah ID sudah ada
                self.cursor.execute("SELECT id FROM mahasiswa WHERE id = ?", (mahasiswa_id,))
                existing_id = self.cursor.fetchone()
                
                if existing_id:
                    # Update data yang sudah ada
                    self.cursor.execute('''
                    UPDATE mahasiswa 
                    SET nama = ?, email = ?
                    WHERE id = ?
                    ''', (
                        str(item.get('nama', '')),
                        str(item.get('email', '')),
                        mahasiswa_id
                    ))
                    logger.debug(f"Updated data for mahasiswa ID: {mahasiswa_id}")
                else:
                    # Tambah data baru
                    self.cursor.execute('''
                    INSERT INTO mahasiswa (id, nama, email)
                    VALUES (?, ?, ?)
                    ''', (
                        mahasiswa_id,
                        str(item.get('nama', '')),
                        str(item.get('email', ''))
                    ))
                    logger.debug(f"Inserted new data for mahasiswa ID: {mahasiswa_id}")
            
            self.conn.commit()
            logger.info(f"Berhasil menyimpan {len(data)} data mahasiswa ke database")
        except sqlite3.Error as e:
            logger.error(f"Error saat menyimpan data mahasiswa ke database: {e}")
            logger.debug(f"Stack trace: ", exc_info=True)
            self.conn.rollback()
    
    def safe_int_convert(self, value, default=None):
        """
        Mengkonversi nilai ke integer dengan aman.
        Jika nilai tidak dapat dikonversi, mengembalikan default.
        
        Args:
            value: Nilai yang akan dikonversi
            default: Nilai default jika konversi gagal
            
        Returns:
            Integer atau default
        """
        if value is None:
            return default
        
        try:
            # Strip string jika tipe data string
            if isinstance(value, str):
                value = value.strip()
                # Jika string kosong, kembalikan default
                if not value:
                    return default
                    
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def save_kelas_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Menyimpan data kelas ke database. Jika ID sudah ada, data diperbarui.
        Jika belum ada, data ditambahkan.
        
        Args:
            data: List data kelas dari API
        """
        if not data:
            logger.warning("Tidak ada data kelas untuk disimpan")
            return

        try:
            for item in data:
                # Pastikan item adalah dictionary
                if not isinstance(item, dict):
                    logger.warning(f"Melewati item non-dictionary: {item}")
                    continue
                
                # Debug item data
                logger.debug(f"Processing kelas item: {json.dumps(item, indent=2)}")
                
                # Ambil ID kelas sebagai string
                kelas_id = str(item.get('id', ''))
                
                if not kelas_id:
                    # Jika tidak ada ID, gunakan UUID atau timestamp sebagai ID unik
                    import uuid
                    import time
                    kelas_id = f"gen_{int(time.time())}_{uuid.uuid4().hex[:8]}"
                    logger.info(f"Generated string ID untuk kelas: {kelas_id}")
                
                # Konversi data lainnya
                dosen_utama_id = self.safe_int_convert(item.get('dosenUtamaId'))
                dosen_pendamping_id = self.safe_int_convert(item.get('dosenPendampingId'))
                jumlah_pertemuan = self.safe_int_convert(item.get('jumlahPertemuan'), 0)
                
                # Debug nilai yang sudah dikonversi
                logger.debug(f"Converted values - kelas ID: {kelas_id}, dosenUtamaId: {dosen_utama_id}, " +
                           f"dosenPendampingId: {dosen_pendamping_id}, jumlahPertemuan: {jumlah_pertemuan}")
                
                # Cek apakah ID sudah ada
                self.cursor.execute("SELECT id FROM kelas WHERE id = ?", (kelas_id,))
                existing_id = self.cursor.fetchone()
                
                if existing_id:
                    # Update data yang sudah ada
                    self.cursor.execute('''
                    UPDATE kelas 
                    SET kodeKelas = ?, namaKelas = ?, pinKelas = ?, 
                        dosenUtamaId = ?, dosenPendampingId = ?,
                        jumlahPertemuan = ?, deskripsi = ?
                    WHERE id = ?
                    ''', (
                        str(item.get('kodeKelas', '')),
                        str(item.get('namaKelas', '')),
                        str(item.get('pinKelas', '')),
                        dosen_utama_id,
                        dosen_pendamping_id,
                        jumlah_pertemuan,
                        str(item.get('deskripsi', '')),
                        kelas_id
                    ))
                    logger.debug(f"Updated data for kelas ID: {kelas_id}")
                else:
                    # Tambah data baru
                    self.cursor.execute('''
                    INSERT INTO kelas (id, kodeKelas, namaKelas, pinKelas, 
                                      dosenUtamaId, dosenPendampingId, 
                                      jumlahPertemuan, deskripsi)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        kelas_id,
                        str(item.get('kodeKelas', '')),
                        str(item.get('namaKelas', '')),
                        str(item.get('pinKelas', '')),
                        dosen_utama_id,
                        dosen_pendamping_id,
                        jumlah_pertemuan,
                        str(item.get('deskripsi', ''))
                    ))
                    logger.debug(f"Inserted new data for kelas ID: {kelas_id}")
            
            self.conn.commit()
            logger.info(f"Berhasil menyimpan {len(data)} data kelas ke database")
        except sqlite3.Error as e:
            logger.error(f"Error saat menyimpan data kelas ke database: {e}")
            logger.debug(f"Stack trace: ", exc_info=True)
            self.conn.rollback()

    def display_data(self, table_name: str) -> None:
        """
        Menampilkan seluruh data dari tabel tertentu ke terminal.
        
        Args:
            table_name: Nama tabel yang akan ditampilkan datanya
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            if not rows:
                logger.info(f"Tidak ada data di tabel {table_name}")
                print(f"\nTidak ada data di tabel {table_name}")
                return
                
            # Mendapatkan nama kolom
            column_names = [description[0] for description in self.cursor.description]
            
            # Menghitung lebar setiap kolom
            col_widths = []
            for i, col in enumerate(column_names):
                # Lebar maksimum antara nama kolom dan nilai terpanjang di kolom tersebut
                max_data_width = max([len(str(row[i])) for row in rows])
                col_widths.append(max(len(col), max_data_width) + 2)  # Tambahkan padding
            
            # Membuat format string untuk header dan data
            fmt = " | ".join([f"{{:{w}}}" for w in col_widths])
            
            # Menghitung panjang total baris
            total_width = sum(col_widths) + (len(col_widths) - 1) * 3  # 3 karakter untuk " | "
            
            # Menampilkan header
            print("\n" + "=" * total_width)
            print(fmt.format(*column_names))
            print("=" * total_width)
            
            # Menampilkan data
            for row in rows:
                print(fmt.format(*[str(item) for item in row]))
            
            print("-" * total_width)
            print(f"Total: {len(rows)} records")
            print("=" * total_width + "\n")
            
            logger.info(f"Menampilkan {len(rows)} data dari tabel {table_name}")
        except sqlite3.Error as e:
            logger.error(f"Error saat menampilkan data tabel {table_name}: {e}")

    def view_tables(self) -> None:
        """Menampilkan semua tabel dalam database dan memungkinkan pengguna memilih tabel untuk ditampilkan."""
        # Buka koneksi database terlebih dahulu
        self.connect()
        
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = self.cursor.fetchall()
            
            if not tables:
                print("Tidak ada tabel dalam database.")
                self.close()  # Tutup koneksi
                return
            
            print("\n=== Daftar Tabel dalam Database ===")
            print("-" * 40)
            
            for i, table in enumerate(tables):
                print(f"{i+1}. {table[0]}")
            
            print("-" * 40)
            print("0. Kembali ke menu utama")
            print("-" * 40)
            
            choice = input("\nPilih tabel untuk ditampilkan (angka): ")
            
            try:
                choice = int(choice)
                if choice == 0:
                    self.close()  # Tutup koneksi
                    return
                
                if 1 <= choice <= len(tables):
                    # Tampilkan data dari tabel yang dipilih
                    table_name = tables[choice-1][0]
                    self.display_data(table_name)
                else:
                    print("Pilihan tidak valid.")
            except ValueError:
                print("Masukkan harus berupa angka.")
            
        except sqlite3.Error as e:
            logger.error(f"Error saat menampilkan daftar tabel: {e}")
            print(f"Error: {e}")
        
        # Tutup koneksi di akhir fungsi
        self.close()   
    
    def login(self, dosen_id: int, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Memeriksa kredensial login dosen.
        
        Args:
            dosen_id: ID dosen
            password: Password dosen
            
        Returns:
            Tuple berisi status login (True/False) dan data/pesan hasil
        """
        try:
            # Validasi input
            if not dosen_id or not password:
                return False, {"message": "ID dan password harus diisi"}
            
            # Cari dosen dengan ID yang diberikan
            self.cursor.execute("SELECT id, nama, password FROM dosen WHERE id = ?", (dosen_id,))
            result = self.cursor.fetchone()
            
            if not result:
                logger.info(f"Login gagal: Dosen dengan ID {dosen_id} tidak ditemukan")
                return False, {"message": f"Dosen dengan ID {dosen_id} tidak ditemukan"}
            
            db_id, db_nama, db_password = result
            
            # Periksa password
            if db_password != password:
                logger.info(f"Login gagal: Password salah untuk dosen ID {dosen_id}")
                return False, {"message": "Password salah"}
            
            # Login berhasil
            logger.info(f"Login berhasil: Dosen ID {dosen_id} ({db_nama})")
            return True, {"id": db_id, "nama": db_nama}
            
        except sqlite3.Error as e:
            logger.error(f"Error saat login: {e}")
            return False, {"message": f"Error database: {str(e)}"}
    
    def pilih_kelas(self, dosen_id: int, kode_kelas: str, pin_kelas: str, nomor_pertemuan: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Validasi pemilihan kelas oleh dosen.
        
        Args:
            dosen_id: ID dosen
            kode_kelas: Kode kelas
            pin_kelas: PIN kelas
            nomor_pertemuan: Nomor pertemuan
            
        Returns:
            Tuple berisi status validasi (True/False) dan data/pesan hasil
        """
        try:
            # Validasi input
            if not dosen_id:
                return False, {"message": "ID dosen harus diisi"}
            if not kode_kelas:
                return False, {"message": "Kode kelas harus diisi"}
            if not pin_kelas:
                return False, {"message": "PIN kelas harus diisi"}
            if nomor_pertemuan <= 0:
                return False, {"message": "Nomor pertemuan harus lebih besar dari 0"}
            
            # Cek apakah dosen ada
            self.cursor.execute("SELECT id FROM dosen WHERE id = ?", (dosen_id,))
            if not self.cursor.fetchone():
                logger.info(f"Pilih kelas gagal: Dosen dengan ID {dosen_id} tidak ditemukan")
                return False, {"message": f"Dosen dengan ID {dosen_id} tidak ditemukan"}
            
            # Cek apakah kelas ada
            self.cursor.execute('''
            SELECT id, dosenUtamaId, dosenPendampingId, pinKelas, jumlahPertemuan 
            FROM kelas 
            WHERE kodeKelas = ?
            ''', (kode_kelas,))
            
            result = self.cursor.fetchone()
            if not result:
                logger.info(f"Pilih kelas gagal: Kelas dengan kode {kode_kelas} tidak ditemukan")
                return False, {"message": f"Kelas dengan kode {kode_kelas} tidak ditemukan"}
            
            kelas_id, dosen_utama_id, dosen_pendamping_id, db_pin_kelas, jumlah_pertemuan = result
            
            # Cek apakah dosen mengajar di kelas tersebut
            if dosen_id != dosen_utama_id and dosen_id != dosen_pendamping_id:
                logger.info(f"Pilih kelas gagal: Dosen ID {dosen_id} bukan pengajar di kelas {kode_kelas}")
                return False, {"message": f"Anda bukan pengajar di kelas {kode_kelas}"}
            
            # Cek apakah PIN kelas benar
            if pin_kelas != db_pin_kelas:
                logger.info(f"Pilih kelas gagal: PIN kelas salah untuk kelas {kode_kelas}")
                return False, {"message": "PIN kelas salah"}
            
            # Cek apakah nomor pertemuan valid
            if nomor_pertemuan > jumlah_pertemuan:
                logger.info(f"Pilih kelas gagal: Nomor pertemuan {nomor_pertemuan} melebihi jumlah pertemuan {jumlah_pertemuan}")
                return False, {"message": f"Nomor pertemuan tidak valid. Maksimal: {jumlah_pertemuan}"}
            
            # Validasi berhasil
            logger.info(f"Pilih kelas berhasil: Dosen ID {dosen_id}, Kelas {kode_kelas}, Pertemuan {nomor_pertemuan}")
            return True, {"kode_kelas": kode_kelas, "nomor_pertemuan": nomor_pertemuan}
            
        except sqlite3.Error as e:
            logger.error(f"Error saat pilih kelas: {e}")
            return False, {"message": f"Error database: {str(e)}"}
    
    def get_kelas_info(self, kode_kelas: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Mendapatkan informasi detail kelas berdasarkan kode kelas.
        
        Args:
            kode_kelas: Kode kelas yang akan dicari
            
        Returns:
            Tuple berisi status (True/False) dan data/pesan hasil
        """
        try:
            # Validasi input
            if not kode_kelas:
                return False, {"message": "Kode kelas harus diisi"}
            
            # Query untuk informasi kelas dan dosen
            self.cursor.execute('''
            SELECT 
                k.namaKelas, 
                k.deskripsi, 
                k.dosenUtamaId, 
                k.dosenPendampingId,
                d1.nama as nama_dosen_utama,
                d2.nama as nama_dosen_pendamping
            FROM kelas k
            LEFT JOIN dosen d1 ON k.dosenUtamaId = d1.id
            LEFT JOIN dosen d2 ON k.dosenPendampingId = d2.id
            WHERE k.kodeKelas = ?
            ''', (kode_kelas,))
            
            result = self.cursor.fetchone()
            
            if not result:
                logger.info(f"Info kelas gagal: Kelas dengan kode {kode_kelas} tidak ditemukan")
                return False, {"message": f"Kelas dengan kode {kode_kelas} tidak ditemukan"}
            
            nama_kelas, deskripsi, dosen_utama_id, dosen_pendamping_id, nama_dosen_utama, nama_dosen_pendamping = result
           
            # Membuat dictionary hasil
            kelas_info = {
                "nama_kelas": nama_kelas or "Tidak ada nama",
                "deskripsi": deskripsi or "Tidak ada deskripsi",
                "dosen_utama": {
                    "id": dosen_utama_id,
                    "nama": nama_dosen_utama or "Tidak diketahui"
                },
                "dosen_pendamping": {
                    "id": dosen_pendamping_id,
                    "nama": nama_dosen_pendamping or "Tidak diketahui"
                }
            }
            
            logger.info(f"Info kelas berhasil: Kelas dengan kode {kode_kelas} ditemukan")
            return True, kelas_info
            
        except sqlite3.Error as e:
            logger.error(f"Error saat mendapatkan info kelas: {e}")
            return False, {"message": f"Error database: {str(e)}"}
    
    def tambah_absensi(self, mahasiswa_id: int, no_pertemuan: int, kode_kelas: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Menambahkan data absensi mahasiswa.
        
        Args:
            mahasiswa_id: ID mahasiswa
            no_pertemuan: Nomor pertemuan
            kode_kelas: Kode kelas
            
        Returns:
            Tuple berisi status (True/False) dan data/pesan hasil
        """
        try:
            # Validasi input
            if not mahasiswa_id:
                return False, {"message": "ID mahasiswa harus diisi"}
            if no_pertemuan <= 0:
                return False, {"message": "Nomor pertemuan harus lebih besar dari 0"}
            if not kode_kelas:
                return False, {"message": "Kode kelas harus diisi"}
            
            # Cek apakah mahasiswa ada
            self.cursor.execute("SELECT id FROM mahasiswa WHERE id = ?", (mahasiswa_id,))
            if not self.cursor.fetchone():
                logger.info(f"Tambah absensi gagal: Mahasiswa dengan ID {mahasiswa_id} tidak ditemukan")
                return False, {"message": f"Mahasiswa dengan ID {mahasiswa_id} tidak ditemukan"}
            
            # Cek apakah kelas ada dan nomor pertemuan valid
            self.cursor.execute('''
            SELECT jumlahPertemuan 
            FROM kelas 
            WHERE kodeKelas = ?
            ''', (kode_kelas,))
            
            result = self.cursor.fetchone()
            if not result:
                logger.info(f"Tambah absensi gagal: Kelas dengan kode {kode_kelas} tidak ditemukan")
                return False, {"message": f"Kelas dengan kode {kode_kelas} tidak ditemukan"}
            
            jumlah_pertemuan = result[0]
            
            # Cek apakah nomor pertemuan valid
            if no_pertemuan > jumlah_pertemuan:
                logger.info(f"Tambah absensi gagal: Nomor pertemuan {no_pertemuan} melebihi jumlah pertemuan {jumlah_pertemuan}")
                return False, {"message": f"Nomor pertemuan tidak valid. Maksimal: {jumlah_pertemuan}"}
            
            # Cek apakah mahasiswa sudah absen pada pertemuan ini
            self.cursor.execute('''
            SELECT id
            FROM absensi
            WHERE mahasiswaId = ? AND noPertemuan = ? AND kodeKelas = ?
            ''', (mahasiswa_id, no_pertemuan, kode_kelas))
            
            if self.cursor.fetchone():
                logger.info(f"Tambah absensi gagal: Mahasiswa {mahasiswa_id} sudah absen pada pertemuan {no_pertemuan} kelas {kode_kelas}")
                return False, {"message": f"Mahasiswa sudah absen pada pertemuan ini"}
            
            # Ambil timestamp saat ini
            jam_absen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Tambahkan data absensi
            self.cursor.execute('''
            INSERT INTO absensi (mahasiswaId, noPertemuan, kodeKelas, statusSync, jamAbsen)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                mahasiswa_id,
                no_pertemuan,
                kode_kelas,
                "pending",
                jam_absen
            ))
            
            self.conn.commit()
            
            # Ambil ID yang baru ditambahkan
            absensi_id = self.cursor.lastrowid
            
            logger.info(f"Tambah absensi berhasil: Mahasiswa {mahasiswa_id}, Pertemuan {no_pertemuan}, Kelas {kode_kelas}")
            return True, {
                "id": absensi_id,
                "mahasiswa_id": mahasiswa_id,
                "no_pertemuan": no_pertemuan,
                "kode_kelas": kode_kelas,
                "jam_absen": jam_absen
            }
            
        except sqlite3.Error as e:
            logger.error(f"Error saat menambahkan absensi: {e}")
            self.conn.rollback()
            return False, {"message": f"Error database: {str(e)}"}
    
    def sync_db_to_server(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Menyinkronkan data absensi yang belum terkirim ke server.
        
        Returns:
            Tuple berisi status (True/False) dan data/pesan hasil
        """
        try:
            # Ambil semua absensi dengan status 'pending'
            self.cursor.execute('''
            SELECT id, mahasiswaId, noPertemuan, kodeKelas
            FROM absensi
            WHERE statusSync = 'pending'
            ''')
            
            pending_absensi = self.cursor.fetchall()
            
            if not pending_absensi:
                logger.info("Tidak ada data absensi yang perlu disinkronkan")
                return True, {"message": "Tidak ada data yang perlu disinkronkan", "synced": 0, "failed": 0}
            
            total_pending = len(pending_absensi)
            synced_count = 0
            failed_count = 0
            failed_list = []
            
            for absensi in pending_absensi:
                absensi_id, mahasiswa_id, no_pertemuan, kode_kelas = absensi
                
                # Siapkan data untuk dikirim ke server
                payload = {
                    "mahasiswaId": str(mahasiswa_id),  # Convert to string as API might expect string
                    "noPertemuan": no_pertemuan,
                    "kodeKelas": kode_kelas,
                    "statusKehadiran": "HADIR"
                }
                
                try:
                    # Kirim data ke server
                    response = requests.post(
                        self.api_url_updateabsensi,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    # Periksa response
                    if response.status_code == 200:
                        # Update status menjadi 'synced'
                        self.cursor.execute('''
                        UPDATE absensi
                        SET statusSync = 'synced'
                        WHERE id = ?
                        ''', (absensi_id,))
                        
                        synced_count += 1
                        logger.info(f"Absensi ID {mahasiswa_id} berhasil disinkronkan")
                    else:
                        failed_count += 1
                        failed_list.append({
                            "id": absensi_id,
                            "status_code": response.status_code,
                            "message": response.text
                        })
                        logger.warning(f"Absensi ID {absensi_id} gagal disinkronkan: {response.status_code} - {response.text}")
                
                except requests.exceptions.RequestException as e:
                    failed_count += 1
                    failed_list.append({
                        "id": absensi_id,
                        "error": str(e)
                    })
                    logger.error(f"Error saat sinkronisasi absensi ID {absensi_id}: {e}")
            
            # Commit semua perubahan
            self.conn.commit()
            
            # Buat laporan hasil sinkronisasi
            result = {
                "message": f"Sinkronisasi selesai. Berhasil: {synced_count}, Gagal: {failed_count}, Total: {total_pending}",
                "synced": synced_count,
                "failed": failed_count,
                "total": total_pending,
                "failed_details": failed_list if failed_list else None
            }
            
            logger.info(f"Sinkronisasi selesai. Berhasil: {synced_count}, Gagal: {failed_count}, Total: {total_pending}")
            return True, result
            
        except sqlite3.Error as e:
            logger.error(f"Error database saat sinkronisasi: {e}")
            self.conn.rollback()
            return False, {"message": f"Error database: {str(e)}"}
        except Exception as e:
            logger.error(f"Error umum saat sinkronisasi: {e}")
            return False, {"message": f"Error: {str(e)}"}

    def process_dosen_data(self) -> None:
        """Proses untuk mengambil dan menyimpan data dosen."""
        self.connect()
        self.create_tables_if_not_exist()
        
        logger.info("Mengambil data dosen dari API...")
        dosen_data = self.fetch_data_from_api(self.api_url_getdosen)
        
        if dosen_data:
            logger.info("Menyimpan data dosen ke database...")
            self.save_dosen_data(dosen_data)
            
            logger.info("Menampilkan data dosen dari database...")
            self.display_data("dosen")
        else:
            logger.warning("Tidak ada data dosen yang diperoleh dari API")
        
        self.close()
    
    def process_kelas_data(self) -> None:
        """Proses untuk mengambil dan menyimpan data kelas."""
        self.connect()
        self.create_tables_if_not_exist()
        
        logger.info("Mengambil data kelas dari API...")
        kelas_data = self.fetch_data_from_api(self.api_url_getkelas)
        
        if kelas_data:
            logger.info("Menyimpan data kelas ke database...")
            self.save_kelas_data(kelas_data)
            
            logger.info("Menampilkan data kelas dari database...")
            self.display_data("kelas")
        else:
            logger.warning("Tidak ada data kelas yang diperoleh dari API")
        
        self.close()
    
    def process_mahasiswa_data(self) -> None:
        """Proses untuk mengambil dan menyimpan data mahasiswa."""
        self.connect()
        self.create_tables_if_not_exist()
        
        logger.info("Mengambil data mahasiswa dari API...")
        mahasiswa_data = self.fetch_data_from_api(self.api_url_getmahasiswa)
        
        if mahasiswa_data:
            logger.info("Menyimpan data mahasiswa ke database...")
            self.save_mahasiswa_data(mahasiswa_data)
            
            logger.info("Menampilkan data mahasiswa dari database...")
            self.display_data("mahasiswa")
        else:
            logger.warning("Tidak ada data mahasiswa yang diperoleh dari API")
        
        self.close()
    
    def test_login(self) -> None:
        """Menu pengujian fungsi login."""
        self.connect()
        
        print("\n=== Test Login ===")
        try:
            # Minta input dari user
            dosen_id = input("Masukkan ID dosen: ")
            password = input("Masukkan password: ")
            
            # Konversi dan validasi input
            try:
                dosen_id = int(dosen_id)
            except ValueError:
                print("ID dosen harus berupa angka.")
                self.close()
                return
            
            # Panggil fungsi login
            status, result = self.login(dosen_id, password)
            
            # Tampilkan hasil
            if status:
                print("\n=== Login Berhasil ===")
                print(f"ID: {result['id']}")
                print(f"Nama: {result['nama']}")
            else:
                print(f"\n=== Login Gagal ===")
                print(f"Pesan: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error saat test login: {e}", exc_info=True)
            print(f"Terjadi error: {e}")
        
        self.close()
    
    def test_pilih_kelas(self) -> None:
        """Menu pengujian fungsi pilih kelas."""
        self.connect()
        
        print("\n=== Test Pilih Kelas ===")
        try:
            # Minta input dari user
            dosen_id = input("Masukkan ID dosen: ")
            kode_kelas = input("Masukkan kode kelas: ")
            pin_kelas = input("Masukkan PIN kelas: ")
            nomor_pertemuan = input("Masukkan nomor pertemuan: ")
            
            # Konversi dan validasi input
            try:
                dosen_id = int(dosen_id)
            except ValueError:
                print("ID dosen harus berupa angka.")
                self.close()
                return
                
            try:
                nomor_pertemuan = int(nomor_pertemuan)
            except ValueError:
                print("Nomor pertemuan harus berupa angka.")
                self.close()
                return
            
            # Panggil fungsi pilih kelas
            status, result = self.pilih_kelas(dosen_id, kode_kelas, pin_kelas, nomor_pertemuan)
            
            # Tampilkan hasil
            if status:
                print("\n=== Pilih Kelas Berhasil ===")
                print(f"Kode Kelas: {result['kode_kelas']}")
                print(f"Nomor Pertemuan: {result['nomor_pertemuan']}")
            else:
                print(f"\n=== Pilih Kelas Gagal ===")
                print(f"Pesan: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error saat test pilih kelas: {e}", exc_info=True)
            print(f"Terjadi error: {e}")
        
        self.close()
    
    def test_kelas_info(self) -> None:
        """Menu pengujian fungsi informasi kelas."""
        self.connect()
        
        print("\n=== Test Informasi Kelas ===")
        try:
            # Minta input dari user
            kode_kelas = input("Masukkan kode kelas: ")
            
            # Panggil fungsi get_kelas_info
            status, result = self.get_kelas_info(kode_kelas)
            
            # Tampilkan hasil
            if status:
                print("\n=== Informasi Kelas ===")
                print(f"Nama Kelas: {result['nama_kelas']}")
                print(f"Deskripsi: {result['deskripsi']}")
                print(f"\nDosen Utama:")
                print(f"  ID: {result['dosen_utama']['id']}")
                print(f"  Nama: {result['dosen_utama']['nama']}")
                print(f"\nDosen Pendamping:")
                print(f"  ID: {result['dosen_pendamping']['id']}")
                print(f"  Nama: {result['dosen_pendamping']['nama']}")
            else:
                print(f"\n=== Informasi Kelas Gagal ===")
                print(f"Pesan: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error saat test informasi kelas: {e}", exc_info=True)
            print(f"Terjadi error: {e}")
        
        self.close()
    
    def test_tambah_absensi(self) -> None:
        """Menu pengujian fungsi tambah absensi."""
        self.connect()
        self.create_tables_if_not_exist()  # Pastikan tabel absensi ada
        
        print("\n=== Test Tambah Absensi ===")
        try:
            # Minta input dari user
            mahasiswa_id = input("Masukkan ID mahasiswa: ")
            kode_kelas = input("Masukkan kode kelas: ")
            no_pertemuan = input("Masukkan nomor pertemuan: ")
            
            # Konversi dan validasi input
            try:
                mahasiswa_id = int(mahasiswa_id)
            except ValueError:
                print("ID mahasiswa harus berupa angka.")
                self.close()
                return
                
            try:
                no_pertemuan = int(no_pertemuan)
            except ValueError:
                print("Nomor pertemuan harus berupa angka.")
                self.close()
                return
            
            # Panggil fungsi tambah absensi
            status, result = self.tambah_absensi(mahasiswa_id, no_pertemuan, kode_kelas)
            
            # Tampilkan hasil
            if status:
                print("\n=== Tambah Absensi Berhasil ===")
                print(f"ID Absensi: {result['id']}")
                print(f"ID Mahasiswa: {result['mahasiswa_id']}")
                print(f"Kode Kelas: {result['kode_kelas']}")
                print(f"Nomor Pertemuan: {result['no_pertemuan']}")
                print(f"Jam Absen: {result['jam_absen']}")
                print(f"Status: pending (menunggu sinkronisasi)")
                
                # Tampilkan data absensi
                print("\n=== Data Absensi dalam Database ===")
                self.display_data("absensi")
            else:
                print(f"\n=== Tambah Absensi Gagal ===")
                print(f"Pesan: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error saat test tambah absensi: {e}", exc_info=True)
            print(f"Terjadi error: {e}")
        
        self.close()
    
    def test_sync_db_to_server(self) -> None:
        """Menu pengujian fungsi sinkronisasi absensi ke server."""
        self.connect()
        
        print("\n=== Test Sinkronisasi Absensi ===")
        try:
            print("Memeriksa data absensi yang belum disinkronkan...")
            
            # Tampilkan data absensi dengan status 'pending'
            self.cursor.execute("SELECT * FROM absensi WHERE statusSync = 'pending'")
            pending_data = self.cursor.fetchall()
            
            if not pending_data:
                print("Tidak ada data absensi yang perlu disinkronkan.")
                print("Coba tambahkan absensi terlebih dahulu.")
                self.close()
                return
            
            # Tampilkan daftar absensi yang akan disinkronkan
            print(f"\nDitemukan {len(pending_data)} data absensi yang perlu disinkronkan:")
            column_names = [description[0] for description in self.cursor.description]
            
            # Tampilkan data dalam format tabel
            max_widths = [max(len(str(col)), max([len(str(row[i])) for row in pending_data])) + 2 
                            for i, col in enumerate(column_names)]
            
            fmt = " | ".join([f"{{:{w}}}" for w in max_widths])
            total_width = sum(max_widths) + (len(max_widths) - 1) * 3
            
            print("=" * total_width)
            print(fmt.format(*column_names))
            print("=" * total_width)
            
            for row in pending_data:
                print(fmt.format(*[str(item) for item in row]))
            
            print("=" * total_width)
            
            # Konfirmasi sinkronisasi
            confirm = input("\nLanjutkan sinkronisasi? (y/n): ")
            if confirm.lower() != 'y':
                print("Sinkronisasi dibatalkan.")
                self.close()
                return
            
            # Jalankan sinkronisasi
            print("\nMulai sinkronisasi...")
            status, result = self.sync_db_to_server()
            
            # Tampilkan hasil
            if status:
                print("\n=== Sinkronisasi Selesai ===")
                print(result["message"])
                
                if result["failed"] > 0 and result["failed_details"]:
                    print("\nDetail kegagalan:")
                    for i, detail in enumerate(result["failed_details"]):
                        print(f"{i+1}. ID Absensi: {detail['id']}")
                        if "status_code" in detail:
                            print(f"   Status: {detail['status_code']}")
                            print(f"   Pesan: {detail['message']}")
                        else:
                            print(f"   Error: {detail['error']}")
                
                # Tampilkan data absensi yang masih pending
                if result["failed"] > 0:
                    print("\n=== Data yang masih pending ===")
                    self.cursor.execute("SELECT * FROM absensi WHERE statusSync = 'pending'")
                    pending_after = self.cursor.fetchall()
                    
                    if pending_after:
                        # Tampilkan data dalam format tabel
                        fmt = " | ".join([f"{{:{w}}}" for w in max_widths])
                        print("=" * total_width)
                        print(fmt.format(*column_names))
                        print("=" * total_width)
                        
                        for row in pending_after:
                            print(fmt.format(*[str(item) for item in row]))
                        
                        print("=" * total_width)
                    else:
                        print("Tidak ada data yang masih pending.")
            else:
                print(f"\n=== Sinkronisasi Gagal ===")
                print(f"Pesan: {result['message']}")
                
        except Exception as e:
            logger.error(f"Error saat test sinkronisasi: {e}", exc_info=True)
            print(f"Terjadi error: {e}")
        
        self.close()


def main():
    """Fungsi utama yang dijalankan ketika script dieksekusi langsung."""
    logger.info("Menjalankan db-manager.py")
    
    db_manager = DatabaseManager()
    
    while True:
        print("\nPilihan:")
        print("0. Lihat semua tabel")
        print("1. Proses data dosen")
        print("2. Proses data kelas")
        print("3. Test login")
        print("4. Test pilih kelas")
        print("5. Keluar")
        print("6. Test informasi kelas")
        print("7. Test tambah absensi")
        print("8. Test sinkronisasi absensi")
        print("9. Proses data mahasiswa")
        
        choice = input("Masukkan pilihan (0-9): ")
        
        try:
            if choice == "0":
                db_manager.view_tables()
            elif choice == "1":
                db_manager.process_dosen_data()
            elif choice == "2":
                db_manager.process_kelas_data()
            elif choice == "3":
                db_manager.test_login()
            elif choice == "4":
                db_manager.test_pilih_kelas()
            elif choice == "5":
                print("Program selesai.")
                break
            elif choice == "6":
                db_manager.test_kelas_info()
            elif choice == "7":
                db_manager.test_tambah_absensi()
            elif choice == "8":
                db_manager.test_sync_db_to_server()
            elif choice == "9":
                db_manager.process_mahasiswa_data()
            else:
                print("Pilihan tidak valid. Silakan coba lagi.")
        except Exception as e:
            logger.error(f"Error pada menu utama: {e}", exc_info=True)
            print(f"Terjadi error: {e}")


if __name__ == "__main__":
   main()