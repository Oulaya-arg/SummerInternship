import threading
import queue
import pandas as pd
import streamlit as st
from io import StringIO 
#import seaborn as sns
#import matplotlib.pyplot as plt


st.title('Word Count using MapReduce algorithm')


text = st.text_input('Insert the text', '')
#st.write('Your input', text)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
     # To read file as bytes:
     bytes_data = uploaded_file.getvalue()
     #st.write(bytes_data)

     # To convert to a string based IO:
     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
     #st.write(stringio)

     # To read file as string:
     text = stringio.read()
     #st.write(string_data)

def data_clean(text):
    NoNumbers = ''.join([i for i in text if not i.isdigit()]) #Removing numbers
    NoNumbers = text.lower()                                  #Making the text to lower case
    import re
    onlyText = re.sub(r"[^a-z\s]+",' ',NoNumbers)             #Removing punctuation
    finaltext = "".join([s for s in onlyText.strip().splitlines(True) if s.strip()]) #Removing the null lines
    return finaltext

def splitlines(text,a):
    linessplit = text.splitlines() #Splitting the lines into a list
    split1 = linessplit[0:a]       #Creating the first split with the first "a" number of lines into split 1
    split2 = linessplit[a:]        #Creating the second split with the first "a" number of lines into split 2
    return split1,split2
 
def mapper(text,out_queue):
    keyval = []
    for i in text:
      wordssplit = i.split()
      for j in wordssplit:
        keyval.append([j,1])      #Appending each word in the line with 1 and storing it in ["word",1] format in a nested list
    out_queue.put(keyval)

def sortedlists(list1,list2):
    out = list1 + list2             #Appending the two input lists into a single list
    out.sort(key= lambda x :x[0])   #Sorting the lists based on the first element of the list which is the "word"
    return out

def partition(sorted_list) :
    sort1out = []
    sort2out = []
    for i in sorted_list:
      if i[0][0] < 'n':             #Partitioning the sorted word list into two separate lists 
        sort1out.append(i)          #with first list containing words starting with a-m and n-z into second
      else : sort2out.append(i)
    return sort1out,sort2out

def reducer(part_out1,out_queue) :
    sum_reduced = []
    count = 1
    for i in range(0,len(part_out1)):
      if i < len(part_out1)-1:
        if part_out1[i] == part_out1[i+1]:
          count = count+1                              #Counting the number of words
        else : 
          sum_reduced.append([part_out1[i][0],count])  #Appending the word along with count to sum_reduced list as ["word",count]
          count = 1 
      else: sum_reduced.append(part_out1[i])          #Appending the last word to the output list    
    out_queue.put(sum_reduced)
  
  
def multi_thread_function(func,map1_input,map2_input):  #func is the function to be used with two threads taking two inputs map1_input and map2_input
    my_queue1 = queue.Queue()  #Using queue to store the values of mapper output to use them in sort function
    my_queue2 = queue.Queue()
    t1 = threading.Thread(target=func, args=(map1_input,my_queue1)) 
    t2 = threading.Thread(target=func, args=(map2_input,my_queue2))  
    t1.start()                 #Starting the execution of thread1
    t2.start()                 #Starting the execution of thread2 to run simultaneously with thread1
    t1.join()                  #Waiting for the thread1 to be completely executed
    t2.join()                  #Waiting for the thread2 to be completely executed
    list1out = my_queue1.get() #Getting the values from the queue into a variable to return its value
    list2out = my_queue2.get()
    return list1out,list2out
  
def main_function(self):  
    cleantext = data_clean(text)
    linessplit = splitlines(cleantext,5000)
    mapperout = multi_thread_function(mapper,linessplit[0],linessplit[1]) 
    sortedwords = sortedlists(mapperout[0],mapperout[1])
    slicedwords = partition(sortedwords)
    reducerout = multi_thread_function(reducer,slicedwords[0],slicedwords[1])
    return reducerout[0]+reducerout[1]

output = main_function(text)
df=pd.DataFrame(output)
df.rename({0:'word',1:'counts'},axis='columns',inplace=True)
st.write('The result:')
st.write(df)



def convert_df(df):
   return df.to_csv()


csv = convert_df(df)

st.download_button(
   "Press to Download",
   csv,
   "MapReduce.csv",
   "text/csv",
   key='download-csv'
)




  # Add some matplotlib code !
