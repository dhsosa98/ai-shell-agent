import os
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstallCommand(install):
    def run(self):
        print("Installing ai-shell-agent...")
        install.run(self)
        print("ai-shell-agent installed successfully, run ai --help for usage information.")

setup(
    name='ai-shell-agent',
    version='0.1.6',
    description='A command-line AI chat application that helps perform tasks by writing and executing terminal commands with user supervision and by answering questions.',
    author='Lael Al-Halawani',
    author_email='laelhalawani@gmail.com',
    license='MIT',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    url='https://github.com/laelhalawani/ai-shell-agent',
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'python-dotenv==1.0.1',
        'langchain_openai==0.3.2',
        'langchain_experimental==0.3.4',
        'prompt_toolkit==3.0.50',
        'langchain-google-genai==2.0.11',
        'colorama==0.4.6',	
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'ai=ai_shell_agent.ai:main',
        ],
    },
)
