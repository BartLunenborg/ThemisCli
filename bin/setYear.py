import os


def get_year():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yearFile = os.path.join(script_dir, "year.txt")
    if os.path.exists(yearFile):
        with open(yearFile, "r") as file:
            stored_year = file.read().strip()
            if stored_year:
                print(f"Current year set to: {stored_year}")

    print("Pick a year to set Themis to:")
    print("(1) 2021-2022")
    print("(2) 2022-2023")
    print("(3) 2023-2024")
    print("(4) No year")
    print("(5) Quit")

    choice = input("Enter the number of your choice: ")
    if choice == "1":
        selected_year = "2021-2022"
    elif choice == "2":
        selected_year = "2022-2023"
    elif choice == "3":
        selected_year = "2023-2024"
    elif choice == "4":
        if os.path.exists(yearFile):
            os.remove(yearFile)
        exit()
    elif choice == "5":
        print("Exiting...")
        exit()
    else:
        print("Invalid choice. Please enter a valid option.")
        print("Exiting")
        exit()

    with open(yearFile, "w") as file:
        file.write(selected_year)

    print(f"Year set to: {selected_year}")
    return selected_year


if __name__ == "__main__":
    get_year()
