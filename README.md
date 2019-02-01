# Start the application

## Start with docker-compose
```
docker-compose up -d
```

### resetdb

In docker to resetdb you have to execute the following command
```
docker-compose exec web otree resetdb
```

_note: All docker containers must be running. After the resetdb the web container must be restarted._
