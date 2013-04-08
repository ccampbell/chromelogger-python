from setuptools import setup

# magic
setup(
    name='chromelogger',
    version='0.2.1',
    description='Python library for Chrome Logger extension.',
    long_description='Chrome Logger allows you to send server side logs to the Google Chrome console.',
    author='Craig Campbell',
    author_email='iamcraigcampbell@gmail.com',
    url='https://github.com/ccampbell/chromelogger-python',
    download_url='https://github.com/ccampbell/chromelogger-python/zipball/0.2.1',
    license='Apache 2.0',
    install_requires=['jsonpickle'],
    py_modules=['chromelogger'],
    platforms=["any"]
)
