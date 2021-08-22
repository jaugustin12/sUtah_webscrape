# Jonathan Augustin

# BELOW IS THE LINK WE WOULD LIKE YOU TO SCRAPE AS A TEST OF YOUR ABILITY:
# Southern Utah University : https://registration.dixie.edu/transfer-guide/

# Please write a python script to extract the “To” and “From” transfer information from the highlighted link.
# The output should be in .JSON format. We would also like you to send the python script as well.
# We want ALL of the transfer information “TO” Southern Utah University, “FROM” every other institution in every state.

import os
import requests
from bs4 import BeautifulSoup
import json
import time
from itertools import chain
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pprint
import time
import progressbar
import threading
import multiprocessing




jsonClass = {
    "from_school": "",
    "from_course_department": "",
    "from_course_code": "",
    "from_course_name": "",
    "from_course_credit_hours": "",
    "from_extra_department": "",
    "from_extra_code": "",
    "from_extra_name": "",
    "from_extra_credit_hours": "",
    "to_school": "Southern Utah University",
    "to_course_department": "",
    "to_course_code": "",
    "to_course_name": "",
    "to_course_credit_hours": "",
    "to_extra_department": "",
    "to_extra_code": "",
    "to_extra_name": "",
    "to_extra_credit_hours": ""
}

states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
schools = []
missing_schools = []

class searchPage(object):
    def __init__(self, number):
    #        #^ The first variable is the class instance in methods.  
    #        #  This is called "self" by convention, but could be any name you want.
    #^ double underscore (dunder) methods are usually special.  This one 
    #  gets called immediately after a new instance is created
        PATH = "/Users/jonathanaugustin/Desktop/chromedriver"
        options = Options()
        self.number = number
        self.driver = webdriver.Chrome(PATH, options=options)
        url = 'https://widgets.collegetransfer.net/EquivWidget?institution=2093&name=Southern%20Utah%20University&theme=cdn/blitzer&direction=receiver&zip=84720'
        self.driver.get(url)
    
    def tearDown(self):
        self.driver.close()


    def getSchools(self):
        beforeScroll = 'initial'
        afterScroll = ''
        schoolsText = ''
        while (beforeScroll != afterScroll):
            beforeScroll = afterScroll
            schools = self.driver.find_element_by_id('schoolsbyname')
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', schools)
            time.sleep(0.7)
            afterScroll = schools.text[-20:]
            schoolsText = schools
        mylist = schools.find_elements_by_class_name('selectableContainer')
        return mylist

    def getNames(self):
        mylist = self.getSchools()
        with progressbar.ProgressBar(max_value=len(mylist)) as bar:
            for x in range(len(mylist)):
                bar.update(x)
                #check to see if school is in US
                time.sleep(1)
                address = mylist[x].find_element_by_class_name('address').text.split(', ')[1]
                if address not in states:
                    schools.append((mylist[x].get_attribute("data-sendername"), "N/A"))
                schools.append((mylist[x].get_attribute("data-sendername"), x))
        return schools


    def updateJson(self, numthreads):
        mylist = self.getSchools()
        global missing_schools
        with progressbar.ProgressBar(max_value=len(mylist)) as bar:
            array = []

            #prepare file for edit
            if missing_schools != []:
                #remove ]
                filename = "utah" + str(self.number) + ".json"
                filesize = os.path.getsize("utahJson/" + filename)

                #if file is empty add [
                if filesize == 0:
                    print("The file is empty: " + str(filesize))
                    my_file = open("utahJson/" + filename, "a")        # Open a file  # write a line to the file
                    my_file.write("[")
                    my_file.close()

                #if file is not empty, remove ending "]" and add ","
                else: 
                    with open("utahJson/" + filename, 'rb+') as filehandle:
                        filehandle.seek(-1, os.SEEK_END)
                        filehandle.truncate()
                    #add back comma
                    my_file = open("utahJson/" + filename, "a")        # Open a file  # write a line to the file
                    my_file.write(",") 
                    my_file.close() 
            for x in missing_schools:
                bar.update(x)
                if x % numthreads == self.number:
                    jsonClass["from_school"] = mylist[x].get_attribute("data-sendername")

                    #First click
                    time.sleep(1.5)
                    mylist[x].click()
                    time.sleep(1.5)
                    beforeScroll = 'initial'
                    afterScroll = ''
                    schoolsText = ''
                    while (beforeScroll != afterScroll):
                        beforeScroll = afterScroll
                        schools = self.driver.find_element_by_id('equivcontent')
                        self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', schools)
                        time.sleep(0.7)
                        afterScroll = schools.text[-20:]
                        schoolsText = schools

                    equivList = self.driver.find_element_by_id('equivcontent')
                    equivalencies = equivList.find_elements_by_class_name('selectableContainer')
                    i = 0
                    for i in range(len(equivalencies)):

                        fromCourse = equivalencies[i].find_element_by_class_name('equivSourceContainer')
                        # print(fromCourse.text)
                        courses = fromCourse.find_elements_by_class_name('course')
                        course = courses[0].find_element_by_class_name('courseId').text.split()
                        jsonClass["from_course_department"] = course[0]
                        jsonClass["from_course_code"] = course[1]
                        jsonClass["from_course_name"] = fromCourse.find_element_by_class_name('courseTitle').text
                        if len(courses) > 1:
                            from_extra_departments = []
                            from_extra_codes = []
                            from_extra_names = []
                            for eClass in courses[1:]:
                                eClass1 = eClass.find_element_by_class_name('courseId').text.split()
                                from_extra_departments.append(eClass1[0])
                                from_extra_codes.append(eClass1[1])
                                from_extra_names.append(eClass.find_element_by_class_name('courseTitle').text)
                            jsonClass["from_extra_department"] = str(from_extra_departments)
                            jsonClass["from_extra_code"] = str(from_extra_codes)
                            jsonClass["from_extra_name"] = str(from_extra_names)
                        else:
                            jsonClass["from_extra_department"] = ""
                            jsonClass["from_extra_code"] = ""
                            jsonClass["from_extra_name"] = ""


                        toCourse = equivalencies[i].find_element_by_class_name('equivTargetContainer')
                        toCourses = toCourse.find_elements_by_class_name('course')
                        tcourse = toCourses[0].find_element_by_class_name('courseId').text.split()
                        jsonClass["to_course_department"] = tcourse[0]
                        jsonClass["to_course_code"] = tcourse[1]
                        jsonClass["to_course_name"] = toCourse.find_element_by_class_name('courseTitle').text
                        if len(toCourses) > 1:
                            to_extra_departments = []
                            to_extra_codes = []
                            to_extra_names = []
                            for eClass in toCourses[1:]:
                                eClass1 = eClass.find_element_by_class_name('courseId').text.split()
                                to_extra_departments.append(eClass1[0])
                                to_extra_codes.append(eClass1[1])
                                to_extra_names.append(eClass.find_element_by_class_name('courseTitle').text)
                            jsonClass["to_extra_department"] = str(to_extra_departments)
                            jsonClass["to_extra_code"] = str(to_extra_codes)
                            jsonClass["to_extra_name"] = str(to_extra_names)
                        else:
                            jsonClass["to_extra_department"] = ""
                            jsonClass["to_extra_code"] = ""
                            jsonClass["to_extra_name"] = ""


                        #Second click
                        equivalencies[i].click()
                        time.sleep(2.5)
                        transferList = self.driver.find_elements_by_class_name('courseListContainer')[0]
                        details = transferList.find_elements_by_class_name('courseDetailContainer')
                        try:
                            creditsCont = transferList.find_element_by_class_name('courseCreditsLine')
                            credits = creditsCont.find_elements_by_tag_name('span')
                            # print(credits[0].text)
                            if credits[0].text == "Credits:":
                                jsonClass["from_course_credit_hours"] = credits[1].text

                            if len(details) > 1:
                                from_extra_credit_hours = []
                                for detail in details[1:]:
                                    try:
                                        detCont = detail.find_element_by_class_name('courseCreditsLine')
                                        detcredits = detCont.find_elements_by_tag_name('span')
                                        # print(detcredits[0].text)
                                        if detcredits[0].text == "Credits:":
                                            from_extra_credit_hours.append(detcredits[1].text)
                                    except:
                                        pass
                                        # print("No credit")
                                jsonClass["from_extra_credit_hours"] = str(from_extra_credit_hours)
                            else:
                                jsonClass["from_extra_credit_hours"] = ""

                        except:
                            # print("No credits")
                            pass

                        dixieList = self.driver.find_elements_by_class_name('courseListContainer')[1]
                        todetails = dixieList.find_elements_by_class_name('courseDetailContainer')
                        try:
                            creditsCont = dixieList.find_element_by_class_name('courseCreditsLine')
                            credits = creditsCont.find_elements_by_tag_name('span')
                            # print(credits[0].text)
                            if credits[0].text == "Credits:":
                                jsonClass["to_course_credit_hours"] = credits[1].text

                            if len(todetails) > 1:
                                from_extra_credit_hours = []
                                for detail in todetails[1:]:
                                    try:
                                        detCont = detail.find_element_by_class_name('courseCreditsLine')
                                        detcredits = detCont.find_elements_by_tag_name('span')
                                        # print(detcredits[0].text)
                                        if detcredits[0].text == "Credits:":
                                            from_extra_credit_hours.append(detcredits[1].text)
                                    except:
                                        # print("No credit")
                                        pass
                                jsonClass["to_extra_credit_hours"] = str(from_extra_credit_hours)
                            else:
                                jsonClass["to_extra_credit_hours"] = ""
                        except:
                            # print("No credits")
                            pass
                        
                        # pp = pprint.PrettyPrinter(indent=4)
                        # pp.pprint(jsonClass)

                        array.append(jsonClass)

                 
                        time.sleep(2)
                        self.driver.find_element_by_id('detail').find_element_by_class_name('ui-corner-top').click()
                        time.sleep(1.5)

                    my_file = open("utahJson/" + filename, "a")        # Open a file
                    my_file.write(json.dumps(array, indent=4))    # write a line to the file
                    my_file.write(",") 
                    my_file.close()    
                        
                    self.driver.find_element_by_id('equivs').find_element_by_class_name('ui-state-default').click()
                    time.sleep(1.5)
                    print(x)
    #     # Remove comma
        with open("utahJson/" + filename, 'rb+') as filehandle:
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()

        # add a ]
        my_file = open("utahJson/" + filename, "a")        # Open a file  # write a line to the file
        my_file.write("]") 
        my_file.close() 

def missingSchools():
    #Check if file is empty
    my_schools = []
    for filename in os.listdir('utahJson'):
        print(filename)
        filesize = os.path.getsize("utahJson/" + filename)
        if filesize == 0:
            print("The file is empty: " + str(filesize))
        else:
            f = open("utahJson/" + filename, "r")
            values = json.loads(f.read())
            for school in values:
                my_schools.append(school[0]['from_school'])
            f.close()
    my_schools = list(set(my_schools))

 # Open a file  # write a line to the file
    my_file = open("utahSchools.txt", "r")       
    lst = json.loads(my_file.read())
    my_file.close()

    with progressbar.ProgressBar(max_value=len(lst)) as bar:
        for school in range(len(lst)):
            bar.update(school)
            if lst[school][0] not in my_schools and lst[school][1] != "N/A":
                missing_schools.append(lst[school][1])

                
    
    print('missing_schools', missing_schools)

    return missing_schools


if __name__ == "__main__":

    a = searchPage(0)
    b = searchPage(1)
    c = searchPage(2)
    d = searchPage(3)
    e = searchPage(4)
    f = searchPage(5)
    g = searchPage(6)
    h = searchPage(7)
    i = searchPage(8)
    j = searchPage(9)
    k = searchPage(10)
    l = searchPage(11)
    m = searchPage(12)

    print('1')

    my_file = open("utahSchools.txt", "w")        # Open a file  # write a line to the file
    my_file.write(json.dumps(a.getNames())) 
    my_file.close()

    print('2')

    missing_schools = missingSchools()

    print('3')

    while missing_schools != []:
        t1 = multiprocessing.Process(target=a.updateJson, args=[13])
        t2 = multiprocessing.Process(target=b.updateJson, args=[13])
        t3 = multiprocessing.Process(target=c.updateJson, args=[13])
        t4 = multiprocessing.Process(target=d.updateJson, args=[13])
        t5 = multiprocessing.Process(target=e.updateJson, args=[13])
        t6 = multiprocessing.Process(target=f.updateJson, args=[13])
        t7 = multiprocessing.Process(target=g.updateJson, args=[13])
        t8 = multiprocessing.Process(target=h.updateJson, args=[13])
        t9 = multiprocessing.Process(target=i.updateJson, args=[13])
        t10 = multiprocessing.Process(target=j.updateJson, args=[13])
        t11 = multiprocessing.Process(target=k.updateJson, args=[13])
        t12 = multiprocessing.Process(target=l.updateJson, args=[13])
        t13 = multiprocessing.Process(target=m.updateJson, args=[13])

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        t9.start()
        t10.start()
        t11.start()
        t12.start()
        t13.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        t7.join()
        t8.join()
        t9.join()
        t10.join()
        t11.join()
        t12.join()
        t13.join()

        #clean up
        missing_schools = missingSchools()

    print('done')                       
          
