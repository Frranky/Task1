from wsgiref.simple_server import make_server
from datetime import datetime
import json
import pytz
from tzlocal import get_localzone
from pytz import timezone, UTC

def application(environ, start_response):
    """WSGI application.
    """
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    if method == 'GET':
        if path == '/':
            tz = UTC
        else:
            tz_name = path[1:]  # Remove leading '/'
            try:
                tz = timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                start_response('400 Bad Request', [('Content-type', 'text/html')])
                return [b'Invalid time zone name.']
        current_time = datetime.now(tz).strftime('%H:%M:%S')
        start_response('200 OK', [('Content-type', 'text/html')])
        return [bytes(f'<h1>Current time in {tz.zone} is: {current_time}</h1>', 'utf-8')]

    elif method == 'POST':
        if path == '/api/v1/convert':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
                data = json.loads(request_body)
                date_str = data['date']
                source_tz = data['tz']
                target_tz = environ.get('QUERY_STRING').split('=')[1]

                source_tz = timezone(source_tz)
                target_tz = timezone(target_tz)

                dt = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
                dt_source = source_tz.localize(dt)
                dt_target = dt_source.astimezone(target_tz)

                converted_date = dt_target.strftime('%m.%d.%Y %H:%M:%S')
                start_response('200 OK', [('Content-type', 'text/plain')])
                return [bytes(f'Converted date: {converted_date}', 'utf-8')]

            except (json.JSONDecodeError, KeyError):
                start_response('400 Bad Request', [('Content-type', 'text/plain')])
                return [bytes('Invalid JSON data or missing required parameters.', 'utf-8')]

        elif path == '/api/v1/datediff':
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
                request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
                data = json.loads(request_body)

                first_date_str = data['first_date']
                first_tz = data['first_tz']
                second_date_str = data['second_date']
                second_tz = data['second_tz']

                first_tz = timezone(first_tz)
                second_tz = timezone(second_tz)

                first_dt = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
                first_dt_aware = first_tz.localize(first_dt)

                # Handle different date formats for second_date
                if ' ' in second_date_str:
                    second_dt = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
                else:
                    second_dt = datetime.strptime(second_date_str, '%Y-%m-%d %H:%M:%S')
                second_dt_aware = second_tz.localize(second_dt)

                time_difference = (first_dt_aware - second_dt_aware).total_seconds()

                start_response('200 OK', [('Content-type', 'text/plain')])
                return [bytes(f'Time difference: {time_difference} seconds', 'utf-8')]

            except (json.JSONDecodeError, KeyError):
                start_response('400 Bad Request', [('Content-type', 'text/plain')])
                return [bytes('Invalid JSON data or missing required parameters.', 'utf-8')]
    else:
        start_response('404 Not Found', [('Content-type', 'text/html')])
        return [bytes('<h1>Not Found</h1>', 'utf-8')]

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
