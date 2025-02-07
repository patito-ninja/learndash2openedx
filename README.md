# learndash2openedx

Migrate LearnDash LMS data to Open edX <tutor> by [edly]()

## Setup

### Development install

```sh
sudo apt update && sudo apt install git python3-venv
mkdir tutor
cd tutor
python3 -m venv ENV
source ENV/bin/activate
pip install libyaml-dev
pip install "tutor[full]"
```

1. Install a local instance of <tutor>

[Installing Tutor](https://docs.tutor.edly.io/install.html)


```sh
export TUTOR_ROOT=$(pwd)
tutor dev launch
```

Create admin

```sh
tutor dev do createuser --staff --superuser yourusername user@email.com
```

Import demo course
```sh
tutor local do importdemocourse
```


Visit http://local.openedx.io:8000

2. Import LearDash LMS data

```sh
docker exec -i mysql_container mysql -uroot -pyour_root_password sys -e 'create database learndash;'
```


Open edX urls

- http://local.openedx.io:8000
- http://studio.local.openedx.io:8001
- http://meilisearch.local.openedx.io:7700
- http://apps.local.openedx.io:1999/authn
- http://apps.local.openedx.io:2001/authoring
- http://apps.local.openedx.io:1997/account
- http://apps.local.openedx.io:1984/communications
- http://apps.local.openedx.io:2002/discussions
- http://apps.local.openedx.io:1994/gradebook
- http://apps.local.openedx.io:1996/learner-dashboard
- http://apps.local.openedx.io:2000/learning
- http://apps.local.openedx.io:1993/ora-grading
- http://apps.local.openedx.io:1995/profile


#### LAter

```

Create a symlink from `docker-compose.override.yml` to tutor's `local` directory.
```
