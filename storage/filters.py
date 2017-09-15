from django.contrib.admin.filters import AllValuesFieldListFilter, \
    RelatedOnlyFieldListFilter, SimpleListFilter


class DropDownFilter(AllValuesFieldListFilter):
    """
    See: https://stackoverflow.com/questions/5429276/how-to-change-the-django-admin-filter-to-use-a-dropdown-instead-of-list
    """
    template = 'admin/dropdown_filter.html'


class RelatedDropDownFilter(RelatedOnlyFieldListFilter):
    """
    """
    template = 'admin/dropdown_filter.html'


class FieldOfResearchFilter(SimpleListFilter):
    """
    A filter that works with FOR codes: filters by the first two digits of the
    FOR code.
    """
    title = 'FOR code'

    parameter_name = 'code'

    codes = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
             '11', '12', '13', '14', '15', '16', '17', '18', '19',
             '20', '21', '22', '99'
             ]

    def queryset(self, request, queryset):
        try:
            index = self.codes.index(self.value())
            return queryset.filter(code__gte=self.codes[index],
                                   code__lt=self.codes[index + 1])
        except ValueError as ve:
            return queryset

    def lookups(self, request, model_admin):
        return (
            ('01', 'Mathematical Sciences'),
            ('02', 'Physical Sciences'),
            ('03', 'Chemical Sciences'),
            ('04', 'Earth Sciences'),
            ('05', 'Environmental Sciences'),
            ('06', 'Biological Sciences'),
            ('07', 'Agriculture and Veterinary Sciences'),
            ('08', 'Information and Computing Sciences'),
            ('09', 'Engineering'),
            ('10', 'Technology'),
            ('11', 'Medical and Health Sciences'),
            ('12', 'Built Environment and Design'),
            ('13', 'Education'),
            ('14', 'Economics'),
            ('15', 'Commerce, Management, Tourism and Services'),
            ('16', 'Studies in Human Society'),
            ('17', 'Psychology and Cognitive Sciences'),
            ('18', 'Law and Legal Studies'),
            ('19', 'Studies in Creative Arts and Writing'),
            ('20', 'Language, Communication and Culture'),
            ('21', 'History and Archaeology'),
            ('22', 'Philosophy and Religious Studies'),
        )
