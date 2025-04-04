from setuptools import setup, find_packages

setup(
    name="side_quest_py",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "python-ulid==3.0.0",
        "Flask==3.0.2",
        "Flask-SQLAlchemy==3.0.5",
        "SQLAlchemy==2.0.40",
        "typing-extensions==4.13.0",
        "python-dotenv==1.0.1",
    ],
    python_requires=">=3.8",
) 