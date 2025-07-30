from datetime import datetime

from ..api.utils import datetime_url_format

def apply_talk_filters(self, queryset):
    """
    Você pode filtrar a lista usando os seguintes parâmetros na URL:
    - `date`: Filtra por data específica. Ex: /talks/?date=2025-07-27T14:30
    - `start_date`: Filtra talks a partir de uma data. Ex: /talks/?start_date=2025-07-27T00:00
    - `end_date`: Filtra talks até uma data. Ex: /talks/?end_date=2025-07-30T23:59
    - `title`: Filtra por título da talk. Ex: /talks/?title=Python
    - `mode`: Filtra por modalidade da talk (Online ou presencial). Ex: /talks/?mode=ON
    """
    def _parse_datetime(datetime_string):
        try:
            return datetime.strptime(datetime_string, datetime_url_format) # Usando a formatação de data 'datetime_url_format' da ../api/utils
        except ValueError:
            return None

    date = self.request.query_params.get('date')
    if date:
        datetime_obj = _parse_datetime(date)
        if datetime_obj:
            queryset = queryset.filter(start_time__date=datetime_obj.date())

    start_date = self.request.query_params.get('start_date')
    if start_date:
        start_datetime_obj = _parse_datetime(start_date)
        if start_datetime_obj:
            queryset = queryset.filter(start_time__gte=start_datetime_obj)

    end_date = self.request.query_params.get('end_date')
    if end_date:
        end_datetime_obj = _parse_datetime(end_date)
        if end_datetime_obj:
            queryset = queryset.filter(start_time__lte=end_datetime_obj)

    title = self.request.query_params.get('title')
    if title:
        queryset = queryset.filter(title__icontains=title)

    mode = self.request.query_params.get('mode')
    if mode:
        queryset = queryset.filter(mode=mode)

    return queryset
