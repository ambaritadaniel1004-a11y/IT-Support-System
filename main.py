import sqlite3
from database import (
    get_connection,
    initialize_database,
    seed_assets,
    get_all_assets, 
    get_asset_by_id,
    add_asset,
    add_ticket,
    get_all_tickets,
    update_asset_status,
    delete_asset,
    update_ticket_status,
    delete_ticket,
    get_ticket_by_id,
    get_dashboard_data,
)

conn = get_connection()
cursor = conn.cursor()

initialize_database(conn)
seed_assets(conn)

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    reporter TEXT NOT NULL,
    problem TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
)
""")

conn.commit()

cursor.execute("""
DELETE FROM tickets
WHERE id = ''
""")

conn.commit()

print("=================================")
print("       IT SUPPORT SYSTEM")
print("=================================")

while True:
    print("1. Lihat Daftar Aset")
    print("2. Tambah Aset")
    print("3. Cari Aset")
    print("4. Buat Tiket Masalah")
    print("5. Lihat Tiket")
    print("6. Keluar")
    print("7. Update Aset")
    print("8. Hapus Aset")
    print("9. Update Status Tiket")
    print("10. Hapus Tiket")
    print("11. Cari Tiket")
    print("12. Dashboard")

    pilihan = input("Pilih menu: ").strip()

    if pilihan == "1":
        print("\nDaftar Aset IT")
        print("---------------------------------")

        assets_data = get_all_assets(conn)

        if assets_data:
            for asset in assets_data:
                print(asset[0], "|", asset[1], "|", asset[2], "|", asset[3])
        else:
            print("Belum ada aset.")

    elif pilihan == "2":
        print("\nTambah Aset IT")
        print("---------------------------------")

        asset_id = input("Masukkan ID aset: ").strip()
        if asset_id == "":
            print("ID aset tidak boleh kosong.")
            continue

        cursor.execute("SELECT id FROM assets WHERE id = ?", (asset_id,))
        if cursor.fetchone():
            print("ID aset sudah digunakan.")
            continue

        device = input("Masukkan jenis perangkat: ").strip()
        if device == "":
            print("Jenis perangkat tidak boleh kosong.")
            continue

        user = input("Masukkan nama pengguna: ").strip()
        if user == "":
            print("Nama pengguna tidak boleh kosong.")
            continue

        status = input("Masukkan status aset: ").strip()
        if status == "":
            print("Status aset tidak boleh kosong.")
            continue

        try:
            add_asset(conn, asset_id, device, user, status)
            print("\nAset berhasil disimpan ke database!")
        except sqlite3.IntegrityError:
            print("\nID aset sudah digunakan.")

    elif pilihan == "3":
        print("\nCari Aset IT")
        print("---------------------------------")

        search_id = input("Masukkan ID aset: ").strip()

        asset = get_asset_by_id(conn, search_id)

        if asset:
            print("\nAset ditemukan!")
            print("ID       :", asset[0])
            print("Perangkat:", asset[1])
            print("Pengguna :", asset[2])
            print("Status   :", asset[3])
        else:
            print("\nAset tidak ditemukan.")

    elif pilihan == "4":
        print("\nBuat Tiket Masalah")
        print("---------------------------------")

        ticket_id = input("Masukkan ID tiket: ").strip()
        if ticket_id == "":
            print("ID tiket tidak boleh kosong.")
            continue

        asset_id = input("Masukkan ID aset: ").strip()
        if asset_id == "":
            print("ID aset tidak boleh kosong.")
            continue

        cursor.execute("SELECT 1 FROM assets WHERE id = ?", (asset_id,))
        if not cursor.fetchone():
            print("\nID aset tidak ditemukan.")
            continue

        cursor.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,))
        if cursor.fetchone():
            print("ID tiket sudah digunakan.")
            continue

        reporter = input("Masukkan nama pelapor: ").strip()
        if reporter == "":
            print("Nama pelapor tidak boleh kosong.")
            continue

        problem = input("Masukkan masalah: ").strip()
        if problem == "":
            print("Masalah tidak boleh kosong.")
            continue

        add_ticket(
            conn,
            ticket_id,
            asset_id,
            reporter,
            problem,
            "Open"
        )

        print("\nTiket berhasil dibuat!")

    elif pilihan == "5":
        print("\nDaftar Tiket Masalah")
        print("---------------------------------")

        tickets_data = get_all_tickets(conn)

        if tickets_data:
            for ticket in tickets_data:
                print(
                    ticket[0],
                    "| Aset:", ticket[1],
                    "| Perangkat:", ticket[2],
                    "| Pelapor:", ticket[3],
                    "| Masalah:", ticket[4],
                    "| Status:", ticket[5]
                )
        else:
            print("Belum ada tiket.")

    elif pilihan == "6":
        print("Program selesai.")
        break

    elif pilihan == "7":
        print("\nUpdate Aset IT")
        print("---------------------------------")

        asset_id = input("Masukkan ID aset: ").strip()
        if asset_id == "":
            print("ID aset tidak boleh kosong.")
            continue

        cursor.execute("SELECT 1 FROM assets WHERE id = ?", (asset_id,))
        if not cursor.fetchone():
            print("\nAset tidak ditemukan.")
            continue

        new_status = input("Masukkan status baru: ").strip()
        if new_status == "":
            print("Status baru tidak boleh kosong.")
            continue

        result = update_asset_status(
            conn,
            asset_id,
            new_status
        )

        if result > 0:
            print("\nAset berhasil diperbarui!")
        else:
            print("\nAset tidak ditemukan.")

    elif pilihan == "8":
        print("\nHapus Aset IT")
        print("---------------------------------")

        asset_id = input("Masukkan ID aset yang ingin dihapus: ").strip()
        if asset_id == "":
            print("ID aset tidak boleh kosong.")
            continue

        cursor.execute("SELECT 1 FROM assets WHERE id = ?", (asset_id,))
        if not cursor.fetchone():
            print("\nAset tidak ditemukan.")
            continue

        result = delete_asset(conn, asset_id)

        if result > 0:
            print("\nAset berhasil dihapus!")
        else:
            print("\nAset tidak ditemukan.")


    elif pilihan == "9":
        print("\nUpdate Status Tiket")
        print("---------------------------------")

        ticket_id = input("Masukkan ID tiket: ").strip()
        if ticket_id == "":
            print("ID tiket tidak boleh kosong.")
            continue

        cursor.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,))
        if not cursor.fetchone():
            print("\nTiket tidak ditemukan.")
            continue

        new_status = input("Masukkan status baru (Open/In Progress/Resolved): ").strip()

        if new_status == "":
            print("Status baru tidak boleh kosong.")
            continue

        allowed_status = ["Open", "In Progress", "Resolved"]

        if new_status not in allowed_status:
            print("Status tidak valid.")
            print("Gunakan: Open, In Progress, atau Resolved.")
            continue

        result = update_ticket_status(
            conn,
            ticket_id,
            new_status
        )

        if result > 0:
            print("\nStatus tiket berhasil diperbarui!")
        else:
            print("\nGagal memperbarui status tiket.")

    elif pilihan == "10":
        print("\nHapus Tiket")
        print("---------------------------------")

        ticket_id = input("Masukkan ID tiket yang ingin dihapus: ").strip()
        if ticket_id == "":
            print("ID tiket tidak boleh kosong.")
            continue

        cursor.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,))
        if not cursor.fetchone():
            print("\nTiket tidak ditemukan.")
            continue

        result = delete_ticket(conn, ticket_id)

        if result > 0:
            print("\nTiket berhasil dihapus!")
        else:
            print("\nGagal menghapus tiket.")

    elif pilihan == "11":
        print("\nCari Tiket Masalah")
        print("---------------------------------")

        search_id = input("Masukkan ID tiket: ").strip()

        ticket = get_ticket_by_id(conn, ticket_id)

        if ticket:
            print("\nTiket ditemukan!")
            print("ID       :", ticket[0])
            print("Aset     :", ticket[1])
            print("Pelapor  :", ticket[2])
            print("Masalah  :", ticket[3])
            print("Status   :", ticket[4])
        else:
            print("\nTiket tidak ditemukan.")

    elif pilihan == "12":
        print("\n=================================")
        print("           DASHBOARD")
        print("=================================")

        dashboard = get_dashboard_data(conn)

        print("\n--- ASSET SUMMARY ---")
        print(f"Total Aset       : {dashboard['total_assets']}")
        print(f"Aset Active      : {dashboard['active_assets']}")
        print(f"Aset Maintenance : {dashboard['maintenance_assets']}")

        print("\n--- TICKET SUMMARY ---")
        print(f"Total Tiket      : {dashboard['total_tickets']}")
        print(f"Tiket Open       : {dashboard['open_tickets']}")
        print(f"Tiket In Progress: {dashboard['in_progress_tickets']}")
        print(f"Tiket Resolved   : {dashboard['resolved_tickets']}")

    else:
        print("Pilihan tidak tersedia.")

conn.close()