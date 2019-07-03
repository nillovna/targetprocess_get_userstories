Get targetprocess assigned to user UserStories
===================

Script to get assigned to user targetprocess UserStories

Requirements
------------

```bash
pip install bs4 requests re
```

Variables
------------

`url` - targetprocess url - default from `TP_URL` environment variable

`user_email` - targetprocess users email - default from `TP_USER_EMAIL` environment variable

`user` - targetprocess user login - default from `TP_USER_EMAIL` environment variable

`password` - targetprocess user password - default from `TP_USER_PASS` environment variable

`base_dir` - directory to clone repos - default `./tp_stories`

Usage
--------------

```bash
./tp.py --url=tp.example.com --user_email=user@example.com --user=example_user --password=SUPER_SECRET_TP_USER_PASSWORD --base_dir tp_dir
```
