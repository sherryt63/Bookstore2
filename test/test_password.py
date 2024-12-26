import uuid
import pytest
from fe.access import auth
from fe import conf

class TestPassword:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        # register a user
        self.user_id = "test_password_{}".format(str(uuid.uuid1()))
        self.old_password = "old_password_" + self.user_id
        self.terminal = "terminal_" + self.user_id

        assert self.auth.register(self.user_id, self.old_password) == 200
        yield

    def test_login_with_correct_credentials(self):
        code, new_token = self.auth.login(
            self.user_id, self.old_password, self.terminal
        )
        assert code == 200

        code = self.auth.logout(self.user_id, new_token)
        assert code == 200

    def test_error_login_with_incorrect_password(self):
        code, new_token = self.auth.login(
            self.user_id, self.old_password + "_x", self.terminal
        )
        assert code != 200

    def test_error_login_with_nonexistent_user(self):
        code = self.auth.login(
            self.user_id + "_x", self.old_password, self.terminal
        )
        assert code != 200
