from flask import Flask, render_template, request, redirect, flash
import pickle
import numpy as np

# Load data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

@app.route('/')
def index():
    top_books = popular_df.head(20)
    return render_template(
        'index.html',
        book_name=list(top_books['Book-Title'].values),
        author=list(top_books['Book-Author'].values),
        image=list(top_books['Image-URL-M'].values),
        votes=list(top_books['num_ratings'].values),
        rating=list(top_books['avg_rating'].values)
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    if user_input not in pt.index:
        error_message = f"No recommendations found for '{user_input}'. Please try a different book name."
        return render_template('recommend.html', error=error_message)
    
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Save the message to a file
    with open('messages.txt', 'a') as file:
        file.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n{'-'*40}\n")
    
    # Flash a success message
    flash("Thank you for reaching out! We will get back to you soon.", "success")

    return redirect('/contact')

if __name__ == '__main__':
    app.run(debug=True)
