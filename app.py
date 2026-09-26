import sqlite3
import re

from flask import Flask, render_template, request, redirect, url_for, flash

from database import (
    get_connection,
    initialize_database,
    seed_assets,
    get_all_assets,
    get_dashboard_data,
    get_all_tickets,
    get_tickets_by_status,
    add_asset,
    add_ticket,
    search_assets,
    ticket_exists,
    asset_exists,
    update_asset_status,
    delete_asset,
    update_ticket_status,
    delete_ticket,
    get_ticket_by_id,
)


app = Flask(__name__)

app.secret_key = "it-support-system-secret"


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    conn = get_connection()

    assets = get_all_assets(conn)

    dashboard = get_dashboard_data(conn)

    if dashboard["total_assets"] > 0:

        dashboard["active_percent"] = round(
            dashboard["active_assets"]
            / dashboard["total_assets"]
            * 100
        )

    else:

        dashboard["active_percent"] = 0

    tickets = get_all_tickets(conn)

    conn.close()

    return render_template(
        "index.html",
        assets=assets,
        dashboard=dashboard,
        tickets=tickets,
    )


# =========================================================
# ADD TICKET
# =========================================================

@app.route("/tickets/add", methods=["GET", "POST"])
def add_ticket_page():

    conn = get_connection()

    if request.method == "POST":

        ticket_id = request.form.get(
            "ticket_id",
            ""
        ).strip()

        asset_id = request.form.get(
            "asset_id",
            ""
        ).strip()

        reporter = request.form.get(
            "reporter",
            ""
        ).strip()

        problem = request.form.get(
            "problem",
            ""
        ).strip()


        # ---------------------------------------------
        # VALIDASI TICKET ID
        # Format: T001
        # ---------------------------------------------

        if not re.fullmatch(
            r"T\d{3}",
            ticket_id
        ):

            flash(
                "ID tiket harus menggunakan format seperti T001.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        # ---------------------------------------------
        # VALIDASI ASSET ID
        # Format: IT001
        # ---------------------------------------------

        if not re.fullmatch(
            r"IT\d{3}",
            asset_id
        ):

            flash(
                "ID aset harus menggunakan format seperti IT001.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        # ---------------------------------------------
        # VALIDASI FIELD
        # ---------------------------------------------

        if not reporter:

            flash(
                "Nama pelapor wajib diisi.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        if not problem:

            flash(
                "Deskripsi masalah wajib diisi.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        # ---------------------------------------------
        # CEK DUPLIKAT TICKET
        # ---------------------------------------------

        if ticket_exists(
            conn,
            ticket_id
        ):

            flash(
                "ID tiket sudah digunakan.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        # ---------------------------------------------
        # CEK ASSET
        # ---------------------------------------------

        if not asset_exists(
            conn,
            asset_id
        ):

            flash(
                "ID aset tidak ditemukan.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        # ---------------------------------------------
        # SIMPAN TICKET
        # ---------------------------------------------

        try:

            add_ticket(
                conn,
                ticket_id,
                asset_id,
                reporter,
                problem,
                "Open"
            )

            flash(
                "Tiket berhasil dibuat.",
                "success"
            )

        except sqlite3.IntegrityError:

            flash(
                "Gagal membuat tiket. Data tiket tidak valid.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_ticket_page")
            )


        conn.close()

        return redirect(
            url_for("home")
        )


    # ---------------------------------------------
    # GET REQUEST
    # ---------------------------------------------

    assets = get_all_assets(conn)

    conn.close()

    return render_template(
        "add_ticket.html",
        assets=assets
    )


# =========================================================
# UPDATE TICKET STATUS
# =========================================================

@app.route(
    "/tickets/update/<ticket_id>",
    methods=["POST"]
)
def update_ticket_page(ticket_id):

    conn = get_connection()

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    # ---------------------------------------------
    # VALIDASI STATUS
    # ---------------------------------------------

    if not new_status:

        flash(
            "Status tiket wajib dipilih.",
            "error"
        )

        conn.close()

        return redirect(
            url_for("home")
        )


    allowed_status = [
        "Open",
        "In Progress",
        "Resolved"
    ]


    if new_status not in allowed_status:

        flash(
            "Status tiket tidak valid.",
            "error"
        )

        conn.close()

        return redirect(
            url_for("home")
        )


    # ---------------------------------------------
    # UPDATE STATUS
    # ---------------------------------------------

    row_count = update_ticket_status(
        conn,
        ticket_id,
        new_status
    )


    if row_count > 0:

        flash(
            "Status tiket berhasil diperbarui.",
            "success"
        )

    else:

        flash(
            "Tiket tidak ditemukan.",
            "error"
        )


    conn.close()

    return redirect(
        url_for("home")
    )


# =========================================================
# ADD ASSET
# =========================================================

@app.route(
    "/assets/add",
    methods=["GET", "POST"]
)
def add_asset_page():

    conn = get_connection()

    if request.method == "POST":

        asset_id = request.form.get(
            "asset_id",
            ""
        ).strip()

        device = request.form.get(
            "device",
            ""
        ).strip()

        user = request.form.get(
            "user",
            ""
        ).strip()

        status = request.form.get(
            "status",
            ""
        ).strip()


        # ---------------------------------------------
        # VALIDASI ASSET ID
        # Format: IT001
        # ---------------------------------------------

        if not re.fullmatch(
            r"IT\d{3}",
            asset_id
        ):

            flash(
                "ID aset harus menggunakan format seperti IT001.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        # ---------------------------------------------
        # VALIDASI DEVICE
        # ---------------------------------------------

        if not device:

            flash(
                "Jenis perangkat wajib diisi.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        # ---------------------------------------------
        # VALIDASI USER
        # ---------------------------------------------

        if not user:

            flash(
                "Nama pengguna wajib diisi.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        # ---------------------------------------------
        # VALIDASI STATUS
        # ---------------------------------------------

        if not status:

            flash(
                "Status aset wajib dipilih.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        allowed_status = [
            "Active",
            "Maintenance"
        ]


        if status not in allowed_status:

            flash(
                "Status aset tidak valid.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        # ---------------------------------------------
        # SIMPAN ASSET
        # ---------------------------------------------

        try:

            add_asset(
                conn,
                asset_id,
                device,
                user,
                status
            )

        except sqlite3.IntegrityError:

            flash(
                "ID aset sudah digunakan.",
                "error"
            )

            conn.close()

            return redirect(
                url_for("add_asset_page")
            )


        flash(
            "Aset berhasil ditambahkan.",
            "success"
        )

        conn.close()

        return redirect(
            url_for("home")
        )


    conn.close()

    return render_template(
        "add_asset.html"
    )


# =========================================================
# UPDATE ASSET STATUS
# =========================================================

@app.route(
    "/assets/update/<asset_id>",
    methods=["POST"]
)
def update_asset_page(asset_id):

    conn = get_connection()

    new_status = request.form.get(
        "status",
        ""
    ).strip()


    # ---------------------------------------------
    # VALIDASI STATUS
    # ---------------------------------------------

    if not new_status:

        flash(
            "Status aset wajib dipilih.",
            "error"
        )

        conn.close()

        return redirect(
            url_for("home")
        )


    allowed_status = [
        "Active",
        "Maintenance"
    ]


    if new_status not in allowed_status:

        flash(
            "Status aset tidak valid.",
            "error"
        )

        conn.close()

        return redirect(
            url_for("home")
        )


    # ---------------------------------------------
    # UPDATE STATUS
    # ---------------------------------------------

    row_count = update_asset_status(
        conn,
        asset_id,
        new_status
    )


    if row_count > 0:

        flash(
            "Status aset berhasil diperbarui.",
            "success"
        )

    else:

        flash(
            "Aset tidak ditemukan.",
            "error"
        )


    conn.close()

    return redirect(
        url_for("home")
    )


# =========================================================
# DELETE ASSET
# =========================================================

@app.route(
    "/assets/delete/<asset_id>",
    methods=["POST"]
)
def delete_asset_page(asset_id):

    conn = get_connection()

    row_count = delete_asset(
        conn,
        asset_id
    )


    if row_count > 0:

        flash(
            "Aset berhasil dihapus.",
            "success"
        )

    else:

        flash(
            "Aset tidak ditemukan.",
            "error"
        )


    conn.close()

    return redirect(
        url_for("home")
    )


# =========================================================
# DELETE TICKET
# =========================================================

@app.route(
    "/tickets/delete/<ticket_id>",
    methods=["POST"]
)
def delete_ticket_page(ticket_id):

    conn = get_connection()

    row_count = delete_ticket(
        conn,
        ticket_id
    )


    if row_count > 0:

        flash(
            "Tiket berhasil dihapus.",
            "success"
        )

    else:

        flash(
            "Tiket tidak ditemukan.",
            "error"
        )


    conn.close()

    return redirect(
        url_for("home")
    )


# =========================================================
# SEARCH TICKET
# =========================================================

@app.route(
    "/tickets/search",
    methods=["GET"]
)
def search_ticket_page():

    conn = get_connection()

    ticket_id = request.args.get(
        "ticket_id",
        ""
    ).strip()

    ticket = None


    if ticket_id:

        ticket = get_ticket_by_id(
            conn,
            ticket_id
        )


    conn.close()

    return render_template(
        "search_ticket.html",
        ticket=ticket,
        ticket_id=ticket_id
    )


# =========================================================
# SEARCH ASSET
# =========================================================

@app.route(
    "/assets/search",
    methods=["GET"]
)
def search_asset_page():

    conn = get_connection()

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    assets = []


    if keyword:

        assets = search_assets(
            conn,
            keyword
        )


    conn.close()

    return render_template(
        "search_asset.html",
        assets=assets,
        keyword=keyword
    )


# =========================================================
# FILTER TICKETS
# =========================================================

@app.route(
    "/tickets/filter",
    methods=["GET"]
)
def filter_tickets_page():

    conn = get_connection()

    status = request.args.get(
        "status",
        ""
    ).strip()

    tickets = []


    if status:

        allowed_status = [
            "Open",
            "In Progress",
            "Resolved"
        ]


        if status in allowed_status:

            tickets = get_tickets_by_status(
                conn,
                status
            )


    conn.close()

    return render_template(
        "filter_ticket.html",
        tickets=tickets,
        status=status
    )


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    conn = get_connection()

    initialize_database(conn)

    seed_assets(conn)

    conn.close()

    app.run(
        debug=True
    )