from app import app
import os



if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    #  app.run(debug = True, ssl_context = "adhoc")
    # app.run(debug = True)
    app.run()