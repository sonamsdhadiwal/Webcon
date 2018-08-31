from __future__ import division
from sklearn.feature_extraction.text import TfidfVectorizer
import tkinter as tk
from random import randint
import numpy as np
from bs4 import BeautifulSoup  # For HTML parsing
import urllib  # Website connections
from urllib.request import urlopen
import re  # Regular expressions
from time import sleep  # To prevent overwhelming the server between connections
from collections import Counter  # Keep track of our term counts
from nltk.corpus import stopwords  # Filter out stopwords, such as 'the', 'or', 'and'
import pandas as pd  # For converting results to a dataframe and bar chart plots
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import operator
import os
import string
import math
import webbrowser

root = tk.Tk()

# Create N frames on top of each other

image = tk.PhotoImage(file="P://Study/Project_870/FinalPresentation/WebFiles/webcon.gif")
label = tk.Label(image=image)
label.pack()

N = 4
frames = []
for n in range(N):
    frame = tk.Frame(root)
    frame.pack(side='top', anchor='w')
    # Store the current frame reference in "frames"
    frames.append(frame)

# Add some widgets in each frame
entryboxes = {frame: [] for frame in frames}
random_width = 15 + randint(0,9)
label5 = tk.Label(frame,text = "job title")
label5.pack(side='left')
e = tk.Entry(frame, width = random_width)
e.pack(side='left')

label6 = tk.Label(frame,text = "city")
label6.pack(side='left')
f = tk.Entry(frame, width = random_width)
f.pack(side='left')

label7 = tk.Label(frame,text = "state")
label7.pack(side='left')
g = tk.Entry(frame, width = random_width)
g.pack(side='left')

def callback():
    seattle_info=skills_info(city=f.get(), state=g.get())

def browsefunc():
    filename1 = tk.filedialog.askopenfilename()
    pathlabel.config(text=filename1)


browsebutton = tk.Button(root, text="Upload CV", command=browsefunc)
browsebutton.pack(side='left',padx = 50)
pathlabel = tk.Label(root)
pathlabel.pack()


def text_cleaner(website):
    try:
        site = urllib.request.urlopen(website).read().decode('utf-8')  # Connect to the job posting
    except:
        return  # Need this in case the website isn't there anymore or some other weird connection problem

    soup_obj = BeautifulSoup(site, 'html.parser')  # Get the html from the site

    for script in soup_obj(["script", "style"]):
        script.extract()  # Remove these two elements from the BS4 object

    text = soup_obj.get_text()  # Get the text from this
    lines = (line.strip() for line in text.splitlines())  # break into lines
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))  # break multi-headlines into a line each

    def chunk_space(chunk):
        chunk_out = chunk + ' '  # Need to fix spacing issue
        return chunk_out

    text = ''.join(chunk_space(chunk) for chunk in chunks if chunk).encode('utf-8')  # Get rid of all blank lines and ends of line
    try:
        text = str(
            text.decode('unicode_escape').encode('ascii', 'ignore'))  # Need this as some websites aren't formatted
    except:  # in a way that this works, can occasionally throw
        return  # an exception

    text = re.sub("[^a-zA-Z.+3]", " ", text)
    text = text.lower().split()  # Go to lower case and split them apart
    stop_words = set(stopwords.words("english"))  # Filter out any stop words
    text = [w for w in text if not w in stop_words]
    text = list(set(text))  # Last, just get the set of these. Ignore counts (we are just looking at whether a term existed
    # or not on the website)
    return text


def skills_info(city=None, state=None):
    final_job = e.get()
    print("Job is",final_job)
    final_job = final_job.split()
    #print("Job is(after splitting)", final_job)
    final_job = '+'.join(word for word in final_job)
    #print("Job is(after joining)", final_job)
    print("city is",f.get())
    print("state is",g.get())
    if city is not None:
        final_city = city.split()
        final_city = '+'.join(word for word in final_city)
        final_site_list = ['http://www.indeed.com/jobs?q=%22', final_job, '%22&l=', final_city,'%2C+', state]  # Join all of our strings together so that indeed will search correctly
    else:
        final_site_list = ['http://www.indeed.com/jobs?q="', final_job, '"']
    final_site = ''.join(final_site_list)  # Merge the html address together into one string
    base_url = 'http://www.indeed.com'

    print("Base url is",base_url)
    try:
        html = urllib.request.urlopen(final_site).read().decode('utf-8')  # Open up the front page of our search first
    except:
        print('Please check your internet connection! Unable to connect http://www.indeed.com!!')  # In case the city is invalid
        return
    soup = BeautifulSoup(html, 'html.parser')  # Get the html from the first page

    num_jobs_area = str(soup.find(id='searchCount').string.encode('utf-8'))  # Now extract the total number of jobs found
    job_numbers = re.findall('\d+', num_jobs_area)  # Extract the total jobs found from the search result

    if len(job_numbers) > 3:  # Have a total number of jobs greater than 1000
        total_num_jobs = (int(job_numbers[2]) * 1000) + int(job_numbers[3])
    else:
        total_num_jobs = int(job_numbers[1])

    city_title = city
    if city is None:
        city_title = 'Nationwide'

    print('We found', total_num_jobs, 'jobs in,', city_title)  # Display how many jobs were found

    num_pages = total_num_jobs / 10  # This will be how we know the number of times we need to iterate over each new
    # search result page
    job_descriptions = []  # Store all our descriptions in this list
    num_pages = int(num_pages)
    # print(num_pages)
    for i in range(1, int(num_pages) + 1):  # Loop through all of our search result pages
        #print('Getting page' + str(i))
        start_num = str(i * 10)  # Assign the multiplier of 10 to view the pages we want
        current_page = ''.join([final_site, '&start=', start_num])
        # Now that we can view the correct 10 job returns, start collecting the text samples from each
        #print("Current Page",current_page)
        html_page = urllib.request.urlopen(current_page).read().decode('utf-8')  # Get the page
        page_obj = BeautifulSoup(html_page, 'html.parser')  # Locate all of the job links
        job_link_area = page_obj.find(id='resultsCol')  # The center column on the page where the job postings exist
        # print(type(page_obj))

        job_URLS = [base_url + str(link.get('href')) for link in job_link_area.find_all('a')]  # Get the URLS for the jobs

        job_URLS = [x for x in job_URLS if 'clk' in x]  # Now get just the job related URLS
        all_job_urls=[]
        #print("Job urls",job_URLS)
        #print("Number of jobs found after discarding irrelevant jobs are:", len(job_URLS))
        for j in range(0, len(job_URLS)):
            #print("Print job url of j==>",job_URLS[j])
            all_job_urls.append(job_URLS[j])
            final_description = text_cleaner(job_URLS[j])
            # print("Final description",final_description)
            if final_description:  # So that we only append when the website was accessed correctly
                job_descriptions.append(final_description)
            sleep(1)  # So that we don't be jerks. If you have a very fast internet connection you could hit the server a lot!
        print("URL's for all the jobs are==>",all_job_urls)
        print('All job postings collected successfully!')
        #print('There were', len(job_descriptions), 'jobs successfully found.')
        #file1 = open('P://Study/Project_870/test1.txt', 'w')
        counter=0
        for item in job_descriptions:
            file1=open('P://Study/Project_870/Text/'+str(counter)+'.txt',"w")
            file1.write("%s\n" % item)
            file1.close()
            counter = counter+1
    print("Successfully created all the neccessary text files!!")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import operator
    import os

    counter1 = 0
    list1 = []
    path1 = 'P://Study/Project_870/Text/'
    for filename in os.listdir(path1):
        if filename.endswith('.txt'):
            #print(filename)
            #file1= open(os.path.join(path1,filename),'r')
            with open(os.path.join(path1,filename))as file1:
                filename = str(file1.readlines())
                list1.append(filename)
    #print(list1)
    #print("successfully created list")
    with open("P://Study/Project_870/PDFs/Huxley1.txt", "r") as myfile1:
        document_original = str(myfile1.readlines())

    #print(document_original)
    # insert document_original at first position in list
    # create for loop inside a list
    list1.insert(0,document_original)
    documents = [filename1 for filename1 in list1]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    print("tfidf matrix is",tfidf_matrix)
    print(tfidf_matrix.shape)
    document_1 = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

    flat_list = []
    for sublist in document_1:
        for item in sublist:
            flat_list.append(item)
    del flat_list[0]
    flat_list = ['%.4f' % elem for elem in flat_list]
    flat_list1 = list(map(float, flat_list))
    print('List with cosine similarity after rounding it to four digits is', flat_list1)

    #[float(i) for i in flat_list1]
    #print('Flat file list is',flat_list1)
    flat_list2=[]
    for i in flat_list1:
        flat_list2.append(float(i))
    cosine_similarity_dictionary = dict(zip(documents, flat_list2))
    print("cosine:",cosine_similarity_dictionary)

    #Extra dictinary
    dictionary1 = dict(zip(all_job_urls,flat_list2))
    sorted_dictionary1 = sorted(dictionary1.items(), key=operator.itemgetter(1), reverse=True)
    print("Arranging the links in ascending order based on cosine similarity",sorted_dictionary1)

    def callback1(event):
        #for key, value in sorted_dictionary1.items():
        for i in range(0,10):
            webbrowser.open_new(sorted_dictionary1[i][0])

    link = tk.Label(root, text="Suggested Jobs", fg="blue", cursor="hand2")
    link.pack()
    link.bind("<Button-1>", callback1)

    #print('Sorting dictionary according to value')
    #sorted_dictionary = sorted(cosine_similarity_dictionary.items(), key=operator.itemgetter(1), reverse=True)
    #print(sorted_dictionary)



#seattle_info = skills_info(city='Seattle', state='WA')
b = tk.Button(frame, text="submit", width=10, command=callback)
b.pack(side = 'left',padx = 10, pady = 10)
print(e.get())
# Launch the app


root.mainloop()
