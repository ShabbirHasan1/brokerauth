import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='brokerauth',
    version='1.9',
    author='Pratik Bhopal',
    author_email='pratikbhopal@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pratiksgith/brokerauth',
    project_urls = {
        "Bug Tracker": "https://github.com/pratiksgith/brokerauth/issues"
    },
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['django-allauth','websocket-client','smartapi-python==1.2.9'],
)