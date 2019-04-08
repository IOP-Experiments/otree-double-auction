/*
This is an example .do-File for Stata to analyze the average prices per round as well as the amount of bots per round. 
Please note that this file only works for one session and for 1 market per session. It is aimed to provide you with a general idea about the data structur of the data export.
Further note that the data ought to be exported as "AllApps" in the wide format.
First import your .csv or excel file. It is commonly labeled as "all_apps_wide_DATE"
*/

keep if sessioncode == " " // Insert the sessioncode you want to analyze. This drops all other sessions.

forvalues x = 1/12{ // Insert the number of rounds + test rounds. 10 Rounds + 2 Test rounds is the default value. 
generate traded_price_r`x' = double_auction`x'playertrade //renames variable
generate was_bot_r`x' = double_auction`x'playeris_bot // renames variable
generate traded_r`x' = 0
}

forvalues x = 1/12{
replace traded_r`x' = 1 if !missing(traded_price_r`x')
}

collapse (mean) traded_price_r* was_bot_r* (count) traded_r* // takes the mean of the prices and calculates share of bots and counts the number of trades

forvalues x = 1/12{ // Insert the number of rounds + test rounds. 10 Rounds + 2 Test rounds is the default value. 
rename traded_price_r`x' average_price_r`x' // rename variable
rename was_bot_r`x' share_bots_r`x' // rename variable
rename traded_r`x' trades_r`x' // rename variable
}

forvalues x = 1/12{ // Insert the number of rounds + test rounds. 10 Rounds + 2 Test rounds is the default value. 
replace trades_r`x' = trades_r`x' / 2 // Two transactions make one trade
}

gen i=1 // helper variable
reshape long average_price_r share_bots_r trades_r, i(i) j(round) //reshapes to long

twoway (scatter average_price_r round, sort msymbol(smcircle)) (connected average_price_r round, msymbol(smx)), yline(60, lpattern(dash)) ytitle(Price) yscale(alt) yscale(range(10 110)) ylabel(10(10)110) xtitle(Rounds) xscale(range(1 12)) xlabel(1(1)12) title(Average Trade prices) legend(off) scheme(s1manual)

twoway (scatter share_bots_r round, sort msymbol(smcircle)) (connected share_bots_r round, msymbol(smx)), yline(60, lpattern(dash)) ytitle(Share Bots) yscale(alt) yscale(range(0 1)) ylabel(0(0.1)1) xtitle(Rounds) xscale(range(1 12)) xlabel(1(1)12) title(Average Share Bots) legend(off) scheme(s1manual)

twoway (scatter trades_r round, sort msymbol(smcircle)) (connected trades_r round, msymbol(smx)), yline(60, lpattern(dash)) ytitle(Nr. of Trades) yscale(alt) yscale(range(0 10)) ylabel(0(1)10) xtitle(Rounds) xscale(range(1 12)) xlabel(1(1)12) title(Number of Trades) legend(off) scheme(s1manual)
