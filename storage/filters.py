from django.contrib.admin.filters import AllValuesFieldListFilter, \
    RelatedOnlyFieldListFilter


class DropDownFilter(AllValuesFieldListFilter):
    """
    See: https://stackoverflow.com/questions/5429276/how-to-change-the-django-admin-filter-to-use-a-dropdown-instead-of-list
    """
    template = 'admin/dropdown_filter.html'


class RelatedDropDownFilter(RelatedOnlyFieldListFilter):
    """
    """
    template = 'admin/dropdown_filter.html'
