from setuptools import setup

# magic
setup(
    name='chromelogger',
    version='0.2.1',
    description='Python library for Chrome Logger extension.',
    long_description='Chrome Logger allows you to send server side data to the Google Chrome console by setting X-ChromeLogger-Data header',
    author='Craig Campbell',
    author_email='iamcraigcampbell@gmail.com',
    install_requires=['jsonpickle'],
    py_modules=['chromelogger']
)
