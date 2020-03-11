from mission_control import MissionControl
from communication import Communication

def main():
    missionControl = MissionControl(Communication())
    missionControl.start()

if __name__ == "__main__":
    main()
