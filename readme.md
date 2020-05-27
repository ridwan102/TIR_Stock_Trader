# Welcome to TIR Stock Trader!
This website allows users to "Buy" and "Sell" stocks. A new user will register for a username and password
and automatically be directed to the homepage where it will list out the amount of cash available,
the amount invested and a list of all the individual stocks, prices, shares and totals.

A user will be able to get quotes for a stock and buy and sell stocks. Checks have been implemented for
the quote, buy and sell tabs to ensure a user inputs the correct stock symbol, the correct amount of shares
to buy/sell (a positive integer), and that a user does not over buy or over sell.

The history tab lists out every single transaction a user has committed with date and time, the stock bought/sold,
the price bought/sold at and the number of shares. 

Happy Trading! 

## Database and Deployment
All user information, buys/sells and transactions are stored in PostgreSQL accessible via Heroku. The web-app was also deployed on the Heroku server.

## Registration
Select the 'Registration' link and type a username and password. You will be prompted if the username is already taken or passwords do not match. Once registered, you will automatically be directed to your homescreen

<img src="https://media.giphy.com/media/W2R7ZXuJVKL3UAiCTx/giphy.gif" width="480">

## Login
If you are a Turing user, please login with your registered username and password. You will be prompted if they are incorrect.

<img src="https://media.giphy.com/media/jq0GCzNRvKzGq14xyC/giphy.gif" width="480">

## Homepage
On your homepage you can see your current portfolio (which company stock you own, how many shares and the price you bought them for). You can navigate back to this page by selecting the "Home" link at the top. 

<img src="https://media.giphy.com/media/YnMmTWb7iKcCmuiB4h/giphy.gif" width="480">

## Quote
If you desire to see the current price of the stock, please navigate to the "Quote" page. There you can enter the ticker symbol and see the current price that stock is trading for. This is real time information pulled from the IEX API.

<img src="https://media.giphy.com/media/kyFwF1rpXnHr3xNFLn/giphy.gif" width="480">

## Buy
Once you're ready to buy your desired stock, please navigate to the "Buy" page. Here, again like the "Quote" page, you will enter your stock ticker then select the number of shares to buy. You will be prompted if you do not have enough funds. Once the purchase is complete, you will be redirected to your Homepage to see your purchase

<img src="https://media.giphy.com/media/Y3kfXY8zuE11Hv1B4d/giphy.gif" width="480">

## Sell
If you decide you are ready to sell your stock, please navigate to the "Sell" page. Here you will be able to sell any of the stock in your portfolio for the given price. Be careful, you could make a profit or experience a loss! Select the desired stock from the drop-down and select the number of shares you would like to sell. You will be prompted if you type in more shares than you own. After selling, you will again be redirected to the Homepage and shown your updated portfolio. 

<img src="https://media.giphy.com/media/XdDzsLdybCvbp9ZMNE/giphy.gif" width="480">

## History
All of your transactions can be seen on the "History" page. Navigate there to see all your "Buys" and "Sells".

<img src="https://media.giphy.com/media/JQYNI1hhAoQAvHrRtx/giphy.gif" width="480">

## Logout
Once you are finishing trading for the day, please ensure you logout and you will be redirected to the login page.

<img src="https://media.giphy.com/media/ZBVJ4jiriuqJOvodrv/giphy.gif" width="480">
