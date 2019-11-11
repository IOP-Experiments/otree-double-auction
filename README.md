# Setup and start the application

NOTE: Please use oTree version 2.1.39 to run this application (use `pip3 install otree==2.1.39`)

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
 - `Redis` (optional, for bots. Please install Redis from <https://github.com/MicrosoftArchive/redis/releases>)

**Installation:**

```
pip install -r requirements_base.txt
```

**Start without bots:**

```
otree devserver
```

**Start with bots:**

> Make sure that Redis is running and `bot_enable` is set in `settings.py`

```
otree runprodserver1of2         // web
otree runprodserver2of2         // worker
```

**Video tutorial**

For inexperienced users we provide a video tutorial on how to set up the Double Auction and run a session with 10 participants (with bots enabled). In this tutorial, we show how to set up oTree and all requirements from scratch, clone this repository and start two production servers. You can find the tutorial here: <https://youtu.be/dsedZKKyFHQ>

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

## Data Export
Data can be exported from the admin panel. For a demonstration analysis, "example_analysis.do" for STATA is provided to graph the average trading price, the average share of bots and the number of trades per round. For this example analysis, the data has to be exported in wide format (i.e. "AllApps") and then imported to STATA manually. Note that this only works for one market per session.
## Creating a Session
Once you run the oTree server, you can create a session by clicking "Create Session" in the "Sessions" tab.

**General Notes**

You need to configure your session by clicking "Configure Session" and verify that the variables "Number of participants" and "market_size" is consistent.
Please acknowledge that the instructions as provided with the game are not completely flexible to all settings. E.g., the examples provided in the instructions might be inconsistent with your settings: We calculate the profit of a trade on the example of a valuation of 50 but if you choose to only distribute valuations from 1 to 10, you would want to change the examples in the instructions manually. In addition, if you disable the bot service, you should change the information about bots in the standard instructions.

**Configure Session**

- `Number of participants`: Enter the total amount of participants of your session. _Note that currently participants are evenly distributed to be buyer and seller. In the case of an odd total number of participants, one more buyer is added to the market._

- `bot_enable`: Check if you want bots enabled (note that you need to run redis). 
  `bot_enable (unchecked)`: Participants who leave the game by terminating their web session, will be indicated as "inactive" without further action. 
  `bot_enable (checked)`: Participants who leave the game by terminating their web session, will be replaced by a bot. A bot will make a bid equal to the valuation (buyer) or production cost at a random point in time. Bots will be indicated as "bot" to all other players. If the participants restore their web session, the respective bots leave the game again.
- `delay_before_market_opens`: Time in seconds before the market opens for trading.

- `market_size`: Maximum number of players in each market. If the market_size is smaller than the Number of participants, more markets within a session will be created.

- `num_of_test_rounds`: Number of test rounds.

- `production_costs_increments`: Production costs increments of the seller.

- `production_costs_max`: Maximum production costs of seller.

- `production_costs_min`: Minimum production costs of seller.

- `time_per_round`: Time in seconds of one round.

- `valuation_increments`: Valuation increments of the buyer.

- `valuation_max`: Maximum valuation of buyer.

- `valuation_min`: Minimum valuation of buyer.

- `participant_fee`: Fixed fee per participant.

- `real_world_currency_per_point`: Convertion rate of one point to real world currency.

**How are valuations and production costs distributed?**

The series of valuations (production costs) is created as following: The minimum valuation (production costs) is incremented by the specified parameter until the maximum valuation (production costs) is reached. The thereby generated values are then randomly assigned to the players. Each value is only assigned once among sellers and among buyers. When the number of players exceeds the number of values, the additional players receive a draw from another series, which is generated as described above.

## General Remarks
- Please make sure that the values of `Number of participants`, `market_size` coincide and do not create a contradiction. 
- The instructions are flexible such that the picture of the market can vary from market_sizes of 2 to 20. After 20 the number of sellers and buyers do not fit the variable but rather shows "a bunch of sellers and buyers".
- In case you want to change the valuations and/or production costs, please make sure to change the example calculations in the instructions.
