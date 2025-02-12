import getpass
import json
import os

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

YEARS = [
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025",
]

BASE = "https://themis.housing.rug.nl"
LOGIN = "https://themis.housing.rug.nl/log/in/oidc"
NAV_API = "https://themis.housing.rug.nl/api/navigation"

HOME = os.path.expanduser("~")
CONFIG_FILE = os.path.join(HOME, ".config", "themis_cli", "config.json")


# Exit the program after print a message
def error_exit(error_msg: str):
    print(error_msg)
    exit(0)


# Create and return a logged in Themis session
def get_loged_in_session(username: str, password: str) -> requests.Session:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    session = requests.Session()

    try:
        driver.get(LOGIN)

        # Find username and password fields and send values to the form
        driver.find_element(By.NAME, "Ecom_User_ID").send_keys(username)
        driver.find_element(By.NAME, "Ecom_Password").send_keys(password)

        # Submit the username and password values
        driver.find_element(By.XPATH, "//button[contains(text(), 'Inloggen')]").click()

        # Wait for the authenticator page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))

        # Get authenticator code from the user and give to the page form
        auth = input("Provide your authenticator code: ")
        driver.find_element(By.NAME, "nffc").send_keys(auth)

        # Submit the authenticator code
        driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]").click()

        # Wait for Themis to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//section[@id='global-motd']"))
        )

        # Give the cookies from the Selenium driver to the requests session (so we can close the Selenium driver).
        session.cookies.update({c["name"]: c["value"] for c in driver.get_cookies()})

    except Exception as e:
        error_exit(f"Error during login!\n{e}\nPlease try again!")
    finally:
        driver.quit()

    return session


# Pick the wanted year from the options
def pick_year(options: list[tuple[str, str]]) -> str:
    max = len(options)
    for i, option in enumerate(options):
        print(f"({i+1}) {option[0]}")
    print(f"({max+1}) Quit")

    while True:
        try:
            user_input = (
                int(input("Please enter the index of the year you want to pick: ")) - 1
            )
            if 0 <= user_input < max:
                return options[user_input][1]
            elif user_input == max:
                error_exit("Goodbye!")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            error_exit("Invalid input. Please enter a valid index.")


# Retrieve the year to use
def get_year(session: requests.Session) -> str:
    r = session.get(NAV_API)
    options = [(option["title"], option["path"]) for option in json.loads(r.text)]

    # Use a stored year if available and possible
    with open(CONFIG_FILE, "r") as f:
        stored_year = json.load(f)["year"]
        if stored_year in {year for year, _ in options}:
            return NAV_API + "/" + stored_year
        else:
            print("Your stored year does not seem to be available on Themis :/")
            print("You can pick one from the available year on Themis")

    # Pick a year from the website's options
    picked_year = pick_year(options)
    return NAV_API + picked_year


# Download (or not) the found .in and .out files
def download_files(session: requests.Session, link: str):
    r = session.get(link)

    if (r.status_code) != 200:
        error_exit("The link you tried to access did not work for some reason :/")

    soup = BeautifulSoup(r.text, "html.parser")
    files = soup.select(
        '.cfg-val a[data-path][data-path$=".in"], .cfg-val a[data-path][data-path$=".out"]'
    )

    print(f"Found the following .in/.out files:")
    for file in files:
        print(file["data-path"])
    print("What do you want to do?")
    print("(1) Download files")
    print("(2) Quit")

    while True:
        try:
            user_input = int(
                input("Please enter the index of the option you want to pick: ")
            )
            if 1 <= user_input <= 2:
                break
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")

    if user_input == 2:
        error_exit("Goodbye!")
    else:
        cd = os.getcwd()
        tests_dir = os.path.join(cd, "tests")
        if not os.path.exists(tests_dir):
            os.makedirs(tests_dir)
        for file in files:
            print("..", end="", flush=True)
            r = session.get(BASE + file["href"])  # type: ignore
            save_path = os.path.join(tests_dir, file["data-path"])  # type: ignore
            with open(save_path, "wb") as file:
                file.write(r.content)
        print()
        error_exit("Done downloading")


# Go down the options until a link that is 'submitable' is found
def options_recurse(session: requests.Session, link: str):
    r = session.get(link)

    if (r.status_code) != 200:
        error_exit("The link you tried to access did not work for some reason :/")

    options = [
        (option["title"], option["path"], option["submitable"])
        for option in json.loads(r.text)
    ]

    if len(options) == 0:
        error_exit(f"Found no more links on page: {link} :/")

    max = len(options)
    for i, option in enumerate(options):
        print(f"({i+1}) {option[0]}")
    print(f"({max+1}) Quit")

    while True:
        try:
            user_input = (
                int(input("Please enter the index of the option you want to pick: "))
                - 1
            )
            if 0 <= user_input < max:
                choice = options[user_input]
                if choice[2] == True:
                    download_files(session, BASE + "/course" + choice[1])
                else:
                    options_recurse(session, NAV_API + choice[1])
            elif user_input == max:
                error_exit("Goodbye!")
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")


def get_tests(username: str, password: str):
    session = get_loged_in_session(username, password)
    options_recurse(session, get_year(session))


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
