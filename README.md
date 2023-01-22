# Training project: Platform for publishing posts and comments on them with HTML templates.

## Technologies used:
Python3, Django Framework, MySQL, HTML, CSS

## Project description:

Platform for publishing posts and comments on them. It is possible to create groups with descriptions, attach posts to groups. You can also subscribe to authors.

The project was accessed via HTML templates, changing content only by authors, creating content only for authenticated applications. View content for everyone.

## How to launch a project:

Clone the repository and switch to it on the command line:

```
https://github.com/Damarkevich/hw05_final.git
```

```
cd hw05_final
```

Create and activate virtual environment:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from a file:

```
pip install -r requirements.txt
```

Run migrations:

```
python3 manage.py migrate
```

Start project:

```
python3 manage.py runserver
```

## Project author
```
Dmitrii Markevich
github: https://github.com/Damarkevich/
```