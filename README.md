# Setup and start the application

Clone this repo:
```
git clone https://github.com/IOP-Experiments/otree-double-auction.git
```


There are two possible ways to setup and use this application:

- classical oTree installation
- run application in Docker container

## Classical Setup

**Requirements:**

 - `Python`
 - `Redis` (optional, for bots)

**Installation:**
```
pip install -r requirements_base.txt
```

**Start without bots:**
```
otree devserver
```

**Start with bots:**

> Make sure that redis is running and `bot_enable` is set in `settings.py`

```
otree runprodserver1of2         // web
otree runprodserver2of2         // worker
```


## Start with docker-compose

**Requirements:**

 - Docker
 - docker-compose


**Start**
```
docker-compose up -d
```

**Reset database**

In docker to `resetdb` you have to execute the following command
```
docker-compose exec web otree resetdb
```

_note: All docker containers must be running. After the resetdb the web container must be restarted._
