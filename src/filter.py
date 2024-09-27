import pandas as pd

# File paths to your TSV files
title_basics_file = 'title.basics.tsv'
title_ratings_file = 'title.ratings.tsv'

# Step 1: Load the title basics file, focusing on the ID and type (movie, tvshow)
title_basics = pd.read_csv(title_basics_file, sep='\t', usecols=['tconst', 'titleType'])
filtered_titles = title_basics[title_basics['titleType'].isin(['movie', 'tvSeries'])]

# Step 2: Load the title ratings file, focusing on the ID, averageRating, and number of votes
title_ratings = pd.read_csv(title_ratings_file, sep='\t', usecols=['tconst', 'averageRating', 'numVotes'])
filtered_ratings = title_ratings[title_ratings['numVotes'] >= 2000]

# Step 3: Merge the two datasets on the 'tconst' column (which is the ID)
merged_data = pd.merge(filtered_titles, filtered_ratings, on='tconst')

merged_data.to_csv('filtered_imdbID.csv', index=False)

movies_data = merged_data[merged_data['titleType'] == 'movie']
tv_series_data = merged_data[merged_data['titleType'] == 'tvSeries']

# Step 5: Save the filtered IMDb IDs to separate CSV files
movies_data[['tconst']].to_csv('filtered_movies_imdbID.csv', index=False)
tv_series_data[['tconst']].to_csv('filtered_tvSeries_imdbID.csv', index=False)

