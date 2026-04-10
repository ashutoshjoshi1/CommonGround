from app.worker import tasks  # noqa: F401

if __name__ == "__main__":
    print(
        "Dramatiq worker module loaded. Run worker with: dramatiq app.worker.tasks --processes 1 --threads 4"
    )
