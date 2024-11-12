import os
import json
import getpass
import requests
from bs4 import BeautifulSoup

YEARS = [
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
]
BASE = "https://themis.housing.rug.nl"
LOGIN = "https://themis.housing.rug.nl/log/in"
HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(HOME, ".config", "themis_cli", "config.json")


# Exit the program after print a message
def error_exit(error_msg: str):
    print(error_msg)
    exit(0)


# Create and return a logged in Themis session
def get_loged_in_session(username, password):
    s = requests.Session()
    r = s.get(LOGIN)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find('input', {'name': '_csrf'})
    payload = {
        '_csrf': csrf['value'],
        'user': username,
        'password': password
    }
    p = s.post(LOGIN, data=payload)
    if p.status_code == 200:
        print("Login successful!")
        return s
    else:
        error_exit("Login failed. Please check your credentials.")


# From a set of years, pick the wanted year
def pick_year(years: list[str]) -> str:
    max = len(years)
    for i, year in enumerate(years):
        print(f"({i+1}) {year}")
    print(f"({max+1}) Quit")

    while True:
        try:
            user_input = int(input("Please enter the index of the year you want to pick: ")) - 1
            if 0 <= user_input < max:
                return years[user_input]
            elif user_input == max:
                error_exit("Goodbye!")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            error_exit("Invalid input. Please enter a valid index.")

# Retrieve the year to use
def get_year(session: requests.Session, seen: set[str]) -> tuple[str, set[str]]:
    r = session.get(BASE + "/course")
    soup = BeautifulSoup(r.text, 'html.parser')
    years = soup.find_all('a', class_='iconize ass-group')
    years_list = list(dict.fromkeys([year['title'] for year in years if year['title'] not in seen]))
    years = set(years_list) - seen

    # Use a stored year if available and possible
    with open(CONFIG_FILE, "r") as f:
        stored_year = json.load(f)["year"]
        if stored_year and "/" + stored_year in years:
            return ("/course/" + stored_year, seen | years | {"/course/" + stored_year})
        else:
            print("Your stored year does not seem to be available on Themis :/")
            print("You can pick one from the available year on Themis")

    # Pick a year from the website
    picked_year = pick_year(years_list)
    return ("/course" + picked_year, seen | {"/course" + year for year in years})


# Download (or not) the found .in and .out files
def download_files(session: requests.Session, files):
        print("Found the following files:")
        for file in files:
            print(file['data-path'])
        print("What do you want to do?")
        print("(1) Download files")
        print("(2) Quit")

        while True:
            try:
                user_input = int(input("Please enter the index of the option you want to pick: "))
                if 1 <= user_input <= 2:
                    break
                else:
                    print("Invalid index. Please enter a valid index.")
            except ValueError:
                print("Invalid input. Please enter a valid index.")

        if (user_input == 2):
            error_exit("Goodbye!")
        else:
            cd = os.getcwd()
            tests_dir = os.path.join(cd, 'tests')
            if not os.path.exists(tests_dir):
                os.makedirs(tests_dir)
            for file in files:
                print("..", end="", flush=True)
                r = session.get(BASE + file['href'])
                save_path = os.path.join(tests_dir, file['data-path'])
                with open(save_path, "wb") as file:
                    file.write(r.content)
            print()
            error_exit("Done downloading")


# Go down the options until .in and .out files are found
def options_recurse(session: requests.Session, state: tuple[str, set[str]]):
    r = session.get(BASE + state[0])
    if (r.status_code) != 200:
        error_exit("The link you tried to access did not work for some reason :/")
    soup = BeautifulSoup(r.text, 'html.parser')

    # Check for .in or .out files (EXITS THE PROGRAM)
    if options := soup.select('.cfg-val a[data-path][data-path$=".in"], .cfg-val a[data-path][data-path$=".out"]'):
        download_files(session, options)
    elif options := soup.select('div.ass-children ul li a'):  # Check for assignments
        options_list = [option['href'] for option in options if option['href'] not in state[1]]
        options = set(options_list)
    elif options := soup.find_all('a', class_='iconize ass-group'):  # Check for others
        options_list = [option['title'] for option in options if option['title'] not in state[1]]
        options = set(options_list)
    else:
        error_exit("Found no more links :(")

    max = len(options_list)
    for i, option in enumerate(options_list):
        print(f"({i+1}) {option}")
    print(f"({max+1}) Quit")

    while True:
        try:
            user_input = int(input("Please enter the index of the option you want to pick: ")) - 1
            if 0 <= user_input < max:
                choice = options_list[user_input]
                options_recurse(session, (choice, options | state[1]))
            elif user_input == max:
                error_exit("Goodbye!")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")


def get_tests(username: str, password: str):
    session = get_loged_in_session(username, password)
    options_recurse(session, get_year(session, {"/", "/course/"}))


# Return the stored username or prompt the user
def get_username():
    with open(CONFIG_FILE, "r") as f:
        stored_username = json.load(f)["user"]
        if stored_username:
            return stored_username

    return input("Enter your username: ")


if __name__ == "__main__":
    if not os.path.isfile(CONFIG_FILE):
        error_exit(
            "ERROR!\nThe themis_cli config file does not exist!\nPlease run `themis setup` to create one"
        )
    username = get_username()
    password = getpass.getpass(f"Please type the password for {username}: ")
    get_tests(username, password)
