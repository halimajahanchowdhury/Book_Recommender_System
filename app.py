import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Book Recommender System', page_icon='📚', layout='wide')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POPULAR_PATH = os.path.join(BASE_DIR, 'popular.pkl')
PT_PATH = os.path.join(BASE_DIR, 'pt.pkl')
BOOKS_PATH = os.path.join(BASE_DIR, 'books.pkl')
SIMILARITY_PATH = os.path.join(BASE_DIR, 'similarity_scores.pkl')

@st.cache_data
def load_data():
    popular_df = pickle.load(open(POPULAR_PATH, 'rb'))
    pt = pickle.load(open(PT_PATH, 'rb'))
    books = pickle.load(open(BOOKS_PATH, 'rb'))
    similarity_scores = pickle.load(open(SIMILARITY_PATH, 'rb'))
    return popular_df, pt, books, similarity_scores

popular_df, pt, books, similarity_scores = load_data()


def recommend(book_name: str):
    index = np.where(pt.index == book_name)[0][0]
    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        if not temp_df.empty:
            row = temp_df.iloc[0]
            data.append({
                'title': row['Book-Title'],
                'author': row['Book-Author'],
                'image': row['Image-URL-M'],
                'score': float(i[1])
            })
    return data


st.title('📚 Book Recommender System')
st.write('Get popular books and personalized book recommendations.')

tab1, tab2 = st.tabs(['⭐ Popular Books', '🔎 Recommend Books'])

with tab1:
    st.subheader('Top 50 Popular Books')
    cols = st.columns(4)
    for idx, row in popular_df.iterrows():
        with cols[idx % 4]:
            st.image(row['Image-URL-M'], use_container_width=True)
            st.markdown(f"**{row['Book-Title']}**")
            st.caption(f"Author: {row['Book-Author']}")
            st.caption(f"Rating: {row['avg_rating']:.2f}")
            st.caption(f"Votes: {int(row['num_ratings'])}")

with tab2:
    st.subheader('Find Similar Books')
    book_list = sorted(pt.index.tolist())
    selected_book = st.selectbox('Choose a book', book_list)

    if st.button('Recommend'):
        recommendations = recommend(selected_book)
        if recommendations:
            cols = st.columns(len(recommendations))
            for col, book in zip(cols, recommendations):
                with col:
                    st.image(book['image'], use_container_width=True)
                    st.markdown(f"**{book['title']}**")
                    st.caption(f"Author: {book['author']}")
                    st.caption(f"Similarity: {book['score'] * 100:.2f}%")
        else:
            st.warning('No recommendations found.')
