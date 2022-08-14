from time import time

from eme.data_access import RepositoryBase


class UserRepositoryBase(RepositoryBase):

    def find_by_username(self, username):
        return self.session.query(self.T)\
            .filter(self.T.username == username)\
        .first()

    def find_by_token(self, token):
        return self.session.query(self.T)\
            .filter(self.T.access_token == token)\
        .first()

    def delete_inactive(self):
        self.session.query(self.T)\
            .filter(self.T.last_active + 14*24*3600 < time())\
        .delete(synchronize_session=False)
        self.session.commit()

    def create(self, ent, commit=True):
        user = self.session.query(self.T).filter(self.T.uid == ent.uid).first()
        if user is not None:
            self.session.delete(user)
            self.session.commit()

        super().create(ent, commit)
