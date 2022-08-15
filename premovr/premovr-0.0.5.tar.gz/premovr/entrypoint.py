import typer
import premovr.game_interfaces.lichess_api as chess_api
from premovr.hardware_interfaces.http_server_api import Board

app = typer.Typer()

@app.command('display')
def display_board():
    '''Displays a dummy chess board'''
    print(chess_api.game)

@app.command('server')
def server():
    '''Some options related to the server'''
    b = Board('192.168.1.1')
    print(b.heartbeat())

def main():
    app()

if __name__ == "__main__":
    main()
