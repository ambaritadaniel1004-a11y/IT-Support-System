import sqlite3
from datetime import datetime, timedelta


DB_NAME = "assets.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# =========================================================
# FORMAT CREATED AT
# =========================================================

def format_created_at(created_at):
    """
    Convert SQLite UTC timestamp to WITA (UTC+8)
    and format it for display.
    """

    if not created_at:
        return "-"

    try:
        utc_time = datetime.strptime(
            created_at,
            "%Y-%m-%d %H:%M:%S"
        )

        wita_time = utc_time + timedelta(hours=8)

        return wita_time.strftime(
            "%d %b %Y, %H:%M"
        )

    except ValueError:
        return created_at


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database(conn):

    cursor = conn.cursor()


    # ---------------------------------------------
    # ASSETS TABLE
    # ---------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        device TEXT NOT NULL,
        user TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)


    # ---------------------------------------------
    # TICKETS TABLE
    # ---------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id TEXT PRIMARY KEY,
        asset_id TEXT NOT NULL,
        reporter TEXT NOT NULL,
        problem TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (asset_id)
            REFERENCES assets(id)
            ON DELETE CASCADE
    )
    """)


    # ---------------------------------------------
    # DATABASE MIGRATION
    # ---------------------------------------------

    cursor.execute(
        "PRAGMA table_info(tickets)"
    )

    columns = [
        column[1]
        for column in cursor.fetchall()
    ]


    if "created_at" not in columns:

        cursor.execute(
            "ALTER TABLE tickets ADD COLUMN created_at TEXT"
        )

        cursor.execute("""
        UPDATE tickets
        SET created_at = datetime('now')
        WHERE created_at IS NULL
        """)


    conn.commit()


# =========================================================
# SEED ASSETS
# =========================================================

def seed_assets(conn):

    cursor = conn.cursor()


    cursor.execute("""
    INSERT OR IGNORE INTO assets (
        id,
        device,
        user,
        status
    )
    VALUES (?, ?, ?, ?)
    """, (
        "IT001",
        "Laptop",
        "Andi",
        "Active"
    ))


    cursor.execute("""
    INSERT OR IGNORE INTO assets (
        id,
        device,
        user,
        status
    )
    VALUES (?, ?, ?, ?)
    """, (
        "IT002",
        "Monitor",
        "Budi",
        "Active"
    ))


    cursor.execute("""
    INSERT OR IGNORE INTO assets (
        id,
        device,
        user,
        status
    )
    VALUES (?, ?, ?, ?)
    """, (
        "IT003",
        "Printer",
        "Citra",
        "Maintenance"
    ))


    conn.commit()


# =========================================================
# ASSET - READ
# =========================================================

def get_all_assets(conn):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM assets
    ORDER BY id
    """)

    return cursor.fetchall()


def get_asset_by_id(conn, asset_id):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM assets WHERE id = ?",
        (asset_id,)
    )

    return cursor.fetchone()


def asset_exists(conn, asset_id):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM assets WHERE id = ?",
        (asset_id,)
    )

    return cursor.fetchone() is not None


# =========================================================
# ASSET - CREATE
# =========================================================

def add_asset(
    conn,
    asset_id,
    device,
    user,
    status
):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO assets (
        id,
        device,
        user,
        status
    )
    VALUES (?, ?, ?, ?)
    """, (
        asset_id,
        device,
        user,
        status
    ))

    conn.commit()


# =========================================================
# ASSET - UPDATE
# =========================================================

def update_asset_status(
    conn,
    asset_id,
    new_status
):

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE assets
        SET status = ?
        WHERE id = ?
        """,
        (
            new_status,
            asset_id
        )
    )

    conn.commit()

    return cursor.rowcount


# =========================================================
# ASSET - DELETE
# =========================================================

def delete_asset(
    conn,
    asset_id
):

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM assets
        WHERE id = ?
        """,
        (asset_id,)
    )

    conn.commit()

    return cursor.rowcount


# =========================================================
# ASSET - SEARCH
# =========================================================

def search_assets(
    conn,
    keyword
):

    cursor = conn.cursor()

    search_pattern = f"%{keyword}%"


    cursor.execute("""
    SELECT *
    FROM assets
    WHERE id LIKE ?
       OR device LIKE ?
       OR user LIKE ?
       OR status LIKE ?
    ORDER BY id
    """, (
        search_pattern,
        search_pattern,
        search_pattern,
        search_pattern
    ))


    return cursor.fetchall()


# =========================================================
# TICKET - CREATE
# =========================================================

def add_ticket(
    conn,
    ticket_id,
    asset_id,
    reporter,
    problem,
    status
):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tickets (
        id,
        asset_id,
        reporter,
        problem,
        status,
        created_at
    )
    VALUES (
        ?,
        ?,
        ?,
        ?,
        ?,
        datetime('now')
    )
    """, (
        ticket_id,
        asset_id,
        reporter,
        problem,
        status
    ))

    conn.commit()


# =========================================================
# TICKET - EXISTENCE
# =========================================================

def ticket_exists(
    conn,
    ticket_id
):

    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM tickets WHERE id = ?",
        (ticket_id,)
    )

    return cursor.fetchone() is not None


# =========================================================
# TICKET - READ ALL
# =========================================================

def get_all_tickets(conn):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        tickets.id,
        tickets.asset_id,
        assets.device,
        tickets.reporter,
        tickets.problem,
        tickets.status,
        tickets.created_at

    FROM tickets

    JOIN assets
        ON tickets.asset_id = assets.id

    ORDER BY tickets.id
    """)


    tickets = cursor.fetchall()

    formatted_tickets = []


    for ticket in tickets:

        formatted_ticket = (
            ticket[:6]
            + (
                format_created_at(
                    ticket[6]
                ),
            )
        )

        formatted_tickets.append(
            formatted_ticket
        )


    return formatted_tickets


# =========================================================
# TICKET - READ BY ID
# =========================================================

def get_ticket_by_id(
    conn,
    ticket_id
):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        tickets.id,
        tickets.asset_id,
        assets.device,
        tickets.reporter,
        tickets.problem,
        tickets.status,
        tickets.created_at

    FROM tickets

    JOIN assets
        ON tickets.asset_id = assets.id

    WHERE tickets.id = ?
    """, (
        ticket_id,
    ))


    ticket = cursor.fetchone()


    if not ticket:
        return None


    return (
        ticket[:6]
        + (
            format_created_at(
                ticket[6]
            ),
        )
    )


# =========================================================
# TICKET - FILTER BY STATUS
# =========================================================

def get_tickets_by_status(
    conn,
    status
):

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        tickets.id,
        tickets.asset_id,
        assets.device,
        tickets.reporter,
        tickets.problem,
        tickets.status,
        tickets.created_at

    FROM tickets

    JOIN assets
        ON tickets.asset_id = assets.id

    WHERE tickets.status = ?

    ORDER BY tickets.id
    """, (
        status,
    ))


    tickets = cursor.fetchall()

    formatted_tickets = []


    for ticket in tickets:

        formatted_ticket = (
            ticket[:6]
            + (
                format_created_at(
                    ticket[6]
                ),
            )
        )

        formatted_tickets.append(
            formatted_ticket
        )


    return formatted_tickets


# =========================================================
# TICKET - UPDATE
# =========================================================

def update_ticket_status(
    conn,
    ticket_id,
    new_status
):

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tickets
        SET status = ?
        WHERE id = ?
        """,
        (
            new_status,
            ticket_id
        )
    )

    conn.commit()

    return cursor.rowcount


# =========================================================
# TICKET - DELETE
# =========================================================

def delete_ticket(
    conn,
    ticket_id
):

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tickets
        WHERE id = ?
        """,
        (
            ticket_id,
        )
    )

    conn.commit()

    return cursor.rowcount


# =========================================================
# DASHBOARD
# =========================================================

def get_dashboard_data(conn):

    cursor = conn.cursor()


    # ---------------------------------------------
    # ASSETS
    # ---------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM assets"
    )

    total_assets = cursor.fetchone()[0]


    cursor.execute("""
    SELECT COUNT(*)
    FROM assets
    WHERE status = 'Active'
    """)

    active_assets = cursor.fetchone()[0]


    cursor.execute("""
    SELECT COUNT(*)
    FROM assets
    WHERE status = 'Maintenance'
    """)

    maintenance_assets = cursor.fetchone()[0]


    # ---------------------------------------------
    # TICKETS
    # ---------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM tickets"
    )

    total_tickets = cursor.fetchone()[0]


    cursor.execute("""
    SELECT COUNT(*)
    FROM tickets
    WHERE status = 'Open'
    """)

    open_tickets = cursor.fetchone()[0]


    cursor.execute("""
    SELECT COUNT(*)
    FROM tickets
    WHERE status = 'In Progress'
    """)

    in_progress_tickets = cursor.fetchone()[0]


    cursor.execute("""
    SELECT COUNT(*)
    FROM tickets
    WHERE status = 'Resolved'
    """)

    resolved_tickets = cursor.fetchone()[0]


    return {
        "total_assets": total_assets,
        "active_assets": active_assets,
        "maintenance_assets": maintenance_assets,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets
    }