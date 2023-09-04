This project was made for estimate the required number of truckers un the next day. 

A brief explanation of its functionation: first bring the data from topus, then make scrapping over
tps, sti and dpw pages to capture the retreats that are not in the bbdd. the following step is to 
process the data to make it functional for the model. and then we run the milp. finally the result is 
delivered by a visualization of the general operation. 

scrapper: use selenium to download the xlsx from the sti, tps and dpw pages. 

df_consumer: process the data to make it usable.

utils: we unificate the data from topus and from the scrapper, then we standarizate the data 
in ordewr to use it in our model. in this script we can find how to parameterize the travels durations.

models: here we define our milp using the dictionaries and lists from the past steps. we weve the functions 
nessesries to run the model. here we call gantt, where we make the vizualization. 

gantt: make the plot and others documents required 

