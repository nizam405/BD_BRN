from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import datetime

class BirthRegistration:
    """
    This program is desinged to make birth registration verification of Bangladesh easy. It acts like a human to write birth registration number and birth date and waits to input captcha. Captcha must be filled up by you. Here a new 'Next' button is added. Just click next after filling up capcha, you will get all data from details page.
    """
    verified = False
    data = None
    checked = False

    def __init__(self, brn:str, dob:datetime.date):
        if self.verify_brn(brn):
            self.brn = brn
        if self.verify_dob(dob):
            self.dob = dob
    
    def verify_brn(self, brn):
        """
        Verifies Birth Registration Number. 
        First, it checks if only number is given.
        Then, checks if number is 17 digit in length.
        """
        # only numbers
        brn = str(brn)
        for d in brn:
            if int(d) not in range(0,10):
                raise ValueError("BRN contains only numbers in english")
        # 17 digit
        if len(brn) != 17:
            raise ValueError("BRN must be 17 digit")
        return True
    
    def verify_dob(self, dob):
        """
        This method verifies the given date is a valid date object.
        """
        if not isinstance(dob, datetime.date):
            raise ValueError("Required valid date")
        return True
    
    def get_data(self):
        """
        This method does all scraping job and outputs data.
        """
        driver = webdriver.Chrome()
        driver.get("https://everify.bdris.gov.bd/")

        brn_input = driver.find_element(By.NAME, 'UBRN')
        dob_input =  driver.find_element(By.NAME, 'BirthDate')
        search_button = driver.find_element(By.XPATH, '//input[@value="Search"]')
        clear_button = driver.find_element(By.XPATH, '//input[@value="Clear"]')
        driver.execute_script("arguments[0].setAttribute('disabled', 'true');", search_button)
        driver.execute_script("arguments[0].remove();", clear_button)

        # Add a "Next" button using JavaScript before the "Search" button.
        next_button_script = """
        var nextButton = document.createElement("input");
        nextButton.type = "button";
        nextButton.value = "Next";
        var searchButton = document.querySelector('input[value="Search"]');
        nextButton.className = searchButton.className;  // Copy the class attribute
        nextButton.style.marginRight = "5px";
        nextButton.onclick = function() {
            // Enable the "Search" button when the "Next" button is clicked.
            var searchButton = document.querySelector('input[value="Search"]');
            searchButton.removeAttribute('disabled');
        };
        var searchButton = document.querySelector('input[value="Search"]');
        searchButton.parentNode.insertBefore(nextButton, searchButton);
        """
        driver.execute_script(next_button_script)
        # Fill up form
        brn_input.send_keys(self.brn)
        dob_input.send_keys(self.dob.strftime("%Y-%m-%d"))
        dob_input.send_keys(Keys.RETURN)

        # Fill captcha and submit form manually
        # Wait for the submit button to become clickable.
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Search"]')))
        search_button.click()

        # Collect data
        data = {
            'registration_date': '',
            'registration_office': '',
            'issuance_date': '',
            'sex': '',
            'name_bn': '',
            'name_en': '',
            'birth_place_bn': '',
            'birth_place_en': '',
            'mother_name_bn': '',
            'mother_name_en': '',
            'mother_nationality_bn': '',
            'mother_nationality_en': '',
            'father_name_bn': '',
            'father_name_en': '',
            'father_nationality_bn': '',
            'father_nationality_en': '',
        }

        container = driver.find_element(By.CLASS_NAME, 'body-content')

        # If no record found break the operation
        try:
            container.find_element(By.XPATH, '//h3[contains(text(), "No Record Found")]')
            return False
        except NoSuchElementException: pass

        # If record found continue
        rows = container.find_elements(By.CLASS_NAME, 'row')
        table1 = rows[0].find_element(By.TAG_NAME, 'table')
        table2 = rows[1].find_element(By.TAG_NAME, 'table')

        table1_rows = table1.find_elements(By.TAG_NAME, 'tr')
        table1_row1 = table1_rows[2].find_elements(By.TAG_NAME, 'td')
        data['registration_date'] = datetime.datetime.strptime(table1_row1[0].text, "%d %B %Y")
        data['registration_office'] = table1_row1[1].text
        data['issuance_date'] = datetime.datetime.strptime(table1_row1[2].text, "%d %B %Y")
        data['sex'] = table1_rows[4].find_elements(By.TAG_NAME, 'td')[2].text

        table2_rows = table2.find_elements(By.TAG_NAME, 'tr')
        data['name_bn'] = table2_rows[0].find_elements(By.TAG_NAME, 'td')[1].text
        data['name_en'] = table2_rows[0].find_elements(By.TAG_NAME, 'td')[3].text
        data['birth_place_bn'] = table2_rows[1].find_elements(By.TAG_NAME, 'td')[1].text
        data['birth_place_en'] = table2_rows[1].find_elements(By.TAG_NAME, 'td')[3].text
        data['mother_name_bn'] = table2_rows[2].find_elements(By.TAG_NAME, 'td')[1].text
        data['mother_name_en'] = table2_rows[2].find_elements(By.TAG_NAME, 'td')[3].text
        data['mother_nationality_bn'] = table2_rows[3].find_elements(By.TAG_NAME, 'td')[1].text
        data['mother_nationality_en'] = table2_rows[3].find_elements(By.TAG_NAME, 'td')[3].text
        data['father_name_bn'] = table2_rows[4].find_elements(By.TAG_NAME, 'td')[1].text
        data['father_name_en'] = table2_rows[4].find_elements(By.TAG_NAME, 'td')[3].text
        data['father_nationality_bn'] = table2_rows[5].find_elements(By.TAG_NAME, 'td')[1].text
        data['father_nationality_en'] = table2_rows[5].find_elements(By.TAG_NAME, 'td')[3].text

        driver.quit()
        return data
    
    def verify(self):
        """
        This method collects data and changes verification flag.
        """
        if self.brn and self.dob:
            self.data = self.get_data()
            if self.data: self.verified = True
            self.checked = True


