import os
import requests
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

import tweepy
import config
from tweepy.auth import OAuthHandler

from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3 import Account
from web3 import middleware
from web3 import EthereumTesterProvider
from web3 import Account
from web3.auto import w3
from eth_account.messages import encode_defunct
from bip44 import Wallet
from eth_account import Account

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json
load_dotenv("api.env")

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

st.set_page_config(page_title='Numisma: Diversify your crypto holdings', layout='wide')

################################################################################
# Set keys
################################################################################

client = tweepy.Client(
    consumer_key=config.TWITTER_CONSUMER_KEY,
    consumer_secret=config.TWITTER_CONSUMER_SECRET,
    access_token=config.TWITTER_ACCESS_TOKEN,
    access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
)

client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)
#####################################################################

# Create a function called `generate_account` that automates the Ethereum
# account creation process
def generate_account(w3):
    """Create a digital wallet and Ethereum account from a mnemonic seed phrase."""
    # Access the mnemonic phrase from the `.env` file
    mnemonic = os.getenv("MNEMONIC")

    # Create Wallet object instance
    wallet = Wallet(mnemonic)

    # Derive Ethereum private key
    private, public = wallet.derive_account("eth")

    # Convert private key into an Ethereum account
    account = Account.privateKeyToAccount(private)

    # Return the account from the function
    return account

# Create a function called `get_balance` that calls = converts the wei balance of the account to ether, and returns the value of ether
def get_balance(w3, address):
    """Using an Ethereum account address access the balance of Ether"""
    # Get balance of address in Wei
    wei_balance = w3.eth.get_balance(address)

    # Convert Wei value to ether
    ether = w3.fromWei(wei_balance, "ether")

    # Return the value in ether
    return ether

# Create a function called `send_transaction` that creates a raw transaction, signs it, and sends it. Return the confirmation hash from the transaction
def send_transaction(w3, account, receiver, ether):
    """Send an authorized transaction."""
    # Set a medium gas price strategy
    w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

    # Convert eth amount to Wei
    wei_value = w3.toWei(ether, "ether")

    # Calculate gas estimate
    gas_estimate = w3.eth.estimateGas({"to": receiver, "from": account.address, "value": wei_value})

    # Construct a raw transaction
    raw_tx = {
        "to": receiver,
        "from": account.address,
        "value": wei_value,
        "gas": gas_estimate,
        "gasPrice": 0,
        "nonce": w3.eth.getTransactionCount(account.address)
    }

    # Sign the raw transaction with ethereum account
    signed_tx = account.signTransaction(raw_tx)

    # Send the signed transactions
    return w3.eth.sendRawTransaction(signed_tx.rawTransaction)

accounts = w3.eth.accounts 

# account = w3.eth.getAccounts().then(function(response) { accounts = response; console.log(accounts[0];} );
#web3.eth.getAccounts(function(response) { account = response; })
#console.log(accounts[0])
# st.write(account.address)

# The contracts have to be loaded separately for eack Token index
# Load the contract once using cache
# Connects to the contract using the contract address and ABI
# loading contract fot --------- token index
@st.cache(allow_output_mutation=True)

def load_contract():

    # Load the contract ABI
    with open(Path('./VentidexToken_plain_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS_VENTIDEXTOKEN_Plain")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi)
    
    return contract
# Load the contract
contract = load_contract()
################################################################################################
# Streamlit page building
#################################################################################################
st.image("./Images/Cryptos.jpeg")
st.title("Numisma")
st.title("Crypto Investment Index Portfolio Management")
# st.write("Learn about your options")
col1, col2, col3 = st.columns(3)
with col1:
    st.header("FarmDex")
    st.image('./Images/farmyield.jpg')
    with st.expander("See explanation"):
        st.write("""
         Yield farming is an investment strategy in decentralised finance or DeFi. It involves lending or staking your cryptocurrency coins or tokens to get rewards in the form of transaction fees or interest.
     """)
with col2:
    st.header("MetaDex")
    st.image('./Images/metaverse.jpg')
    with st.expander("See explanation"):
        st.write("""
         Metaverse is the technology behind a virtual universe where people can shop, game, buy and trade currencies and objects and more. Think of it as a combination of augmented reality, virtual reality, social media, gaming and cryptocurrencies.
     """)
with col3:
    st.header("VentiDex")
    st.image('./Images/venti.jpg')
    with st.expander("See explanation"):
        st.write("""
         Market cap allows you to compare the total value of one cryptocurrency with another so you can make more informed investment decisions. Cryptocurrencies are classified by their market cap into three categories: Large-cap cryptocurrencies, including Bitcoin and Ethereum, have a market cap of more than $10 billion.
     """)

st.markdown("---")

##################################################################################
share_detail_m = "BTC, ETH"


portfolios_dict = {'Metadex Portfolio': {'Contract':contract,'Price':0.30001,'Logo':'Images/Metadex_pie.jpg', 'Description':'Metaverse is the technology behind a virtual universe where people can shop, game, buy and trade currencies and objects and more. Think of it as a combination of augmented reality, virtual reality, social media, gaming and cryptocurrencies. This Index is designed to capture the trend of entertainment, sports and business shifting to a virtual environment.', 'Creation':'For this Index Weight Calculation, we uses a combination of root market cap and liquidity weighting to arrive at the final index weights. We believe that liquidity is an important consideration in this space and should be considered when determining portfolio allocation.','Pie':'Images/metaPIE.PNG'}, 
                   'Ventidex Portfolio':{'Contract':contract,'Price':0.30001,'Logo':'Images/Ventidex_pie.jpg', 'Description':'Market cap allows you to compare the total value of one cryptocurrency with another so you can make more informed investment decisions. Cryptocurrencies are classified by their market cap into three categories: Large-cap cryptocurrencies, including Bitcoin and Ethereum, have a market cap of more than $10 billion.', 'Creation':'Why and how we came up with this index','Pie':'Images/coinbasePIE.PNG'},
                   'Farmdex Portfolio':{'Contract':contract,'Price':0.30001,'Logo':'Images/Farmdex_pie.jpg', 'Description':'Yield farming is an investment strategy in decentralised finance or DeFi. It involves lending or staking your cryptocurrency coins or tokens to get rewards in the form of transaction fees or interest.', 'Creation':'Why and how we came up with this index','Pie':'Images/farmPIE.PNG'}}

#################################################################################
# Sidebar setup
###############################################################################
st.sidebar.header('Portfolio selection')

sorted_portfolio = ['Metadex Portfolio', 'Ventidex Portfolio', 'Farmdex Portfolio']

selected_portfolio = st.sidebar.selectbox("Available Portfolio", sorted_portfolio)

st.subheader('Current Portfolio Selection: ' + selected_portfolio)
st.image(portfolios_dict[selected_portfolio]['Logo'], width = 500)

st.subheader(" ")
st.header(f"{selected_portfolio}' Porfolio Description")
st.write(portfolios_dict[selected_portfolio]['Description'])

st.header(f"{selected_portfolio}' Creation strategy")
st.write(portfolios_dict[selected_portfolio]['Creation'])

st.markdown("---")


################################################################################
# Buying the portfolio
################################################################################
st.title(f"Buy The {selected_portfolio}")

st.image(portfolios_dict[selected_portfolio]['Pie'])


receiver = "0x33dEA8432248DD86680428696975755715a85fFC"
# Use a streamlit component to get the address of the user
address = st.selectbox("Select your wallet", accounts)

balance = get_balance(w3, address)
st.subheader(f'You have ETH: {balance:.3f} in this wallet')

amount = st.number_input("How many shares do you want to buy?", min_value=1, value=1, step=1)
st.subheader(f"You have selected {amount} shares")

st.markdown(f" You will get Total {share_detail_m} for each share")

share_price = portfolios_dict[selected_portfolio]['Price']
cost = (share_price) * amount

st.write(f'Your total is {cost} ETH')


if st.button("Buy Now"):
    # Use the contract to send a transaction to the purchase function
    
    ## need a other function to take in count the amount od eth to be sent!!
    #########################################################################
    
    # transaction_hash = send_transaction(w3, account, receiver, cost)

    
    ##########################################################################
    tx_hash = contract.functions.mint().transact({
        "from": address, "gas": 1000000})
    
    
    

    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write("Congratulation on your purchase, Here is your Blockchain receipt")
    st.success(dict(receipt))
st.markdown("---")


################################################################################
# Helper functions to pin files and json to Pinata
################################################################################
def pin_artwork(index_name, artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file)

    # Build a token metadata file for the artwork
    token_json = {
        "name": index_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash


def pin_appraisal_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash


################################################################################
# Register New Porfolio
################################################################################
st.markdown("## Register Your Portfolio")
index_name = st.text_input("Enter the name of your portfolio")
holder_name = st.text_input("Enter your full name")
initial_index_value = cost * 2800

#file = portfolios_dict[selected_portfolio]['Logo']
#file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"]) ## have to have the getvalue() function in pin_artwork
file = st.camera_input("Picture recording")

if st.button("Register Index Portfolio"):
    # Use the `pin_artwork` helper function to pin the file to IPFS
    artwork_ipfs_hash =  pin_artwork(index_name, file)
    artwork_uri = f"ipfs://{artwork_ipfs_hash}"
    tx_hash = contract.functions.registerPortfolio(
        address,
        index_name,
        holder_name,
        int(initial_index_value)
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.success(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{artwork_ipfs_hash})")
st.markdown("---")

################################################################################
# Display a Token
################################################################################
st.markdown("## Display information about my Token")

#selected_address = st.selectbox("Select Account", options=accounts)

tokens = contract.functions.balanceOf(address).call()

st.write(f"This address owns {tokens} tokens")

# token_id = st.selectbox("Index Portfolio Tokens", list(range(tokens)))

if st.button("Display"):

    # Use the contract's `ownerOf` function to get the art token owner
    owner =  holder_name
    #contract.functions.ownerOf(tokens).call()

    st.write(f"The token is registered to {owner}")
    
    # value of the portfolio
    
    st.write(f"Your portfolio is valued at ${initial_index_value}")

    # Use the contract's `tokenURI` function to get the art token's URI
    
    #token_uri =  contract.functions.tokenURI(tokens).call()

   # st.write(f"The tokenURI is {token_uri}")
    st.image(portfolios_dict[selected_portfolio]['Pie'])

################################################################################
# Identify top twitter usernames on crytocurrency
################################################################################

# @cz_binance is the founder and CEO of Binance 
# @MMCrypto is one of the world's elite group of traders
# @aantonop is one of the world's foremost trusted educators of Bitcoin

popular_twitter_usernames = ("metaversenoir","cz_binance", "mmcrypto", "aantonop")

username_choice = st.sidebar.selectbox("SELECT POPULAR TWITTER USERNAMES", (popular_twitter_usernames))

metaversenoir = '1450997150477815808'
cz_binance = '902926941413453824'
mmcrypto = '904700529988820992'
aantonop = '1469101279'       

if username_choice == 'metaversenoir':
    id = metaversenoir
if username_choice == 'cz_binance':
    id = cz_binance
if username_choice == 'mmcrypto':
    id = mmcrypto
if username_choice == 'aantonop':
    id = aantonop       
    
# tweets = client.get_users_tweets(id=id, tweet_fields=['context_annotations','created_at','geo'])

# for tweet in tweets.data:
#     st.sidebar.write(tweet)

    
st.title(f'@{username_choice}')    
col1, col2, col3 = st.columns(3)
with col1:
    st.header("Top Tweeter")
    st.image('./Images/twitter.jpg')
    tweets = client.get_users_tweets(id=id, tweet_fields=['context_annotations','created_at','geo'])
    with st.expander("See Tweets"):
        for tweet in tweets.data:
            st.write(tweet)
with col2:
    st.header("Likes")
    st.image('./Images/like.jpg')
    tweets = client.get_liked_tweets(id=id, tweet_fields=['context_annotations','created_at','geo'])
    with st.expander("See Liked Tweets"):
        for tweet in tweets.data:
            st.write(tweet)
with col3:
    st.header("Followers")
    st.image('./Images/followers.jpg')
    users = client.get_users_followers(id=id, user_fields=['profile_image_url'])
    with st.expander("See List of Potential Clients"):
        for user in users.data:
            st.write(user.name)

            st.markdown("---")
    