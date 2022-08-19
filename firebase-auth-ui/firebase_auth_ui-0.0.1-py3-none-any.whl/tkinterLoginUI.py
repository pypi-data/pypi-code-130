import logging

from pyrebaseAuthentication import FirebaseAuthenticationAPI
from tkinter import Tk
from tkinter import *
import urllib.request
from PIL import Image, ImageTk
import pyglet
from tkinter import scrolledtext
import webbrowser
import pygame
import pkg_resources

# Install these dependencies
# To install tkinter, please follow the latest installation process by checking their documentation on online
# pip install tk / pip install tkinter
# pip install pygame
# pip install Pillow
# pip install pyglet


def get_path(folder_name_str, file_name_str):
    file_resource = __name__
    file_path = '/'.join((folder_name_str, file_name_str))
    get_file_address = pkg_resources.resource_stream(file_resource, file_path).name
    return get_file_address

# Adding fonts
font_resource = __name__
font_path = '/'.join(('fonts', 'Quicksand_Bold.otf'))
get_font_address = pkg_resources.resource_stream(font_resource, font_path).name
pyglet.font.add_file(get_font_address)

def play_audio(click=False, email_sent=False, error=False):
    try:
        pygame.mixer.init()
    except:
        pass

    if click:
        try:
            click_resource = __name__
            click_path = '/'.join(('authenticationUI', 'clicks.mp3'))
            get_click_address = pkg_resources.resource_stream(click_resource, click_path).name

            pygame.mixer.music.load(get_click_address)
            pygame.mixer.music.play(loops=0)
        except:
            pass

    if email_sent:
        try:
            email_resource = __name__
            email_path = '/'.join(('authenticationUI', 'emailSent.mp3'))
            get_email_path = pkg_resources.resource_stream(email_resource, email_path).name

            pygame.mixer.music.load(get_email_path)
            pygame.mixer.music.play(loops=0)
        except:
            pass

    if error:
        try:
            error_resource = __name__
            error_path = '/'.join(('authenticationUI', 'error.mp3'))
            get_error_address = pkg_resources.resource_stream(error_resource, error_path).name

            pygame.mixer.music.load(get_error_address)
            pygame.mixer.music.play(loops=0)
        except:
            pass



class DrawAuthentication:
    def __init__(self):
        self.authentication_success = False
        self.authentication_email_verified = False
        self.authentication_correct_email_password = False

    def drawLogin(self):
        if not self.check_internet_connection():
            self.draw_no_internet()
            return

        try:
            root_sign_up.destroy()
        except:
            pass

        try:
            resend.destroy()
        except:
            pass

        try:
            reset_root.destroy()
        except:
            pass

        global root
        root = Tk()
        version = "1.0"
        root.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        root.geometry(window_string)
        root.minsize(window_x, window_y)
        root.maxsize(window_x, window_y)

        # root.iconbitmap("authenticationUI/anyIcon.ico")

        login_resource = __name__
        login_path = '/'.join(('authenticationUI', 'loginUI.png'))
        get_login_address = pkg_resources.resource_stream(login_resource, login_path).name

        main_ui = Image.open(get_login_address)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(root, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        global user_email
        global user_password

        user_email = Entry(root,
                           bg="#FCE3DF",
                           border=0,
                           highlightthickness=0,
                           font=("Quicksand Book", 14),
                           )
        user_email.pack()
        user_email.place(x=364,
                         y=200,
                         width=350,
                         height=50,
                         )

        user_password = Entry(root,
                              bg="#FCE3DF",
                              border=0,
                              highlightthickness=0,
                              font=("Quicksand Book", 20),
                              show="▰"
                              )
        user_password.pack()
        user_password.place(x=364,
                            y=294,
                            width=350,
                            height=50,
                            )

        sign_in_button = Button(root,
                                bg="#FCE3DF",
                                text="Sign in",
                                border=0,
                                font=("Quicksand Bold", 20),
                                activebackground="#FCE3DF",
                                command=self.firebase_login
                                )

        sign_in_button.place(x=570,
                             y=414,
                             width=192,
                             height=50,
                             )

        # Binding the enter key for sign in
        def call_firebase_login_on_enter_key_pressed(event):
            self.firebase_login()

        root.bind("<Return>", call_firebase_login_on_enter_key_pressed)

        sign_up_here_button = Button(root,
                                     bg="#FCE3DF",
                                     text="here",
                                     border=0,
                                     font=("Quicksand Bold", 10),
                                     activebackground="#FCE3DF",
                                     foreground="#F4509A",
                                     command=self.sign_up_draw
                                     )
        sign_up_here_button.place(x=544,
                                  y=388,
                                  width=34,
                                  height=20,
                                  )

        def mousePosition(mouse_xy):
            mouse_x = mouse_xy.x
            mouse_y = mouse_xy.y

            # print(f"x:{mouse_x}, y:{mouse_y}")

            if 356 <= mouse_x <= 480 and 412 <= mouse_y <= 426:
                self.draw_reset_password()

            # Change the url values according to your needs
            urls = {"yourApp": "http://google.com",
                    "facebook": "http://google.com",
                    "instagram": "http://google.com",
                    "website": "http://google.com",
                    "linkedin": "http://google.com",
                    "email": "mailto:yourEmail@demo.com"
                    }

            if 630 <= mouse_x <= 648 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["facebook"])
                print("Facebook")
            elif 660 <= mouse_x <= 678 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["instagram"])
                print("Instagram")
            elif 690 <= mouse_x <= 706 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["website"])
                print("Website")
            elif 720 <= mouse_x <= 736 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["linkedin"])
                print("Linkedin")
            elif 750 <= mouse_x <= 766 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["email"])
                print("Email")
            elif 8 <= mouse_x <= 128 and 510 <= mouse_y <= 520:
                webbrowser.open_new(urls["yourApp"])
                print("yourApp")

        root.bind("<Button 1>", mousePosition)

        root.mainloop()

    def firebase_login(self):
        get_user_email = user_email.get()
        get_user_password = user_password.get()

        firebase_user = FirebaseAuthenticationAPI()

        # Return sign_in_complete, email_verified, local_id, display_name
        sign_in_success = firebase_user.register_authentication_in_system(get_user_email, get_user_password)

        # Returns local_id, display_name, sign_in_success
        authentication = firebase_user.check_authentication()

        # sign_in = firebase_user.sign_in(get_user_email, get_user_password)
        # print(sign_in[0])

        if not sign_in_success[0]:
            self.authentication_success = False
            self.authentication_email_verified = False
            self.authentication_correct_email_password = False

            self.invalid_email_password_during_login()

        elif authentication[2]:
            self.authentication_success = True
            self.authentication_email_verified = True
            self.authentication_correct_email_password = True
            print("Open App")
            root.destroy()
            return self.authentication_success, self.authentication_email_verified, self.authentication_correct_email_password


        elif not sign_in_success[1]:
            self.authentication_success = False
            self.authentication_email_verified = False
            self.authentication_correct_email_password = True
            print("Authentication Failed.")

            self.authentication_failed_message()

    def authentication_failed_message(self):
        play_audio(error=True)
        global authentication_message

        try:
            invalid_email_password_message.destroy()
        except:
            pass

        authentication_message = Label(root,
                                       text="Email is not verified! Check your email.",
                                       foreground="red",
                                       background="#FCE3DF",
                                       font=("Quicksand Book", 10),
                                       )

        authentication_message.place(x=450,
                                     y=80,
                                     width=250,
                                     height=50,
                                     )

        verification_resend_button = Button(root,
                                            text="Not found? Resend",
                                            bg="#FCE3DF",
                                            border=0,
                                            font=("Quicksand Bold", 10),
                                            activebackground="#FCE3DF",
                                            foreground="#F4509A",
                                            command=self.draw_resend_email_verification
                                            )
        verification_resend_button.place(x=500,
                                         y=110,
                                         width=150,
                                         height=20
                                         )

    def invalid_email_password_during_login(self):
        global invalid_email_password_message

        try:
            authentication_message.destroy()
        except:
            pass

        play_audio(error=True)
        invalid_email_password_message = Label(root,
                                               text="Invalid email and password combination/No account found!",
                                               foreground="red",
                                               background="#FCE3DF",
                                               font=("Quicksand Book", 10),
                                               )

        invalid_email_password_message.place(x=360,
                                             y=80,
                                             width=400,
                                             height=44,
                                             )

    # Draw sign up ui
    def sign_up_draw(self):
        try:
            root.destroy()
        except:
            pass

        global root_sign_up
        root_sign_up = Tk()

        version = "1.0"
        root_sign_up.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = root_sign_up.winfo_screenwidth()
        screen_height = root_sign_up.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        root_sign_up.geometry(window_string)
        root_sign_up.minsize(window_x, window_y)
        root_sign_up.maxsize(window_x, window_y)

        # root_sign_up.iconbitmap("authenticationUI/anyIcon.ico")

        sign_up_ui_path = get_path("authenticationUI", "signUpUI.png")
        main_ui = Image.open(sign_up_ui_path)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(root_sign_up, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        global sign_up_full_name
        global sign_up_email
        global sign_up_password

        # Sign up name
        sign_up_full_name = Entry(root_sign_up,
                                  bg="#FCE3DF",
                                  border=0,
                                  highlightthickness=0,
                                  font=("Quicksand Book", 10),
                                  )
        sign_up_full_name.place(x=402,
                                y=184,
                                width=304,
                                height=28,
                                )

        # Sign up email
        sign_up_email = Entry(root_sign_up,
                              bg="#FCE3DF",
                              border=0,
                              highlightthickness=0,
                              font=("Quicksand Book", 10),
                              )
        sign_up_email.place(x=402,
                            y=242,
                            width=304,
                            height=28,
                            )

        # Sign up password
        sign_up_password = Entry(root_sign_up,
                                 bg="#FCE3DF",
                                 border=0,
                                 highlightthickness=0,
                                 font=("Quicksand Book", 10),
                                 show="▰"
                                 )
        sign_up_password.place(x=402,
                               y=300,
                               width=304,
                               height=28,
                               )

        sign_up_button = Button(root_sign_up,
                                bg="#FCE3DF",
                                text="Sign up",
                                border=0,
                                font=("Quicksand Bold", 20),
                                activebackground="#FCE3DF",
                                command=self.firebase_sign_up
                                )

        sign_up_button.place(x=570,
                             y=414,
                             width=192,
                             height=50,
                             )

        # Binding the enter key for sign up
        def call_firebase_sign_up_on_enter_key_pressed(event):
            self.firebase_sign_up()

        root_sign_up.bind("<Return>", call_firebase_sign_up_on_enter_key_pressed)

        already_have_account_button = Button(root_sign_up,
                                             bg="#FCE3DF",
                                             text="Log in",
                                             border=0,
                                             font=("Quicksand Bold", 10),
                                             activebackground="#FCE3DF",
                                             foreground="#F4509A",
                                             command=self.drawLogin
                                             )
        already_have_account_button.place(x=532,
                                          y=388,
                                          width=44,
                                          height=20,
                                          )

        # self.mousePositions(root_sign_up)

        def mouse(mouse_xy):
            mouse_x = mouse_xy.x
            mouse_y = mouse_xy.y

            # print(f"x:{mouse_x}, y:{mouse_y}")

            # Change the url values according to your needs
            urls = {"yourApp": "http://google.com",
                    "facebook": "http://google.com",
                    "instagram": "http://google.com",
                    "website": "http://google.com",
                    "linkedin": "http://google.com",
                    "email": "mailto:yourEmail@demo.com"
                    }

            if 630 <= mouse_x <= 648 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["facebook"])
                print("Facebook")
            elif 660 <= mouse_x <= 678 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["instagram"])
                print("Instagram")
            elif 690 <= mouse_x <= 706 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["website"])
                print("Website")
            elif 720 <= mouse_x <= 736 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["linkedin"])
                print("Linkedin")
            elif 750 <= mouse_x <= 766 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["email"])
                print("Email")
            elif 8 <= mouse_x <= 128 and 510 <= mouse_y <= 520:
                webbrowser.open_new(urls["yourApp"])
                print("yourApp")
            elif 384 <= mouse_x <= 544 and 344 <= mouse_y <= 356:
                self.draw_terms_and_condition()
                print("Terms and Condition")

        root_sign_up.bind("<Button 1>", mouse)

        root_sign_up.mainloop()

    def firebase_sign_up(self):
        get_name = sign_up_full_name.get()
        get_email = sign_up_email.get()
        get_password = sign_up_password.get()

        firebase_user = FirebaseAuthenticationAPI()
        sign_up = firebase_user.sign_up(user_email=get_email,
                                        user_password=get_password,
                                        display_name=get_name
                                        )

        if not sign_up:
            play_audio(error=True)
            error_message = "Invalid email/email already exists/password length is less than 6"
            message = Label(root_sign_up,
                            text=error_message,
                            foreground="red",
                            background="#FCE3DF",
                            font=("Quicksand Book", 10),
                            )

            message.place(x=300,
                          y=68,
                          width=480,
                          height=34,
                          )
        else:
            play_audio(email_sent=True)
            email_verification_message = "Email verification link is sent. " \
                                         "\nPlease check your email and don't miss to check the spam folder also."
            message = Label(root_sign_up,
                            text=email_verification_message,
                            foreground="#EC4E38",
                            background="#FCE3DF",
                            font=("Quicksand Bold", 10),
                            )

            message.place(x=300,
                          y=68,
                          width=480,
                          height=34,
                          )

    # Draw resend email verification
    def draw_resend_email_verification(self):
        try:
            root.destroy()
        except Exception:
            logging.exception(Exception)
            pass

        global resend
        resend = Tk()

        version = "1.0"
        resend.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = resend.winfo_screenwidth()
        screen_height = resend.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        resend.geometry(window_string)
        resend.minsize(window_x, window_y)
        resend.maxsize(window_x, window_y)

        # resend.iconbitmap("authenticationUI/anyIcon.ico")

        resend_ui_path = get_path("authenticationUI", "verifyEmail.png")
        main_ui = Image.open(resend_ui_path)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(resend, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        # Sign up email
        resend_email = Entry(resend,
                             bg="#FCE3DF",
                             border=0,
                             highlightthickness=0,
                             font=("Quicksand Book", 10),
                             )
        resend_email.place(x=402,
                           y=242,
                           width=304,
                           height=28,
                           )

        # Sign up password
        resend_password = Entry(resend,
                                bg="#FCE3DF",
                                border=0,
                                highlightthickness=0,
                                font=("Quicksand Book", 10),
                                show="▰"
                                )
        resend_password.place(x=402,
                              y=300,
                              width=304,
                              height=28,
                              )

        def resend_email_verification_error_message(resend_message):
            message = Label(resend,
                            text=resend_message,
                            foreground="#EC4E38",
                            background="#FCE3DF",
                            font=("Quicksand Bold", 10),
                            )

            message.place(x=300,
                          y=68,
                          width=480,
                          height=34,
                          )

        def resend_email_verification():
            user = FirebaseAuthenticationAPI()

            try:
                resend_info = user.send_email_verification_again(resend_email.get(), resend_password.get())
                if resend_info == "already verified":
                    play_audio(error=True)
                    resend_email_verification_error_message("Email is already verified!")
                elif resend_info == "sent":
                    play_audio(email_sent=True)
                    resend_email_verification_error_message("Verification link is sent your email. Please don't miss"
                                                            "to check spam also.")
                elif resend_info == "error":
                    play_audio(error=True)
                    resend_email_verification_error_message("Too many attempts! Try after a while.")
            except Exception:
                print("Resend email verification failed.")
                logging.exception(Exception)

        resend_button = Button(resend,
                               bg="#FCE3DF",
                               text="Resend",
                               border=0,
                               font=("Quicksand Bold", 20),
                               activebackground="#FCE3DF",
                               command=resend_email_verification
                               )

        resend_button.place(x=570,
                            y=414,
                            width=192,
                            height=50,
                            )

        already_verified_button = Button(resend,
                                         bg="#FCE3DF",
                                         text="Log in",
                                         border=0,
                                         font=("Quicksand Bold", 10),
                                         activebackground="#FCE3DF",
                                         foreground="#F4509A",
                                         command=self.drawLogin
                                         )
        already_verified_button.place(x=532,
                                      y=386,
                                      width=44,
                                      height=20,
                                      )

        # Binding the enter key for resend email verification
        def call_resend_email_verification_on_enter_key_pressed(event):
            resend_email_verification()

        resend.bind("<Return>", call_resend_email_verification_on_enter_key_pressed)

        self.mousePositions(resend)

        resend.mainloop()

    # Draw reset password
    def draw_reset_password(self):
        root.destroy()

        global reset_root
        reset_root = Tk()

        version = "1.0"
        reset_root.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = reset_root.winfo_screenwidth()
        screen_height = reset_root.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        reset_root.geometry(window_string)
        reset_root.minsize(window_x, window_y)
        reset_root.maxsize(window_x, window_y)

        # reset_root.iconbitmap("authenticationUI/anyIcon.ico")

        reset_ui_path = get_path("authenticationUI", "resetPassword.png")
        main_ui = Image.open(reset_ui_path)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(reset_root, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        # Email to reset password
        reset_password_user_email = Entry(reset_root,
                                          bg="#FCE3DF",
                                          border=0,
                                          highlightthickness=0,
                                          font=("Quicksand Book", 10),
                                          )
        reset_password_user_email.place(x=402,
                                        y=242,
                                        width=304,
                                        height=28,
                                        )

        def reset_password_message(resend_message):
            message = Label(reset_root,
                            text=resend_message,
                            foreground="#EC4E38",
                            background="#FCE3DF",
                            font=("Quicksand Bold", 10),
                            )

            message.place(x=300,
                          y=200,
                          width=480,
                          height=34,
                          )

        def reset_password():
            user = FirebaseAuthenticationAPI()
            reset_password_info = user.reset_password(reset_password_user_email.get())
            if reset_password_info:
                play_audio(email_sent=True)
                reset_password_message(f"Reset link is sent to {reset_password_user_email.get()}")
            else:
                play_audio(error=True)
                reset_password_message(f"No account found with this email {reset_password_user_email.get()}")

        # Reset Password button
        reset_password_button = Button(reset_root,
                                       bg="#FCE3DF",
                                       text="Reset",
                                       border=0,
                                       font=("Quicksand Bold", 20),
                                       activebackground="#FCE3DF",
                                       command=reset_password
                                       )

        reset_password_button.place(x=570,
                                    y=414,
                                    width=192,
                                    height=50,
                                    )

        # Remember password
        remember_password_button = Button(reset_root,
                                          bg="#FCE3DF",
                                          text="Log in",
                                          border=0,
                                          font=("Quicksand Bold", 10),
                                          activebackground="#FCE3DF",
                                          foreground="#F4509A",
                                          command=self.drawLogin
                                          )
        remember_password_button.place(x=532,
                                       y=386,
                                       width=44,
                                       height=20,
                                       )

        # Binding the enter key for reset password
        def call_reset_password_on_enter_key_pressed(event):
            reset_password()

        reset_root.bind("<Return>", call_reset_password_on_enter_key_pressed)

        # Calling mousePosition function for external link clicks
        self.mousePositions(reset_root)

        reset_root.mainloop()

    # Get mouse position for external links
    def mousePositions(self, root_name):
        # Change the url values according to your needs
        urls = {"yourApp": "http://google.com",
                "facebook": "http://google.com",
                "instagram": "http://google.com",
                "website": "http://google.com",
                "linkedin": "http://google.com",
                "email": "mailto:yourEmail@demo.com"
                }
        def get_mouse_position(mouse_xy):
            mouse_x = mouse_xy.x
            mouse_y = mouse_xy.y

            # print(f"x:{mouse_x}, y:{mouse_y}")

            if 630 <= mouse_x <= 648 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["facebook"])
                print("Facebook")
            elif 660 <= mouse_x <= 678 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["instagram"])
                print("Instagram")
            elif 690 <= mouse_x <= 706 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["website"])
                print("Website")
            elif 720 <= mouse_x <= 736 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["linkedin"])
                print("Linkedin")
            elif 750 <= mouse_x <= 766 and 500 <= mouse_y <= 520:
                webbrowser.open_new(urls["email"])
                print("Email")
            elif 8 <= mouse_x <= 128 and 510 <= mouse_y <= 520:
                webbrowser.open_new(urls["yourApp"])
                print("yourApp")

        root_name.bind("<Button 1>", get_mouse_position)

    # Check internet connection
    def check_internet_connection(self, host="http://google.com"):
        try:
            internet_root.destroy()
        except:
            pass

        try:
            urllib.request.urlopen(host)
            return True
        except:
            return False

    # Draw no internet
    def draw_no_internet(self):
        global internet_root
        internet_root = Tk()

        version = "1.0"
        internet_root.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = internet_root.winfo_screenwidth()
        screen_height = internet_root.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        internet_root.geometry(window_string)
        internet_root.minsize(window_x, window_y)
        internet_root.maxsize(window_x, window_y)

        # internet_root.iconbitmap("authenticationUI/anyIcon.ico")

        internet_ui_path = get_path("authenticationUI", "internetConnection.png")
        main_ui = Image.open(internet_ui_path)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(internet_root, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        play_audio(error=True)

        # Internet connection check again button
        check_connection_again_button = Button(internet_root,
                                               bg="#FCE3DF",
                                               text="Check again",
                                               border=0,
                                               font=("Quicksand Bold", 20),
                                               activebackground="#FCE3DF",
                                               command=self.drawLogin
                                               )
        check_connection_again_button.place(x=570,
                                            y=420,
                                            width=192,
                                            height=48,
                                            )

        # Binding the enter key for check connection again button
        def call_check_connection_again_on_enter_key_pressed(event):
            self.drawLogin()

        internet_root.bind("<Return>", call_check_connection_again_on_enter_key_pressed)

        internet_root.mainloop()

    # Draw terms and conditions
    def draw_terms_and_condition(self):
        try:
            root_sign_up.destroy()
        except:
            pass

        terms_root = Tk()

        version = "1.0"
        terms_root.title(f"User Authentication v{version}")

        window_x = 800
        window_y = 540

        screen_width = terms_root.winfo_screenwidth()
        screen_height = terms_root.winfo_screenheight()

        centered_x = int(screen_width / 2 - window_x / 2)
        centered_y = int(screen_height / 2 - window_y / 2)

        window_string = f"{window_x}x{window_y}+{centered_x}+{centered_y}"

        # Constant Windows size
        terms_root.geometry(window_string)
        terms_root.minsize(window_x, window_y)
        terms_root.maxsize(window_x, window_y)

        # terms_root.iconbitmap("authenticationUI/anyIcon.ico")

        terms_ui_path = get_path("authenticationUI", "terms.png")
        main_ui = Image.open(terms_ui_path)
        resize_main_ui = main_ui.resize((window_x, window_y))
        resized_main_ui = ImageTk.PhotoImage(resize_main_ui)

        bg_canvas = Canvas(terms_root, width=window_x, height=window_y)
        bg_canvas.pack(fill=BOTH, expand=True)
        bg_canvas.create_image(0, 0, image=resized_main_ui, anchor="nw")

        def call_on_close_terms():
            terms_root.destroy()
            self.sign_up_draw()

        terms_root.protocol("WM_DELETE_WINDOW", call_on_close_terms)

        terms_text = scrolledtext.ScrolledText(terms_root,
                                               bg="#CEBEBE",
                                               border=0,
                                               highlightthickness=0,
                                               font=10,
                                               )
        terms_text.pack()
        terms_text.place(x=574 / 2 + 5,
                         y=232 / 2 + 5,
                         width=960 / 2 - 10,
                         height=732 / 2 - 10,
                         )
        terms_text.vbar.config(cursor="sb_v_double_arrow")

        self.mousePositions(terms_root)

        # Write your sign up terms and conditions here
        sign_up_terms_and_conditions = "No terms and condition."


        terms_text.insert(INSERT, sign_up_terms_and_conditions)
        terms_text.config(state=DISABLED)

        terms_root.mainloop()

