//scoin ico

pragma solidity ^0.5.1;

contract scoin_ico{
    
    uint public max_scoins = 100000;
    uint public usd_conv = 100;
    uint public scoins_total_bought = 0;
    
    mapping(address => uint) equity_scoins;
    mapping(address =>uint) equity_usd;
    
    
    modifier can_buy(uint invested){
        require (invested*max_scoins + scoins_total_bought <= max_scoins);
        _; //to indicate function which uses this modifier
    }
    
    function get_equity_scoins(address investor) external view  returns(uint){
        return equity_scoins[investor];
    }
    
    function get_equity_usd(address investor) external view  returns(uint){
        return equity_usd[investor];
    }
    
    
        
    function buy_scoins(address investor, uint usd_invested) external
    can_buy(usd_invested) {
        uint scoins_bought = usd_invested*usd_conv;
        equity_scoins[investor] += scoins_bought;
        equity_usd[investor] = equity_scoins[investor]/usd_conv;
        scoins_total_bought +=scoins_bought;
    }
    
    function sell_scoins(address investor, uint scoins_to_sell) external {
        //uint scoins_bought = usd_invested*usd_conv;
        equity_scoins[investor] -= scoins_to_sell;
        equity_usd[investor] = equity_scoins[investor]/usd_conv;
        scoins_total_bought -=scoins_to_sell;
    }
    
}