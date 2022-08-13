import logging
from flask import redirect, render_template, request, url_for, flash
from flask import current_app as app
from flask_login import login_required, current_user

from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.user import User
from cryptoadvance.specter.wallet import Wallet
from .service import FaucetService


logger = logging.getLogger(__name__)

faucet_endpoint = FaucetService.blueprint

def ext() -> FaucetService:
    ''' convenience for getting the extension-object'''
    return app.specter.ext["faucet"]

def specter() -> Specter:
    ''' convenience for getting the specter-object'''
    return app.specter


@faucet_endpoint.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = app.specter.user_manager.get_user()
    available = 0
    addr = ""
    show_menu = FaucetService.id in user.services
    try:
        rpc = app.specter.rpc.listwallets()
        if "" not in rpc:
            try:
                app.specter.rpc.loadwallet("")
            except:
                app.specter.rpc.createwallet("")
        w = app.specter.rpc.wallet()
        available = w.getbalances().get("mine", {}).get("trusted", 0)
        addr = w.getnewaddress()
        # automatically bootstrap blockchain to 101 blocks
        if available == 0:
            blockcount = w.getblockcount()
            if blockcount < 100:
                w.generatetoaddress(101-blockcount, addr)
                available = w.getbalances().get("mine", {}).get("trusted", 0)
        if request.method == "POST":
            action = request.form["action"]
            if action == "settings":
                show_menu = request.form.get("show_menu")
                if show_menu:
                    user.add_service(FaucetService.id)
                else:
                    user.remove_service(FaucetService.id)
            elif action == "generate":
                numblocks = int(request.form.get("numblocks", 1))
                w.generatetoaddress(numblocks, addr)
                flash(f"{numblocks} blocks generated")
            elif action == "fund":
                amount = float(request.form["amount"])
                fundaddr = request.form["address"]
                w.sendtoaddress(fundaddr, amount)
                # w.generatetoaddress(1, addr)
                flash(f"Sent {amount} BTC to {fundaddr}")
            else:
                flash(f"Wrong action {action}", "error")
    except Exception as e:
        flash(f"Failed to reach default wallet: {e}", "error")
    return render_template(
        "faucet/index.jinja",
        available=available,
        addr=addr,
        show_menu=show_menu
    )

