def homework(anime_data, metric_column, n):
    df = anime_data.copy()

    df = df.sort_values(metric_column, ascending=False)

    ranks = df[metric_column].rank(method='first', ascending=False)
    groups = pd.qcut(ranks, n, labels=False)

    result = df.groupby(groups)[metric_column].sum() / df[metric_column].sum()

    result = result.sort_values(ascending=False)
    result.index = [f"Group {i}" for i in range(1, n + 1)]
    result.name = None

    return result