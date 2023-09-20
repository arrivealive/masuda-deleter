# Masuda Deleter
Masuda Deleter is a Django application to list and delete posts of Hatena AnonymousDiary.

![whole](https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/whole.png "whole")

# Features
* Fetching the posts by logging in and crawling the user pages of Hatena AnonymousDiary
* Searchable list of the posts
* Deleting the posts of Hatena AnonymousDiary selectively
* Graphs of posted datetime and posts with bookmarks 

# Requirement

* Docker <=20.10.16
* Docker Compose <=1.29.2
 
# Installation

Clone this repository. 
```bash
git clone https://github.com/oribeolive/masuda-deleter
```

Build Docker containers.
```bash
cd [masuda-deleter's directory]
docker-compose build
```

Execute below to generate a secret key for Django.
```bash
docker-compose run app python /code/masuda/generate_secret_key.py
```

Write Hatena id and password to .env.
```bash
cd backend/python/src/masuda
cp .env.example .env
vim .env
```

.env
```
HATENA_ID={Hatena ID}
HATENA_PASSWORD={PASSWORD}
```

Execute migration.
```
docker-compose run app python /code/masuda/manage.py migrate
```

Start containers.
```bash
docker-compose up -d
```

Access to http://localhost:8107/web/ after containers start.

# Usage
Access the posts page( /web/ ). Input target page numbers of Hatena AnonymousDiary and push the fetch(取込) button.

<img src="https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/fetch.png" width="50%" />

Wait several seconds to minutes and refresh the browser to display the list.

![list](https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/list.png "list")
 
Check the posts you want to delete.

<img src="https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/select.png" width="50%" />

Push the delete checked posts(「あとで消す」記事をついに消す) button.

<img src="https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/delete.png" width="50%" />

Push the delete(削除) button in the modal. The posts will be deleted in several seconds to minutes.

<img src="https://github.com/oribeolive/masuda-deleter/blob/readme_images/ss/delete_modal.png" width="50%" />
 
# Author
mu

https://twitter.com/loglesslove

# License
Masuda Deleter is under [MIT license](https://github.com/oribeolive/masuda-deleter/blob/main/LICENSE).

