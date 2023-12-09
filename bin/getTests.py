import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import getpass
import sys
import time


def start_flow(username, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://themis.housing.rug.nl/log/in")

    username_field = driver.find_element("name", "user")
    password_field = driver.find_element("name", "password")
    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//section[@id='global-motd' and contains(., 'Welcome, logged in as')]")))
        print("Login successful!")
    except TimeoutException:
        print("Login failed. Please check your credentials.")
        driver.quit()
        sys.exit(0)

    title_href_seen = {}
    title_href_seen["/"] = "root"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    year_file = os.path.join(script_dir, "year.txt")
    if os.path.exists(year_file):
        with open(year_file, "r") as file:
            stored_year = file.read().strip()
            stored_year = "/" + stored_year
            if stored_year:
                driver.get("https://themis.housing.rug.nl/course" + stored_year)
                title_href_seen["/2021-2022"] = "a"
                title_href_seen["/2022-2023"] = "a"
                title_href_seen["/2023-2024"] = "a"
                pick_course(driver, stored_year, title_href_seen)
    else:
        pick_year(driver, title_href_seen)


def pick_year(driver, seen):
    links = driver.find_elements(By.CSS_SELECTOR, 'a.iconize.ass-group[title^="/"]')
    title_href_map = {}
    for link in links:
        title = link.get_attribute("title")
        href = link.get_attribute("href")
        if title and href and title not in seen:
            title_href_map[title] = href
            seen[title] = href

    index = 1
    for title, href in title_href_map.items():
        print(f"({index}) {title}")
        index += 1

    print(f"({index}) exit")

    while True:
        try:
            user_input = int(input("Please enter the index of the year you want to pick: "))
            if 1 <= user_input <= index:
                break
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")

    if user_input == index:
        print("Goodbye!")
        driver.quit()
        sys.exit()
    else:
        chosen_year = list(title_href_map.keys())[user_input-1]
        chosen_year_link = list(title_href_map.values())[user_input-1]
        driver.get(chosen_year_link)
        pick_course(driver, chosen_year, seen)


def pick_course(driver, target_year, seen):
    section = driver.find_element(By.ID, target_year)
    links = section.find_elements(By.CSS_SELECTOR, 'div.subsec.round.shade.ass-children ul.round li.large span.ass-link a.iconize.ass-group')
    title_href_map = {}
    for link in links:
        title = link.get_attribute("title")
        href = link.get_attribute("href")
        if title and href and title not in seen:
            title_href_map[title] = href
            seen[title] = href

    index = 1
    for title, href in title_href_map.items():
        print(f"({index}) {title}")
        index += 1

    print(f"({index}) quit")

    while True:
        try:
            user_input = int(input("Please enter the index of the course you want to pick: "))
            if 1 <= user_input <= index:
                break
            else:
                print("Invalid index. Please enter a valid index.")
        except ValueError:
            print("Invalid input. Please enter a valid index.")

    if user_input == index:
        print("Goodbye!")
        driver.quit()
        sys.exit(0)
    else:
        chosen_course = list(title_href_map.values())[user_input-1]
        driver.get(chosen_course)
        pick_assignment(driver, seen)


def pick_assignment(driver, seen):
    test_elements = driver.find_elements(By.CSS_SELECTOR, '.cfg-val a[data-path]')
    if not test_elements or len(test_elements) < 4:
        links = driver.find_elements(By.CSS_SELECTOR, '.ass-link a.iconize.ass-submitable, .ass-link a.iconize.ass-group')
        title_href_map = {}
        for link in links:
            title = link.get_attribute("title")
            href = link.get_attribute("href")
            if title and href and title not in seen:
                title_href_map[title] = href
                seen[title] = href

        index = 1
        for title, href in title_href_map.items():
            print(f"({index}) {title}")
            index += 1

        print(f"({index}) quit")

        while True:
            try:
                user_input = int(input("Please enter the index of the assignment you want to pick: "))
                if 1 <= user_input <= index:
                    break
                else:
                    print("Invalid index. Please enter a valid index.")
            except ValueError:
                print("Invalid input. Please enter a valid index.")

        if user_input == index:
            print("Goodbye!")
            driver.quit()
            sys.exit(0)
        else:
            chosen_assignment = list(title_href_map.values())[user_input-1]
            driver.get(chosen_assignment)
            pick_assignment(driver, seen)

    else:
        file_links = driver.find_elements(By.CSS_SELECTOR, '.cfg-val a[data-path]')
        file_title_href_map = {link.get_attribute("data-path"): link.get_attribute("href") for link in file_links if not link.get_attribute("data-path").endswith(".pdf") }

        print("Found the following files:")
        for title, _ in file_title_href_map.items():
            print(title)

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
            print("Goodbye!")
            driver.quit()
            sys.exit(0)
        else:
            cd = os.getcwd()
            tests_dir = os.path.join(cd, 'tests')
            if not os.path.exists(tests_dir):
                os.makedirs(tests_dir)
            for title, link in file_title_href_map.items():
                print("..", end="", flush=True)
                driver.get(link)
                time.sleep(0.2)
                content = driver.find_element("tag name", "pre").text + "\n"
                save_path = os.path.join(tests_dir, title)
                with open(save_path, "w") as file:
                    file.write(content)

            print()
            print("Done downloading")
            driver.quit()
            sys.exit(0)


def get_username():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    username_file_path = os.path.join(script_dir, "user.txt")

    if os.path.exists(username_file_path):
        with open(username_file_path, "r") as file:
            stored_username = file.read().strip()
            if stored_username:
                return stored_username

    username = input("Enter your username: ")
    return username


if __name__ == "__main__":
    username = get_username()
    password = getpass.getpass(f"Please type the password for {username}: ")
    start_flow(username, password)
