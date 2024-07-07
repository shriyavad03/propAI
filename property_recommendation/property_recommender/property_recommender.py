from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def property_recommender(data, bedrooms, min_price, max_price, location):
    # Normalize the location input to match the location names in the dataset
    location_normalized = location.strip().lower()

    # Filter by location first
    location_filtered_data = data[data['Location'].str.lower().str.contains(location_normalized)]
    print("Location Filtered Data:")
    print(location_filtered_data)

    # Filter by number of bedrooms
    bedrooms_filtered_data = location_filtered_data[location_filtered_data['No. of Bedrooms'] == bedrooms]
    print("Bedrooms Filtered Data:")
    print(bedrooms_filtered_data)

    # Filter by price range
    price_filtered_data = bedrooms_filtered_data[
        (bedrooms_filtered_data['Price'] >= min_price) & 
        (bedrooms_filtered_data['Price'] <= max_price)
    ]
    print("Price Filtered Data:")
    print(price_filtered_data)

    if price_filtered_data.empty:
        print(f"No properties found for location '{location}' with the given criteria.")
        return None

    # Combine relevant columns into a single 'Description' column for similarity calculation
    price_filtered_data['Description'] = price_filtered_data['Location'] + ' ' + price_filtered_data['No. of Bedrooms'].astype(str)
    print("Price Filtered Data with Description:")
    print(price_filtered_data)

    # Compute similarity based on the combined description
    count_vectorizer = CountVectorizer()
    description_matrix = count_vectorizer.fit_transform(price_filtered_data['Description'].values.astype('U'))
    similarity_matrix = cosine_similarity(description_matrix, description_matrix)
    print("Similarity Matrix:")
    print(similarity_matrix)

    # Get indices of similar properties
    similar_indices = similarity_matrix.argsort()[:, ::-1]
    print("Similar Indices:")
    print(similar_indices)

    # Get top 5 similar properties excluding the property itself
    top_indices = similar_indices[0, 1:6]
    print("Top Indices:")
    print(top_indices)

    # Get recommended properties
    recommended_properties = price_filtered_data.iloc[top_indices]
    print("Recommended Properties:")
    print(recommended_properties)

    return recommended_properties
