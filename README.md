## Overview

Chromelogger is a Python library for logging variables to the Google Chrome console using the Chrome Logger extension.

## Getting Started

1. Install [Chrome Logger](https://chrome.google.com/extensions/detail/noaneddfkdjfnfdakjjmocngnfkfehhd) from the Chrome Web Store

2.  Click the extension icon to enable on the current tab's domain

    ![toggling](http://cdn.craig.is/img/chromelogger/toggle.gif)

3. Install the Python library

    ```python
    pip install chromelogger
    ```

4.  Start logging

    ```python
    import chromelogger as console
    console.log('Hello console!')
    ```

## Sending Headers

Since every framework deals with setting headers slightly differently the library stores the header information and it is up to you to send it at the end of your request.

### Using with Django

The library includes a middleware for using with Django.  All you have to do is in your ``settings.py`` file make sure to update your list of middleware and add

```python
MIDDLEWARE_CLASSES = (
    'chromelogger.DjangoMiddleware'
)
```

After that you can import the chromelogger class from any file in your application and add logs.

### Using with Tornado

Using with tornado is slightly more complicated.  You have to make sure you are using your own custom request handler and that all your requests you want logged inherit from that.  Here is an example of how you would implement it

```python
import tornado
import chromelogger

class CustomRequestHandler(tornado.web.RequestHandler):
    def finish(self, chunk=None):
        header = chromelogger.get_header()

        if header is not None:

            # in Tornado RequestHandler.set_header() function limits
            # header length to 1000 bytes, so set directly for this case
            self._headers[header[0]] = header[1]

        return super(CustomRequestHandler, self).finish(chunk=chunk)
```

## API Documentation

