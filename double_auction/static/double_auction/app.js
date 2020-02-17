$(function() {
    if (seconds_to_start > 0) {
	$('.otree-timer').css({"display": "none"})
    }
    var currentDate = new Date();
    var milliseconds = Math.floor(seconds_to_start * 1000);
    $('#start-delay-timer').countdown(currentDate.valueOf() + milliseconds)
	.on('update.countdown', function (event) {
	    // %-N is "Total count of minutes till the end, non-padded"
	    // %S is seconds left
	    var format = '%-S';
	    $(this).html(event.strftime(format));
	})
	.on('finish.countdown', function (event) {
	    if (daForm) {
		daForm.started = true
	    }
	    $('.otree-timer').css({"display": "block"})
	});
});


var submitForm = function(event) {
    var el = document.getElementById("form");
    if (el.checkValidity()) {
        var formValue = parseInt(document.querySelector('[name=offer]').value);
        if (player.role==="seller") {
            var betterBids = data.bids.filter( function(bid) { return bid.value > formValue; });
        } else {
            var betterBids = data.asks.filter( function(ask) { return ask.value < formValue; });
        }
        if (betterBids.length) {
            modal.type = "bid";
            modal.strings = getStringsFor(player.role)
            modal.value = formValue;
            modal.otherValue = betterBids[0].value;
            modal.result = modal.otherValue;
            openModal()
        } 
        sendmessage(formValue);
    }
    else {
        el.reportValidity()
    }
}

function getStringsFor( type ) {
    return {
        seller: {
            valueType: "ask",
            otherType: "bid",
            comparison: "higher",
        },
        buyer: {
            valueType: "bid",
            otherType: "ask",
            comparison: "lower",
        }
    }[type];
}

var modal = new Vue({
    el: '#confirmModal',
    data: {
        type: 'accept',
        confirm: false,
        strings: getStringsFor("seller"),
        value: 0,
        playerId: null,
        playerIdInGroup: null,
        result: 0,
        otherValue: 0,
    },
    methods: {
        sendIt: function(event) {
            if ( data.bids.filter(bid => bid.id === this.playerId).length || data.asks.filter(ask => ask.id === this.playerId).length )
                sendmessage(this.value, this.playerId)
            else {
                toastr.error("Sorry, the offer is not available anymore.")
                closeModal()
            }
        }
    }
})

var data = {
    bids: [],
    asks: [],
};

var info = new Vue({
    el: '#info',
    data: {
        playerId: player.id
    }
});

var app = new Vue({
    el: '#app',
    data: {
        table: {
            rows: []
        },
        playerId: player.id,
        playerRole: player.role,
        maxValue: player.maxValue,
        minValue: player.minValue,
        bestBids: {
            seller: 0,
            buyer: 0
        },
        lock: null,
        match: player.match
    },
    methods: {
        accept: function(bid) {
            modal.type = "accept";
            modal.playerId = bid.id;
            modal.playerIdInGroup = bid.id_in_group;
            modal.value = bid.value;
            modal.result = bid.value;
            // openModal()
            sendmessage(bid.value, bid.id)
        },
        isAcceptable: function(entry, entryRole) {
            var otherRole = entryRole === "buyer" ? "seller" : "buyer";
            var playerHasEnoughValuation = this.playerRole === "buyer" ? entry.value <= this.maxValue : entry.value >= this.minValue;
            var isBestBid = entry.value === this.bestBids[entryRole];
            var isRoleCorrect = this.playerRole === otherRole;
            var hasNoMatch = !this.match;

            return isRoleCorrect && isBestBid && playerHasEnoughValuation && hasNoMatch;
        }
    }
})

var participantTable = new Vue({
    el: '#participant_table',
    data: {
        participants: player.participants,
        playerId: player.id
    }
})

var daForm = new Vue({
    el: '#da_form',
    data: {
        value: player.value,
        lock: null,
        started: seconds_to_start > 0 ? false : true,
        match: player.match
    },
    methods: {
        submitForm: submitForm
    }
})

function updateDomFromWsObj(obj) {

    switch (obj.type) {
        case "go":
            document.getElementById("form").submit()
            break;

        case "action.match":

            if (obj.buyer === player.id || obj.seller === player.id) {
                daForm.match = true;
                app.match = true;
                toastr.success("You are trading!")
            }

            // set match flag on bid and ask
            data.bids.filter( bid => bid.id === obj.buyer)[0].match = true;
            data.asks.filter( ask => ask.id === obj.seller)[0].match = true;

            transformToTable(app.table, data.asks, data.bids)

            // remove ask and bid after 3 sec
            setTimeout( () => {
                data.bids = data.bids.filter( bid => bid.id !== obj.buyer)
                data.asks = data.asks.filter( ask => ask.id !== obj.seller)
                prepareDataForTable(data)
                transformToTable(app.table, data.asks, data.bids)
            }, 3000)

            break;

        case "action.clear":
            if (obj.player_id === player.id) {
                daForm.value = null;
                daForm.lock = null;
                app.lock = null;
                toastr.success("Bid cleared")
            }
            data.bids = data.bids.filter( elem => {
                return elem.id !== obj.player_id;
            })
            data.asks = data.asks.filter( elem => {
                return elem.id !== obj.player_id;
            })
            break;

        case "action.error":
            if (player.role==="buyer") {
                toastr.error("There is a better bid than yours")
            } else {
                toastr.error("There is a lower offer")
            }
            break;

        case "action.status":
            participantTable.participants.forEach( function(p) {
                if (p[0].id === obj.player_id) {
                    p[0].status = obj.status;
                } else if (p[1].id === obj.player_id) {
                    p[1].status = obj.status;
                }
            })
            break;

        default: 

            updateOrCreate(data, obj)
            if (obj.player_id === player.id) {
                daForm.lock = true;
                app.lock = true;
                daForm.value = obj.value;
            }
    }

    prepareDataForTable(data)
    transformToTable(app.table, data.asks, data.bids)


    // console.log(app)
    console.log(data)
    // #console.log("player ", player);
}

function transformToTable(table, row1, row2) {
    table.rows = [];
    for (var i=0; i<Math.max(row1.length, row2.length); i++) {


        var r1 = row1[i] ? row1[i] : null;
        var r2 = row2[i] ? row2[i] : null;

        table.rows.push({
            r1: r1,
            r2: r2
        })

    }
}

function updateOrCreate(list, obj) {

    key = obj.type === "action.value.seller" ? "asks" : "bids";
    var existingElement = list[key].filter(el => el.id === obj.player_id)[0] || null;

    if (existingElement) {
        existingElement.value = obj.value;
    }
    else {
        list[key].push({
            id: obj.player_id,
            id_in_group: obj.player_id_in_group,
            value: obj.value
        })
    }

}

function prepareDataForTable(data) {
    calculateBestBids(data, "seller")
    calculateBestBids(data, "buyer")
    data.bids.sort( function(a, b) {
        return a.value-b.value
    })
    data.asks.sort( function(a, b) {
        return b.value-a.value
    })
}

function calculateBestBids(data, type) {
    key = type === "seller" ? "asks" : "bids";
    minOrMax = type === "seller" ? "min" : "max";
    app.bestBids[type] = Math[minOrMax].apply(
        null,
        data[key]
            .filter( function (dataElement) { return !dataElement.match })
            .map( function (dataElement) { return dataElement.value; } ));
}

function openModal() {
    $('#confirmModal').modal();
}
function closeModal() {
    $('#confirmModal').modal('hide');
}

