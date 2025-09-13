from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

from selenium.webdriver.support import expected_conditions as EC

import time


def login(driver, credentials = None):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-box"))
    )

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "user-name"))
    )

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "password"))
    )

    login_div = driver.find_element(By.CLASS_NAME, "login-box")    
    form = login_div.find_element(By.CSS_SELECTOR, value="form")
    login_field = form.find_element(By.ID, "user-name")
    password_field = form.find_element(By.ID, "password")

    login_field.clear()
    login_field.send_keys("standard_user")

    time.sleep(1)

    password_field.clear()
    password_field.send_keys("secret_sauce")

    input_buttom = form.find_element(By.ID, "login-button")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_buttom))
    input_buttom.click()

def get_products_list(driver):
    items = []
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
    )
    product_list = driver.find_elements(By.CLASS_NAME, "inventory_item")
    for div in product_list:
        items.append(div)
    return items

def get_cost(item):
    text = item.find_element(By.CLASS_NAME, "inventory_item_price").text
    text = text.replace("$", "")
    cost = float(text)
    return cost

def get_name(item):
    name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
    return name

def add_to_card(item):
    price_bar = item.find_element(By.CLASS_NAME, "pricebar")
    WebDriverWait(price_bar, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button"))
    )
    add_to_card_button = price_bar.find_element(By.CSS_SELECTOR, "button")
    add_to_card_button.click()


def delete_from_card(driver, item_name):
    product_list = driver.find_elements(By.CLASS_NAME, "cart_item")
    
    for item in product_list:
        name = get_name(item)
        print(name)
        if name == item_name:
            delete_button = item.find_element(By.CLASS_NAME, "cart_button")

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(delete_button)
            )

            delete_button.click()

def go_to_card(driver):
    driver.execute_script("window.scrollBy(0, 500);")   
    card_link = driver.find_element(By.CLASS_NAME, "shopping_cart_link")
    card_link.click()

if __name__ == "__main__":
    driver = webdriver.Edge()
    driver.get("https://www.saucedemo.com/")
    login(driver)
    products = get_products_list(driver)
    sorted_products_by_cost = sorted(get_products_list(driver), key=get_cost)

    most_expensive = sorted_products_by_cost[-1]

    driver.execute_script("arguments[0].scrollIntoView();", most_expensive)
    time.sleep(2)
    most_expensive_cost = get_cost(sorted_products_by_cost[-1])
    most_expensive_name = get_name(sorted_products_by_cost[-1])

    print(f"Most expensive cost: {most_expensive_cost}")
    print(f"Most expensive name: {most_expensive_name}")

    add_to_card(most_expensive)
    time.sleep(2)
    go_to_card(driver)
    time.sleep(2)
    delete_from_card(driver, most_expensive_name)

    time.sleep(30)

    driver.quit()


