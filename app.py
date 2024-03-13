from flask import Flask, render_template, request, redirect
from nltk.tokenize import sent_tokenize
from nltk import RegexpTokenizer
from bs4 import BeautifulSoup
from itertools import chain
import pickle
import re
from nltk import *



#Function tokenizeJobtitle will generate the tokens

def tokenizeJobtitle(data): 
    
    jobs_lower= [data.lower()] #lowercase
    
    sentences = sent_tokenize(jobs_lower[0])
    pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?"   # tokenize each sentence
    tokenizer = RegexpTokenizer(pattern) 
    token_lists = [tokenizer.tokenize(sen) for sen in sentences]
    
    # merge them into a list of tokens
    tokenised_info = list(chain.from_iterable(token_lists))
    return tokenised_info


# The idea of the first parameter is to give Flask an idea of what belongs to my application.
# This name is used to find resources on the filesystem, can be used by extensions to improve debugging 
# information and a lot more.

app = Flask(__name__)


# @app.route decorator registers the decorated function as a route. 
#Function index, accounting_finance and so on  are  register as handles for the URL "/", "/accounting_finance" and so on. 
# ender_template() function returns the static web pages

@app.route('/')
def index():   
    return render_template('home.html')

@app.route('/accounting_finance')
def accounting_finance():   
    return render_template('accounting_finance.html')


@app.route('/engineering')
def engineering():   
    return render_template('engineering.html')

@app.route('/healthcare_nursing')
def healthcare_nursing():   
    return render_template('healthcare_nursing.html')

@app.route('/sales')
def sales():   
    return render_template('sales.html')


@app.route('/contact')
def contact():   
    return render_template('contact.html')


# I create a routes for all job description file. One for each job file.
#I will create routes that take passed-in arguments from the user.

@app.route('/<folder>/<filename>')
def article(folder,filename):   
    return render_template('/' + folder + '/' + filename + '.html')


# admin.html file has the structure where the user will input title and description information. 
# Function admin() read the title and description provide by user. 
# Then, if the user click on "Claasify" The model will predict the category of this new job advertisement.

@app.route('/admin', methods=['GET','POST'])
def admin():
    # Read the content and title
    if request.method=="POST":
        f_title = request.form['title']
        f_content = request.form['description']
        
        # Classify the content
        if request.form['button'] == 'Classify':
            tokenized_title=tokenizeJobtitle(f_title)
            tokenized_cont=tokenizeJobtitle(f_content)
            tokenize_title_descrip= tokenized_title + tokenized_cont
            
            count_vectorizer=pickle.load(open("CountVectorizer.pickle", "rb"))
            
            count_features=count_vectorizer.fit_transform(' '.join(x) for x in [tokenize_title_descrip])
        
            pkl_filename="jobs_LR.pkl"
            with open (pkl_filename, "rb") as file: 
                model= pickle.load(file)
    
            y_pred=model.predict(count_features)
            y_pred= y_pred[0]
    
            #predicted_message="The category of this job is {}.".format(y_pred)
            return render_template('admin.html', prediction=y_pred, title=f_title, description=f_content)
        
         
         # If the user click on save, it will verify is the space is not empty or belong to the
         # correct categories avaibales if these happen, it will return a red message. 
         #code author: Dr. Minyi Li  Some parts were modified. 
  
        if request.form['button'] == 'Save':
            # First check if the recommended category is empty
            cat_recommend = request.form['category']
            if cat_recommend == '':
                return render_template('admin.html', prediction=cat_recommend,
                                       title=f_title, description=f_content,
                                       category_flag='Recommended category must not be empty.')
            elif cat_recommend not in ['Accounting_Finance', 'Engineering', 'Healthcare_Nursing', 'Sales']:
                return render_template('admin.html', prediction=cat_recommend,
                                       title=f_title, description=f_content,
                                       category_flag='Recommended category must belong to: Accounting_Finance, Engineering, Healthcare_Nursing, Sales.')
             
             
            #Otherwise, It will read a html template where the new job will be saved it. 
            # First read the html template  and save it in "soup".
            else:
                
                soup = BeautifulSoup(open('templates/job_template.html'), 'html.parser')
                    
                # Then adding the title and the content into the template
                # First, add the title
                div_page_title = soup.find('div', { 'class' : 'title' })
                title = soup.new_tag('h1', id='data-title')                
                title.append(f_title)
                div_page_title.append(title)

                # Second, add the description information
                div_page_content = soup.find('div', { 'class' : 'data-article' })
                content = soup.new_tag('p')
                content.append(f_content)
                div_page_content.append(content)

                # Finally, write to a new html file
                title_words=re.findall(r"\w+", f_title)
                title_only_words=[]
                for word in title_words:
                    title_only_words.append(word)
                filename = '_'.join( title_only_words)
                filename =  cat_recommend + '/' + filename + ".html"
                with open("templates/" + filename, "w", encoding='utf-8') as file:
                    print(filename)
                    file.write(str(soup))

                # Redirect to the newly-generated news article
                # Here, new information is posted in a new html file and user can see it.
                return redirect('/' + filename.replace('.html', ''))
            
            
         #If the user click on submit   
        elif request.form['button'] == 'submit':
            # It will access to the information on select a new category.
            cat_recommend = request.form['select']
            # Then, it will read the new template where the new information will be saved it.
            soup = BeautifulSoup(open('templates/job_template.html'), 'html.parser')
                    
            # Then adding the title and the description content to the template
            div_page_title = soup.find('div', { 'class' : 'title' })
            title = soup.new_tag('h1', id='data-title')
            title.append(f_title)
            div_page_title.append(title)
            
            div_page_content = soup.find('div', { 'class' : 'data-article' })
            content = soup.new_tag('p')
            content.append(f_content)
            div_page_content.append(content)

            # Finally write to a new html file
            title_words=re.findall(r"\w+", f_title)
            title_only_words=[]
            for word in title_words:
                title_only_words.append(word)
            filename = '_'.join(title_only_words)
            filename =  cat_recommend + '/' + filename + ".html"
            with open("templates/" + filename, "w", encoding='utf-8') as file:
                print(filename)
                file.write(str(soup))

            # Redirect to the newly-generated news job 
            return redirect('/' + filename.replace('.html', ''))
               
    else:
        return render_template('admin.html')

        
    


    
