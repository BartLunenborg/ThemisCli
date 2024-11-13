import os
import json


# Exit the program after print a message
def error_exit(error_msg: str):
    print(error_msg)
    exit(0)


OPTIONS = [
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
    "No year",
    "Quit",
]


def get_year():
    home = os.path.expanduser("~")
    config_file = os.path.join(home, ".config", "themis_cli", "config.json")

    if not os.path.isfile(config_file):
        error_exit(
            "ERROR!\nThe themis_cli config file does not exist!\nPlease run `themis setup` to create one"
        )

    with open(config_file, "r") as f:
        config = json.load(f)

    if config["year"]:
        print(f"Current year set to: {config["year"]}")

    print("Pick a year to set Themis to:")
    for i, option in enumerate(OPTIONS):
        print(f"({i+1}) {option}")

    choice = input("Enter the number of your choice: ")

    if "1" <= choice <= "4":
        config["year"] = OPTIONS[int(choice) - 1]
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Year set to: {config["year"]}")
    elif choice == "5":
        config["year"] = ""
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        print("Year is no longer set.")
    elif choice != "6":
        print("Invalid choice. Please enter a valid option.")

    print("Exiting")


if __name__ == "__main__":
    get_year()
