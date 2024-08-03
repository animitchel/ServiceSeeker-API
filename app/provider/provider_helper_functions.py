
def get_max_rating(queryset) -> int:
    """Get the maximum rating for a service and return munis 1"""
    max_rating = 0
    for i in queryset:
        for ii in i.user_reviews_rating.all():
            if ii.rating > max_rating:
                max_rating = ii.rating
    return max_rating - 1
