#!/usr/bin/env python
from __future__ import print_function
from selenium import webdriver
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from time import sleep
import getpass
import sys
import logging
if sys.version[0] == '3': raw_input=input   # for python 2/3 cross compatibility

# https://www.reddit.com/r/Python/comments/396aau/fb_eraser_automate_deleting_your_old_facebook/
class Searcher(object):
    """
    Searcher class to remove Facebook content
    Set up, log in, go to activity page, then repeat delete
    If having trouble, use scroll down method or increase wait time
    Don't forget to quit in the end
    """

    def __init__(self, email, password, wait=1):
        """
        Set up the searcher
        :return: Null
        """
        # self.driver = webdriver.Chrome()
        self.driver = webdriver.PhantomJS()
        self.email = email
        self.password =password
#         self.profile_name = "zuck"            # this will end up being the facebook user name
        self.count = 0                      # counter of number of elements deleted
        self.wait = wait

    def quit(self):
        """
        Quit the program (close out the browser)
        :return: Null
        """
        self.driver.quit()

    def login(self):
        """
        Log in to Facebook, set profile name
        :return: Null
        """
        self.driver.get('https://www.facebook.com/login/')
        email_element = self.driver.find_element_by_id('email')
        email_element.send_keys(self.email)
        password_element = self.driver.find_element_by_id('pass')
        password_element.send_keys(self.password)
        password_element.submit()

        soup = BeautifulSoup(self.driver.page_source)
        profile_link = soup.find('a', {'title': 'Profile'})
        self.profile_name = profile_link.get('href')[25:]    # link appears as http://www.facebook.com/PROFILE

    def search(self, keyword):
        self.driver.get('https://www.facebook.com/search/str/'+keyword+'/keywords_pages')
        sleep(self.wait)

    def _get_page_id(self, id_object):
        page_id = id_object.get_attribute("href").split("/").pop(-2)
        return page_id

    def _is_it_end_of_page(self):
        self.driver.find_element_by_xpath(".//*[@id='browse_end_of_results_footer']/div/div/div")


    def collect_pageids(self):
        # soup = BeautifulSoup(self.driver.page_source)
        # TODO: need to pick out each of the page's link (and the group name), just log them to screen
        # consider the delete_element method as an example
        # For example: https://www.facebook.com/search/str/epilepsy/keywords_pages
        # has "EpilepsySociety", and "epilepsysupports", etc as list of page ids
        #logging.info(pageid)

        page_id_xpath = ".//*[@class='_gll']/a"
        page_id = self.driver.find_elements_by_xpath(page_id_xpath)
        page_id = list(map(self._get_page_id, page_id))
        # get actual page_id
        
        #page_id = [self._get_page_id(id) for id in page_id] #self.driver.current_url.split("/").pop(-2)
        return page_id

        
    def go_to_activity_page(self):
        """
        Go to the activity page and prepare to start deleting
        :return: Null
        """
        if not self.profile_name:
            # the user hasn't logged in properly
            sys.exit(-2)
        # go to the activity page (filter by 'Your Posts')
        activity_link = 'https://www.facebook.com/' + self.profile_name + '/allactivity?privacy_source=activity_log&log_filter=cluster_11'
        self.driver.get(activity_link)
        sleep(self.wait)
    

    def scroll_down(self):
        """
        Executes JS to scroll down on page.
        Use if having trouble seeing elements
        :return:
        """
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(self.wait)

    def delete_element(self):
        """
        Find the first available element and delete it
        :return: Null
        """

        # click hidden from timeline so the delete button shows up
        soup = BeautifulSoup(self.driver.page_source)
        # Priority: highlights, allowed, hidden
        menu_button = soup.find('a', {'aria-label': 'Highlighted on Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Allowed on Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Hidden from Timeline'})
        if menu_button is None:
            menu_button = soup.find('a', {'aria-label': 'Shown on Timeline'})
        menu_element = self.driver.find_element_by_id(menu_button.get('id'))
        menu_element.click()
        sleep(self.wait)

        # now that the delete button comes up, find the delete link and click
        # sometimes it takes more than one click to get the delete button to pop up
        if menu_button is not None:
            i = 0
            while i < 3:
                try:
                    self.driver.find_element_by_link_text('Delete').click()
                    break
                except:
                    print('[*] Clicking menu again')
                    menu_element.click()
                    i += 1
        sleep(self.wait)

        # click the confirm button, increment counter and display success
        self.driver.find_element_by_class_name('layerConfirm').click()
        self.count += 1
        print('[+] Element Deleted ({count} in total)'.format(count=self.count))
        sleep(self.wait)

    
        

if __name__ == '__main__':
#     """
#     Main section of script
#     """
#     # set up the command line argument parser
#     parser = ArgumentParser(description='Delete your Facebook activity.  Requires Firefox')
#     parser.add_argument('--wait', type=float, default=1, help='Explicit wait time between page loads (default 1 second)')
#     args = parser.parse_args()
# 
#     # execute the script
#     email = raw_input("Please enter Facebook login email: ")
#     password = getpass.getpass()
    keyword="epilepsy"
    searcher = Searcher(email="", password="", wait=1)
    searcher.login()
    searcher.search(keyword)
    # track failures
    #fail_count = 0
    while True:
        try:
            searcher._is_it_end_of_page()
            for id in searcher.collect_pageids():
                print(id)
            searcher.driver.close()
        except:
            searcher.scroll_down()
        
    #     if fail_count >= 3:
    #         print('[*] Scrolling down')
    #         searcher.scroll_down()
    #         fail_count = 0
    #         sleep(5)
    #     try:
    #         print('[*] Trying to collect pageids ')
    #         searcher.collect_pageids()
    #         fail_count = 0
    #     except (Exception, ) as e:
    #         print('[-] Problem finding element')
    #         fail_count += 1
    #         sleep(2)
    # searcher.driver.close()

