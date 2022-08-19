import logging
from tkinter import Tk
from tkinter import *
from pyrebaseAuthentication import FirebaseAuthenticationAPI
from tkinterLoginUI import DrawAuthentication


def my_app(user_name):
    # Put your whole Tkinter app inside this function
    root = Tk()
    root.title("My App")
    root.geometry("800x540")
    root.config(bg="#23241f")

    def logout():
        try:
            user = FirebaseAuthenticationAPI()
            root.destroy()
            user.logout()
            authentication_to_enter_the_app()
        except Exception:
            print("Failed to log out.")
            # logging.exception(Exception)

    user_name_label = Label(root,
                            text=f"Hi, {user_name}!",
                            height=2,
                            bg="#3e3c32",
                            foreground="white",
                            font=("Helvetica", 20)
                            )
    user_name_label.pack(fill=BOTH)

    logout_button = Button(root,
                           bg="#584b3e",
                           text="Log out",
                           border=0,
                           foreground="white",
                           command=logout,
                           font=("Helvetica", 20)
                           )
    logout_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    root.mainloop()
    print("Authentication Complete. Your app is running.")


# Get your firebase config credentials from your Firebase project console
# Put all your values here from your Firebase project
# Don't need to put values of databaseURL key, just keep it "" empty string, but don't remove the key from
# firebase_config_values
firebase_config_values = {
            "apiKey": "Put values",
            "authDomain": "Put values",
            "projectId": "Put values",
            "storageBucket": "Put values",
            "messagingSenderId": "Put values",
            "appId": "Put values",
            "measurementId": "Put values",
            "databaseURL": ""
        }

firebaseAuth = FirebaseAuthenticationAPI()
firebaseAuth.initialize_firebase(firebase_config_values)

def test_app():
    read_authentication = firebaseAuth.check_authentication()
    uui, display_name, signed_in = read_authentication

    if not signed_in:
        login = DrawAuthentication()
        login.drawLogin()

        if login.authentication_success and login.authentication_email_verified and login.authentication_correct_email_password:
            uui, display_name, signed_in = firebaseAuth.check_authentication()
            # Call App Function
            my_app(display_name)
    else:
        # Call App Function
        my_app(display_name)
