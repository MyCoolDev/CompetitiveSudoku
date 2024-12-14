from flask import Flask, render_template, request

app = Flask(__name__)

from Server.ServerSocket import ServerSocket

server_socket = ServerSocket()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        server_socket.toggle_status()

    return render_template('index.html', server_status=server_socket.get_status())


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
