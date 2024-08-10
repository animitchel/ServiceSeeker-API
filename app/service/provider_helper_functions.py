
def get_max_ratings(queryset) -> int:
    """Get the maximum rating for a service and return munis 1"""
    max_rating = max(
        (ii.rating for i in queryset for ii in i.user_reviews_rating.all()
         ), default=0)
    return max_rating - 1
