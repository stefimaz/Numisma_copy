import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List
import streamlit as st
from PIL import Image

from pinata import pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

st.set_page_config(page_title='Numisma: Diversify your crypto holdings', layout='wide')

st.title("Numisma. Crypto Index Portfolio Management")

st.sidebar.header('Portfolio selection')

portfolios_dict = {'Metadex Portfolio': {'Logo':'Images/Metadex_pie.jpg', 'Description':'The Metaverse Index is designed to capture the trend of entertainment, sports and business shifting to a virtual environment.', 'Creation':'For this Index Weight Calculation, we uses a combination of root market cap and liquidity weighting to arrive at the final index weights. We believe that liquidity is an important consideration in this space and should be considered when determining portfolio allocation.'}, 'Ventidex Portfolio':{'Logo':'Images/Ventidex_pie.jpg', 'Description':'', 'Creation':''}, 'Farmdex Portfolio':{'Logo':'Images/Farmdex_pie.jpg', 'Description':'', 'Creation':''}}

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


load_dotenv("api.env")
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# The contracts have to be loaded separately for eack Token index
# Load the contract once using cache
# Connects to the contract using the contract address and ABI
# loading contract fot --------- token index
@st.cache(allow_output_mutation=True)

def load_contract():

    # Load the contract ABI
    with open(Path('./Token_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi)
    
    return contract

# Load the contract
contract = load_contract()


################################################################################
# Buying the portfolio
################################################################################
st.title("Buy This Portfolio")

accounts = w3.eth.accounts 

# Use a streamlit component to get the address of the user
address = st.selectbox("Select your wallet", accounts)

amount = st.number_input("How many shares do you want to buy?", min_value=1, value=1, step=1)


if st.button("Buy Now"):

    # Use the contract to send a transaction to the purchase function
    tx_hash = contract.functions.transfer(address, amount).transact({
        "from": address, "gas": 1000000})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.success(dict(receipt))
st.markdown("---")

################################################################################
# Helper functions to pin files and json to Pinata
################################################################################


def pin_index(index_name, index_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(index_file.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": index_name,
        "image": ipfs_file_hash
    }
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash


def pin_index_report(report_content):
    json_report = convert_data_to_json(report_content)
    report_ipfs_hash = pin_json_to_ipfs(json_report)
    return report_ipfs_hash


################################################################################
# Register New Artwork
################################################################################
st.markdown("## Register Your Portfolio")
index_name = st.text_input("Enter the name of the artwork")
holder_name = st.text_input("Enter your name")
initial_index_value = st.text_input("Enter the initial index amount")
file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])
if st.button("Register Portfolio"):
    # Use the `pin_artwork` helper function to pin the file to IPFS
    index_ipfs_hash =  pin_index(index_name, file)
    index_uri = f"ipfs://{index_ipfs_hash}"
    tx_hash = contract.functions.registerPortfolio(
        address,
        index_name,
        holder_name,
        int(initial_index_value)
    ).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link")
    st.markdown(f"[Artwork IPFS Gateway Link](https://ipfs.io/ipfs/{index_ipfs_hash})")
st.markdown("---")

#############################################################

import streamlit.components.v1 as components

#components.iframe(
#    f"https://calendar.google.com/calendar/embed?src={input_calendar_id_number}&ctz=Europe%2FMadrid",
#    width=1200, height=800, scrolling=True)

# accounts = w3.ethereum.request('eth_requestAccounts')

# html_string = ''' <button class="enableEthereumButton">Enable Ethereum</button>
#                   <h2>Account: <span class="showAccount"></span></h2>'''

#st.markdown(html_string, unsafe_allow_html=True)
#st.markdown(html_string2, unsafe_allow_html=True)

# if st.button("Connect Metamask"):
#    w3.eth.accounts[0]
    
    

# import useState, useEffect from react
# import Calendar from './components/Calendar';
#
html_string = '''
<script language="javascript">
<script src="https://unpkg.com/@metamask/detect-provider/dist/detect-provider.min.js"></script>
<script type="text/javascript">
  const provider = await detectEthereumProvider()

  if (provider) {
    // handle provider
  } else {
    // handle no provider
  }
</script>

  '''

components.html(html_string)

def connect():    
      if provider == detectEthereumProvider():
            returns(accounts)
def accounts():
    
    provider.request({ method: "eth_requestAccounts" })

    if array != 0:
            account = accounts[0]
                    
    elif accounts.length > 0:
        
        console.log('account found', accounts)
        setAccount(accounts[0])
        
    else:
        alert('No account found')
      