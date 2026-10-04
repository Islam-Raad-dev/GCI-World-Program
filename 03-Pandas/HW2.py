def homework(anime_data_extracted):
    
    result = anime_data_extracted.groupby('Type')['Score'].mean().sort_values(ascending=False)
    
    return result