import os

OPTIONS = [
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
    "No year",
    "Quit",
]


def get_year():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    year_file_path = os.path.join(script_dir, "year.txt")
    year_file = (os.path.exists(year_file_path), year_file_path)

    if year_file[0]:
        with open(year_file[1], "r") as file:
            if stored_year := file.read().strip():
                print(f"Current year set to: {stored_year}")

    print("Pick a year to set Themis to:")
    for i, option in enumerate(OPTIONS):
        print(f"({i+1}) {option}")

    choice = input("Enter the number of your choice: ")

    if "1" <= choice <= "4":
        selected_year = OPTIONS[int(choice) - 1]
        with open(year_file[1], "w") as file:
            file.write(selected_year)
        print(f"Year set to: {selected_year}")
    elif choice == "5":
        print("Year is no longer set.")
        if year_file[0]:
            os.remove(year_file[1])
    elif choice != "6":
        print("Invalid choice. Please enter a valid option.")

    print("Exiting")


if __name__ == "__main__":
    get_year()
