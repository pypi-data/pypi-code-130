from flask import url_for, render_template, request
from flask_login import current_user, logout_user, login_required, login_user
from werkzeug.utils import redirect

from eme.data_access import get_repo

from ..dal.user_repository import UserRepositoryBase
from ..services import auth


class UsersController:
    def __init__(self, server, UserCls):
        self.server = server
        self.repo: UserRepositoryBase = get_repo(UserCls)
        self.route = ''

    @login_required
    def get_profile(self):
        return "l"

    def get_list(self):
        if not current_user.admin:
            return redirect(url_for('Home:welcome'))

        users = self.repo.list_all()

        return render_template('/users/list.html', users=users)

    @auth.login_forbidden
    def auth(self):
        if current_user.is_authenticated:
            return "already logged in"

        if 'code' in request.args:
            # 2nd step in authorization: authorization code provided
            code = request.args['code']
            state = request.args['state']

            # get access token
            access_token = auth.fetch_token(code)

            # todo: @later: handle all error cases

            # store user in DB
            user = auth.fetch_user(access_token)

            user.access_token = access_token

            self.repo.create(user)

            # we do not rely on access_token, but sessions for the web interface!
            login_user(user, remember=True)

            return redirect('/')

        return redirect(auth.get_authorize_url())

    def get_logout(self):
        logout_user()

        return redirect('/')