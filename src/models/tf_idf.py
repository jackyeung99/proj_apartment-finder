
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def get_tf(df):
    df['UnitAmenity'] = df['UnitAmenity'].fillna('')
    
    # Step 1: Group the amenities by UnitId and concatenate them into a single string
    df_grouped = df.groupby('UnitId')['UnitAmenity'].apply(lambda x: ' '.join(x)).reset_index()

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df_grouped['UnitAmenity'])


    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
    tfidf_df['UnitId'] = df_grouped['UnitId'].values

    # Step 6: Reorder columns to have 'UnitId' first
    tfidf_df = tfidf_df[['UnitId'] + [col for col in tfidf_df.columns if col != 'UnitId']]

    return tfidf_df