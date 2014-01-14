## Overview

Chromelogger is a Python library for logging variables to the Google Chrome console using the Chrome Logger extension.

For more information about Chrome Logger check out [http://chromelogger.com](http://chromelogger.com).

This module is designed to be used during development and not in production.  It is not thread safe, and you do not want to risk leaking sensitive data to users!

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
    console.get_header()
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

Using with tornado is slightly more complicated.  You have to make sure you are using your own custom request handler and that all your requests you want logged inherit from that.  Here is an example of how you could implement it

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

### Using with Flask

For using chromelogger with Flask, you can use a custom response-handler like this:

```python
# put this somewhere in your application setup

if app.debug:
    import chromelogger as console
 
    @app.after_request
    def chromelogger(response):
        header = console.get_header()
        if header is not None:
            response.headers.add(*header)
        return response
```

This ensures that chromelogger is only active, if the apllication runs in debug-mode.

## API Documentation

The chromelogger module exposes some of the chrome logger methods.  The others will be coming in a future release.

### chromelogger.log(*args)
### chromelogger.warn(*args)
### chromelogger.error(*args)
### chromelogger.info(*args)
### chromelogger.group(*args)
### chromelogger.group_end(*args)
### chromelogger.group_collapsed(*args)
### chromelogger.table(*args)

Logs data to the console.  You can pass any number of arguments just as you would in the browser.

```python
chromelogger.log('width', width, 'height', height)
```

### chromelogger.version

Outputs a string of the current version of this module

### chromelogger.get_header(flush=True)

Returns a tuple with the header name and value to set in order to transmit your logs.

If ``flush`` argument is ``True`` all the data stored during this request will be flushed.

This is the preferred way to use this module.  At the end of each request you should call this method and add this header to the response.

```python
import chromelogger
chromelogger.log(123)
chromelogger.get_header()
# ('X-ChromeLogger-Data', 'eyJyb3dzIjogW1tbMTIzXSwgIjxzdGRpbj4gOiAxIiwgWyJsb2ciXV1dLCAidmVyc2lvbiI6ICIwLjIuMiIsICJjb2x1bW5zIjogWyJsb2ciLCAiYmFja3RyYWNlIiwgInR5cGUiXX0=')
```

``chromelogger.get_header()`` will return ``None`` if there is no data to log.

### chromelogger.set_header = None

As an alternative to ``get_header`` you can specify a function that can be used to set a header.  The function should accept two parameters (header name and value).  Usage would look something like:

```python
def set_header(name, value):
    # do stuff here to set header
    pass

chromelogger.set_header = set_header
```

When ``chromelogger.set_header`` is not equal to ``None`` it will be called each time data is logged to set the header.  The class is a singleton so it will just keep overwriting the same header with more data as more data is added.

If you are going to use this you have to make sure to call ``chromelogger.reset()`` at the beginning of each request or at the end of each request in order to ensure the same data does not carry over into future requests.

### chromelogger.reset()

Clears out any data that has been set during this request.


