from setuptools import setup

setup(
    name='tagcounter',
    version='1.0',
    author='Ushakova',
    packages=['tagcounter'],
    description='Программа для подсчета и сохранения количества тегов на сайте',
    package_data={'': []},
    entry_points={'console_scripts': ['tagcounter = tagcounter.tagcounter:main']},
)