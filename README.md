# Masuda Deleter
Masuda Deleter is a Django application to list and delete posts of Hatena AnonymousDiary.
 
# Features
* Fetching the posts by logging in and crawling the user pages of Hatena AnonymousDiary
* Searchable list of the posts
* Deleting the posts of Hatena AnonymousDiary selectively
* Graphs of posted datetime and posts with bookmarks 

# Requirement

* Docker <=20.10.16
* docker-compose <=1.29.2
 
# Installation

Clone this repository. 
```bash
git clone https://github.com/arrivealive/masuda-deleter
```

Write Hatena id and password to .env.
```bash
cd [masuda-deleter's directory]/backend/python/src/masuda
cp .env.example .env
vim .env
```
.env
```
HATENA_ID={Hatena ID}
HATENA_PASSWORD={PASSWORD}
```

Build and start containers.
```bash
cd [masuda-deleter's directory]/
docker-compose up -d --bulid
```

Access to http://0.0.0.0:8001/web/ after containers start.

# Usage
Access the posts page( /web/ ). Input target page numbers of Hatena AnonymousDiary and push the fetch(取込) button.


Wait several seconds to minutes and refresh the browser to display the list. 

 
Check the posts you want to delete.


Push the delete checked posts(「あとで消す」記事をついに消す) button.


Push the delete(削除) button in the modal. The posts will be deleted after several seconds to minutes.

 
# Author
mu

https://twitter.com/loglesslove

# License
Masuda Deleter is under MIT license.
 