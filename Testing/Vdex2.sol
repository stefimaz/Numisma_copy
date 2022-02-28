// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Vdex2 is ERC20 {

    address public admin;

    constructor() ERC20("vdextest", "VDXT") {
        _mint(msg.sender, 100000 * 10 ** decimals());
        admin = msg.sender;
    }

    function mint (address to, uint amount) external {
        require(msg.sender == admin, "Only admin can create new token");
        _mint(to, amount);
    }

}