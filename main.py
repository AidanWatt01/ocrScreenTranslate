import time
from controller import Controller

def main():
    print("F8 = Show overlay | F9 = Close overlay | Ctrl+C = Quit")
    controller = Controller()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[App] Exiting cleanly.")

if __name__ == "__main__":
    main()
