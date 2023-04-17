from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
# requires the installation of geckodriver to use


def firefox_driver():
    driver = webdriver.Firefox()
    return driver


def privacy_popup(driver):
    privacy_button = driver.find_element(By.XPATH, "//button[text()='Accept all']")
    privacy_button.click()
    time.sleep(5)


def edit_stock_filter(driver):
    edit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Edit']]"))
    )
    edit_button.click()

    driver.execute_script("window.scrollBy(0, 100);")

    small_cap = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//button[text()='Small Cap']"))
    )
    small_cap.click()

    volume = WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.XPATH, "//span[text()='greater than']"))
    )
    volume.click()

    volume2 = WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.XPATH, "//span[text()='between']"))
    )
    volume2.click()

    input_field1 = WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.XPATH,
                                          "//input[@class='Fz(s) Pstart(8px) H(28px) Bgc($lv3BgColor) "
                                          "C($primaryColor) Mend(8px) W(80px) Bdc($seperatorColor) "
                                          "Bdc($linkColor):f' and @value='5000000']"))
    )
    input_field1.clear()
    input_field1.send_keys("0")

    input_field2 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH,
                                          "//input[@class='Fz(s) Pstart(8px) H(28px) Bgc($lv3BgColor) "
                                          "C($primaryColor) Mstart(10px) W(80px) Bdc($seperatorColor) "
                                          "Bdc($linkColor):f' and @value='']"))
    )
    input_field2.clear()
    input_field2.send_keys("999999999")
    time.sleep(5)


def scrape_stock_table(driver):
    find_stock_button = driver.find_element(By.CSS_SELECTOR, "[data-test='find-stock']")
    find_stock_button.click()

    time.sleep(40)

    data = []

    while True:
        driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
        time.sleep(10)

        stocks = driver.find_elements(By.TAG_NAME, 'tr')[1:]

        for stock in stocks:
            symbol_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Symbol']"))
            )
            symbol = symbol_element.text

            name_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Name']"))
            )
            name = name_element.text

            intraday_price_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Price (Intraday)']"))
            )
            intraday_price = intraday_price_element.text

            change_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Change']"))
            )
            change = change_element.text

            percentage_change_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='% Change']"))
            )
            percentage_change = percentage_change_element.text

            volume_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Volume']"))
            )
            volume = volume_element.text

            avg_vol_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Avg Vol (3 month)']"))
            )
            avg_vol = avg_vol_element.text

            market_cap_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='Market Cap']"))
            )
            market_cap = market_cap_element.text

            pe_ratio_element = WebDriverWait(stock, 5).until(
                EC.presence_of_element_located((By.XPATH, ".//td[@aria-label='PE Ratio (TTM)']"))
            )
            pe_ratio = pe_ratio_element.text

            data.append({
                "Symbol": symbol,
                "Name": name,
                "Intraday Price": intraday_price,
                "Change": change,
                "% Change": percentage_change,
                "Volume": volume,
                "Avg Vol (3 month)": avg_vol,
                "Market Cap": market_cap,
                "PE Ratio (TTM)": pe_ratio
            })

        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[@class='Va(m) H(20px) Bd(0) M(0) P(0) Fz(s) Pstart(10px) O(n):f Fw(500) C($linkColor)']/span"))
            )
            if next_button.get_attribute("aria-disabled") == "true":
                break
            next_button.click()
            time.sleep(5)
        except StaleElementReferenceException:
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[@class='Va(m) H(20px) Bd(0) M(0) P(0) Fz(s) Pstart(10px) O(n):f Fw(500) C($linkColor)']/span"))
            )
            if next_button.get_attribute("aria-disabled") == "true":
                break
            next_button.click()
            time.sleep(10)

        df = pd.DataFrame(data)
        df.to_csv('Yahoo_most_active_stocks.csv', index=False, header=True)
        print(df)


def main():
    URL = "https://finance.yahoo.com/most-active?count=100&offset=0"
    driver = firefox_driver()
    driver.get(URL)

    privacy_popup(driver)
    edit_stock_filter(driver)
    scrape_stock_table(driver)

    driver.quit()


if __name__ == "__main__":
    main()
