from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    requires = [l.strip() for l in fp.readlines() if l]

with open('README.md') as f:
    long_description = f.read()

setup(
    name='firev2-cli',
    version='0.1',
    author='edgesider',
    author_email='yingkaidang@gmail.com',
    description='command line tool for firev2',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=find_packages(),
    install_requires=requires,
    python_requires='>=3.5',

    entry_points={
        'console_scripts': ['fv2 = firev2_cli.fv2:main']
    }
)
