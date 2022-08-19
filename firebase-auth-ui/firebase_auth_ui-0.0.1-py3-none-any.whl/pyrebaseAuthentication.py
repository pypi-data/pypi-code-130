import logging
import pyrebase
import os

# pip install pyrebase4




class FirebaseAuthenticationAPI:
    def __init__(self):
        self.user_email = ""
        self.user_password = ""

    def initialize_firebase(self, firebase_config):
        global firebase
        global auth
        firebase = pyrebase.initialize_app(firebase_config)

        # Initialize authentication
        auth = firebase.auth()


    def sign_up(self, user_email, user_password, display_name=""):
        print("Signing Up")
        try:
            user = auth.create_user_with_email_and_password(user_email, user_password, display_name)
            id_token = auth.get_account_info(user["idToken"])

            users_information = id_token["users"][0]
            email_verified = users_information["emailVerified"]

            self.send_email_verification(user["idToken"])
            return email_verified, users_information, id_token
        except Exception:
            # logging.exception(Exception)
            print("Invalid email/email already exists.")
            return False

    def sign_in(self, user_email, user_password):
        print("Signing In")
        try:
            user = auth.sign_in_with_email_and_password(user_email, user_password)
            id_token = auth.get_account_info(user["idToken"])

            users_information = id_token["users"][0]
            email_verified = users_information["emailVerified"]

            sign_in_complete = True

            local_id = auth.get_account_info(user["idToken"])["users"][0]["localId"]
            print("Successfully signed in.")

            return sign_in_complete, email_verified, local_id, user["displayName"]

        except Exception:
            sign_in_complete = False
            email_verified = False
            print("Invalid email and password combination/No account found.")
            return sign_in_complete, email_verified, None, None

    def check_email_verified_status(self, user_email, user_password):
        return self.sign_in(user_email, user_password)

    def send_email_verification(self, id_token):
        print("Sending a verification link to email.")
        auth.send_email_verification(id_token)
        print("Verification link is sent.")

    def send_email_verification_again(self, user_email, user_password):
        resend_successful = ""
        try:
            user = auth.sign_in_with_email_and_password(user_email, user_password)
            id_token = auth.get_account_info(user["idToken"])

            users_information = id_token["users"][0]
            email_verified = users_information["emailVerified"]

            if email_verified:
                email_verification = True

                print("Your email is already verified.")
                resend_successful = "already verified"

                return resend_successful
                # return email_verification
            else:
                self.send_email_verification(user["idToken"])
                resend_successful = "sent"
                print("Email verification link is sent.")
                return resend_successful

        except Exception:
            resend_successful = "error"
            # logging.exception(Exception)
            print("Invalid email and password combination/No account found/Too many attempts. "
                  "\nTry resending the email verification link after a while.")
            return resend_successful

    def reset_password(self, user_email):
        try:
            user = auth.send_password_reset_email(user_email)
            print("Password reset link is sent to the email.")
            return True
        except Exception:
            # logging.exception(Exception)
            return False

    # Save user information in the system after login
    # Call this method when login
    def register_authentication_in_system(self, user_email, user_password):
        signed_in_info = self.check_email_verified_status(user_email, user_password)
        sign_in_complete, email_verified, local_id, display_name = signed_in_info

        # Creating a folder inside C:\ProgramData
        make_directory_path = "C:\ProgramData\Firebase Authentication API"
        if not os.path.exists(make_directory_path):
            os.makedirs(make_directory_path)
        else:
            print("Path already exists.")


        # Creating authentication file
        authentication_file_path = f"{make_directory_path}\FirebaseAuthentication.txt"
        authentication = open(authentication_file_path, "w")

        if email_verified:
            authentication.write(f"User's Local ID: {local_id}\nUser's Name: {display_name}")
            authentication.close()
        else:
            authentication.write(f"User's Local ID: INVALID\nUser's Name: {display_name}")

        authentication.close()

        return sign_in_complete, email_verified, local_id, display_name

    # Check authentication. If authentication return sign_in_success is True then open tha main app.
    # If sign_in_success is False, that means email verification is not complete.
    def check_authentication(self):
        try:
            read_authentication = open("C:\ProgramData\Firebase Authentication API\FirebaseAuthentication.txt", "r")
            read_authentication_data = read_authentication.read().splitlines()
            local_id = read_authentication_data[0][17:]
            display_name = read_authentication_data[1][13:]

            if local_id == "INVALID":
                sign_in_success = False
            elif local_id == "":
                sign_in_success = False
            else:
                sign_in_success = True

            read_authentication.close()
            return local_id, display_name, sign_in_success
        except Exception:
            print("No authentication file found.")
            return False, False, False

    def logout(self):
        try:
            clear_authentication = open("C:\ProgramData\Firebase Authentication API\FirebaseAuthentication.txt", "w")
            local_id = ""
            display_name = ""
            clear_authentication.write(f"User's Local ID: {local_id}\nUser's Name: {display_name}")
            clear_authentication.close()
        except Exception:
            print("Failed to remove authentication information from authentication file")
            # logging.exception(Exception)

