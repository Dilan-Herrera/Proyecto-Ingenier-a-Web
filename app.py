from app import create_app

# ESTA línea es la importante: gunicorn va a buscar esta variable
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
