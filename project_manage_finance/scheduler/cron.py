from datetime import datetime


def run_scheduler_tick() -> None:
    print(f"Scheduler heartbeat at {datetime.now().isoformat()}")


if __name__ == "__main__":
    run_scheduler_tick()
