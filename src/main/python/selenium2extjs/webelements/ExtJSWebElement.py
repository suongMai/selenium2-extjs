'''
'''
from selenium.webdriver.support.wait import WebDriverWait


FUNCTION_highlight = '''
    MyExt.highlight = function(element, timesec) {
        var prevBackgroundColor = element.style.backgroundColor;
        var prevBorder = element.style.order;
        element.style.backgroundColor = "#FDFF47";
        element.style.border = "3px solid #11FF11";
        window.setTimeout(function(element, prevBackgroundColor, prevBorder) {
            element.style.backgroundColor = prevBackgroundColor;
            element.style.border = prevBorder;
        }, timesec * 1000, element, prevBackgroundColor, prevBorder)
    };
'''

FUNCTION_htmlEscape = '''
    MyExt.htmlEscape = function(str) {
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
'''


class ExtJSWebElement(object):
    '''
    classdocs
    '''

    driver = None
    wait = 0
    top_element = None
    timeout_seconds = 5
    sleep_in_millis = 300

    def __init__(self, driver, js_code="", top_element=None):
        '''
        Constructor
        '''
        self.set_driver(driver)
        
        if js_code:
            self.find_element_by_script(js_code)
            
        if top_element:
            self.set_element(top_element)

    def set_driver(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, self.timeout_seconds,
                                  self.sleep_in_millis)
        
    def set_element(self, element):
        self.top_element = element
    
    def find_element_by_script(self, js_code):
        element = None
        try:
            element = self.driver.execute_script(js_code)
            
        finally:
            self.set_element(element)

    def exec_script_clean(self, js_code):
        self.wait_for_finish_ajax_request()
        return self.driver.execute_script(js_code)

    def exec_script_on_top_level_element(self, js_code):
        return self.exec_script_on_element(js_code, self.top_element)

    def exec_script_on_element(self, js_code, element):
        self.wait_for_finish_ajax_request()
        script = "var el = arguments[0]; %s;" % (js_code)
        return self.driver.execute_script(script, element)
    
    def click(self):
        self.top_element.click()

    def wait_for_finish_ajax_request(self):
        return True
