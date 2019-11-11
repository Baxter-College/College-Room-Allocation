from flask import Flask, render_template, request

app = Flask(__name__)

#TODO: everything that needs to be done on startup

@app.before_request
def before_request():
    #TODO: everythin that needs to be done before a request
    pass

@app.route("/rooms/select", methods=["GET"])
def select_rooms():
    #TODO: get the data from fucntions
    data = get_data()

    return render_template("select.html", data=data)

if __name__ == "__main__":
    app.run()